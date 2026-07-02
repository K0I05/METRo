## Summary

Implemented the roadmap item: [**"Include prediction of freezing point of water into forecast XML file (optional parameter)"**](home:/home/lavco/projects/system-models/metro-model/src/model/balanc.f).

**What I found:** the Fortran physics core (`balanc.f`/`coupla.f`) already had a fully-designed `FP` ("Freezing point (C)") parameter threaded through `SRFHUM`, `VERGLAS`, and `RODCON` — it just was never wired up. The C glue layer (`macadam.c`) hardcoded it to a scalar `0.0` and never exposed it to Python. So this wasn't a from-scratch physics feature — it was finishing plumbing the original authors had already half-built.

**Changes**, following the exact same pattern already used for anthropogenic flux (`FA`), the closest existing "optional per-timestep forecast field":

- **Fortran** ([balanc.f](home:/home/lavco/projects/system-models/metro-model/src/model/balanc.f), [coupla.f](home:/home/lavco/projects/system-models/metro-model/src/model/coupla.f)): `FP` changed from a scalar to a `DTMAX`-sized array, indexed by timestep at all 5 use sites.
- **C/SWIG** ([macadam.c](home:/home/lavco/projects/system-models/metro-model/src/model/macadam.c), [macadam.h](home:/home/lavco/projects/system-models/metro-model/src/model/macadam.h), [macadam.i](home:/home/lavco/projects/system-models/metro-model/src/model/macadam.i)): `Do_Metro` gained a `double* dpFP` parameter, replacing the hardcoded `double dFp=0.0`.
- **Python**: new `--use-freezing-point-forecast` CLI flag ([metro_config.py](home:/home/lavco/projects/system-models/metro-model/src/frontend/metro_config.py)) registers an optional `<tfz>` element in the forecast XML; `metro_preprocess_interpol_forecast.py` interpolates it (defaulting to `0.0`°C — pure water — when absent, exactly matching the old hardcoded behavior); `metro_model.py` passes it into `Do_Metro`.

**Verification:**
- Full rebuild caught and fixed a real fixed-form Fortran 72-column overflow in `balanc.f` (`FP`→`FP(i)` pushed one line over the limit).
- Selftest output is **byte-for-byte identical** to before — confirms zero behavior change when the flag isn't used.
- All 49 regression cases still pass.
- Built a synthetic test injecting `<tfz>-3.0</tfz>` (simulating a salted/treated road) into the selftest forecast: with `--use-freezing-point-forecast`, the surface temperature and road-condition code visibly diverge from baseline at the point where the road would normally cross 0°C — confirming the parameter reaches the compiled physics core and produces a physically sensible effect, not just inert plumbing.

I copied the rebuilt `.so`/`macadam.py` and changed Python files directly into `/usr/local/share/metro` (same workaround as before — `setup.sh` is still broken by the `INSTALL`/`LICENSE`/`README.devel` renames). The source changes are uncommitted in your repo, sitting on top of your commit `0bbeb3c`. Let me know if you'd like me to commit them, or also fix `setup.sh` while I'm in there.