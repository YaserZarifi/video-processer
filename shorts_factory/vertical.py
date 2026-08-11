import subprocess
import logging
from pathlib import Path

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
    blur_sigma: int = 20,
    branding_text: str = "",
    subtitle_path: str = "",
    logo_path: str = "",
) -> str:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    filter_complex = (
        f"[0:v]scale={target_width}:{target_height}:force_original_aspect_ratio=increase,"
        f"crop={target_width}:{target_height},gblur=sigma={blur_sigma}[bg];"
        f"[0:v]scale={target_width}:-2[fg_base];"
    )

    if logo_path:
        filter_complex += f"[1:v]scale=150:-1[logo];[fg_base][logo]overlay=0:H-h[fg];"
    else:
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
    fonts_dir = str(Path("fonts").absolute())
    font_file = str(Path("fonts/Vazirmatn-Bold.ttf").absolute())

    if branding_text:
        filter_complex += f";[{last_node}]drawtext=text='{branding_text}':fontfile='{font_file}':fontcolor=white:fontsize=50:x=(w-text_w)/2:y=200:box=1:boxcolor=black@0.6:boxborderw=15[branded]"
        last_node = "branded"

    if subtitle_path:
        style = "FontName=Vazirmatn,FontSize=12,Bold=1,PrimaryColour=&H0000FFFF,OutlineColour=&H00000000,Outline=1,Shadow=1,Alignment=2,MarginV=25"
        filter_complex += f";[{last_node}]subtitles={subtitle_path}:fontsdir='{fonts_dir}':force_style='{style}'[subbed]"
        last_node = "subbed"

    filter_complex += f";[{last_node}]null[out]"

    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
    ]

    if logo_path:
        cmd.extend(["-i", logo_path])

    cmd.extend([
        "-filter_complex", filter_complex,
        "-map", "[out]",
        "-map", "0:a?",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "copy",
        output_path,
    ])

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
