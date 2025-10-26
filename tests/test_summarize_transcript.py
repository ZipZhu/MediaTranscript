from __future__ import annotations

import types

import pytest

import summarize_transcript


class DummyClient:
    def __init__(self, text: str):
        self._text = text

    class Response:
        def __init__(self, text: str):
            self.output_text = text

    class ResponseMgr:
        def __init__(self, outer: "DummyClient"):
            self.outer = outer

        def create(self, *_, **__):
            return DummyClient.Response(self.outer._text)

    @property
    def responses(self):
        return DummyClient.ResponseMgr(self)


def test_load_client_requires_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(EnvironmentError):
        summarize_transcript.load_client(api_key=None, base_url=None)


def test_summarize_text_returns_output():
    client = DummyClient("摘要内容")
    summary = summarize_transcript.summarize_text(
        client=client,
        model="mock-model",
        transcript="需要总结的文本",
        system_prompt="请总结",
        max_output_tokens=128,
    )
    assert summary == "摘要内容"


def test_summarize_text_rejects_empty_input():
    client = DummyClient("摘要")
    with pytest.raises(ValueError):
        summarize_transcript.summarize_text(
            client=client,
            model="mock-model",
            transcript="  \n  ",
            system_prompt="",
            max_output_tokens=32,
        )
