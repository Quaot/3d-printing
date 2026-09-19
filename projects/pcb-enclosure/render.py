"""Draw line views of the example enclosure into docs/.

    python render.py
"""

from pathlib import Path

from build import build
from build123d import Compound, ExportSVG, LineType
from src.params import Params

EXAMPLE = Path(__file__).parent / "examples" / "test_board.kicad_pcb"
DOCS = Path(__file__).parent / "docs"
VIEWS = {"base": (-1.2, -1.6, 1.3), "lid": (1.0, -1.5, 1.2)}


def main() -> None:
    DOCS.mkdir(exist_ok=True)
    _, parts = build(EXAMPLE, ["J1"], Params())
    for name, view in VIEWS.items():
        visible, hidden = parts[name].project_to_viewport(view)
        size = max(*Compound(children=visible + hidden).bounding_box().size)
        svg = ExportSVG(scale=100 / size)
        svg.add_layer("visible", line_weight=0.3)
        svg.add_layer("hidden", line_color="darkgray", line_type=LineType.ISO_DOT, line_weight=0.15)
        svg.add_shape(visible, layer="visible")
        svg.add_shape(hidden, layer="hidden")
        svg.write(str(DOCS / f"{name}.svg"))
        print(f"wrote docs/{name}.svg")


if __name__ == "__main__":
    main()
