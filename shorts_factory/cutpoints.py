import re
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SILENCE_START_RE = re.compile(r"silence_start:\s*([0-9.]+)")
SILENCE_END_RE = re.compile(r"silence_end:\s*([0-9.]+)")


def detect_silences(path: str, noise_db: str = "-30dB", min_duration: float = 0.5) -> list[tuple[float, float]]:
    """
    Run ffmpeg's silencedetect filter and return a list of (start, end)
    timestamps (in seconds) for each detected silence window.
    """
    cmd = [
        "ffmpeg", "-i", path,
        "-af", f"silencedetect=noise={noise_db}:d={min_duration}",
        "-f", "null", "-",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    starts = [float(m) for m in SILENCE_START_RE.findall(result.stderr)]
    ends = [float(m) for m in SILENCE_END_RE.findall(result.stderr)]

    # silence_end is only logged once silence actually ends; if the file
    # ends while still silent, we'll have one more start than end.
    if len(starts) > len(ends):
        starts = starts[:len(ends)]

    return list(zip(starts, ends))


def compute_cut_points(
    duration: float,
    silences: list[tuple[float, float]],
    max_chunk_duration: float = 600.0,
    search_window: float = 10.0,
    safety_margin: float = 1.5,
) -> list[tuple[float, float]]:
    """
    Given total duration and detected silences, compute a list of
    (start, end) chunk boundaries, preferring silence midpoints near
    the effective max mark over hard cuts. safety_margin shaves time
    off max_chunk_duration so real output files (after ffmpeg's own
    frame-boundary rounding) never sneak past the platform's hard cap.
    """
    effective_max = max_chunk_duration - safety_margin
    chunks = []
    current_pos = 0.0

    while current_pos < duration:
        target = current_pos + effective_max

        if target >= duration:
            # Last chunk — just go to the end
            chunks.append((current_pos, duration))
            break

        window_start = target - search_window

        # For each silence window, find the point *inside* it closest to target
        # (clamped to the window's own start/end), but only consider windows
        # that actually overlap our search range and start after current_pos.
        candidates = []
        for s, e in silences:
            if e < current_pos or s > target:
                continue  # no overlap with usable range at all
            clamped = min(max(target, s), e)  # closest point in [s, e] to target
            if window_start <= clamped <= target and clamped > current_pos:
                candidates.append(clamped)

        if candidates:
            cut_at = max(candidates)  # closest to target, from below
        else:
            cut_at = target
            logger.warning(
                f"No natural cut point found near {target:.2f}s — hard cutting."
            )

        chunks.append((current_pos, cut_at))
        current_pos = cut_at

    return chunks


if __name__ == "__main__":
    import sys
    from .prober import probe_video

    path = sys.argv[1]
    info = probe_video(path)
    silences = detect_silences(path)
    chunks = compute_cut_points(info["duration"], silences)

    print(f"Duration: {info['duration']}s")
    print(f"Detected {len(silences)} silence windows: {silences}")
    print(f"Computed {len(chunks)} chunks:")
    for i, (s, e) in enumerate(chunks, 1):
        print(f"  Part {i}: {s:.2f} - {e:.2f} ({e - s:.2f}s)")
