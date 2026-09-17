"""Test prints for finding the right fits on a given printer.

switch coupon: a 1.5 mm plate with one cutout per size in
coupon_cutouts, smallest on the left. Notches along the front edge count
the position (1 notch = first size).

stem coupon: a row of keycap sockets, one per value in
coupon_stem_clearances, numbered the same way.
"""

from build123d import Align, Box, Cylinder, Part, Pos

from .keycap import make_stem_cross
from .params import Params

BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)
NOTCH_WIDTH = 0.8
NOTCH_GAP = 0.8
NOTCH_DEPTH = 1.2


def notches(count: int, x: float, front_y: float, height: float) -> Part:
    total = count * NOTCH_WIDTH + (count - 1) * NOTCH_GAP
    start = x - total / 2 + NOTCH_WIDTH / 2
    marks = None
    for i in range(count):
        mark = Pos(start + i * (NOTCH_WIDTH + NOTCH_GAP),
                   front_y + NOTCH_DEPTH / 2, 0) * Box(
            NOTCH_WIDTH, NOTCH_DEPTH, height, align=BOTTOM)
        marks = mark if marks is None else marks + mark
    return marks


def x_positions(p: Params, count: int) -> list[float]:
    return [(i - (count - 1) / 2) * p.coupon_pitch for i in range(count)]


def make_switch_coupon(p: Params) -> Part:
    count = len(p.coupon_cutouts)
    length = count * p.coupon_pitch + 2
    width = p.coupon_pitch + 4
    plate = Box(length, width, p.plate_thickness, align=BOTTOM)
    front_y = -width / 2
    for i, (x, size) in enumerate(zip(x_positions(p, count), p.coupon_cutouts)):
        plate -= Pos(x, 1, 0) * Box(size, size, p.plate_thickness, align=BOTTOM)
        plate -= notches(i + 1, x, front_y, p.plate_thickness)
    return plate


def make_stem_coupon(p: Params) -> Part:
    count = len(p.coupon_stem_clearances)
    pitch = 10.0
    base_height = 1.5
    length = count * pitch + 2
    width = 12.0
    part = Box(length, width, base_height, align=BOTTOM)
    front_y = -width / 2
    positions = [(i - (count - 1) / 2) * pitch for i in range(count)]
    for i, (x, clearance) in enumerate(zip(positions, p.coupon_stem_clearances)):
        socket = Cylinder(p.stem_socket_diameter / 2,
                          p.stem_socket_depth + base_height, align=BOTTOM)
        part += Pos(x, 1, 0) * socket
        part -= Pos(x, 1, 0) * make_stem_cross(
            p, clearance, p.stem_socket_depth + base_height)
        part -= notches(i + 1, x, front_y, base_height)
    return part
