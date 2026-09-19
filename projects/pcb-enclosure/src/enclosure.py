"""Base and lid built around a KiCad board.

Part coordinates are centred on the board outline, with y flipped so the
part matches the board as seen from the top in KiCad.
"""

from dataclasses import dataclass

from build123d import Align, Box, Cylinder, Kind, Part, Polygon, Pos, extrude, offset

from .kicad_board import Board, Footprint
from .params import Params

BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)


@dataclass
class Cutout:
    reference: str
    wall: str            # "left", "right", "top" or "bottom", as seen in KiCad
    x: float             # centre in part coordinates
    y: float
    z_min: float
    z_max: float
    size_x: float
    size_y: float


class Layout:
    def __init__(self, board: Board, p: Params):
        self.board = board
        self.p = p
        x0, y0, x1, y1 = board.bbox()
        self.cx, self.cy = (x0 + x1) / 2, (y0 + y1) / 2
        self.board_bottom_z = p.floor_thickness + p.standoff_height
        self.board_top_z = self.board_bottom_z + board.thickness
        self.wall_top_z = self.board_top_z + p.top_clearance

    def xy(self, x: float, y: float) -> tuple:
        return x - self.cx, -(y - self.cy)

    def outline_face(self, grow: float):
        pts = [self.xy(x, y) for x, y in self.board.outline_pts]
        signed_area = sum(pts[i - 1][0] * pts[i][1] - pts[i][0] * pts[i - 1][1] for i in range(len(pts)))
        if signed_area < 0:
            pts.reverse()   # counter-clockwise, so faces point up and extrude upwards
        return offset(Polygon(*pts, align=None), grow, kind=Kind.INTERSECTION)

    def cutout(self, fp: Footprint) -> Cutout:
        p = self.p
        bx0, by0, bx1, by1 = self.board.bbox()
        fx0, fy0, fx1, fy1 = fp.bbox()
        distance = {"left": fx0 - bx0, "right": bx1 - fx1, "top": fy0 - by0, "bottom": by1 - fy1}
        wall = min(distance, key=distance.get)

        through = p.board_gap + p.wall_thickness + 2
        m = p.connector_margin
        if wall in ("left", "right"):
            y0, y1 = fy0 - m, fy1 + m
            edge = bx0 if wall == "left" else bx1
            x0, x1 = (edge - through, edge + 1) if wall == "left" else (edge - 1, edge + through)
        else:
            x0, x1 = fx0 - m, fx1 + m
            edge = by0 if wall == "top" else by1
            y0, y1 = (edge - through, edge + 1) if wall == "top" else (edge - 1, edge + through)

        if fp.side == "F":
            z_min, z_max = self.board_top_z - m, self.board_top_z + p.connector_height + m
        else:
            z_min, z_max = self.board_bottom_z - p.connector_height - m, self.board_bottom_z + m
        cx, cy = self.xy((x0 + x1) / 2, (y0 + y1) / 2)
        return Cutout(fp.reference, wall, cx, cy, z_min, z_max, x1 - x0, y1 - y0)


def make_base(board: Board, p: Params, connectors=()) -> Part:
    lay = Layout(board, p)
    base = extrude(lay.outline_face(p.board_gap + p.wall_thickness), lay.wall_top_z)
    base -= Pos(0, 0, p.floor_thickness) * extrude(lay.outline_face(p.board_gap), lay.wall_top_z)

    for hole in board.holes:
        x, y = lay.xy(hole.x, hole.y)
        radius = hole.drill / 2 + p.standoff_wall
        standoff = Cylinder(radius, p.standoff_height + 0.01, align=BOTTOM)
        pilot = Cylinder((hole.drill - p.pilot_undersize) / 2, p.standoff_height + 0.02, align=BOTTOM)
        base += Pos(x, y, p.floor_thickness - 0.01) * standoff
        base -= Pos(x, y, p.floor_thickness) * pilot

    for c in connector_cutouts(board, p, connectors):
        base -= Pos(c.x, c.y, c.z_min) * Box(c.size_x, c.size_y, c.z_max - c.z_min, align=BOTTOM)
    return base


def make_lid(board: Board, p: Params) -> Part:
    """Printed plate-down: the lip points up in the exported file."""
    lay = Layout(board, p)
    lid = extrude(lay.outline_face(p.board_gap + p.wall_thickness), p.lid_thickness)
    lip_outer = p.board_gap - p.lid_clearance
    lip = extrude(lay.outline_face(lip_outer), p.lid_lip_height)
    lip -= extrude(lay.outline_face(lip_outer - p.lid_lip_wall), p.lid_lip_height)
    return lid + Pos(0, 0, p.lid_thickness) * lip


def connector_cutouts(board: Board, p: Params, connectors) -> list:
    lay = Layout(board, p)
    missing = [ref for ref in connectors if ref not in board.footprints]
    if missing:
        raise ValueError(f"no footprint with reference {', '.join(missing)} on {board.name}")
    return [lay.cutout(board.footprints[ref]) for ref in connectors]
