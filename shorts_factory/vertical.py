import subprocess
import logging
from pathlib import Path
from tqdm import tqdm
from .prober import probe_video

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# def convert_to_vertical(
#     input_path: str,
#     output_path: str,
#     target_width: int = 1080,
#     target_height: int = 1920,
#     blur_sigma: int = 20,
#     branding_text: str = "",
#     subtitle_path: str = "",
# ) -> str:
#     Path(output_path).parent.mkdir(parents=True, exist_ok=True)

#     filter_complex = (
#         f"[0:v]scale={target_width}:{target_height}:force_original_aspect_ratio=increase,"
#         f"crop={target_width}:{target_height},gblur=sigma={blur_sigma}[bg];"
#         f"[0:v]scale={target_width}:-2[fg];"
#         f"[bg][fg]overlay=(W-w)/2:(H-h)/2[merged]"
#     )

#     last_node = "merged"

#     if branding_text:
#         filter_complex += f";[{last_node}]drawtext=text='{branding_text}':fontcolor=white:fontsize=50:x=(w-text_w)/2:y=200:box=1:boxcolor=black@0.6:boxborderw=15[branded]"
#         last_node = "branded"



#         # English

#     # if subtitle_path:
#     #     style = "FontSize=12,Bold=1,PrimaryColour=&H0000FFFF,OutlineColour=&H00000000,Outline=1,Shadow=1,Alignment=2,MarginV=50"
#     #     filter_complex += f";[{last_node}]subtitles={subtitle_path}:force_style='{style}'[subbed]"
#     #     last_node = "subbed"



# # Persian


#     if subtitle_path:
#         fonts_path = str(Path("fonts").absolute())
#         style = "FontName=Vazirmatn,FontSize=12,Bold=1,PrimaryColour=&H0000FFFF,OutlineColour=&H00000000,Outline=1,Shadow=1,Alignment=2,MarginV=25"
#         filter_complex += f";[{last_node}]subtitles={subtitle_path}:fontsdir='{fonts_path}':force_style='{style}'[subbed]"
#         last_node = "subbed"



#     filter_complex += f";[{last_node}]null[out]"

#     cmd = [
#         "ffmpeg", "-y",
#         "-i", input_path,
#         "-filter_complex", filter_complex,
#         "-map", "[out]",
#         "-map", "0:a?",
#         "-c:v", "libx264",
#         "-preset", "fast",
#         "-crf", "23",
#         "-c:a", "copy",
#         output_path,
#     ]

#     logger.info(f"Converting {input_path} -> {output_path} (vertical {target_width}x{target_height})")
#     result = subprocess.run(cmd, capture_output=True, text=True)

#     if result.returncode != 0:
#         raise RuntimeError(f"ffmpeg failed converting {input_path}: {result.stderr}")

#     return output_path



def convert_to_vertical(
    input_path: str,
    output_path: str,
    target_width: int = 1080,
    target_height: int = 1920,
    blur_sigma: int = 40,
    branding_text: str = "",
    subtitle_path: str = "",
    logo_path: str = "",
    bottom_text: str = "",
    target_size_mb: float = 0,
    duration: float = 0,
    audio_bitrate_kbps: int = 128,
) -> str:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # If a size target + duration were given, compute the exact video
    # bitrate budget so a two-pass encode lands right at target_size_mb
    # (minus a small safety margin), instead of letting CRF float the size.
    video_bitrate_kbps = None
    if target_size_mb and duration:
        safety_margin = 0.97  # leave ~3% headroom for container/muxing overhead
        total_kbits = target_size_mb * 8 * 1024 * safety_margin
        audio_kbits = audio_bitrate_kbps * duration
        video_bitrate_kbps = max((total_kbits - audio_kbits) / duration, 150)
        logger.info(
            f"Targeting {target_size_mb}MB over {duration:.1f}s -> "
            f"video bitrate ~{video_bitrate_kbps:.0f}kbps (two-pass)"
        )

    filter_complex = (
        f"[0:v]scale={target_width}:{target_height}:force_original_aspect_ratio=increase,"
        f"crop={target_width}:{target_height},scale=iw/4:ih/4,"
        f"gblur=sigma={max(blur_sigma // 4, 1)},scale={target_width}:{target_height}[bg];"
        f"[0:v]scale={target_width}:-2[fg_base];"
    )

    filter_complex += f"[fg_base]null[fg];"

    filter_complex += f"[bg][fg]overlay=(W-w)/2:(H-h)/2[merged]"

    # last_node = "merged"

    # if branding_text:
    #     filter_complex += f";[{last_node}]drawtext=text='{branding_text}':fontcolor=white:fontsize=50:x=(w-text_w)/2:y=200:box=1:boxcolor=black@0.6:boxborderw=15[branded]"
    #     last_node = "branded"

    # if subtitle_path:
    #     fonts_path = str(Path("fonts").absolute())
    #     style = "FontName=Vazirmatn,FontSize=12,Bold=1,PrimaryColour=&H0000FFFF,OutlineColour=&H00000000,Outline=1,Shadow=1,Alignment=2,MarginV=25"
    #     filter_complex += f";[{last_node}]subtitles={subtitle_path}:fontsdir='{fonts_path}':force_style='{style}'[subbed]"
    #     last_node = "subbed"


    last_node = "merged"

    if logo_path:
        filter_complex += f";[1:v]scale=150:-1[logo];[{last_node}][logo]overlay=(W-w)/2:H-h-300[logoed]"
        last_node = "logoed"

    fonts_dir = str(Path("fonts").absolute())
    font_file = str(Path("fonts/Vazirmatn-Bold.ttf").absolute())

    if branding_text:
        filter_complex += f";[{last_node}]drawtext=text='{branding_text}':fontfile='{font_file}':fontcolor=white:fontsize=50:x=(w-text_w)/2:y=200:box=1:boxcolor=black@0.6:boxborderw=15[branded]"
        last_node = "branded"

    if bottom_text:
        filter_complex += f";[{last_node}]drawtext=text='{bottom_text}':fontfile='{font_file}':fontcolor=white:fontsize=50:x=(w-text_w)/2:y=main_h-300:box=1:boxcolor=black@0.6:boxborderw=15[bottomtxt]"
        last_node = "bottomtxt"

    if subtitle_path:
        style = "FontName=Vazirmatn,FontSize=12,Bold=1,PrimaryColour=&H0000FFFF,OutlineColour=&H00000000,Outline=1,Shadow=1,Alignment=2,MarginV=25"
        filter_complex += f";[{last_node}]subtitles={subtitle_path}:fontsdir='{fonts_dir}':force_style='{style}'[subbed]"
        last_node = "subbed"

    filter_complex += f";[{last_node}]null[out]"

    base_cmd = ["ffmpeg", "-y", "-i", input_path]
    if logo_path:
        base_cmd.extend(["-i", logo_path])
    base_cmd.extend(["-filter_complex", filter_complex, "-map", "[out]"])

    if video_bitrate_kbps:
        # Two-pass CBR-ish encode: pass 1 analyzes complexity, pass 2 spends
        # the exact bit budget where it helps quality most. This is what
        # actually lands on target_size_mb — CRF alone can't guarantee a size.
        passlogfile = str(Path(output_path).with_suffix(""))
        maxrate = f"{int(video_bitrate_kbps * 1.5)}k"
        bufsize = f"{int(video_bitrate_kbps * 2)}k"

        pass1_cmd = base_cmd + [
            "-map", "0:a?",
            "-c:v", "h264_nvenc",
            "-preset", "p4",
            "-b:v", f"{video_bitrate_kbps:.0f}k",
            "-maxrate", maxrate,
            "-bufsize", bufsize,
            "-pass", "1",
            "-passlogfile", passlogfile,
            "-an",
            "-f", "mp4",
            "-y", "/dev/null",
        ]
        logger.info(f"Pass 1/2 encoding {input_path}...")
        result = subprocess.run(pass1_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg pass 1 failed for {input_path}: {result.stderr}")

        pass2_cmd = base_cmd + [
            "-map", "0:a?",
            "-c:v", "h264_nvenc",
            "-preset", "p4",
            "-b:v", f"{video_bitrate_kbps:.0f}k",
            "-maxrate", maxrate,
            "-bufsize", bufsize,
            "-pass", "2",
            "-passlogfile", passlogfile,
            "-c:a", "aac",
            "-b:a", f"{audio_bitrate_kbps}k",
            output_path,
        ]
        logger.info(f"Pass 2/2 encoding {input_path} -> {output_path}...")
        result = subprocess.run(pass2_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg pass 2 failed for {input_path}: {result.stderr}")

        for leftover in Path(".").glob(f"{Path(passlogfile).name}-0.log*"):
            leftover.unlink(missing_ok=True)


    else:
        chunk_duration = probe_video(input_path)["duration"]

        # Hit a fixed file-size target directly by budgeting bitrate, instead
        # of leaving size up to qp/cq (which varies with footage complexity).
        size_goal_mb = 145  # a little under 150 for safety margin
        target_audio_kbps = 128
        safety_margin = 0.97
        total_kbits = size_goal_mb * 8 * 1024 * safety_margin
        audio_kbits = target_audio_kbps * chunk_duration
        video_bitrate_kbps = max((total_kbits - audio_kbits) / chunk_duration, 300)
        maxrate_kbps = video_bitrate_kbps * 1.5
        bufsize_kbps = video_bitrate_kbps * 2

        cmd = base_cmd + [
            "-map", "0:a?",
            "-c:v", "h264_nvenc",
            "-preset", "p4",
            "-rc", "vbr",
            "-b:v", f"{video_bitrate_kbps:.0f}k",
            "-maxrate", f"{maxrate_kbps:.0f}k",
            "-bufsize", f"{bufsize_kbps:.0f}k",
            "-c:a", "aac",
            "-b:a", f"{target_audio_kbps}k",
            "-progress", "pipe:1",
            "-nostats",
            output_path,
        ]

        logger.info(f"Converting {input_path} -> {output_path} (vertical {target_width}x{target_height})")
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        bar = tqdm(total=100, desc=Path(input_path).name, unit="%", leave=False)
        last_percent = 0

        for line in process.stdout:
            if line.startswith("out_time_ms="):
                value = line.strip().split("=")[1]
                if not value.isdigit():
                    continue
                out_time_s = int(value) / 1_000_000
                percent = min(int((out_time_s / chunk_duration) * 100), 100)
                bar.update(percent - last_percent)
                last_percent = percent

        process.wait()
        bar.close()

        if process.returncode != 0:
            stderr_output = process.stderr.read()
            raise RuntimeError(f"ffmpeg failed converting {input_path}: {stderr_output}")

    return output_path

if __name__ == "__main__":
    import sys

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "output/vertical/vertical_test_branded.mp4"

    test_text = "Season 1 - Episode 1 - Part 20"

    convert_to_vertical(input_path, output_path, branding_text=test_text)
    print(f"Created: {output_path}")
