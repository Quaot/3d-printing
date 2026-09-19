"""Sanity checks on the enclosure built for the example board.

    python check.py
"""

from pathlib import Path

from build import build
from build123d import Align, Axis, Box, Cylinder, Pos
from src.enclosure import Layout, connector_cutouts
from src.params import Params

EXAMPLE = Path(__file__).parent / "examples" / "test_board.kicad_pcb"
BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)


def overlap(part, probe) -> float:
    return (part & probe).volume


def main() -> None:
    failures = []

    def expect(ok: bool, message: str) -> None:
        if not ok:
            failures.append(message)
            print("FAIL", message)

    p = Params()
    board, parts = build(EXAMPLE, ["J1"], p)
    base, lid = parts["base"], parts["lid"]
    lay = Layout(board, p)

    for name, part in parts.items():
        expect(part.is_valid, f"{name} is not a valid solid")
        expect(len(part.solids()) == 1, f"{name} has {len(part.solids())} solids")

    x0, y0, x1, y1 = board.bbox()
    top_face = base.faces().sort_by(Axis.Z)[-1]
    inner = max(top_face.inner_wires(), key=lambda w: w.bounding_box().size.X)
    size = inner.bounding_box().size
    want_x, want_y = x1 - x0 + 2 * p.board_gap, y1 - y0 + 2 * p.board_gap
    expect(abs(size.X - want_x) < 1e-3 and abs(size.Y - want_y) < 1e-3,
           f"cavity {size.X:.2f} x {size.Y:.2f}, expected {want_x:.2f} x {want_y:.2f}")

    outer = base.bounding_box().size
    grow = 2 * (p.board_gap + p.wall_thickness)
    expect(abs(outer.X - (x1 - x0 + grow)) < 1e-3, f"base width {outer.X:.2f}")
    expect(abs(outer.Z - lay.wall_top_z) < 1e-3, f"base height {outer.Z:.2f}")

    expect(len(board.holes) == 4, f"found {len(board.holes)} mounting holes, expected 4")
    mid_z = p.floor_thickness + p.standoff_height / 2
    for hole in board.holes:
        x, y = lay.xy(hole.x, hole.y)
        pilot_r = (hole.drill - p.pilot_undersize) / 2
        ring_x = x + pilot_r + p.standoff_wall / 2
        solid = overlap(base, Pos(ring_x, y, mid_z) * Box(0.5, 0.5, 0.5))
        empty = overlap(base, Pos(x, y, mid_z) * Cylinder(pilot_r * 0.8, 0.5))
        expect(solid > 0.1, f"no standoff at ({hole.x}, {hole.y})")
        expect(empty < 1e-6, f"no pilot hole at ({hole.x}, {hole.y})")

    cutouts = connector_cutouts(board, p, ["J1"])
    expect(len(cutouts) == 1 and cutouts[0].wall == "left", "J1 opening should be in the left wall")
    wall_x = -(x1 - x0) / 2 - p.board_gap - p.wall_thickness / 2
    c = cutouts[0]
    in_opening = Pos(wall_x, c.y, (c.z_min + c.z_max) / 2) * Box(0.5, 0.5, 0.5)
    below_opening = Pos(wall_x, c.y, p.floor_thickness + 1) * Box(0.5, 0.5, 0.5)
    expect(overlap(base, in_opening) < 1e-6, "left wall is not open at J1")
    expect(overlap(base, below_opening) > 0.1, "left wall is missing below J1")

    lid_size = lid.bounding_box().size
    expect(abs(lid_size.Z - (p.lid_thickness + p.lid_lip_height)) < 1e-3, f"lid height {lid_size.Z:.2f}")
    lip_gap = p.board_gap - p.lid_clearance
    lip_probe = Pos(-(x1 - x0) / 2 - lip_gap + p.lid_lip_wall / 2, 0, p.lid_thickness + 1) * Box(0.5, 0.5, 0.5)
    expect(overlap(lid, lip_probe) > 0.1, "lid lip missing")

    print("all checks passed" if not failures else f"{len(failures)} check(s) failed")
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
