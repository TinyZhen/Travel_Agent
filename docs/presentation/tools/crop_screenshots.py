"""Crop the panels used by the deck and the poster from the app's screenshots.

The originals in docs/screenshots are 2x captures. Each crop keeps the native pixels (no scaling),
so nothing is upscaled or blurred. Run from anywhere:

    python3 docs/presentation/tools/crop_screenshots.py
"""

from pathlib import Path

from PIL import Image

PRESENTATION = Path(__file__).resolve().parent.parent
SRC = PRESENTATION.parent / "screenshots"
OUT = PRESENTATION / "screenshots"

# name: (source screenshot, (left, top, right, bottom) in source pixels)
CROPS = {
    "plan.png": ("04_plan.png", (1058, 215, 2668, 2096)),
    "start.png": ("01_start.png", (207, 210, 1010, 760)),
    "esc_budget.png": ("03_over_budget_escalation.png", (1056, 220, 2672, 790)),
    "esc_question.png": ("03_over_budget_escalation.png", (210, 1375, 1010, 1965)),
    "winter_ask.png": ("08_winter_detroit.png", (210, 240, 1005, 545)),
    "winter_warn.png": ("08_winter_detroit.png", (210, 1125, 1005, 1385)),
    "guide_top.png": ("07_visit_guide.png", (0, 330, 1616, 1160)),
}


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for name, (source, box) in CROPS.items():
        crop = Image.open(SRC / source).crop(box)
        crop.save(OUT / name, optimize=True)
        print(f"{name}: {crop.size[0]} x {crop.size[1]} px from {source}")


if __name__ == "__main__":
    main()
