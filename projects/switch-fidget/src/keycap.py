"""Simple flat keycap with an MX cross socket. Print it upside down."""

from build123d import Align, Axis, Box, Cylinder, Part, Pos, fillet

from .params import Params

BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)


def make_stem_cross(p: Params, clearance: float, depth: float) -> Part:
    length = p.stem_cross_length + 2 * clearance
    bar_h = Box(length, p.stem_bar_h + 2 * clearance, depth, align=BOTTOM)
    bar_v = Box(p.stem_bar_v + 2 * clearance, length, depth, align=BOTTOM)
    return bar_h + bar_v


def make_keycap(p: Params) -> Part:
    cap = Box(p.keycap_size, p.keycap_size, p.keycap_height, align=BOTTOM)
    cap = fillet(cap.edges().filter_by(Axis.Z), 2.0)

    hollow_size = p.keycap_size - 2 * p.keycap_skirt_thickness
    hollow_height = p.keycap_height - p.keycap_top_thickness
    hollow = Box(hollow_size, hollow_size, hollow_height, align=BOTTOM)
    cap -= hollow

    socket = Cylinder(p.stem_socket_diameter / 2, hollow_height, align=BOTTOM)
    socket -= make_stem_cross(p, p.stem_clearance, p.stem_socket_depth)
    cap += socket

    top_edges = cap.edges().group_by(Axis.Z)[-1]
    return fillet(top_edges, 0.6)
