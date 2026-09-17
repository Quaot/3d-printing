"""Bottom cap: a flat plate with a lip that press-fits into the housing."""

from build123d import Align, Axis, Box, Part, Pos, fillet

from .params import Params

BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)


def make_cap(p: Params) -> Part:
    plate = Box(p.body_size, p.body_size, p.cap_thickness, align=BOTTOM)
    plate = fillet(plate.edges().filter_by(Axis.Z), p.corner_radius)

    lip_size = p.inner_size - 2 * p.cap_clearance
    lip_radius = max(p.corner_radius - p.wall_thickness, 0.5)
    lip_wall = 1.2
    lip = Box(lip_size, lip_size, p.cap_lip_height, align=BOTTOM)
    lip = fillet(lip.edges().filter_by(Axis.Z), lip_radius)
    lip_hollow = Box(lip_size - 2 * lip_wall, lip_size - 2 * lip_wall,
                     p.cap_lip_height, align=BOTTOM)
    lip -= lip_hollow

    return plate + Pos(0, 0, p.cap_thickness) * lip
