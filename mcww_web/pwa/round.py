#!/bin/python
import argparse
import os
from PIL import Image, ImageChops, ImageDraw


def create_rounded_icon(
    image_path: str, output_path: str, pad_pct: float, radius_pct: float
):
    """Crops a square image by a percentage and rounds its corners using a percentage."""
    if not os.path.exists(image_path):
        print(f"Error: The file '{image_path}' does not exist.")
        return

    if pad_pct >= 50:
        print(
            "Error: Pad percentage must be less than 50% (otherwise the image collapses)."
        )
        return

    if radius_pct > 50:
        print(
            "Warning: A radius greater than 50% will clip awkwardly. Capping at 50% (perfect circle)."
        )
        radius_pct = 50

    with Image.open(image_path) as img:
        img = img.convert("RGBA")
        width, height = img.size

        # 1. Convert pad percentage to pixels
        pad_px = int(width * (pad_pct / 100.0))
        crop_box = (pad_px, pad_px, width - pad_px, height - pad_px)

        cropped_img = img.crop(crop_box)
        crop_w, crop_h = cropped_img.size

        # 2. Convert radius percentage to pixels (based on the new cropped size)
        # A 50% radius means the radius equals half the width, making a circle.
        radius_px = int(crop_w * (radius_pct / 100.0))

        # 3. Create the mask using pixel values
        mask = Image.new("L", (crop_w, crop_h), 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle(
            (0, 0, crop_w, crop_h), radius=radius_px, fill=255
        )

        # 4. Merge alpha channels
        orig_alpha = cropped_img.split()[3]
        final_alpha = ImageChops.multiply(orig_alpha, mask)
        cropped_img.putalpha(final_alpha)

        # 5. Save the result
        cropped_img.save(output_path, "PNG")
        print(f"Success! Rounded icon saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Crop a square icon and round its corners using percentages."
    )

    # Positional argument
    parser.add_argument("input", help="Path to the input square icon image.")

    # Percentage arguments
    parser.add_argument(
        "-p",
        "--pad",
        type=float,
        required=True,
        help="Percentage (0-49) to crop from each side.",
    )
    parser.add_argument(
        "-r",
        "--radius",
        type=float,
        required=True,
        help="Corner radius as a percentage (0-50) of the cropped image.",
    )

    # Optional output argument
    parser.add_argument(
        "-o",
        "--output",
        default="rounded_output.png",
        help="Path to save the output image (default: rounded_output.png).",
    )

    args = parser.parse_args()

    create_rounded_icon(
        image_path=args.input,
        output_path=args.output,
        pad_pct=args.pad,
        radius_pct=args.radius,
    )


if __name__ == "__main__":
    main()