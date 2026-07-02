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

Both features leave default behavior byte-for-byte unchanged (verified against `--selftest` and the full `test_suite.py` suite) when unused.
