import sys
from pathlib import Path
from rembg import remove
from PIL import Image

def remove_background(input_path: str, output_path: str = None) -> str:
    input_path = Path(input_path)
    if output_path is None:
        output_path = input_path.with_suffix(".png").with_stem(input_path.stem + "_nobg")
    else:
        output_path = Path(output_path)

    with Image.open(input_path) as img:
        result = remove(img)
        result.save(output_path, format="PNG")

    return str(output_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python remove_bg.py <input_image> [output_path.png]")
        sys.exit(1)

    in_path = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) > 2 else None

    result_path = remove_background(in_path, out_path)
    print(f"Saved: {result_path}")
