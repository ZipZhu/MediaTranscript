from pathlib import Path

from docx import Document

from generate_report import generate_docx, generate_pdf


def test_generate_docx_creates_file(tmp_path):
    output = tmp_path / "report.docx"
    generate_docx("转录内容", "摘要内容", output)

    assert output.exists()
    doc = Document(output)
    texts = "\n".join(p.text for p in doc.paragraphs)
    assert "摘要内容" in texts
    assert "转录内容" in texts


def test_generate_pdf_creates_file(tmp_path):
    output = tmp_path / "report.pdf"
    generate_pdf("转录内容", "摘要内容", output)

    assert output.exists()
    assert output.stat().st_size > 0
