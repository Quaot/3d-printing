# switch-fidget

A pocket fidget toy built around an MX-style mechanical keyboard switch. All the parts are parametric Python (build123d). Each build writes STL files for slicing and STEP files you can open and edit in Fusion 360.

<!-- TODO: add a photo of the printed fidget here -->

## Parts

| Part | Size (mm) | Notes |
|---|---|---|
| `housing` | 30 × 30 × 16 | Its top wall is a 1.5 mm switch plate; open bottom |
| `cap` | 30 × 30 × 4.6 | Press-fits into the bottom of the housing |
| `keycap` | 18 × 18 × 6 | Flat cap with an MX cross socket |
| `switch_coupon` | 116 × 23 × 1.5 | Switch cutouts from 13.8 to 14.3 mm |
| `stem_coupon` | 62 × 12 × 5.3 | Keycap sockets with clearance from 0.00 to 0.25 mm |

## Bill of materials

- 1 × MX-compatible switch (plate-mount, 3-pin or 5-pin; clicky feels best)
- Filament: PLA or PETG, about 15 g

## Build

```
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python build.py
.venv\Scripts\python check.py
```

The build writes `out/stl/` and `out/step/`. Every dimension is in `src/params.py`. Any float in that file can be overridden on the command line:

```
.venv\Scripts\python build.py --fit_clearance 0.15 --cap_clearance 0.05
```

## Tuning the fit

Every printer prints holes a little differently, so print the coupons first.

1. Print `switch_coupon`. The notches along the front edge count its cutouts, from 1 notch (13.8 mm) to 6 notches (14.3 mm). Find the smallest cutout where the switch clips in firmly without cracking the plate.
2. Set `fit_clearance = (that size − 14.0) / 2`.
3. Print `stem_coupon`. Its sockets go from 1 notch (0.00 mm) to 6 notches (0.25 mm). Pick the one that grips the switch stem without splitting, and set `stem_clearance` to that value.
4. Print the housing and cap. If the cap is loose, lower `cap_clearance`; if it won't go in, raise it.

## Print settings

- 0.2 mm layers, 3 walls, 20% infill, no supports
- `housing`: print upside down, with the switch plate on the bed
- `cap`: print with the flat plate down
- `keycap`: print upside down, with the flat top on the bed
- Coupons: print flat as exported

## Revision log

| Rev | Change | Result |
|---|---|---|
| | | |

<!-- TODO: add a row for each print: what you changed and how it fit -->

## Known issue

On some Windows installs, `import build123d` fails because `C:\Windows\Fonts\mstmc.ttf` is a stub file, not a real font. `src/__init__.py` skips files like that, so import `src` before `build123d`.

## License

MIT
