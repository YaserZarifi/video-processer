# Shorts Factory — Command Reference

Run everything from the project root: `~/projects/shorts_factory`

## Environment

**Activate the venv** (do this first, every new terminal session)
```bash
source venv/bin/activate
```

**Deactivate the venv**
```bash
deactivate
```

**Install/update dependencies**
```bash
pip install -r requirements.txt
```

## Running the Pipeline

**Full pipeline** (probe → detect silences → chunk → convert to vertical)
Prompts for Season and Episode number.
```bash
python -m shorts_factory.pipeline input/your_video.mp4
```

**Vertical-only** (skip chunking — reuses existing chunks in `output/raw_chunks/`)
Prompts for Season, Episode, and bottom text (leave blank to skip).
Much faster when you already have raw chunks and just want to re-render the vertical output (e.g. after a logo/text/quality tweak).
```bash
python run_vertical_only.py
```
Optional custom paths:
```bash
python run_vertical_only.py path/to/chunks path/to/output
```

## Individual Module Scripts (for testing/debugging one step)

**Probe a video's metadata** (duration, resolution, fps, audio)
```bash
python -m shorts_factory.prober input/your_video.mp4
```

**Detect silences + compute cut points** (no actual file output, just prints)
```bash
python -m shorts_factory.cutpoints input/your_video.mp4
```

**Split a video into raw chunks only**
```bash
python -m shorts_factory.splitter input/your_video.mp4 output/raw_chunks
```

**Transcribe a single chunk** (Persian, faster-whisper)
```bash
python -m shorts_factory.transcriber output/raw_chunks/chunk_001.mp4
```

**Convert a single chunk to vertical manually** (quick one-off test)
```bash
python -m shorts_factory.vertical output/raw_chunks/chunk_001.mp4 output/vertical/test_output.mp4
```

## File Locations

| What | Where |
|---|---|
| Source videos | `input/` |
| Logo | `input/logo.png` (path set in `configs/default.yaml`) |
| Raw (pre-vertical) chunks | `output/raw_chunks/` |
| Final vertical Reels output | `output/vertical/` |
| Config (chunk length, branding, logo) | `configs/default.yaml` |

## Notes

- `ffmpeg` and `ffprobe` must be installed and on your PATH.
- Chunking (silence detection + splitting) is the slow/resource-heavy step — use `run_vertical_only.py` whenever you're just tweaking vertical-conversion settings (logo, text, quality, CRF) and don't need to re-chunk.
- Progress bars (`tqdm`) show per-chunk % and overall chunk count during `run_vertical_only.py`.
