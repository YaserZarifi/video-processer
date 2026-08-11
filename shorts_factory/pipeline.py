import logging
from .prober import probe_video
from .cutpoints import detect_silences, compute_cut_points
from .splitter import split_video

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_pipeline(
    input_path: str,
    output_dir: str,
    filename_prefix: str = "chunk",
) -> list[str]:
    """
    Run the full raw-chunking pipeline on a single input video:
    probe -> detect silences -> compute cut points -> split.

    Returns list of output chunk file paths, in order.
    """
    logger.info(f"Probing {input_path}...")
    info = probe_video(input_path)
    logger.info(
        f"Duration: {info['duration']:.2f}s | "
        f"{info['width']}x{info['height']} | "
        f"{info['fps']:.2f} fps | has_audio={info['has_audio']}"
    )

    logger.info("Detecting silences...")
    silences = detect_silences(input_path)
    logger.info(f"Found {len(silences)} silence windows")

    logger.info("Computing cut points...")
    chunks = compute_cut_points(info["duration"], silences)
    logger.info(f"Computed {len(chunks)} chunks")

    logger.info(f"Splitting into '{output_dir}'...")
    output_paths = split_video(input_path, chunks, output_dir, filename_prefix)
    logger.info(f"Done. Created {len(output_paths)} chunk files.")

    return output_paths


if __name__ == "__main__":
    import sys

    input_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "output/raw_chunks"

    paths = run_pipeline(input_path, output_dir)
    print(f"\nCreated {len(paths)} chunks:")
    for p in paths:
        print(f"  {p}")
