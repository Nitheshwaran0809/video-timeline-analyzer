# 🎥 Video Timeline Analyzer

An intelligent AI-powered video analysis system that automatically detects screen changes and correlates them with spoken discussion to create comprehensive, searchable timelines.

## ✨ Features

### 🔍 **Smart Screen Change Detection**
- Advanced computer vision algorithms detect meaningful screen transitions
- Filters out minor cursor movements, typing, and insignificant changes
- Configurable sensitivity and minimum duration thresholds
- High-quality screenshot capture at each transition

### 🎤 **Accurate Speech-to-Text**
- Powered by Groq's Whisper API for high-quality transcription
- Precise timestamp alignment with visual content
- Handles multiple speakers and conversation breaks
- Supports various audio qualities and accents

### 🧠 **Intelligent Content Correlation**
- Maps visual content to verbal discussion automatically
- Generates concise summaries for each screen segment
- Extracts key topics and identifies content types
- Confidence scoring for correlation accuracy

### 🎨 **Professional Web Interface**
- Modern, responsive design with Tailwind CSS
- Real-time processing progress tracking
- Interactive timeline visualization
- Advanced filtering and search capabilities

### 📄 **Export & Sharing**
- **PDF Reports**: Professional, formatted analysis reports
- **JSON Export**: Raw data for further processing
- **Screenshot Gallery**: High-quality screen captures
- **Shareable Links**: Easy collaboration and review

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project
cd video-timeline-analyzer

# Install dependencies
pip install -r requirements.txt
```

### 2. Setup Environment

Create a `.env` file with your Groq API key:
```bash
GROQ_API_KEY=your_groq_api_key_here
```

Get your free API key at: [https://console.groq.com/](https://console.groq.com/)

### 3. Start the Application

**Option A: Easy Start (Recommended)**
```bash
python start.py
```

**Option B: Direct Start**
```bash
python main.py
```

**Option C: Demo Mode (CLI)**
```bash
python demo.py path/to/your/video.mp4
```

### 4. Access the Interface

Open your browser and go to:
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📋 System Requirements

### Required
- **Python 3.8+**
- **Groq API Key** (free tier available)
- **8GB RAM** (minimum, 16GB recommended)
- **2GB free disk space**

### Optional but Recommended
- **FFmpeg** (for advanced video processing)
- **GPU** (for faster computer vision processing)
- **SSD Storage** (for better I/O performance)

## 🎯 Use Cases

### 📊 **Business Meetings**
- Track presentation slides and discussion points
- Generate meeting summaries with visual context
- Create searchable meeting archives

### 🎓 **Training & Tutorials**
- Map instructional content to visual demonstrations
- Create interactive learning materials
- Generate step-by-step guides

### 💻 **Product Demos**
- Analyze feature demonstrations
- Track user interface changes
- Document product workflows

### 📺 **Webinars & Presentations**
- Correlate slides with speaker notes
- Generate comprehensive event summaries
- Create searchable content libraries

## 🏗️ Architecture

```
video-timeline-analyzer/
├── core/                   # Core analysis engines
│   ├── video_analyzer.py   # Screen change detection
│   ├── speech_processor.py # Speech-to-text processing
│   ├── content_correlator.py # Content correlation
│   └── pdf_exporter.py     # PDF report generation
├── utils/                  # Utility functions
│   ├── file_utils.py       # File operations
│   └── time_utils.py       # Time formatting
├── templates/              # HTML templates
│   ├── base.html          # Base template
│   ├── index.html         # Upload interface
│   └── timeline.html      # Timeline viewer
├── static/                # CSS, JS, assets
├── uploads/               # Uploaded videos
├── exports/               # Generated reports
├── main.py               # FastAPI application
├── start.py              # Easy startup script
└── demo.py               # CLI demo script
```

## 🔧 Configuration

### Video Analysis Settings
```python
# In core/video_analyzer.py
similarity_threshold = 0.85  # Screen change sensitivity (0.0-1.0)
min_duration = 2.0          # Minimum segment duration (seconds)
frame_skip = 30             # Process every Nth frame
```

### Speech Processing Settings
```python
# In core/speech_processor.py
chunk_duration = 30         # Audio chunk size (seconds)
model = "whisper-large-v3"  # Groq model selection
```

## 📊 Output Formats

### Timeline Segments
Each analyzed segment includes:
- **Time Range**: Start and end timestamps
- **Screenshot**: High-quality screen capture
- **Transcript**: Complete spoken content
- **Summary**: AI-generated discussion summary
- **Topics**: Extracted key topics and themes
- **Confidence Score**: Correlation accuracy (0-100%)

### PDF Report Structure
1. **Title Page**: Video info and executive summary
2. **Statistics**: Analysis metrics and insights
3. **Detailed Timeline**: Complete segment breakdown
4. **Screenshots**: Visual content gallery

## 🛠️ API Reference

### Upload Video
```http
POST /upload
Content-Type: multipart/form-data

file: video file (MP4, AVI, MOV, MKV)
```

### Get Processing Status
```http
GET /status/{session_id}
```

### Get Results
```http
GET /results/{session_id}
```

### Export PDF
```http
POST /export/pdf/{session_id}
```

## 🔍 Troubleshooting

### Common Issues

**"Groq API key not found"**
- Ensure `.env` file exists with valid `GROQ_API_KEY`
- Check API key format and permissions

**"FFmpeg not found"**
- Install FFmpeg: https://ffmpeg.org/download.html
- Add FFmpeg to system PATH

**"Out of memory errors"**
- Reduce video file size or resolution
- Increase system RAM or use smaller chunks
- Close other applications during processing

**"Processing takes too long"**
- Use smaller video files for testing
- Adjust `frame_skip` parameter for faster processing
- Consider using GPU acceleration

### Performance Tips

1. **Optimize Video Files**
   - Use MP4 format for best compatibility
   - Compress videos to reduce file size
   - Limit resolution to 1080p for faster processing

2. **System Optimization**
   - Close unnecessary applications
   - Use SSD storage for better I/O
   - Ensure stable internet for API calls

3. **Configuration Tuning**
   - Increase `similarity_threshold` for fewer segments
   - Adjust `min_duration` to filter short segments
   - Use higher `frame_skip` for faster analysis

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines for:
- Code style and standards
- Testing requirements
- Pull request process
- Issue reporting

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Groq** for providing excellent speech-to-text API
- **OpenCV** for computer vision capabilities
- **FastAPI** for the robust web framework
- **Tailwind CSS** for beautiful UI components

## 📞 Support

- **Documentation**: Check this README and code comments
- **Issues**: Report bugs via GitHub issues
- **API Help**: Visit Groq documentation
- **Community**: Join our discussions

---

**Made with ❤️ for the video analysis community**
