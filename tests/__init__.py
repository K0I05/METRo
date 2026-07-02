"""
    Puts src/frontend on sys.path[0] before any test imports a metro_* module.

    This matters for two reasons:
    1) Several modules (metro_data.py, etc.) do bare imports like
       `import metro_logger`, which only resolve if src/frontend itself is
       on sys.path (that's how metro.py's own launcher does it).
    2) metro_util.py resolves METRo's install root from sys.path[0] at
       import time (get_metro_root_path()) to find usr/share/locale for
       gettext. Pointing sys.path[0] at <repo>/src/frontend makes it resolve
       to <repo>, which has usr/share/locale/*.mo checked into the repo.
"""

import os
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SRC_FRONTEND = os.path.join(_REPO_ROOT, 'src', 'frontend')
if sys.path[0] != _SRC_FRONTEND:
    sys.path.insert(0, _SRC_FRONTEND)

# metro_error.py and toolbox/metro_util.py import each other (metro_util
# imports metro_error partway through its own body, before its own
# init_translation is defined; metro_error needs init_translation
# immediately at import time). Importing metro_error here, first, in its
# own fresh pass breaks the cycle: metro_error -> toolbox.metro_util (runs
# to completion, defining init_translation) -> back to metro_error, which
# can now call it. This is what the real METRo entrypoint relies on too
# (metro_config_validation.py imports metro_error before anything else
# reaches toolbox.metro_util) - it is just never been an explicit,
# guaranteed order, so it is reproduced here rather than assumed.
import metro_error  # noqa: F401,E402
