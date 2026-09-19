#!/usr/bin/env python3
"""Generates the 1024x1024 App Store icon for TodoNotes.

Run with: python3 scripts/generate_app_icon.py
Requires Pillow (pip install pillow).
"""
from PIL import Image, ImageDraw
import os

SIZE = 1024
BG_COLOR = (250, 197, 51, 255)       # warm yellow, matches the note palette
BOX_COLOR = (35, 33, 30, 255)        # near-black
BAR_COLOR = (35, 33, 30, 255)
CHECK_COLOR = (250, 197, 51, 255)    # yellow check on dark filled box

img = Image.new("RGBA", (SIZE, SIZE), BG_COLOR)
draw = ImageDraw.Draw(img)

box_size = 150
box_radius = 30
bar_height = 46
bar_radius = 23
left_margin = 190
row_gap = 210
first_row_center = 322
bar_end = 860

for i in range(3):
    center_y = first_row_center + i * row_gap
    box_top = center_y - box_size // 2
    box_left = left_margin
    box_right = box_left + box_size
    box_bottom = box_top + box_size

    if i == 0:
        draw.rounded_rectangle(
            [box_left, box_top, box_right, box_bottom],
            radius=box_radius, fill=BOX_COLOR
        )
        # checkmark
        cx0, cy0 = box_left + 34, center_y + 6
        cx1, cy1 = box_left + 62, box_top + box_size - 40
        cx2, cy2 = box_right - 30, box_top + 34
        draw.line([(cx0, cy0), (cx1, cy1)], fill=CHECK_COLOR, width=22, joint="curve")
        draw.line([(cx1, cy1), (cx2, cy2)], fill=CHECK_COLOR, width=22, joint="curve")
    else:
        draw.rounded_rectangle(
            [box_left, box_top, box_right, box_bottom],
            radius=box_radius, outline=BOX_COLOR, width=20
        )

    bar_left = box_right + 46
    bar_top = center_y - bar_height // 2
    bar_bottom = bar_top + bar_height
    width_factor = 1.0 if i != 2 else 0.7
    this_bar_end = bar_left + int((bar_end - bar_left) * width_factor)
    draw.rounded_rectangle(
        [bar_left, bar_top, this_bar_end, bar_bottom],
        radius=bar_radius, fill=BAR_COLOR
    )

out_dir = os.path.join(os.path.dirname(__file__), "..", "TodoNotes", "Assets.xcassets", "AppIcon.appiconset")
os.makedirs(out_dir, exist_ok=True)
img.convert("RGB").save(os.path.join(out_dir, "AppIcon.png"), "PNG")
print("Wrote", os.path.join(out_dir, "AppIcon.png"))
