import json
import subprocess
from pathlib import Path


def probe_video(path: str) -> dict:
    """
    Run ffprobe on a video file and return key metadata.

    Returns a dict with:
        duration (float, seconds)
        width (int)
        height (int)
        fps (float)
        has_audio (bool)
    Raises RuntimeError if ffprobe fails or file has no video stream.
    """
    if not Path(path).is_file():
        raise FileNotFoundError(f"Video file not found: {path}")

    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format", "-show_streams",
        path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed for {path}: {result.stderr}")

    data = json.loads(result.stdout)

    video_stream = next(
        (s for s in data["streams"] if s["codec_type"] == "video"), None
    )
    if video_stream is None:
        raise RuntimeError(f"No video stream found in {path}")

    audio_stream = next(
        (s for s in data["streams"] if s["codec_type"] == "audio"), None
    )

    # r_frame_rate comes as a fraction string like "30/1"
    num, den = video_stream["r_frame_rate"].split("/")
    fps = float(num) / float(den)

    duration = float(data["format"]["duration"])
    format_bit_rate = data["format"].get("bit_rate")
    if format_bit_rate is not None:
        bit_rate = float(format_bit_rate)
    else:
        # Some containers don't report an overall bitrate — estimate it
        # from file size instead so downstream chunk-size logic still works.
        file_size_bytes = Path(path).stat().st_size
        bit_rate = (file_size_bytes * 8) / duration if duration > 0 else 0.0

    return {
        "duration": duration,
        "width": int(video_stream["width"]),
        "height": int(video_stream["height"]),
        "fps": fps,
        "has_audio": audio_stream is not None,
        "bit_rate": bit_rate,
    }


if __name__ == "__main__":
    import sys
    result = probe_video(sys.argv[1])
    print(json.dumps(result, indent=2))
