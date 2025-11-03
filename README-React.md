# 🎥 Video Timeline Analyzer - React + FastAPI Version

An intelligent AI-powered video analysis system with a modern React frontend and FastAPI backend that automatically detects screen changes and correlates them with spoken discussion to create comprehensive, searchable timelines.

## 🏗️ Architecture

This project now uses a **modern React + FastAPI architecture**:

- **Frontend**: React 18 with modern hooks, Tailwind CSS, and Lucide React icons
- **Backend**: FastAPI with async support, CORS enabled for React frontend
- **Communication**: RESTful API with JSON responses
- **Development**: Separate dev servers with hot reload
- **Production**: Optimized build with static file serving

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Node.js 16+** and **npm**
- **Groq API Key** (free tier available at [https://console.groq.com/](https://console.groq.com/))

### 1. Setup Environment

Create a `.env` file with your Groq API key:
```bash
GROQ_API_KEY=your_groq_api_key_here
```

### 2. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### 3. Development Mode (Recommended)

**Easy Start - Both servers:**
```bash
python start-dev.py
```

This will:
- Install frontend dependencies automatically
- Start FastAPI backend on http://localhost:8000
- Start React frontend on http://localhost:3000
- Enable hot reload for both frontend and backend

**Manual Start:**
```bash
# Terminal 1 - Backend
python main.py

# Terminal 2 - Frontend
cd frontend
npm install
npm start
```

### 4. Production Build

```bash
python build-production.py
python main_production.py
```

## 🌐 Access Points

### Development Mode
- **React Frontend**: http://localhost:3000 (main interface)
- **FastAPI Backend**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

### Production Mode
- **Full Application**: http://localhost:8000 (serves React app + API)
- **API Documentation**: http://localhost:8000/docs

## 📁 Project Structure

```
video-timeline-analyzer/
├── frontend/                    # React frontend application
│   ├── public/                 # Public assets
│   ├── src/
│   │   ├── components/         # Reusable React components
│   │   │   ├── Navbar.js
│   │   │   ├── Footer.js
│   │   │   └── VideoUpload.js
│   │   ├── pages/              # Page components
│   │   │   ├── Home.js
│   │   │   └── Timeline.js
│   │   ├── App.js              # Main App component
│   │   ├── index.js            # React entry point
│   │   └── index.css           # Tailwind CSS styles
│   ├── package.json            # Frontend dependencies
│   └── tailwind.config.js      # Tailwind configuration
├── core/                       # Backend analysis engines
│   ├── video_analyzer.py       # Screen change detection
│   ├── speech_processor.py     # Speech-to-text processing
│   ├── content_correlator.py   # Content correlation
│   └── pdf_exporter.py         # PDF report generation
├── utils/                      # Utility functions
├── templates/                  # Legacy Jinja2 templates (kept for reference)
├── static/                     # Production build output
├── uploads/                    # Uploaded videos and processing files
├── exports/                    # Generated reports
├── main.py                     # FastAPI application (development)
├── main_production.py          # FastAPI application (production)
├── start-dev.py               # Development startup script
├── build-production.py        # Production build script
└── requirements.txt           # Python dependencies
```

## ⚛️ React Frontend Features

### Modern React Architecture
- **React 18** with functional components and hooks
- **React Router** for client-side routing
- **Axios** for API communication
- **Tailwind CSS** for responsive styling
- **Lucide React** for beautiful icons

### Key Components
- **VideoUpload**: Drag-and-drop file upload with progress tracking
- **Timeline**: Interactive timeline viewer with filtering and search
- **Navbar**: Navigation with routing
- **Footer**: Application footer

### User Experience
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Updates**: Live progress tracking during video processing
- **Interactive Filtering**: Search and filter timeline segments
- **Modern UI**: Clean, professional interface with smooth animations

## 🔧 API Endpoints

The FastAPI backend provides a RESTful API:

### Core Endpoints
- `POST /upload` - Upload video file
- `GET /status/{session_id}` - Get processing status
- `GET /results/{session_id}` - Get analysis results
- `POST /export/pdf/{session_id}` - Export timeline to PDF
- `DELETE /session/{session_id}` - Clean up session data
- `GET /health` - Health check

### Static File Serving
- `/uploads/` - Uploaded files and screenshots
- `/exports/` - Generated PDF reports
- `/static/` - Frontend assets (production)

## 🛠️ Development

### Frontend Development
```bash
cd frontend
npm start          # Start dev server
npm run build      # Build for production
npm test           # Run tests
```

### Backend Development
```bash
python main.py     # Start FastAPI server
# Server auto-reloads on file changes
```

### Adding New Features

**Frontend (React):**
1. Create components in `frontend/src/components/`
2. Add pages in `frontend/src/pages/`
3. Update routing in `frontend/src/App.js`
4. Style with Tailwind CSS classes

**Backend (FastAPI):**
1. Add endpoints in `main.py`
2. Create core modules in `core/`
3. Add utilities in `utils/`

## 🔍 Key Differences from Original

### What Changed
- ✅ **Frontend**: Migrated from Jinja2 templates to React SPA
- ✅ **Styling**: Maintained Tailwind CSS with component-based approach
- ✅ **Icons**: Switched from Lucide CDN to Lucide React components
- ✅ **Routing**: Client-side routing with React Router
- ✅ **API**: Added CORS support for cross-origin requests
- ✅ **Development**: Hot reload for both frontend and backend

### What Stayed the Same
- ✅ **Backend Logic**: All video analysis functionality preserved
- ✅ **API Endpoints**: Same REST API structure
- ✅ **Features**: All original features maintained
- ✅ **Dependencies**: Same Python requirements
- ✅ **Configuration**: Same environment variables

## 📊 Performance Benefits

### Development
- **Hot Reload**: Instant updates during development
- **Separate Concerns**: Frontend and backend developed independently
- **Modern Tooling**: React DevTools, ESLint, Prettier support

### Production
- **Optimized Bundle**: Minified and compressed React build
- **Static Assets**: Efficient serving of CSS, JS, and images
- **API Efficiency**: JSON responses instead of server-side rendering

## 🚀 Deployment Options

### Development
```bash
python start-dev.py
```

### Production (Single Server)
```bash
python build-production.py
python main_production.py
```

### Production (With Gunicorn)
```bash
pip install gunicorn
python build-production.py
gunicorn main_production:app -w 4 -k uvicorn.workers.UvicornWorker --host 0.0.0.0 --port 8000
```

### Docker (Optional)
```dockerfile
# Frontend build stage
FROM node:18-alpine as frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Backend stage
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .
COPY --from=frontend-build /app/frontend/build ./static
EXPOSE 8000
CMD ["python", "main_production.py"]
```

## 🤝 Contributing

The project now supports modern development workflows:

1. **Frontend Changes**: Work in `frontend/` directory with React
2. **Backend Changes**: Work in root directory with FastAPI
3. **Testing**: Both frontend and backend have separate test suites
4. **Linting**: ESLint for React, Black/Flake8 for Python

## 📄 Migration Notes

If you're migrating from the original template-based version:

1. **Data Compatibility**: All existing session data and exports remain compatible
2. **API Compatibility**: All existing API endpoints work the same way
3. **Configuration**: Same `.env` file and requirements.txt
4. **Features**: All original features are preserved and enhanced

---

**🎉 You now have a modern React + FastAPI application with all the original functionality plus improved developer experience and user interface!**
