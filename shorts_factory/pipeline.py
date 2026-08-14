import logging
import yaml
from pathlib import Path
from .prober import probe_video
from .cutpoints import detect_silences, compute_cut_points
from .splitter import split_video
from .vertical import convert_to_vertical
from .transcriber import transcribe_chunk
from .subtitles import create_srt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_config(config_path: str = "configs/default.yaml") -> dict:
    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return {}

def run_pipeline(
    input_path: str,
    output_dir: str,
    vertical_dir: str,
    filename_prefix: str = "chunk",
    season: str = "1",
    episode: str = "1",
    bottom_text: str = "",
) -> list[str]:
    config = load_config()
    branding_config = config.get("branding", {})
    branding_enabled = branding_config.get("enabled", False)
    branding_template = branding_config.get("text_format", "")
    logo_path = branding_config.get("logo_path", "")

    logger.info(f"Probing {input_path}...")
    info = probe_video(input_path)
    logger.info(
        f"Duration: {info['duration']:.2f}s | "
        f"{info['width']}x{info['height']} | "
        f"{info['fps']:.2f} fps | has_audio={info['has_audio']}"
    )

    chunking_config = config.get("chunking", {})
    max_chunk_duration = float(chunking_config.get("chunk_length_minutes", 5)) * 60.0
    logger.info(f"Chunk length cap: {max_chunk_duration:.0f}s")

    logger.info("Detecting silences...")
    silences = detect_silences(input_path)
    logger.info(f"Found {len(silences)} silence windows")

    logger.info("Computing cut points...")
    chunks = compute_cut_points(info["duration"], silences, max_chunk_duration=max_chunk_duration)
    logger.info(f"Computed {len(chunks)} chunks")

    logger.info(f"Splitting into '{output_dir}'...")
    raw_paths = split_video(input_path, chunks, output_dir, filename_prefix)
    logger.info(f"Done. Created {len(raw_paths)} raw chunk files.")

    logger.info("Starting vertical conversion phase...")
    vertical_paths = []
    for index, raw_path in enumerate(raw_paths):
        part_number = index + 1
        out_name = Path(raw_path).stem + "_vertical.mp4"
        out_path = str(Path(vertical_dir) / out_name)

        current_text = ""
        if branding_enabled and branding_template:
            current_text = branding_template.replace("{season}", season).replace("{episode}", episode).replace("{part}", str(part_number))

        # logger.info(f"Transcribing chunk {part_number}...")
        # segments = transcribe_chunk(raw_path, model_size="small")
        # srt_path = str(Path(vertical_dir) / (Path(raw_path).stem + ".srt"))
        # create_srt(segments, srt_path)

        logger.info(f"Converting chunk {part_number}/{len(raw_paths)} to vertical with subtitles...")
        final_path = convert_to_vertical(
            input_path=raw_path,
            output_path=out_path,
            branding_text=current_text,
            # subtitle_path=srt_path
            subtitle_path="",
            logo_path=logo_path,
            bottom_text=bottom_text,
        )
        vertical_paths.append(final_path)

    logger.info("Pipeline complete!")
    return vertical_paths

if __name__ == "__main__":
    import sys

    input_path = sys.argv[1]
    raw_dir = "output/raw_chunks"
    vert_dir = "output/vertical"

    season_input = input("Enter Season number: ")
    episode_input = input("Enter Episode number: ")
    bottom_text_input = input("Enter text to show under the logo (leave empty for none): ")

    paths = run_pipeline(input_path, raw_dir, vert_dir, season=season_input, episode=episode_input, bottom_text=bottom_text_input)
    print(f"\nCreated {len(paths)} final vertical shorts:")
    for p in paths:
        print(f"  {p}")
