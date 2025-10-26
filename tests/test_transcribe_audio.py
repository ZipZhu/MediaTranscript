from __future__ import annotations

import wave
from pathlib import Path

import pytest

import transcribe_audio


class DummyModel:
    def __init__(self, expected_path: Path):
        self.expected_path = expected_path
        self.called_with = None

    def transcribe(self, path: str, language=None, fp16=False, verbose=False):
        self.called_with = {
            "path": path,
            "language": language,
            "fp16": fp16,
            "verbose": verbose,
        }
        assert Path(path).resolve() == self.expected_path.resolve()
        return {"text": "你好，这是测试转录。"}


def _create_silent_wav(path: Path, seconds: int = 1, sample_rate: int = 16000) -> None:
    n_frames = seconds * sample_rate
    with wave.open(str(path), "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b"\x00\x00" * n_frames)


def test_transcribe_audio_writes_output(monkeypatch, tmp_path):
    input_path = tmp_path / "input.wav"
    output_path = tmp_path / "transcript.txt"
    _create_silent_wav(input_path)

    dummy_model = DummyModel(input_path)

    monkeypatch.setattr(transcribe_audio, "whisper", type("W", (), {"load_model": lambda *args, **kwargs: dummy_model}))
    monkeypatch.setattr(transcribe_audio, "torch", type("T", (), {"cuda": type("Cuda", (), {"is_available": staticmethod(lambda: False)})}))

    transcribe_audio.transcribe_audio(
        input_path=input_path,
        output_path=output_path,
        model_name="tiny",
        language="zh",
        device="cpu",
        verbose=False,
    )

    assert output_path.exists()
    assert "你好，这是测试转录" in output_path.read_text(encoding="utf-8")


def test_resolve_device_prefers_cuda(monkeypatch):
    monkeypatch.setattr(transcribe_audio.torch.cuda, "is_available", lambda: True)
    assert transcribe_audio.resolve_device("auto") == "cuda"


def test_transcribe_audio_rejects_wrong_extension(tmp_path):
    input_path = tmp_path / "audio.ogg"
    input_path.write_bytes(b"dummy")
    output_path = tmp_path / "out.txt"

    with pytest.raises(ValueError):
        transcribe_audio.transcribe_audio(
            input_path=input_path,
            output_path=output_path,
            model_name="tiny",
            language=None,
            device="cpu",
            verbose=False,
        )
