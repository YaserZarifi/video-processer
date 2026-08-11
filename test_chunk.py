import sys
import yaml
import logging
from pathlib import Path
from shorts_factory.transcriber import transcribe_chunk
from shorts_factory.subtitles import create_srt
from shorts_factory.vertical import convert_to_vertical

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_single(raw_path: str, out_dir: str = "output/vertical"):
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    try:
        with open("configs/default.yaml", "r") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        config = {}

    branding_config = config.get("branding", {})
    logo_path = branding_config.get("logo_path", "")
    branding_text = "Test Season - Test Episode - Part 1"

    logger.info(f"Transcribing {raw_path}...")
    segments = transcribe_chunk(raw_path, model_size="small")

    srt_path = str(Path(out_dir) / (Path(raw_path).stem + ".srt"))
    create_srt(segments, srt_path)

    out_path = str(Path(out_dir) / (Path(raw_path).stem + "_vertical.mp4"))

    logger.info("Converting to vertical...")
    convert_to_vertical(
        input_path=raw_path,
        output_path=out_path,
        branding_text=branding_text,
        subtitle_path=srt_path,
        logo_path=logo_path
    )
    logger.info(f"Created: {out_path}")

if __name__ == "__main__":
    process_single(sys.argv[1])
