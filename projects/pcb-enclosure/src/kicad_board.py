"""Read the parts of a .kicad_pcb file that matter for an enclosure.

Coordinates are KiCad board coordinates in mm: x to the right, y down.
"""

import math
import re
from dataclasses import dataclass, field
from pathlib import Path

TOKEN = re.compile(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+')
MOUNTING_HOLE_MIN_DRILL = 2.5
ARC_SEGMENTS = 16


def parse_sexpr(text: str) -> list:
    stack = [[]]
    for tok in TOKEN.findall(text):
        if tok == "(":
            stack.append([])
        elif tok == ")":
            done = stack.pop()
            stack[-1].append(done)
        elif tok.startswith('"'):
            stack[-1].append(tok[1:-1].replace('\\"', '"'))
        else:
            stack[-1].append(tok)
    return stack[0][0]


def children(node: list, name: str) -> list:
    return [c for c in node[1:] if isinstance(c, list) and c and c[0] == name]


def child(node: list, name: str):
    found = children(node, name)
    return found[0] if found else None


def floats(node, count: int) -> tuple:
    return tuple(float(v) for v in node[1:1 + count])


def layer_of(node: list):
    lay = child(node, "layer")
    return lay[1] if lay else None


@dataclass
class Hole:
    x: float
    y: float
    drill: float


@dataclass
class Footprint:
    reference: str
    lib_id: str
    x: float
    y: float
    rotation: float
    side: str                      # "F" or "B"
    pad_points: list = field(default_factory=list)
    courtyard_points: list = field(default_factory=list)

    def body_points(self) -> list:
        return self.courtyard_points or self.pad_points

    def bbox(self) -> tuple:
        pts = self.body_points()
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        return min(xs), min(ys), max(xs), max(ys)


@dataclass
class Board:
    name: str
    thickness: float
    outline_pts: list
    holes: list
    footprints: dict

    def bbox(self) -> tuple:
        xs = [p[0] for p in self.outline_pts]
        ys = [p[1] for p in self.outline_pts]
        return min(xs), min(ys), max(xs), max(ys)


def to_board(fx, fy, rotation, x, y) -> tuple:
    """Footprint-local point to board coordinates (KiCad rotates CCW on screen)."""
    a = math.radians(rotation)
    return (fx + x * math.cos(a) + y * math.sin(a),
            fy - x * math.sin(a) + y * math.cos(a))


def arc_points(start, mid, end, segments=ARC_SEGMENTS) -> list:
    (x1, y1), (x2, y2), (x3, y3) = start, mid, end
    d = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
    if abs(d) < 1e-9:
        return [start, end]
    ux = ((x1**2 + y1**2) * (y2 - y3) + (x2**2 + y2**2) * (y3 - y1) + (x3**2 + y3**2) * (y1 - y2)) / d
    uy = ((x1**2 + y1**2) * (x3 - x2) + (x2**2 + y2**2) * (x1 - x3) + (x3**2 + y3**2) * (x2 - x1)) / d
    r = math.hypot(x1 - ux, y1 - uy)
    a1 = math.atan2(y1 - uy, x1 - ux)
    a2 = math.atan2(y2 - uy, x2 - ux)
    a3 = math.atan2(y3 - uy, x3 - ux)
    sweep = (a3 - a1) % (2 * math.pi)
    if (a2 - a1) % (2 * math.pi) > sweep:
        sweep -= 2 * math.pi
    return [(ux + r * math.cos(a1 + sweep * i / segments),
             uy + r * math.sin(a1 + sweep * i / segments)) for i in range(segments + 1)]


def edge_segments(pcb: list) -> list:
    segments = []
    for node in pcb[1:]:
        if not isinstance(node, list) or layer_of(node) != "Edge.Cuts":
            continue
        kind = node[0]
        if kind == "gr_line":
            segments.append([floats(child(node, "start"), 2), floats(child(node, "end"), 2)])
        elif kind == "gr_arc":
            segments.append(arc_points(floats(child(node, "start"), 2),
                                       floats(child(node, "mid"), 2),
                                       floats(child(node, "end"), 2)))
        elif kind == "gr_rect":
            (x1, y1), (x2, y2) = floats(child(node, "start"), 2), floats(child(node, "end"), 2)
            segments.append([(x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)])
        elif kind == "gr_poly":
            pts = [floats(xy, 2) for xy in children(child(node, "pts"), "xy")]
            segments.append(pts + [pts[0]])
    return segments


def chain_outline(segments: list, tol: float = 0.01) -> list:
    """Join Edge.Cuts pieces into the longest closed loop (the board edge)."""
    if not segments:
        raise ValueError("no Edge.Cuts outline found")

    def close(a, b):
        return abs(a[0] - b[0]) < tol and abs(a[1] - b[1]) < tol

    loops = []
    remaining = [list(s) for s in segments]
    while remaining:
        loop = remaining.pop(0)
        grown = True
        while grown and not close(loop[0], loop[-1]):
            grown = False
            for i, seg in enumerate(remaining):
                if close(loop[-1], seg[0]):
                    loop += seg[1:]
                elif close(loop[-1], seg[-1]):
                    loop += seg[-2::-1]
                else:
                    continue
                remaining.pop(i)
                grown = True
                break
        if close(loop[0], loop[-1]):
            loops.append(loop[:-1])

    if not loops:
        raise ValueError("Edge.Cuts outline is not closed")

    def area(pts):
        return abs(sum(pts[i][0] * pts[i - 1][1] - pts[i - 1][0] * pts[i][1]
                       for i in range(len(pts)))) / 2

    return max(loops, key=area)


def read_footprint(node: list) -> tuple:
    fx, fy = floats(child(node, "at"), 2)
    at = child(node, "at")
    rotation = float(at[3]) if len(at) > 3 and at[3] != "unlocked" else 0.0
    side = "B" if (layer_of(node) or "F.Cu").startswith("B") else "F"

    reference = "?"
    for prop in children(node, "property"):
        if prop[1] == "Reference":
            reference = prop[2]
    for text in children(node, "fp_text"):
        if text[1] == "reference":
            reference = text[2]

    fp = Footprint(reference, node[1], fx, fy, rotation, side)
    holes = []
    for pad in children(node, "pad"):
        px, py = floats(child(pad, "at"), 2)
        sx, sy = floats(child(pad, "size"), 2)
        for dx, dy in ((-sx / 2, -sy / 2), (sx / 2, -sy / 2), (sx / 2, sy / 2), (-sx / 2, sy / 2)):
            fp.pad_points.append(to_board(fx, fy, rotation, px + dx, py + dy))
        drill = child(pad, "drill")
        if drill is None:
            continue
        sizes = [float(v) for v in drill[1:] if not isinstance(v, list) and v != "oval"]
        if not sizes:
            continue
        is_mount_fp = node[1].split(":")[-1].startswith("MountingHole")
        if is_mount_fp or (pad[2] == "np_thru_hole" and sizes[0] >= MOUNTING_HOLE_MIN_DRILL):
            hx, hy = to_board(fx, fy, rotation, px, py)
            holes.append(Hole(hx, hy, sizes[0]))

    for shape in node[1:]:
        if not isinstance(shape, list) or not str(layer_of(shape) or "").endswith("CrtYd"):
            continue
        local = []
        if shape[0] in ("fp_line", "fp_rect"):
            (x1, y1), (x2, y2) = floats(child(shape, "start"), 2), floats(child(shape, "end"), 2)
            local = [(x1, y1), (x2, y2)] if shape[0] == "fp_line" else [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
        elif shape[0] == "fp_arc":
            local = arc_points(floats(child(shape, "start"), 2), floats(child(shape, "mid"), 2),
                               floats(child(shape, "end"), 2), 8)
        elif shape[0] == "fp_circle":
            (cx, cy), (ex, ey) = floats(child(shape, "center"), 2), floats(child(shape, "end"), 2)
            r = math.hypot(ex - cx, ey - cy)
            local = [(cx - r, cy - r), (cx + r, cy + r), (cx - r, cy + r), (cx + r, cy - r)]
        elif shape[0] == "fp_poly":
            local = [floats(xy, 2) for xy in children(child(shape, "pts"), "xy")]
        fp.courtyard_points += [to_board(fx, fy, rotation, x, y) for x, y in local]

    return fp, holes


def load_board(path) -> Board:
    path = Path(path)
    pcb = parse_sexpr(path.read_text(encoding="utf-8"))
    if pcb[0] != "kicad_pcb":
        raise ValueError(f"{path} is not a KiCad board file")

    general = child(pcb, "general")
    thickness_node = child(general, "thickness") if general else None
    thickness = float(thickness_node[1]) if thickness_node else 1.6

    holes, footprints = [], {}
    for node in children(pcb, "footprint"):
        fp, fp_holes = read_footprint(node)
        holes += fp_holes
        footprints[fp.reference] = fp

    unique = []
    for h in holes:
        if not any(abs(h.x - u.x) < 0.01 and abs(h.y - u.y) < 0.01 for u in unique):
            unique.append(h)

    outline = chain_outline(edge_segments(pcb))
    return Board(path.stem, thickness, outline, unique, footprints)
