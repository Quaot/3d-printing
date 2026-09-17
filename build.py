"""Build every part and export STL (for slicing) and STEP (for Fusion 360).

    python build.py
    python build.py --fit_clearance 0.15 --cap_clearance 0.05
"""

import argparse
from dataclasses import fields
from pathlib import Path

import src  # noqa: F401  (must come before build123d, see src/__init__.py)
from build123d import export_step, export_stl
from src.cap import make_cap
from src.housing import check_depth, make_housing
from src.keycap import make_keycap
from src.params import Params
from src.tolerance_coupon import make_stem_coupon, make_switch_coupon

OUT_DIR = Path(__file__).parent / "out"

PARTS = {
    "housing": make_housing,
    "cap": make_cap,
    "keycap": make_keycap,
    "switch_coupon": make_switch_coupon,
    "stem_coupon": make_stem_coupon,
}


def parse_params() -> Params:
    parser = argparse.ArgumentParser(description=__doc__)
    for field in fields(Params):
        if field.type is float or field.type == "float":
            parser.add_argument(f"--{field.name}", type=float)
    args = parser.parse_args()
    overrides = {k: v for k, v in vars(args).items() if v is not None}
    return Params(**overrides)


def build_all(p: Params) -> dict:
    check_depth(p)
    return {name: make(p) for name, make in PARTS.items()}


def main() -> None:
    p = parse_params()
    (OUT_DIR / "stl").mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "step").mkdir(parents=True, exist_ok=True)

    for name, part in build_all(p).items():
        export_stl(part, str(OUT_DIR / "stl" / f"{name}.stl"))
        export_step(part, str(OUT_DIR / "step" / f"{name}.step"))
        size = part.bounding_box().size
        print(f"{name:14} {size.X:6.1f} x {size.Y:5.1f} x {size.Z:5.1f} mm")

    print(f"switch cutout {p.cutout_size:.2f} mm, files in {OUT_DIR}")


if __name__ == "__main__":
    main()
