import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def split_video(
    input_path: str,
    chunks: list[tuple[float, float]],
    output_dir: str,
    filename_prefix: str = "chunk",
) -> list[str]:
    """
    Split input_path into separate files based on chunk (start, end) times.
    Uses stream copy (no re-encode) for speed.

    Returns list of output file paths, in order.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_paths = []

    for i, (start, end) in enumerate(chunks, 1):
        out_path = str(Path(output_dir) / f"{filename_prefix}_{i:03d}.mp4")
        duration = end - start

        cmd = [
            "ffmpeg", "-y",
            "-ss", str(start),
            "-i", input_path,
            "-t", str(duration),
            "-c", "copy",
            "-avoid_negative_ts", "make_zero",
            out_path,
        ]

        logger.info(f"Splitting chunk {i}: {start:.2f}s - {end:.2f}s -> {out_path}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg failed splitting chunk {i}: {result.stderr}")

        output_paths.append(out_path)

    return output_paths


if __name__ == "__main__":
    import sys
    from .prober import probe_video
    from .cutpoints import detect_silences, compute_cut_points

    input_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "output/raw_chunks"

    info = probe_video(input_path)
    silences = detect_silences(input_path)
    chunks = compute_cut_points(info["duration"], silences)

    paths = split_video(input_path, chunks, output_dir)
    print(f"Created {len(paths)} chunks:")
    for p in paths:
        print(f"  {p}")
