"""Command-line utility to extract audio from video files using FFmpeg.

适用于 MediaTranscript 项目中的 `extract_audio_agent`：
- 输入：视频文件路径（如 MP4/MOV/AVI 等）
- 输出：音频文件路径（支持 WAV 或 MP3）

示例：
    python extract_audio.py --input input.mp4 --output output.wav
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path
from typing import List


def build_ffmpeg_command(input_path: Path, output_path: Path, overwrite: bool) -> List[str]:
    """Construct the FFmpeg command tailored to the requested output format."""

    ext = output_path.suffix.lower()
    if ext not in {".wav", ".mp3"}:
        raise ValueError("输出文件扩展名仅支持 .wav 或 .mp3")

    base_command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(input_path),
        "-vn",
    ]

    if ext == ".wav":
        base_command += ["-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1"]
    elif ext == ".mp3":
        base_command += ["-codec:a", "libmp3lame", "-qscale:a", "2"]

    if overwrite:
        base_command.append("-y")
    else:
        base_command.append("-n")

    base_command.append(str(output_path))
    return base_command


def extract_audio(input_path: Path, output_path: Path, overwrite: bool = False) -> None:
    """Run FFmpeg to extract audio from the given video file."""

    if not input_path.exists():
        raise FileNotFoundError(f"输入文件不存在: {input_path}")

    if not input_path.is_file():
        raise FileNotFoundError(f"输入路径不是文件: {input_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    command = build_ffmpeg_command(input_path, output_path, overwrite)

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"FFmpeg 执行失败，返回码 {exc.returncode}") from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="从视频文件提取音频并保存为 WAV/MP3。")
    parser.add_argument("--input", required=True, help="输入视频文件路径")
    parser.add_argument("--output", required=True, help="输出音频文件路径 (.wav 或 .mp3)")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="如目标文件已存在，允许覆盖",
    )
    return parser.parse_args()


def main() -> None:
    if shutil.which("ffmpeg") is None:
        raise EnvironmentError("未检测到 FFmpeg，请先安装并加入 PATH")

    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()

    extract_audio(input_path, output_path, overwrite=args.overwrite)
    print(f"已生成音频文件: {output_path}")


if __name__ == "__main__":
    main()

