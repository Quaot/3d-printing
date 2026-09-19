"""Write examples/test_board.kicad_pcb: a 60 x 40 mm board with four M3
mounting holes and a barrel jack (J1) on the left edge.

Footprints are copied from the KiCad 10 library, so this needs KiCad
installed. The generated board is committed; you only need to rerun this
to change the example.

    python examples/make_test_board.py [path to kicad/share/kicad/footprints]
"""

import os
import re
import sys
from pathlib import Path

DEFAULT_LIB = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs/KiCad/10.0/share/kicad/footprints"
OUT = Path(__file__).parent / "test_board.kicad_pcb"

BOARD_X, BOARD_Y, BOARD_W, BOARD_H = 100.0, 100.0, 60.0, 40.0
HOLE_INSET = 3.5

PLACEMENTS = [
    ("MountingHole", "MountingHole_3.2mm_M3", "H1", BOARD_X + HOLE_INSET, BOARD_Y + HOLE_INSET, 0),
    ("MountingHole", "MountingHole_3.2mm_M3", "H2", BOARD_X + BOARD_W - HOLE_INSET, BOARD_Y + HOLE_INSET, 0),
    ("MountingHole", "MountingHole_3.2mm_M3", "H3", BOARD_X + HOLE_INSET, BOARD_Y + BOARD_H - HOLE_INSET, 0),
    ("MountingHole", "MountingHole_3.2mm_M3", "H4", BOARD_X + BOARD_W - HOLE_INSET, BOARD_Y + BOARD_H - HOLE_INSET, 0),
    # The jack body reaches 14 mm behind pin 1, so its opening sits 0.3 mm inside the edge.
    ("Connector_BarrelJack", "BarrelJack_Horizontal", "J1", BOARD_X + 14.3, BOARD_Y + BOARD_H / 2, 0),
]


def place(lib_dir: Path, lib: str, name: str, ref: str, x: float, y: float, rot: float) -> str:
    text = (lib_dir / f"{lib}.pretty" / f"{name}.kicad_mod").read_text(encoding="utf-8")
    text = re.sub(r'\s*\((version|generator|generator_version) [^()]*\)', "", text, count=3)
    text = text.replace(f'(footprint "{name}"', f'(footprint "{lib}:{name}"', 1)
    text = text.replace('(layer "F.Cu")', f'(layer "F.Cu")\n\t(at {x} {y} {rot})', 1)
    return text.replace('"REF**"', f'"{ref}"').strip()


def main() -> None:
    lib_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_LIB
    footprints = "\n".join(place(lib_dir, *p) for p in PLACEMENTS)
    board = f"""(kicad_pcb
\t(version 20260206)
\t(generator "pcbnew")
\t(generator_version "10.0")
\t(general
\t\t(thickness 1.6)
\t\t(legacy_teardrops no)
\t)
\t(paper "A4")
{footprints}
\t(gr_rect
\t\t(start {BOARD_X} {BOARD_Y})
\t\t(end {BOARD_X + BOARD_W} {BOARD_Y + BOARD_H})
\t\t(stroke (width 0.1) (type solid))
\t\t(fill no)
\t\t(layer "Edge.Cuts")
\t)
)
"""
    OUT.write_text(board, encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
