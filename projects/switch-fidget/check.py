"""Sanity checks on the generated geometry. Run after changing params.

    python check.py
"""

from build import build_all
from build123d import Axis
from src.params import Params


def top_hole_size(part) -> float:
    top_face = part.faces().sort_by(Axis.Z)[-1]
    holes = top_face.inner_wires()
    assert len(holes) == 1, f"expected one hole in the top face, got {len(holes)}"
    size = holes[0].bounding_box().size
    assert abs(size.X - size.Y) < 1e-6, "cutout is not square"
    return size.X


def main() -> None:
    failures = 0
    for fit_clearance in (0.0, 0.1, 0.2):
        p = Params(fit_clearance=fit_clearance)
        parts = build_all(p)

        for name, part in parts.items():
            if not part.is_valid:
                print(f"FAIL {name}: invalid solid")
                failures += 1
            if len(part.solids()) != 1:
                print(f"FAIL {name}: {len(part.solids())} solids, expected 1")
                failures += 1

        hole = top_hole_size(parts["housing"])
        if abs(hole - p.cutout_size) > 1e-3:
            print(f"FAIL housing cutout {hole:.3f}, expected {p.cutout_size:.3f}")
            failures += 1

        box = parts["housing"].bounding_box().size
        if abs(box.X - p.body_size) > 1e-3 or abs(box.Z - p.body_height) > 1e-3:
            print(f"FAIL housing size {box}")
            failures += 1

        cap_lip = parts["cap"].bounding_box().size.Z
        if abs(cap_lip - (p.cap_thickness + p.cap_lip_height)) > 1e-3:
            print(f"FAIL cap height {cap_lip:.3f}")
            failures += 1

        print(f"fit_clearance {fit_clearance}: cutout {hole:.2f} mm")

    print("all checks passed" if failures == 0 else f"{failures} check(s) failed")
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
