"""Build a base and lid for a KiCad board and export STL and STEP.

    python build.py examples/test_board.kicad_pcb --connectors J1
    python build.py my_board.kicad_pcb --connectors J1,J3 --top_clearance 12
"""

import argparse
from dataclasses import fields
from pathlib import Path

import src  # noqa: F401  (must come before build123d, see src/__init__.py)
from build123d import export_step, export_stl
from src.enclosure import connector_cutouts, make_base, make_lid
from src.kicad_board import load_board
from src.params import Params

OUT_DIR = Path(__file__).parent / "out"


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("board", type=Path, help=".kicad_pcb file")
    parser.add_argument("--connectors", default="", help="comma-separated references to cut openings for")
    parser.add_argument("--out", type=Path, default=OUT_DIR)
    for field in fields(Params):
        parser.add_argument(f"--{field.name}", type=float, help=f"default {field.default}")
    args = parser.parse_args()
    overrides = {f.name: getattr(args, f.name) for f in fields(Params) if getattr(args, f.name) is not None}
    connectors = [c.strip() for c in args.connectors.split(",") if c.strip()]
    return args.board, connectors, args.out, Params(**overrides)


def build(board_path, connectors, p: Params) -> dict:
    board = load_board(board_path)
    return board, {"base": make_base(board, p, connectors), "lid": make_lid(board, p)}


def main() -> None:
    board_path, connectors, out_dir, p = parse_args()
    board, parts = build(board_path, connectors, p)
    target = out_dir / board.name
    target.mkdir(parents=True, exist_ok=True)

    x0, y0, x1, y1 = board.bbox()
    print(f"{board.name}: {x1 - x0:.1f} x {y1 - y0:.1f} mm board, "
          f"{len(board.holes)} mounting holes, {board.thickness} mm thick")
    for c in connector_cutouts(board, p, connectors):
        print(f"  {c.reference}: opening in the {c.wall} wall")
    for name, part in parts.items():
        export_stl(part, str(target / f"{name}.stl"))
        export_step(part, str(target / f"{name}.step"))
        size = part.bounding_box().size
        print(f"  {name:5} {size.X:6.1f} x {size.Y:5.1f} x {size.Z:5.1f} mm")
    print(f"files in {target}")


if __name__ == "__main__":
    main()
