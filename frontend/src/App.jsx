import { useState } from 'react';
import axios from 'axios';

const REPORT_FORMATS = [
  { value: 'docx', label: 'DOCX' },
  { value: 'pdf', label: 'PDF' },
];

const WHISPER_MODELS = ['tiny', 'base', 'small', 'medium', 'large-v3'];

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [apiKey, setApiKey] = useState('');
  const [reportFormat, setReportFormat] = useState('docx');
  const [whisperModel, setWhisperModel] = useState('small');
  const [summaryModel, setSummaryModel] = useState('gpt-4o-mini');
  const [prompt, setPrompt] = useState('');
  const [status, setStatus] = useState('');
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files?.[0] ?? null);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setResult(null);

    if (!selectedFile) {
      setError('请先选择一个视频或音频文件。');
      return;
    }

    setIsProcessing(true);
    setStatus('处理中，请稍候…这可能需要几分钟');

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('reportFormat', reportFormat);
      formData.append('whisperModel', whisperModel);
      formData.append('summaryModel', summaryModel);
      formData.append('summaryMaxTokens', '256');
      if (apiKey) formData.append('apiKey', apiKey);
      if (prompt) formData.append('prompt', prompt);

      const response = await axios.post('/api/process', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 1000 * 60 * 15,
      });

      setResult(response.data);
      setStatus('处理完成');
    } catch (requestError) {
      const message =
        requestError.response?.data?.error || requestError.message || '发生未知错误';
      setError(message);
      setStatus('');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="app-container">
      <header>
        <h1>MediaTranscript 控制台</h1>
        <p>上传视频/音频，自动完成提取、转录、总结与报告生成。</p>
      </header>

      <main>
        <form className="upload-form" onSubmit={handleSubmit}>
          <label className="form-group">
            <span>选择媒体文件</span>
            <input type="file" accept="audio/*,video/*" onChange={handleFileChange} />
          </label>

          <label className="form-group">
            <span>OpenAI API Key（仅在浏览器本地保存）</span>
            <input
              type="password"
              placeholder="sk-..."
              value={apiKey}
              onChange={(event) => setApiKey(event.target.value)}
            />
          </label>

          <label className="form-group">
            <span>Whisper 模型</span>
            <select value={whisperModel} onChange={(event) => setWhisperModel(event.target.value)}>
              {WHISPER_MODELS.map((model) => (
                <option key={model} value={model}>
                  {model}
                </option>
              ))}
            </select>
          </label>

          <label className="form-group">
            <span>摘要模型</span>
            <input
              type="text"
              value={summaryModel}
              onChange={(event) => setSummaryModel(event.target.value)}
            />
          </label>

          <label className="form-group">
            <span>自定义摘要提示词（可选）</span>
            <textarea
              rows={3}
              placeholder="可留空使用默认提示词"
              value={prompt}
              onChange={(event) => setPrompt(event.target.value)}
            />
          </label>

          <label className="form-group">
            <span>报告格式</span>
            <select value={reportFormat} onChange={(event) => setReportFormat(event.target.value)}>
              {REPORT_FORMATS.map(({ value, label }) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </label>

          <button type="submit" disabled={isProcessing}>
            {isProcessing ? '处理中...' : '开始处理'}
          </button>

          {status && <p className="status">{status}</p>}
          {error && <p className="error">{error}</p>}
        </form>

        {result && (
          <section className="result-panel">
            <h2>摘要结果</h2>
            <p className="summary-text">{result.summary}</p>

            <h3>完整转录</h3>
            <pre className="transcript-text">{result.transcript}</pre>

            <a className="download-link" href={result.reportUrl} target="_blank" rel="noreferrer">
              下载报告
            </a>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
