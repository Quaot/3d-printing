# 3D Printing

[![switch-fidget checks](https://github.com/Quaot/3d-printing/actions/workflows/switch-fidget.yml/badge.svg)](https://github.com/Quaot/3d-printing/actions/workflows/switch-fidget.yml)
[![License: MIT](https://img.shields.io/github/license/Quaot/3d-printing)](LICENSE)
[![Last commit](https://img.shields.io/github/last-commit/Quaot/3d-printing)](https://github.com/Quaot/3d-printing/commits/main)
[![Repo size](https://img.shields.io/github/repo-size/Quaot/3d-printing)](https://github.com/Quaot/3d-printing)
![Projects](https://img.shields.io/badge/projects-3-blue)
![Fusion 360](https://img.shields.io/badge/Fusion_360-F3D-orange?logo=autodesk&logoColor=white)
![Python](https://img.shields.io/badge/Python-build123d-3776AB?logo=python&logoColor=white)
![Cura](https://img.shields.io/badge/Slicer-Cura-196ef0?logo=ultimaker&logoColor=white)
![Printer](https://img.shields.io/badge/Printer-Anycubic_Mega_Pro-222)
![Material](https://img.shields.io/badge/Material-PLA-green)

My 3D printing projects: design files, printable STLs, and notes on each one.

| Project | Tools | Status |
|---|---|---|
| [IB Physics sensor mount](projects/ib-physics-sensor-mount/) | Fusion 360, FDM | Printed (Sep–Oct 2025) |
| [Toothpaste squeezer](projects/toothpaste-squeezer/) | FDM | Printed (Dec 2025) |
| [Switch fidget](projects/switch-fidget/) | Python (build123d), FDM | In progress, not printed yet |

## Printer and settings

- Anycubic Mega Pro, PLA
- Cura profile: [profiles/Mega Pro PLA.curaprofile](profiles/Mega%20Pro%20PLA.curaprofile), Anycubic's recommended PLA settings for the Mega Pro

## Layout

```
projects/<name>/
  README.md    what it is, versions, what changed
  fusion/      Fusion 360 source (.f3d)
  stl/         print-ready files
```
