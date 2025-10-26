"""CLI 工具：使用 Whisper 将音频文件转录为文本。

对应 AGENTS.md 中的 `speech_to_text_agent`。

示例：
    python transcribe_audio.py --input audio.wav --output transcript.txt
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

import torch
import whisper


def resolve_device(preferred: Optional[str]) -> str:
    """Determine which device Whisper should use."""

    if preferred and preferred.lower() != "auto":
        return preferred

    return "cuda" if torch.cuda.is_available() else "cpu"


def transcribe_audio(
    input_path: Path,
    output_path: Path,
    model_name: str,
    language: Optional[str],
    device: str,
    verbose: bool,
) -> None:
    """Load Whisper model and write transcription to the output file."""

    if not input_path.exists():
        raise FileNotFoundError(f"输入音频文件不存在: {input_path}")

    if input_path.suffix.lower() not in {".wav", ".mp3"}:
        raise ValueError("仅支持 WAV 或 MP3 格式的音频文件")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    model = whisper.load_model(model_name, device=device)

    transcription = model.transcribe(
        str(input_path),
        language=language,
        fp16=(device.startswith("cuda")),
        verbose=verbose,
    )

    text = transcription.get("text", "").strip()
    if not text:
        raise RuntimeError("Whisper 没有返回任何文本。")

    output_path.write_text(text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="使用 Whisper 将音频转录为文本。")
    parser.add_argument("--input", required=True, help="输入音频文件路径 (.wav/.mp3)")
    parser.add_argument("--output", required=True, help="输出转录文本文件路径")
    parser.add_argument(
        "--model",
        default="small",
        help="Whisper 模型名称（如 tiny/base/small/medium/large-v3，默认 small）",
    )
    parser.add_argument(
        "--language",
        default=None,
        help="音频语言代码（可选，例如 zh / en；不提供则自动检测）",
    )
    parser.add_argument(
        "--device",
        default="auto",
        help="运行设备：auto/cpu/cuda:0 等，默认自动选择",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="显示 Whisper 详细输出",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    input_path = Path(args.input).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()

    device = resolve_device(args.device)

    transcribe_audio(
        input_path=input_path,
        output_path=output_path,
        model_name=args.model,
        language=args.language,
        device=device,
        verbose=args.verbose,
    )

    print(f"转录完成，结果已保存到: {output_path}")


if __name__ == "__main__":
    main()

