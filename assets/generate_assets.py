#!/usr/bin/env python3
"""
Generates clean YouTube branding icons and Android TV Leanback banners.
Can be executed in GitHub Actions or locally with: python generate_assets.py
"""

import os
from PIL import Image, ImageDraw

def draw_youtube_icon(size: int) -> Image.Image:
    # 32-bit RGBA
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    margin = size * 0.12
    rect_box = [margin, margin, size - margin, size - margin]
    radius = size * 0.22

    # Draw YouTube Red rounded rectangle (#FF0000)
    red_color = (255, 0, 0, 255)
    draw.rounded_rectangle(rect_box, radius=radius, fill=red_color)

    # Draw White Play Triangle
    center_x = size / 2.0
    center_y = size / 2.0
    tri_width = size * 0.28
    tri_height = size * 0.32

    p1 = (center_x - tri_width * 0.42, center_y - tri_height * 0.5)
    p2 = (center_x - tri_width * 0.42, center_y + tri_height * 0.5)
    p3 = (center_x + tri_width * 0.58, center_y)

    draw.polygon([p1, p2, p3], fill=(255, 255, 255, 255))
    return img

def draw_tv_banner(width: int = 320, height: int = 180) -> Image.Image:
    # Leanback banner (320x180)
    img = Image.new("RGBA", (width, height), (18, 18, 18, 255)) # Dark elegant background
    draw = ImageDraw.Draw(img)

    # Center YouTube Icon on the banner
    icon_height = height * 0.62
    icon_width = icon_height * 1.35
    x0 = (width - icon_width) / 2.0
    y0 = (height - icon_height) / 2.0
    radius = icon_height * 0.28

    draw.rounded_rectangle([x0, y0, x0 + icon_width, y0 + icon_height], radius=radius, fill=(255, 0, 0, 255))

    # Center Play Triangle inside the icon
    cx = x0 + icon_width / 2.0
    cy = y0 + icon_height / 2.0
    tw = icon_width * 0.26
    th = icon_height * 0.36

    p1 = (cx - tw * 0.38, cy - th * 0.5)
    p2 = (cx - tw * 0.38, cy + th * 0.5)
    p3 = (cx + tw * 0.62, cy)

    draw.polygon([p1, p2, p3], fill=(255, 255, 255, 255))
    return img

def main():
    os.makedirs("assets", exist_ok=True)

    sizes = {
        "app_icon_mdpi.png": 48,
        "app_icon_hdpi.png": 72,
        "app_icon_xhdpi.png": 96,
        "app_icon_xxhdpi.png": 144,
        "app_icon_xxxhdpi.png": 192,
        "app_icon_512.png": 512,
    }

    for name, sz in sizes.items():
        icon = draw_youtube_icon(sz)
        icon.save(os.path.join("assets", name), "PNG")
        print(f"Generated assets/{name} ({sz}x{sz})")

    banner = draw_tv_banner(320, 180)
    banner.save(os.path.join("assets", "app_banner_320x180.png"), "PNG")
    print("Generated assets/app_banner_320x180.png (320x180)")

if __name__ == "__main__":
    main()
