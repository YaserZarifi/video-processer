import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def convert_to_vertical(
    input_path: str,
    output_path: str,
    target_width: int = 1080,
    target_height: int = 1920,
    blur_sigma: int = 20,
    branding_text: str = "",
) -> str:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    filter_complex = (
        f"[0:v]scale={target_width}:{target_height}:force_original_aspect_ratio=increase,"
        f"crop={target_width}:{target_height},gblur=sigma={blur_sigma}[bg];"
        f"[0:v]scale={target_width}:-2[fg];"
        f"[bg][fg]overlay=(W-w)/2:(H-h)/2"
    )

    if branding_text:
        filter_complex += f"[merged];[merged]drawtext=text='{branding_text}':fontcolor=white:fontsize=50:x=(w-text_w)/2:y=200:box=1:boxcolor=black@0.6:boxborderw=15[out]"
    else:
        filter_complex += "[out]"

    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-filter_complex", filter_complex,
        "-map", "[out]",
        "-map", "0:a?",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "copy",
        output_path,
    ]

    logger.info(f"Converting {input_path} -> {output_path} (vertical {target_width}x{target_height})")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed converting {input_path}: {result.stderr}")

    return output_path


if __name__ == "__main__":
    import sys

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "output/vertical/vertical_test_branded.mp4"

    test_text = "Season 1 - Episode 1 - Part 20"

    convert_to_vertical(input_path, output_path, branding_text=test_text)
    print(f"Created: {output_path}")
