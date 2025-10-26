"""Utility script to validate the MediaTranscript development environment.

This script checks the availability of FFmpeg, verifies key Python packages,
and (optionally) exercises an OpenAI-compatible text summarization endpoint.
Use it after setting up the environment to confirm everything is wired up.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from typing import Tuple


def check_ffmpeg() -> Tuple[bool, str]:
    """Return (status, message) indicating FFmpeg availability."""

    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError:
        return False, "FFmpeg executable not found in PATH."
    except subprocess.CalledProcessError as exc:
        message = exc.stderr.strip() or str(exc)
        return False, f"FFmpeg command failed: {message}"

    first_line = result.stdout.strip().splitlines()[0]
    return True, first_line


def check_python_packages() -> Tuple[bool, str]:
    """Verify that Whisper, Flask, and the OpenAI client are importable."""

    package_map = {
        "whisper": "openai-whisper",
        "flask": "Flask",
        "openai": "openai",
    }

    missing = []
    for module_name, package_name in package_map.items():
        try:
            __import__(module_name)
        except ImportError as exc:
            missing.append(f"{package_name} ({exc})")

    if missing:
        detail = ", ".join(missing)
        return False, f"Missing or broken Python packages: {detail}"

    return True, "Required Python packages are importable."


def try_openai_summary(text: str, model: str) -> Tuple[bool, str]:
    """Attempt to call an OpenAI-compatible endpoint to summarize text."""

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return False, "OPENAI_API_KEY not set; skipping API request."

    try:
        from openai import OpenAI
    except ImportError as exc:  # pragma: no cover - handled earlier but defensive
        return False, f"OpenAI client unavailable: {exc}"

    base_url = os.getenv("OPENAI_BASE_URL")
    client_kwargs = {"api_key": api_key}
    if base_url:
        client_kwargs["base_url"] = base_url

    client = OpenAI(**client_kwargs)

    try:
        response = client.responses.create(
            model=model,
            input=(
                "Please provide a concise summary for the following text:\n\n"
                f"{text}"
            ),
            max_output_tokens=120,
        )
    except Exception as exc:  # Broad to surface SDK/server issues clearly
        return False, f"OpenAI-compatible request failed: {exc}"

    summary = getattr(response, "output_text", "").strip()
    if not summary:
        return False, "Received empty response from the API."

    return True, summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate dependencies and test OpenAI-compatible summarization API."
    )
    parser.add_argument(
        "--text",
        default=(
            "MediaTranscript extracts audio, transcribes speech with Whisper, "
            "summarizes content using GPT, and emits downloadable reports."
        ),
        help="Sample text to summarize via the OpenAI-compatible API.",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        help="Model name to use for the API call (default from OPENAI_MODEL or gpt-4o-mini).",
    )
    parser.add_argument(
        "--fail-on-missing-api",
        action="store_true",
        help="Exit with code 1 if API credentials are missing or the call fails.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    ffmpeg_ok, ffmpeg_msg = check_ffmpeg()
    print(f"FFmpeg status : {'OK' if ffmpeg_ok else 'FAIL'} - {ffmpeg_msg}")

    packages_ok, packages_msg = check_python_packages()
    print(f"Python packages: {'OK' if packages_ok else 'FAIL'} - {packages_msg}")

    api_ok, api_msg = try_openai_summary(args.text, args.model)
    status = "OK" if api_ok else "SKIP" if "not set" in api_msg.lower() else "FAIL"
    print(f"OpenAI API    : {status} - {api_msg}")

    if not ffmpeg_ok or not packages_ok:
        return 1

    if args.fail_on_missing_api and not api_ok:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

