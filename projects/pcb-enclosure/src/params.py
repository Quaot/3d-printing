"""Enclosure dimensions in millimetres. Every field can be overridden from build.py."""

from dataclasses import dataclass


@dataclass
class Params:
    wall_thickness: float = 2.0
    floor_thickness: float = 2.0
    board_gap: float = 0.5          # space between board edge and inner wall
    top_clearance: float = 15.0     # room above the board surface for parts

    standoff_height: float = 6.0
    standoff_wall: float = 2.0      # standoff radius beyond the hole radius
    pilot_undersize: float = 0.7    # pilot hole = mounting hole - this, for self-tapping screws

    lid_thickness: float = 2.0
    lid_clearance: float = 0.2      # gap on each side of the lid lip
    lid_lip_height: float = 3.0
    lid_lip_wall: float = 1.2

    connector_height: float = 11.0  # cutout height above the board surface
    connector_margin: float = 0.5   # added around each connector cutout
