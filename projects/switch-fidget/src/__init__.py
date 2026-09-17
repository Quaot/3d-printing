"""Package setup.

build123d reads every system font on import and crashes on files that
aren't real fonts (Windows ships a 4 KB stub, mstmc.ttf). Skip those
before build123d is imported. This must run before any build123d import.
"""

from types import SimpleNamespace

import fontTools.ttLib
from fontTools.ttLib import TTLibError

_real_ttfont = fontTools.ttLib.TTFont


def _safe_ttfont(path, *args, **kwargs):
    try:
        return _real_ttfont(path, *args, **kwargs)
    except TTLibError:
        # An empty variable font: build123d registers no faces for it.
        return {"name": SimpleNamespace(names=[]),
                "fvar": SimpleNamespace(instances=[])}


fontTools.ttLib.TTFont = _safe_ttfont
