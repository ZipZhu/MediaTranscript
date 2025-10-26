from __future__ import annotations

import io
from pathlib import Path

import pytest

import app as flask_app


@pytest.fixture(autouse=True)
def ensure_outputs_dir(tmp_path, monkeypatch):
    # 将 outputs 目录指向临时路径，避免污染真实环境
    monkeypatch.setattr(flask_app, "OUTPUT_DIR", tmp_path)
    (tmp_path).mkdir(exist_ok=True)
    yield


def test_process_endpoint_handles_large_file(monkeypatch):
    fake_transcript = "这是一个测试转录。"
    fake_summary = "这是摘要。"

    def mock_extract(input_path, output_path, overwrite=False):
        output_path.write_bytes(b"audio")

    def mock_transcribe(**kwargs):
        Path(kwargs["output_path"]).write_text(fake_transcript, encoding="utf-8")

    class DummyClient:
        pass

    def mock_load_client(**kwargs):
        return DummyClient()

    def mock_summarize_text(**kwargs):
        return fake_summary

    def mock_generate_docx(transcript, summary, output_path):
        output_path.write_bytes(b"DOCX")

    def mock_generate_pdf(transcript, summary, output_path):
        output_path.write_bytes(b"PDF")

    monkeypatch.setattr(flask_app, "extract_audio", mock_extract)
    monkeypatch.setattr(flask_app, "transcribe_audio", mock_transcribe)
    monkeypatch.setattr(flask_app, "load_client", mock_load_client)
    monkeypatch.setattr(flask_app, "summarize_text", mock_summarize_text)
    monkeypatch.setattr(flask_app, "generate_docx", mock_generate_docx)
    monkeypatch.setattr(flask_app, "generate_pdf", mock_generate_pdf)

    client = flask_app.app.test_client()

    large_file = io.BytesIO(b"0" * 5 * 1024 * 1024)  # 约 5MB
    data = {
        "file": (large_file, "test.mp4"),
        "reportFormat": "pdf",
        "whisperModel": "tiny",
    }

    response = client.post("/api/process", data=data, content_type="multipart/form-data")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["summary"] == fake_summary
    assert payload["transcript"] == fake_transcript
    assert payload["reportUrl"].endswith("report.pdf")


def test_process_endpoint_requires_file():
    client = flask_app.app.test_client()
    response = client.post("/api/process")
    assert response.status_code == 400
    assert "请上传" in response.get_json()["error"]
