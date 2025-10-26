"""Flask API：接收媒体文件并按流水线处理，生成摘要报告。"""

from __future__ import annotations

import os
import uuid
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

from extract_audio import extract_audio
from transcribe_audio import resolve_device, transcribe_audio
from summarize_transcript import DEFAULT_PROMPT, load_client, summarize_text
from generate_report import generate_docx, generate_pdf


app = Flask(__name__)
CORS(app)

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv"}
AUDIO_EXTS = {".wav", ".mp3"}
REPORT_FORMATS = {"docx", "pdf"}


def build_job_directory() -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    job_id = f"job_{timestamp}_{uuid.uuid4().hex[:8]}"
    job_dir = OUTPUT_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    return job_dir


def validate_file_extension(filename: str) -> str:
    if not filename:
        raise ValueError("未提供文件名。")
    return Path(filename).suffix.lower()


@app.post("/api/process")
def process_media():
    upload = request.files.get("file")
    if upload is None or upload.filename == "":
        return jsonify({"error": "请上传有效的视频或音频文件。"}), 400

    try:
        file_ext = validate_file_extension(upload.filename)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if file_ext not in VIDEO_EXTS | AUDIO_EXTS:
        return jsonify({"error": "仅支持视频 (mp4/mov/avi/mkv/flv/wmv) 或音频 (wav/mp3) 文件。"}), 400

    whisper_model = request.form.get("whisperModel", "small")
    whisper_language = request.form.get("language") or None
    summary_model = request.form.get("summaryModel") or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    report_format = request.form.get("reportFormat", "docx").lower()

    if report_format not in REPORT_FORMATS:
        return jsonify({"error": f"报告格式不支持：{report_format}"}), 400

    try:
        api_client = load_client(api_key=request.form.get("apiKey"), base_url=request.form.get("apiBase"))
    except Exception as exc:  # 包含缺少 API key 的情况
        return jsonify({"error": f"无法初始化摘要服务：{exc}"}), 500

    job_dir = build_job_directory()

    try:
        with TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            input_path = tmpdir_path / secure_filename(upload.filename)
            upload.save(input_path)

            if file_ext in VIDEO_EXTS:
                audio_path = tmpdir_path / "audio.wav"
                extract_audio(input_path, audio_path, overwrite=True)
            else:
                audio_path = tmpdir_path / f"audio{file_ext}"
                input_path.replace(audio_path)

            transcript_tmp = tmpdir_path / "transcript.txt"
            device = resolve_device("auto")
            transcribe_audio(
                input_path=audio_path,
                output_path=transcript_tmp,
                model_name=whisper_model,
                language=whisper_language,
                device=device,
                verbose=False,
            )

            transcript_text = transcript_tmp.read_text(encoding="utf-8")

            try:
                max_tokens = int(request.form.get("summaryMaxTokens", "256"))
            except ValueError:
                max_tokens = 256

            summary_text = summarize_text(
                client=api_client,
                model=summary_model,
                transcript=transcript_text,
                system_prompt=request.form.get("prompt") or DEFAULT_PROMPT,
                max_output_tokens=max_tokens,
            )

    except Exception as exc:
        # 清理 job 目录，避免留空
        if job_dir.exists():
            for child in job_dir.iterdir():
                child.unlink(missing_ok=True)
            job_dir.rmdir()
        return jsonify({"error": f"处理失败：{exc}"}), 500

    transcript_output = job_dir / "transcript.txt"
    summary_output = job_dir / "summary.txt"
    report_output = job_dir / ("report.docx" if report_format == "docx" else "report.pdf")

    transcript_output.write_text(transcript_text, encoding="utf-8")
    summary_output.write_text(summary_text, encoding="utf-8")

    if report_format == "docx":
        generate_docx(transcript_text, summary_text, report_output)
    else:
        generate_pdf(transcript_text, summary_text, report_output)

    return jsonify(
        {
            "jobId": job_dir.name,
            "transcript": transcript_text,
            "summary": summary_text,
            "reportUrl": f"/api/reports/{job_dir.name}/{report_output.name}",
        }
    )


@app.get("/api/reports/<job_id>/<path:filename>")
def download_report(job_id: str, filename: str):
    report_path = OUTPUT_DIR / job_id / filename
    if not report_path.exists():
        return jsonify({"error": "报告不存在。"}), 404
    return send_file(report_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
