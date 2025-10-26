"""CLI 工具：调用 OpenAI 兼容 API 对转录文本进行总结。

示例：
    python summarize_transcript.py --input transcript.txt --output summary.txt

环境变量支持：
- OPENAI_API_KEY: API 密钥（必需或通过 --api-key 提供）
- OPENAI_BASE_URL: 可选，自定义兼容 API 的基础 URL
- OPENAI_MODEL: 默认模型名称，可被 --model 覆盖
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from openai import OpenAI


DEFAULT_PROMPT = (
    "你是一名专业的内容总结助手。请在保持关键信息的同时，"
    "生成一段简洁、结构清晰的摘要，突出主题、要点和任何重要行动项。"
)


def load_client(api_key: str | None, base_url: str | None) -> OpenAI:
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise EnvironmentError("未提供 OPENAI_API_KEY，无法调用 AI 接口。")

    client_kwargs = {"api_key": key}
    base_url = base_url or os.getenv("OPENAI_BASE_URL")
    if base_url:
        client_kwargs["base_url"] = base_url

    return OpenAI(**client_kwargs)


def summarize_text(
    client: OpenAI,
    model: str,
    transcript: str,
    system_prompt: str,
    max_output_tokens: int,
) -> str:
    if not transcript.strip():
        raise ValueError("输入转录文本为空，无法生成总结。")

    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    "请总结以下转录内容：\n\n" + transcript.strip()
                ),
            },
        ],
        max_output_tokens=max_output_tokens,
    )

    summary = getattr(response, "output_text", "").strip()
    if not summary:
        raise RuntimeError("API 返回为空，请检查服务端是否正常工作。")

    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="调用 AI API 对转录文本生成摘要。")
    parser.add_argument("--input", required=True, help="输入转录文本文件路径")
    parser.add_argument("--output", required=True, help="输出摘要文本文件路径")
    parser.add_argument(
        "--model",
        default=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        help="使用的模型名称，默认读取 OPENAI_MODEL 或 gpt-4o-mini",
    )
    parser.add_argument(
        "--prompt",
        default=DEFAULT_PROMPT,
        help="系统提示词，可自定义摘要风格",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="可选，直接传入 API 密钥；若未提供则读取环境变量",
    )
    parser.add_argument(
        "--base-url",
        default=None,
        help="可选，自定义兼容 API 的基础 URL",
    )
    parser.add_argument(
        "--max-output-tokens",
        type=int,
        default=256,
        help="限制摘要长度的最大输出 token 数，默认 256",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    input_path = Path(args.input).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()

    if not input_path.exists():
        raise FileNotFoundError(f"输入文本文件不存在: {input_path}")

    transcript = input_path.read_text(encoding="utf-8")

    client = load_client(api_key=args.api_key, base_url=args.base_url)

    summary = summarize_text(
        client=client,
        model=args.model,
        transcript=transcript,
        system_prompt=args.prompt,
        max_output_tokens=args.max_output_tokens,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(summary, encoding="utf-8")

    print(f"摘要已生成，保存路径: {output_path}")


if __name__ == "__main__":
    main()

