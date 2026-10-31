#!/usr/bin/env python3
"""
Generates clean PNG assets without any external dependencies (using only python standard library: zlib, struct).
"""
import os
import struct
import zlib

def make_png(width: int, height: int, rgba_bytes: bytes) -> bytes:
    def chunk(chunk_type: bytes, data: bytes) -> bytes:
        crc = zlib.crc32(chunk_type + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + chunk_type + data + struct.pack(">I", crc)

    header = b"\x89PNG\r\n\x1a\n"
    # IHDR: width, height, bit_depth=8, color_type=6 (RGBA), compression=0, filter=0, interlace=0
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    ihdr = chunk(b"IHDR", ihdr_data)

    # Scanlines: each line starts with filter byte 0
    raw_lines = bytearray()
    line_stride = width * 4
    for y in range(height):
        raw_lines.append(0)
        raw_lines.extend(rgba_bytes[y * line_stride : (y + 1) * line_stride])

    compressed = zlib.compress(bytes(raw_lines), 9)
    idat = chunk(b"IDAT", compressed)
    iend = chunk(b"IEND", b"")
    return header + ihdr + idat + iend

def generate_youtube_icon(size: int) -> bytes:
    # YouTube Red: #FF0000, Triangle: #FFFFFF, Background: Transparent
    pixels = bytearray(size * size * 4)

    margin = size * 0.12
    r = size * 0.22
    x_min, x_max = margin, size - margin
    y_min, y_max = margin, size - margin

    # Center triangle coordinates
    cx = size / 2.0
    cy = size / 2.0
    tw = size * 0.28
    th = size * 0.32
    p1 = (cx - tw * 0.42, cy - th * 0.5)
    p2 = (cx - tw * 0.42, cy + th * 0.5)
    p3 = (cx + tw * 0.58, cy)

    def in_triangle(px, py):
        # Barycentric coordinates or cross product
        v0x, v0y = p3[0] - p1[0], p3[1] - p1[1]
        v1x, v1y = p2[0] - p1[0], p2[1] - p1[1]
        v2x, v2y = px - p1[0], py - p1[1]
        den = v0x * v1y - v1x * v0y
        if abs(den) < 1e-6:
            return False
        u = (v2x * v1y - v1x * v2y) / den
        v = (v0x * v2y - v2x * v0y) / den
        return (u >= 0) and (v >= 0) and (u + v <= 1.0)

    for y in range(size):
        for x in range(size):
            idx = (y * size + x) * 4

            # Rounded rectangle test
            in_rect = False
            if x_min <= x <= x_max and y_min <= y <= y_max:
                # Check corners
                dx = 0
                dy = 0
                if x < x_min + r:
                    dx = x - (x_min + r)
                elif x > x_max - r:
                    dx = x - (x_max - r)

                if y < y_min + r:
                    dy = y - (y_min + r)
                elif y > y_max - r:
                    dy = y - (y_max - r)

                if dx * dx + dy * dy <= r * r:
                    in_rect = True

            if in_rect:
                if in_triangle(x + 0.5, y + 0.5):
                    # White play triangle
                    pixels[idx : idx + 4] = b"\xFF\xFF\xFF\xFF"
                else:
                    # YouTube Red
                    pixels[idx : idx + 4] = b"\xFF\x00\x00\xFF"
            else:
                pixels[idx : idx + 4] = b"\x00\x00\x00\x00"

    return make_png(size, size, bytes(pixels))

def generate_banner(width: int = 320, height: int = 180) -> bytes:
    # Dark TV background #121212 with centered YouTube button
    pixels = bytearray(width * height * 4)

    icon_h = height * 0.62
    icon_w = icon_h * 1.35
    x0 = (width - icon_w) / 2.0
    y0 = (height - icon_h) / 2.0
    x1 = x0 + icon_w
    y1 = y0 + icon_h
    r = icon_h * 0.28

    cx = x0 + icon_w / 2.0
    cy = y0 + icon_h / 2.0
    tw = icon_w * 0.26
    th = icon_h * 0.36
    p1 = (cx - tw * 0.38, cy - th * 0.5)
    p2 = (cx - tw * 0.38, cy + th * 0.5)
    p3 = (cx + tw * 0.62, cy)

    def in_triangle(px, py):
        v0x, v0y = p3[0] - p1[0], p3[1] - p1[1]
        v1x, v1y = p2[0] - p1[0], p2[1] - p1[1]
        v2x, v2y = px - p1[0], py - p1[1]
        den = v0x * v1y - v1x * v0y
        if abs(den) < 1e-6:
            return False
        u = (v2x * v1y - v1x * v2y) / den
        v = (v0x * v2y - v2x * v0y) / den
        return (u >= 0) and (v >= 0) and (u + v <= 1.0)

    for y in range(height):
        for x in range(width):
            idx = (y * width + x) * 4

            in_rect = False
            if x0 <= x <= x1 and y0 <= y <= y1:
                dx = 0
                dy = 0
                if x < x0 + r:
                    dx = x - (x0 + r)
                elif x > x1 - r:
                    dx = x - (x1 - r)

                if y < y0 + r:
                    dy = y - (y0 + r)
                elif y > y1 - r:
                    dy = y - (y1 - r)

                if dx * dx + dy * dy <= r * r:
                    in_rect = True

            if in_rect:
                if in_triangle(x + 0.5, y + 0.5):
                    pixels[idx : idx + 4] = b"\xFF\xFF\xFF\xFF"
                else:
                    pixels[idx : idx + 4] = b"\xFF\x00\x00\xFF"
            else:
                # Dark TV banner background
                pixels[idx : idx + 4] = b"\x14\x14\x14\xFF"

    return make_png(width, height, bytes(pixels))

def main():
    os.makedirs("assets", exist_ok=True)

    sizes = {
        "app_icon_mdpi.png": 48,
        "app_icon_hdpi.png": 72,
        "app_icon_xhdpi.png": 96,
        "app_icon_xxhdpi.png": 144,
        "app_icon_xxxhdpi.png": 192,
    }

    for name, sz in sizes.items():
        data = generate_youtube_icon(sz)
        with open(os.path.join("assets", name), "wb") as f:
            f.write(data)
        print(f"Created assets/{name} ({sz}x{sz})")

    banner_data = generate_banner(320, 180)
    with open(os.path.join("assets", "app_banner_320x180.png"), "wb") as f:
        f.write(banner_data)
    print("Created assets/app_banner_320x180.png (320x180)")

if __name__ == "__main__":
    main()
