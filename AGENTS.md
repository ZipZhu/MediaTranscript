以下是一个完整的 **AGENTS.md** 文件，它包括了所有相关代理的定义、参数、方法以及如何执行它们。

````markdown
# AGENTS.md: Video & Audio Processing with AI Summarization

## Overview
项目名叫“MediaTranscript”

This document outlines the agents required to process video/audio files, transcribe speech to text, and summarize the transcriptions using AI (ChatGPT) in a local environment. It provides a step-by-step guide on how to execute commands to achieve each task and manage the entire workflow.

## Agents

### 1. `extract_audio_agent`
- **Purpose**: Extracts audio from a given video file.
- **Input**: Video file (e.g., MP4, MOV, AVI)
- **Output**: Audio file (e.g., WAV, MP3)
- **Method**:
    - Use FFmpeg to extract audio from the video.
    - Save the extracted audio to a temporary location.
  
#### Example Command:
```bash
extract_audio_agent --input /path/to/video.mp4 --output /path/to/output/audio.wav
````

#### Parameters:

| Parameter  | Description                            | Required | Default |
| ---------- | -------------------------------------- | -------- | ------- |
| `--input`  | Path to the input video file.          | Yes      | N/A     |
| `--output` | Path to save the extracted audio file. | Yes      | N/A     |

---

### 2. `speech_to_text_agent`

* **Purpose**: Converts the audio file into text using Whisper (local ASR).
* **Input**: Audio file (e.g., WAV, MP3)
* **Output**: Transcribed text file
* **Method**:

  * Use Whisper to transcribe the audio.
  * Return the transcribed text.

#### Example Command:

```bash
speech_to_text_agent --input /path/to/audio.wav --output /path/to/output/transcript.txt
```

#### Parameters:

| Parameter  | Description                             | Required | Default |
| ---------- | --------------------------------------- | -------- | ------- |
| `--input`  | Path to the input audio file.           | Yes      | N/A     |
| `--output` | Path to save the transcribed text file. | Yes      | N/A     |

---

### 3. `generate_summary_agent`

* **Purpose**: Summarizes the transcribed text using GPT-3 (Cloud).
* **Input**: Transcribed text file
* **Output**: Summary text
* **Method**:

  * Send the transcribed text to GPT-3 for summarization.
  * Receive a summarized version of the text.

#### Example Command:

```bash
generate_summary_agent --input /path/to/output/transcript.txt --output /path/to/output/summary.txt
```

#### Parameters:

| Parameter  | Description                         | Required | Default |
| ---------- | ----------------------------------- | -------- | ------- |
| `--input`  | Path to the transcribed text file.  | Yes      | N/A     |
| `--output` | Path to save the summary text file. | Yes      | N/A     |

---

### 4. `generate_report_agent`

* **Purpose**: Combines the transcribed text and AI-generated summary into a downloadable report.
* **Input**: Transcribed text, AI summary
* **Output**: Report file (PDF or DOCX)
* **Method**:

  * Combine the original transcription and the summary into one document.
  * Provide options for downloading the final report.

#### Example Command:

```bash
generate_report_agent --transcript /path/to/output/transcript.txt --summary /path/to/output/summary.txt --output /path/to/output/final_report.pdf
```

#### Parameters:

| Parameter      | Description                               | Required | Default |
| -------------- | ----------------------------------------- | -------- | ------- |
| `--transcript` | Path to the transcribed text file.        | Yes      | N/A     |
| `--summary`    | Path to the AI-generated summary file.    | Yes      | N/A     |
| `--output`     | Path to save the final report (PDF/DOCX). | Yes      | N/A     |

---

## Interaction Flow

1. **Step 1**: Upload video/audio.

   * Use `extract_audio_agent` to extract audio if the input is a video.
2. **Step 2**: Transcribe audio to text.

   * Use `speech_to_text_agent` to convert the audio file to text.
3. **Step 3**: Generate AI summary.

   * Use `generate_summary_agent` to summarize the transcription.
4. **Step 4**: Generate final report.

   * Use `generate_report_agent` to combine the transcription and summary, and provide the final report in the desired format.

---

## Example Workflow

1. **Extract audio from a video**:

   ```bash
   extract_audio_agent --input /path/to/video.mp4 --output /path/to/output/audio.wav
   ```
2. **Convert audio to text**:

   ```bash
   speech_to_text_agent --input /path/to/output/audio.wav --output /path/to/output/transcript.txt
   ```
3. **Generate AI summary**:

   ```bash
   generate_summary_agent --input /path/to/output/transcript.txt --output /path/to/output/summary.txt
   ```
4. **Generate final report**:

   ```bash
   generate_report_agent --transcript /path/to/output/transcript.txt --summary /path/to/output/summary.txt --output /path/to/output/final_report.pdf
   ```

---

## Agent Commands and Parameters

| Command                  | Description                               | Required Parameters                                                              |
| ------------------------ | ----------------------------------------- | -------------------------------------------------------------------------------- |
| `extract_audio_agent`    | Extract audio from video file             | `--input <video_path>`, `--output <audio_path>`                                  |
| `speech_to_text_agent`   | Convert audio to text                     | `--input <audio_path>`, `--output <text_path>`                                   |
| `generate_summary_agent` | Summarize transcribed text                | `--input <text_path>`, `--output <summary_path>`                                 |
| `generate_report_agent`  | Create a report with transcript & summary | `--transcript <text_path>`, `--summary <summary_path>`, `--output <report_path>` |

---

## Notes

* **Whisper**: The `speech_to_text_agent` relies on Whisper for ASR (Automatic Speech Recognition), which works entirely locally and doesn't require internet access.
* **GPT-3**: The `generate_summary_agent` requires internet access as it uses GPT-3 for summarizing the transcriptions.
* **FFmpeg**: The `extract_audio_agent` uses FFmpeg to extract audio from video files, so ensure FFmpeg is installed and properly configured on your system.

---

## Troubleshooting

1. **Audio Extraction Failed**:

   * Ensure that FFmpeg is installed and the video file format is supported (MP4, AVI, MOV, etc.).
2. **Speech Recognition Errors**:

   * Check that Whisper is properly installed and has access to the necessary model files.
   * Ensure the audio quality is good and clear for transcription.
3. **Summary Generation Errors**:

   * If the GPT-3 API fails, check your network connection or API limits.
   * Ensure that the input text is not empty or malformed.

---

This **AGENTS.md** provides a clear structure for defining and using agents to process video/audio files, transcribe audio to text, generate summaries using AI, and create a downloadable report. You can now use these commands to efficiently work through each step of the workflow.

```

### 解释

- **各个代理**：每个代理（`extract_audio_agent`、`speech_to_text_agent`、`generate_summary_agent`、`generate_report_agent`）都被详细列出，包括目的、输入输出、命令参数和示例命令。
- **工作流程**：按照从上传视频/音频到生成报告的步骤进行说明。
- **命令和参数**：为每个代理提供了所需的参数和默认值说明。
- **常见问题**：帮助调试和解决常见问题，如音频提取失败、语音识别错误等。

现在，你可以根据这个结构在Codex中执行相关命令，开发和测试你的视频音频处理程序。
```
