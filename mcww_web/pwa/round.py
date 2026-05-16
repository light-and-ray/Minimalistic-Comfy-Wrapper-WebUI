#!/usr/bin/env python3
import argparse
import os
import math
from PIL import Image, ImageChops, ImageDraw

def generate_superellipse_points(width: int, height: int, n: float, num_points: int = 1000):
    """Calculates the coordinates for a superellipse polygon."""
    points = []
    a = width / 2.0
    b = height / 2.0

    for i in range(num_points):
        theta = 2 * math.pi * i / num_points

        cos_t = math.cos(theta)
        sin_t = math.sin(theta)

        # Parametric equations for superellipse
        x = a * (abs(cos_t) ** (2 / n)) * math.copysign(1, cos_t)
        y = b * (abs(sin_t) ** (2 / n)) * math.copysign(1, sin_t)

        # Shift coordinates so the center is at (a, b)
        points.append((x + a, y + b))

    return points

def create_superellipse_icon(
    image_path: str, output_path: str, pad_pct: float, exponent: float
):
    """Crops a square image by a percentage and applies a superellipse mask."""
    if not os.path.exists(image_path):
        print(f"Error: The file '{image_path}' does not exist.")
        return

    if pad_pct >= 50:
        print("Error: Pad percentage must be less than 50% (otherwise the image collapses).")
        return

    if exponent < 2:
        print("Warning: An exponent less than 2 creates a star-like shape. Typically use 2 (circle) to 5 (squircle).")

    with Image.open(image_path) as img:
        img = img.convert("RGBA")
        width, height = img.size

        # 1. Convert pad percentage to pixels
        pad_px = int(width * (pad_pct / 100.0))
        crop_box = (pad_px, pad_px, width - pad_px, height - pad_px)

        cropped_img = img.crop(crop_box)
        crop_w, crop_h = cropped_img.size

        # 2. Create a high-resolution mask for anti-aliasing
        # We draw the polygon at 4x size and then scale it down for smooth edges.
        scale = 4
        mask_w, mask_h = crop_w * scale, crop_h * scale

        mask = Image.new("L", (mask_w, mask_h), 0)
        draw = ImageDraw.Draw(mask)

        # Calculate superellipse points at the upscaled size
        polygon_points = generate_superellipse_points(mask_w, mask_h, exponent)

        # 3. Draw the polygon and resize the mask down to the target size
        draw.polygon(polygon_points, fill=255)
        mask = mask.resize((crop_w, crop_h), Image.Resampling.LANCZOS)

        # 4. Merge alpha channels
        orig_alpha = cropped_img.split()[3]
        final_alpha = ImageChops.multiply(orig_alpha, mask)
        cropped_img.putalpha(final_alpha)

        # 5. Save the result
        cropped_img.save(output_path, "PNG")
        print(f"Success! Superellipse icon saved to: {output_path}")

def main():
    parser = argparse.ArgumentParser(
        description="Crop a square icon and apply a superellipse (squircle) mask."
    )

    # Positional argument
    parser.add_argument("input", help="Path to the input square icon image.")

    # Modified arguments
    parser.add_argument(
        "-p",
        "--pad",
        type=float,
        required=True,
        help="Percentage (0-49) to crop from each side.",
    )
    parser.add_argument(
        "-n",
        "--exponent",
        type=float,
        default=4.0,
        help="Superellipse exponent (e.g., 2 for circle, 4 or 5 for iOS-like squircle). Default is 4.0.",
    )

    # Optional output argument
    parser.add_argument(
        "-o",
        "--output",
        default="superellipse_output.png",
        help="Path to save the output image (default: superellipse_output.png).",
    )

    args = parser.parse_args()

    create_superellipse_icon(
        image_path=args.input,
        output_path=args.output,
        pad_pct=args.pad,
        exponent=args.exponent,
    )

if __name__ == "__main__":
    main()