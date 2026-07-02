# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

METRo (Model of the Environment and Temperature of Roads) — a road weather forecast tool from Environment Canada / Centre météorologique canadien. Given RWIS road-station observations plus an atmospheric forecast, it predicts road surface conditions (freezing rain, snow accumulation, frost, thaw). GPL-2+, mostly Python 3 with a Fortran physics core bridged to Python via SWIG/C. Packages under `src/frontend/external_lib` are third-party, not METRo code.

## Build, install, run

System deps (see `INSTALL`, `.gitlab-ci.yml`): `python3`, `python3-dev`, `python3-numpy`, `python3-libxml2`, `gfortran`, `swig`, `cpio`.

- Build + install into a destination: `./setup.sh <destination_path>` — builds the Fortran model via `scripts/do_macadam`, then copies `usr/`, docs, and wires up `<destination_path>/metro/usr/bin/metro` (symlink to `metro.py`). The install lands at `<destination_path>/metro`, not `<destination_path>` directly.
- Rebuild only the Fortran/SWIG core: `cd src/model && ../../scripts/do_macadam <dest>`. `../../scripts/do_macadam clean` removes build artifacts (`_macadam.so`, `*.o`, `macadam.py`, `macadam_wrap.c`). Honors `$PYTHON_INCLUDE` and `$FC` env vars when auto-detection (`python3-config`, `gfortran`/`g77`) guesses wrong.
- Run: `python3 <install>/usr/bin/metro [options]`. Full flag list is `CFG_SHORT_OPTIONS`/`CFG_LONG_OPTIONS` in `src/frontend/metro_config.py` (e.g. `--input-forecast=`, `--input-observation=`, `--input-station=`, `--output-roadcast=`, `--config=`, `--generate-config=`, `--verbose-level=`, `--lang=`, `--selftest`).
- Selftest (single end-to-end run against bundled fixtures): `--selftest` reads `usr/share/metro/data/selftest/{forecast,observation,station}.xml` and writes `roadcast.xml` alongside them. Pass/fail is a diff against `roadcast_reference.xml`, ignoring the `<production-date>` element:
  `diff --ignore-matching-lines='.*<production-date>.*</production-date>' roadcast.xml roadcast_reference.xml`

## Test suite

`usr/share/metro/data/test_suite/test_suite.py` runs the numbered regression cases (`case001`, `case002`, ...), each a self-contained directory of `forecast.xml`/`observation.xml`/`station.xml`/`config.json`/`roadcast_reference.xml`. It must be run from inside that directory, against an *installed* METRo (it shells out to the `metro` executable). There is no pytest/unittest suite in this repo — correctness is validated exclusively through these end-to-end XML-in/XML-out cases.

- All cases: `python3 test_suite.py`
- Specific case(s): `python3 test_suite.py -c 12 34`
- Skip case(s): `python3 test_suite.py -s 12 34` (`-c` and `-s` are mutually exclusive)
- Verbose: `-v`
- Custom error tolerance (default `0.01`): `-e 0.05`
- Clean generated output files: `python3 test_suite.py --clean` (meaningful only with `-v`)

Each case's `config.json` has `addition_to_command_line` (extra flags passed to `metro` for that case), `expected_running_result` (`SUCCESS`/`FAILURE`), and an optional per-case `error_tolerance`.

## Developing against `src/` without reinstalling

`./init_devel.sh` (one-time) symlinks the repo so `metro` runs straight from the checkout instead of via a `setup.sh` install:
- `src/frontend/model -> usr/share/metro/model`
- `usr/bin/metro -> src/frontend/metro.py`

The Fortran model still needs to be compiled once (`cd src/model && ../../scripts/do_macadam`) before `usr/bin/metro` will import cleanly, since it does `from model import macadam` (the compiled SWIG extension).

## Architecture

**Pipeline of modules driven by config.** `metro.py` reads `INIT_MODULE_EXECUTION_SEQUENCE` from `metro_config.py` — a fixed, hardcoded ordered list of module names — and dynamically imports/instantiates each from `src/frontend/executable_module/`. `metro_execute_module()` then runs them strictly in sequence: `object.start()` → `object.send_data_to(next)` → `object.stop()`. Every module subclasses `Metro_module` (`executable_module/metro_module.py`) and must implement `get_receive_type()`/`get_send_type()` (types: `NONE`, `INPUT`, `DATA_IN`, `DATA_OUT`, `DOM_OUT`); `metro.py` checks each handoff and aborts via the logger on a type mismatch. Data flows between modules through a shared `infdata_container` keyed by string (`'FORECAST'`, `'OBSERVATION'`, `'STATION'`, ...).

The sequence itself: read → validate → string2dom for each of forecast/observation/station, `metro_dom2metro` (DOM → internal matrix form), several `metro_preprocess_*` stages (QA/QC, sun/shadow via `fsint2`, interpolation, combining forecast+observation into one matrix), `metro_model` (the physics core), `metro_postprocess_*` (subsampling/rounding), `metro_metro2dom`, `metro_write_roadcast`.

**Physics core is Fortran, not Python.** `src/model/*.f` (`grille`, `coupla`, `balanc`, `constPhys`, `lib_therm`, `lib_gen`, `flxsurfz`, `initial`, `array2matrix`) implement the actual road-temperature model. `scripts/do_macadam` compiles them with gfortran, SWIGs `macadam.i`/`macadam.c` into a Python extension (`_macadam.so` + generated `macadam.py`), and copies both into `usr/share/metro/model/`. Only `executable_module/metro_model.py` touches it, via `from model import macadam` and calls like `macadam.Do_Metro(...)`, `macadam.get_ra()`, `macadam.get_sst()` — plain array in/out, no Python-side OOP wrapper.

**Data model.** `data_module/metro_data.py`'s `Metro_data` wraps one 2D numpy matrix (`npMatrix`) plus named columns — the tabular form of forecast/observation/station data. `metro_data_collection*.py` aggregate multiple `Metro_data` objects. `metro_infdata.py`/`metro_infdata_container.py` are the generic key → typed-value container passed between pipeline modules; a `Metro_data` table is one possible payload inside an infdata slot, not the same abstraction.

**Configuration** (`metro_config.py`) merges three layers in order — hardcoded defaults → config file (Plist-XML, read/written via `external_lib/Plist_config`) → command line — with each key tagged `CFG_HARDCODED`/`CFG_CONFIGFILE`/`CFG_COMMANDLINE` so callers of `metro_config.get_value()` don't need to know the source. `--generate-config=<file>` dumps the merged config back out as a config file.

**XML I/O is pluggable but single-implementation.** `toolbox/metro_xml.py` loads an XML backend by name at runtime (`metro_xml.init(sMetro_xml_lib)`); only `toolbox/metro_xml_libxml2.py` (python-libxml2 bindings) exists, and only it supports validation. Missing bindings fail fast at startup with an explicit "install python-libxml2" error, before the module pipeline runs.

**i18n**: `metro_util.init_translation('<module>')` is called at the top of most modules for gettext-based `_()` strings; `metro.py` normalizes `LANGUAGE`/`LC_ALL` to `en`/`fr` before anything else executes. `.po`/`.mo` handling lives in `scripts/{check_translation,copy_msgid_msgstr,create_mo}.py`.

## Optional features added on top of upstream METRo 4.0.0

End-user usage for both of these is documented in `README-DEV.md`. Both required touching the compiled Fortran/C core (`src/model/`), not just Python — a rebuild (`do_macadam`) is required after editing them.

**Freezing point of water in the forecast** (`--use-freezing-point-forecast`, optional `<tfz>` element per forecast prediction). Wires up a `FP` parameter that already existed throughout the Fortran physics (`SRFHUM`/`VERGLAS`/`RODCON` in `balanc.f`/`coupla.f`, documented there as "Frozing point (C)") but was hardcoded to a scalar `0.0` in `macadam.c`. `FP` is now an array indexed by timestep in Fortran, threaded from Python as `TFZ` (config key, XML tag `tfz`, matrix column) through `metro_preprocess_interpol_forecast.py`'s `__interpolate_TFZ` (defaults to `0.0`, i.e. pure water, when absent — this is what makes the feature backward compatible) and `metro_model.py`'s `Do_Metro` call. Do not confuse `FP` (this, an input) with the pre-existing output array `dpFP`/roadcast `<fp>` (phase-change flux, W/m²) — same letters, unrelated quantity, both are the original authors' naming.

**Custom road layer type** (`<type>custom</type>` + `<capacity>`/`<conductivity>` in a station file's `<roadlayer>`, material code 5 alongside the 4 built-ins in `XML_STATION_ROADLAYER_VALID_TYPE`). Adds a 5th branch to the material lookup in `grille.f` (`MAT(k).eq.5`) that reads capacity/conductivity from new `USERCS`/`USERKS` arrays instead of a hardcoded value, threaded from Python's `metro_preprocess_qa_qc_station.py` (`__check_custom_roadlayer`, also where validation lives) through `metro_model.py` to `Do_Metro`'s new `dpLayerCapacity`/`dpLayerConductivity` params.

Custom capacity/conductivity are range-validated (`fCUSTOM_CAPACITY_MIN/MAX`, `fCUSTOM_CONDUCTIVITY_MIN/MAX` in `metro_preprocess_qa_qc_station.py`: capacity `[1e6, 1e7]` J/m³/K, conductivity `[0.05, 3.5]` W/m/K). This is not cosmetic input validation — `grille.f`'s ground grid is a fixed-size array with no bounds checking, and values outside this empirically-determined range crash the compiled core with a segfault instead of failing gracefully. If you touch these bounds, re-verify by sweeping conductivity/capacity values and checking the exit code, not just the selftest — a segfault won't show up in the regression suite's normal cases.

**Grip / traction index** (`--output-grip-index`, optional `<grip>` element per roadcast prediction, 0.0-1.0). Pure Python, no Fortran/C changes — a new `src/frontend/toolbox/metro_grip.py::compute_grip(rc, water_mm, snow_cm, surface_temp_c, freezing_point_c)` derives grip from RC/RA/SN/ST (already computed by the model) plus the effective freezing point (`TFZ`, from the feature above; `0.0` if unused). Wired into `metro_model.py`'s `__create_roadcast_collection` via `roadcast.append_matrix_col('GRIP', ...)` — note it's `append_matrix_col`, not `set_matrix_col`: extended roadcast items are never included in the `Metro_data` column list at construction time (`lItems = lStandard_items`, see the `# FFTODO append all lExtended_items to metrodata` comment there — a pre-existing gap in upstream, not something introduced here), so a genuinely new extended column must be appended, not set. `TL`/`--output-subsurface-levels` is the precedent this whole feature mirrors.

STATUS: unlike the two features above, this one is a heuristic with no physical ground truth to verify against — there is no equivalent of `--selftest`'s reference file for "is this grip value correct." The constants in `metro_grip.py` (dry/wet/ice/icing-rain grip levels, saturation depths, cold-recovery range) are a first-pass qualitative model, explicitly not yet calibrated against real sensor or field data. Before treating grip output as reliable, validate against real observations (e.g. RWIS friction sensors) and expect to retune the constants.

**JSON roadcast output** (`--output-roadcast-json=<file>`). Pure Python, independent of the XML path — new module `metro_write_roadcast_json.py` (subclasses `Metro_write`, appended to `INIT_MODULE_EXECUTION_SEQUENCE` right after `metro_write_roadcast`) reads the same post-rounding `Metro_data` (`roadcast_data.get_subsampled_data()`) that `metro_metro2dom.py` turns into XML, and serializes it via new `toolbox/metro_json.py::metro_data_to_dict()`, reusing the `NAME`/`XML_TAG`/`DATA_TYPE` item definitions so JSON and XML use identical field names/values. Multi-column fields (`TL`) are skipped with a warning — not supported yet.

**Refined precipitation type** (`--output-precip-type`, optional `<precip-type>` roadcast element: 1=rain, 2=snow, 3=freezing rain/drizzle). The physics core and the existing `PI` column (rain/snow) are untouched — do not be tempted to add a 3rd value directly into `PI`. `PI` goes through `metro_util.interpolate()` (linear) then `numpy.around()`, which only produces valid output because there are exactly 2 adjacent codes; interpolating between codes `1` and a hypothetical `3` can round to a spurious `2` (snow) partway through. This was an actual regression caught by `test_suite.py` while building this feature (5 cases failed) — the fix was to add a *separate* binary `PI_FREEZING` column in `metro_preprocess_interpol_forecast.py::__interpolate_PI` (safe to interpolate the same way, since it's still only 2 values), and combine `PI`+`PI_FREEZING` into the refined 1/2/3 value only at roadcast-build time in `metro_model.py`, after both have already been safely interpolated/rounded. If you touch `__interpolate_PI` again, keep this constraint in mind.

**Config file as JSON** (`--config`/`--generate-config` autodetect `.json` by extension, no new flag). `metro_config.py::read_config_file`/`write_config_file` branch on `_is_json_config_filename()`; JSON is a flat `{KEY: value}` object via stdlib `json`, everything else still goes through the existing `Plist_config` (`external_lib/Plist_config/`). JSON output has no comments (unlike the Plist writer's per-key `COMMENTS`).

**Unit tests** (`tests/`, stdlib `unittest`, no new dependency — matches `.gitlab-ci.yml`, which doesn't install pytest). Run via `python3 -m unittest discover -s tests -t .`. Covers `metro_config.overlay_config`, `Metro_data` matrix ops, several `metro_util` helpers, and `metro_grip.compute_grip` — all previously only reachable indirectly through `test_suite.py`'s end-to-end XML diffs. `tests/__init__.py` is not boilerplate: it deliberately imports `metro_error` before anything else, because `metro_error.py` and `toolbox/metro_util.py` import each other (`metro_util` imports `metro_error` partway through its own body, before its own `init_translation` is defined further down the same file; `metro_error` needs `init_translation` immediately at import time). Importing `metro_util` as the very first module in a fresh process reliably crashes with `AttributeError: partially initialized module` — production code only avoids this by accident, because something else (`metro_config_validation.py`) happens to import `metro_error` first. Two real, pre-existing bugs surfaced while building this test suite and are now fixed: `metro_util.init_translation()` crashed outright (rather than degrading) for any module without a pre-built `.mo` file (fixed with `gettext.translation(..., fallback=True)`), and `usr/share/locale/en/LC_MESSAGES/metro_data.po` had a translation with a truncated `%s` → `%` format specifier that raised `ValueError: incomplete format` on a real (if rare) error path.

All features above leave default behavior byte-for-byte unchanged (verified against `--selftest` and the full `test_suite.py` suite) when unused.
