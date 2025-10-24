# Media Transcription and Summarization API

A Flask-based API for transcribing media files using Whisper and generating text summaries using OpenAI-compatible APIs.

## Features

-🎙️ **Media Transcription**: Convert audio/video files to text using Whisper
- 📝 **Text Summarization**: Generate summaries using OpenAI-compatible APIs
-🔄 **Async Processing**: Background job processing for long-running transcription tasks
- 🌐 **REST API**: Simple HTTP endpoints for easy integration

## Prerequisites

- Python 3.8+
- FFmpeg (installed automatically on Windows via winget)
- OpenAI API key (or compatible API endpoint)

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/mediatranscript.git
   cd mediatranscript
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

4. **Verify installation**:
   ```bash
   python test_setup.py
   ```

## Usage

### Start the server

```bash
python app.py
```

The server will start on `http://localhost:5000`

### API Endpoints

#### Health Check
```
GET /health
```

#### Transcribe Media File
```
POST /transcribe
Content-Type: multipart/form-data

file: <media-file>
```

Returns a job ID for tracking the transcription status.

#### Check Transcription Status
```
GET /transcribe/<job_id>
```

#### Generate Summary
```
POST /summarize
Content-Type: application/json

{
  "text": "text to summarize"
}
```

### Example Usage

```bash
# Upload a file for transcription
curl -X POST -F "file=@sample.mp3" http://localhost:5000/transcribe

# Check status (replace with actual job_id)
curl http://localhost:5000/transcribe/1234-5678-...

# Generate summary
curl -X POST -H "Content-Type: application/json" -d '{"text": "Long text here..."}' http://localhost:5000/summarize
```

## Supported File Formats

- Audio: MP3, WAV, OGG, M4A
- Video: MP4, AVI, MOV

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | `your-api-key-here` |
| `OPENAI_API_BASE` | OpenAI API endpoint | `https://api.openai.com/v1` |
| `UPLOAD_FOLDER` | Directory for uploaded files | `uploads` |
| `MAX_CONTENT_LENGTH` | Maximum file size (bytes) | `16777216` (16MB) |

## Development

### Testing
```bash
python test_setup.py
```

### Running in Development Mode
```bash
export FLASK_ENV=development
python app.py
```

## Production Considerations

For production deployment:

1. Use a production WSGI server (Gunicorn, uWSGI)
2. Set up proper file storage (S3, Azure Blob, etc.)
3. Add authentication/authorization
4. Configure proper logging
5. Set up monitoring and health checks

## Troubleshooting

### FFmpeg Issues
- Ensure FFmpeg is in your PATH
- Test with: `ffmpeg -version`

### Whisper Model Issues
- The first run will download models (~1-2GB)
- Ensure sufficient disk space
- Check internet connectivity for model downloads

### OpenAI API Issues
- Verify your API key is correct
- Check API rate limits and billing status

## License

MIT License

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.