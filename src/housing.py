"""Main body: a rounded box with the switch plate as its top wall."""

from build123d import Align, Axis, Box, Part, fillet

from .params import Params

BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)


def make_housing(p: Params) -> Part:
    body = Box(p.body_size, p.body_size, p.body_height, align=BOTTOM)
    body = fillet(body.edges().filter_by(Axis.Z), p.corner_radius)

    # Open-bottom cavity; the top wall left behind is the switch plate.
    cavity_height = p.body_height - p.plate_thickness
    inner_radius = max(p.corner_radius - p.wall_thickness, 0.5)
    cavity = Box(p.inner_size, p.inner_size, cavity_height, align=BOTTOM)
    cavity = fillet(cavity.edges().filter_by(Axis.Z), inner_radius)
    body -= cavity

    cutout = Box(p.cutout_size, p.cutout_size, p.body_height, align=BOTTOM)
    body -= cutout

    top_edges = body.edges().group_by(Axis.Z)[-1]
    outer_top = [e for e in top_edges if e.length > p.cutout_size + 1]
    return fillet(outer_top, 1.0)


def check_depth(p: Params) -> None:
    cavity_height = p.body_height - p.plate_thickness
    if cavity_height - p.cap_lip_height < p.switch_depth:
        raise ValueError(
            f"cavity too shallow: {cavity_height - p.cap_lip_height:.1f} mm "
            f"left under the plate, switch needs {p.switch_depth} mm"
        )
