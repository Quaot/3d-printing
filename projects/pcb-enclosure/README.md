# pcb-enclosure

[![checks](https://github.com/Quaot/3d-printing/actions/workflows/pcb-enclosure.yml/badge.svg)](https://github.com/Quaot/3d-printing/actions/workflows/pcb-enclosure.yml)
![Status](https://img.shields.io/badge/status-in_progress-yellow)
![KiCad](https://img.shields.io/badge/KiCad-10-314CB0?logo=kicad&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
![Exports](https://img.shields.io/badge/exports-STL_%7C_STEP-lightgrey)

**Status: in progress. The generator works; no case has been printed yet.**

Point it at a KiCad board file and it builds a printable case for that board. The base has walls that follow the board outline, a standoff under each mounting hole, and openings for the connectors you name. The lid has a lip that press-fits into the base.

<img src="docs/base.svg" width="360" alt="Base for the example board"> <img src="docs/lid.svg" width="360" alt="Lid for the example board">

*The CAD output for [examples/test_board.kicad_pcb](examples/test_board.kicad_pcb): a 60 × 40 mm board with four M3 holes and a barrel jack.*

## Use

```
cd projects\pcb-enclosure
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python build.py path\to\board.kicad_pcb --connectors J1,J2
```

This writes `out/<board>/base.stl`, `lid.stl`, and STEP copies of both for editing in Fusion 360. Every size in [src/params.py](src/params.py) can be overridden on the command line, for example `--top_clearance 12 --standoff_height 5`.

`python check.py` builds the example and checks the geometry. `python render.py` redraws the pictures above.

## What it reads from the board

| Board feature | How it's used |
|---|---|
| Edge.Cuts lines, arcs, rectangles, polygons | Joined into the board outline; the walls follow it with a 0.5 mm gap |
| Board thickness | Sets the height of the board above the floor |
| `MountingHole:*` footprints, or non-plated holes of 2.5 mm or more | A standoff under each, with a pilot hole for a self-tapping screw |
| The footprints named with `--connectors` | An opening in the nearest wall, sized from the courtyard (or the pads if there's no courtyard) |

Tested on the example board and on KiCad's `pic_programmer` demo, a 160 × 99 mm board with seven mounting holes.

## Limits

- Parts are not checked for height. Set `--top_clearance` above your tallest part.
- Openings are rectangles cut straight through the nearest wall of the board's bounding box, which suits rectangular boards best.
- A non-plated hole of 2.5 mm or more gets a standoff even if it belongs to a connector.
- The lid is held by friction; there are no screw bosses or snap fits yet.

## Print settings

- PLA, 0.2 mm layers, 3 walls, 20% infill
- Base: print as exported, open side up. No supports needed unless an opening is taller than about 10 mm.
- Lid: print plate down, lip up.
- Screws: the pilot hole is 0.7 mm smaller than the mounting hole, e.g. 2.5 mm for M3 self-tapping screws.

## Revision log

| Rev | Board | Change | Result |
|---|---|---|---|
| | | | |

<!-- TODO: add a row for each case printed: which board, what changed, how it fit -->
