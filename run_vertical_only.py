import sys
from pathlib import Path
from tqdm import tqdm
from shorts_factory.pipeline import load_config
from shorts_factory.vertical import convert_to_vertical

raw_dir = sys.argv[1] if len(sys.argv) > 1 else "output/raw_chunks"
vertical_dir = sys.argv[2] if len(sys.argv) > 2 else "output/vertical"

config = load_config()
branding_config = config.get("branding", {})
branding_enabled = branding_config.get("enabled", False)
branding_template = branding_config.get("text_format", "")
logo_path = branding_config.get("logo_path", "")

season = input("Enter Season number: ")
episode = input("Enter Episode number: ")
bottom_text = input("Enter text to show under the logo (leave empty for none): ")

raw_paths = sorted(Path(raw_dir).glob("*.mp4"))
print(f"Found {len(raw_paths)} raw chunks in '{raw_dir}'")

for index, raw_path in enumerate(tqdm(raw_paths, desc="Overall progress", unit="chunk")):
    part_number = index + 1
    out_name = raw_path.stem + "_vertical.mp4"
    out_path = str(Path(vertical_dir) / out_name)

    current_text = ""
    if branding_enabled and branding_template:
        current_text = (
            branding_template
            .replace("{season}", season)
            .replace("{episode}", episode)
            .replace("{part}", str(part_number))
        )

    print(f"Converting {part_number}/{len(raw_paths)}: {raw_path.name}")
    convert_to_vertical(
        input_path=str(raw_path),
        output_path=out_path,
        branding_text=current_text,
        subtitle_path="",
        logo_path=logo_path,
        bottom_text=bottom_text,
    )

print("Done!")
