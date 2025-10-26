import subprocess
from pathlib import Path

import pytest

from extract_audio import build_ffmpeg_command, extract_audio


def _create_dummy_video(path: Path) -> None:
    """使用 ffmpeg 生成一个 1 秒钟的静音测试视频。"""

    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-f",
        "lavfi",
        "-i",
        "sine=frequency=1000:duration=1",
        "-f",
        "lavfi",
        "-i",
        "color=c=black:s=320x240:d=1",
        "-shortest",
        str(path),
    ]
    subprocess.run(command, check=True)


def test_build_ffmpeg_command_for_wav(tmp_path):
    input_path = tmp_path / "input.mp4"
    output_path = tmp_path / "output.wav"
    command = build_ffmpeg_command(input_path, output_path, overwrite=True)

    assert "-acodec" in command
    assert "pcm_s16le" in command
    assert command[-1] == str(output_path)


def test_extract_audio_creates_wav(tmp_path):
    video_path = tmp_path / "sample.mp4"
    audio_path = tmp_path / "extracted.wav"

    _create_dummy_video(video_path)

    extract_audio(video_path, audio_path, overwrite=True)

    assert audio_path.exists()
    assert audio_path.stat().st_size > 0


def test_extract_audio_invalid_extension(tmp_path):
    input_path = tmp_path / "sample.mp4"
    output_path = tmp_path / "audio.txt"
    _create_dummy_video(input_path)

    with pytest.raises(ValueError):
        extract_audio(input_path, output_path)
