"""Auto-trim whitespace around figure images.

For each input image, finds the bounding box of all non-background (non-white)
pixels, expands it by a small margin, and writes the cropped result. This
removes the large blank borders that the NCVEC diagram exports ship with, so
the figures display tightly on Anki cards.

Example:
    python scripts/crop_figures.py "Diagram T1.jpg" "Diagram T2.jpg" \
        --out-dir figures --names T-1,T-2 --margin 16
"""
import argparse
import os

from PIL import Image


def autocrop(image, margin=16, bg_threshold=240):
    """Return `image` cropped to its non-white content plus `margin` pixels.

    `bg_threshold` is the grayscale value (0-255) at or above which a pixel is
    treated as background; 240 tolerates JPEG noise near pure white.
    """
    gray = image.convert('L')
    content_mask = gray.point(lambda p: 255 if p < bg_threshold else 0)
    bbox = content_mask.getbbox()
    if bbox is None:
        return image  # Wholly blank image; nothing to crop.

    left, upper, right, lower = bbox
    left = max(0, left - margin)
    upper = max(0, upper - margin)
    right = min(image.width, right + margin)
    lower = min(image.height, lower + margin)

    return image.crop((left, upper, right, lower))


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inputs", nargs="+", help="Input image files.")
    parser.add_argument("--out-dir", required=True, help="Directory to write cropped images to.")
    parser.add_argument("--margin", type=int, default=16, help="Pixels of margin to keep (default: 16).")
    parser.add_argument("--names", default=None,
                        help="Comma-separated output stems, one per input "
                             "(e.g. 'T-1,T-2,T-3'). Defaults to the input names.")
    parser.add_argument("--format", default="png", help="Output image format/extension (default: png).")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    names = args.names.split(",") if args.names else [None] * len(args.inputs)
    if len(names) != len(args.inputs):
        parser.error("--names must provide exactly one name per input file.")

    for in_path, name in zip(args.inputs, names):
        stem = name if name else os.path.splitext(os.path.basename(in_path))[0]
        out_path = os.path.join(args.out_dir, "{}.{}".format(stem, args.format))

        with Image.open(in_path) as image:
            before = image.size
            cropped = autocrop(image, margin=args.margin)
            cropped.save(out_path)

        print("{}  {} -> {}  ({})".format(
            os.path.basename(in_path), before, cropped.size, out_path))


if __name__ == "__main__":
    main()
