import os
import json
import tempfile
import logging
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime

# Import our core modules
from core.video_analyzer import VideoAnalyzer
from core.speech_processor import SpeechProcessor
from core.whisper_speech_processor import WhisperSpeechProcessor
from core.simple_audio_processor import SimpleAudioProcessor
from core.content_correlator import ContentCorrelator
from core.pdf_exporter import PDFExporter

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Video Timeline Analyzer",
    description="Intelligent video analysis system that detects screen changes and correlates them with speech",
    version="1.0.0"
)

# Add CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/exports", StaticFiles(directory="exports"), name="exports")

# Global variables to store analysis results
analysis_results = {}
processing_status = {}

# Initialize processors with real video processing approach
video_analyzer = VideoAnalyzer(
    similarity_threshold=0.85,  # Higher threshold for more accurate detection
    min_duration=2.0           # Minimum 2 seconds like reference code
)

# Initialize speech processor with fallback chain: Groq -> Whisper -> Simple
speech_processor = None
processor_type = "none"

# Try Groq first (if API key available)
try:
    speech_processor = SpeechProcessor()
    processor_type = "groq"
    logger.info("✅ Groq speech processor initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize Groq speech processor: {e}")
    
    # Try Whisper as fallback
    try:
        speech_processor = WhisperSpeechProcessor()
        processor_type = "whisper"
        logger.info("✅ Whisper speech processor initialized successfully")
    except Exception as e2:
        logger.error(f"❌ Failed to initialize Whisper speech processor: {e2}")
        
        # Final fallback to simple audio processor
        speech_processor = SimpleAudioProcessor()
        processor_type = "simple"
        logger.info("⚠️ Using simple audio processor (audio detection only)")

logger.info(f"🎤 Active speech processor: {processor_type}")

content_correlator = ContentCorrelator()
pdf_exporter = PDFExporter()


@app.post("/upload")
async def upload_video(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Upload and process video file"""
    if not file.filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
        raise HTTPException(status_code=400, detail="Unsupported video format")
    
    # Create unique session ID
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save uploaded file
    upload_dir = Path("uploads") / session_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    video_path = upload_dir / file.filename
    with open(video_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Initialize processing status
    processing_status[session_id] = {
        "status": "uploaded",
        "progress": 0,
        "message": "Video uploaded successfully",
        "video_filename": file.filename
    }
    
    # Start background processing
    background_tasks.add_task(process_video, session_id, str(video_path))
    
    return {"session_id": session_id, "message": "Video uploaded. Processing started."}

async def process_video(session_id: str, video_path: str):
    """Background task to process video"""
    try:
        logger.info(f"Starting video processing for session {session_id}")
        
        # Update status
        processing_status[session_id].update({
            "status": "processing",
            "progress": 10,
            "message": "Analyzing video frames..."
        })
        
        # Create output directories
        frames_dir = Path("uploads") / session_id / "frames"
        frames_dir.mkdir(exist_ok=True)
        
        # Step 1: Analyze video for screen changes
        logger.info("Step 1: Analyzing screen changes")
        screen_segments = video_analyzer.analyze_video(video_path, str(frames_dir))
        
        processing_status[session_id].update({
            "progress": 40,
            "message": f"Found {len(screen_segments)} screen segments. Processing audio..."
        })
        
        # Step 2: Process speech
        logger.info("Step 2: Processing speech")
        transcript_segments = speech_processor.process_video_audio(video_path)
        
        processing_status[session_id].update({
            "progress": 70,
            "message": "Correlating content..."
        })
        
        # Step 3: Correlate content
        logger.info("Step 3: Correlating content")
        timeline_segments = content_correlator.correlate_content(screen_segments, transcript_segments)
        
        processing_status[session_id].update({
            "progress": 90,
            "message": "Finalizing analysis..."
        })
        
        # Store results
        analysis_results[session_id] = {
            "timeline_segments": timeline_segments,
            "screen_segments": screen_segments,
            "transcript_segments": transcript_segments,
            "video_path": video_path,
            "processed_at": datetime.now().isoformat()
        }
        
        # Update final status
        processing_status[session_id].update({
            "status": "completed",
            "progress": 100,
            "message": f"Analysis complete! Found {len(timeline_segments)} timeline segments."
        })
        
        logger.info(f"Video processing completed for session {session_id}")
        
    except Exception as e:
        logger.error(f"Error processing video for session {session_id}: {e}")
        processing_status[session_id].update({
            "status": "error",
            "progress": 0,
            "message": f"Error: {str(e)}"
        })

@app.get("/status/{session_id}")
async def get_processing_status(session_id: str):
    """Get processing status for a session"""
    if session_id not in processing_status:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return processing_status[session_id]

@app.get("/results/{session_id}")
async def get_results(session_id: str):
    """Get analysis results for a session"""
    if session_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Results not found")
    
    results = analysis_results[session_id]
    
    # Convert timeline segments to JSON-serializable format
    timeline_data = []
    for segment in results["timeline_segments"]:
        segment_data = {
            "id": segment.id,
            "start_time": segment.start_time,
            "end_time": segment.end_time,
            "duration": segment.duration,
            "formatted_time_range": segment.formatted_time_range,
            "screenshot_path": f"/uploads/{session_id}/frames/{os.path.basename(segment.screenshot_path)}",
            "transcript": segment.transcript,
            "summary": segment.summary,
            "key_topics": segment.key_topics,
            "screen_description": segment.screen_description,
            "confidence_score": segment.confidence_score
        }
        timeline_data.append(segment_data)
    
    return {
        "session_id": session_id,
        "timeline_segments": timeline_data,
        "metadata": {
            "total_segments": len(timeline_data),
            "video_filename": processing_status.get(session_id, {}).get("video_filename", "Unknown"),
            "processed_at": results["processed_at"]
        }
    }


@app.post("/export/pdf/{session_id}")
async def export_pdf(session_id: str):
    """Export timeline to PDF"""
    if session_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Results not found")
    
    try:
        results = analysis_results[session_id]
        timeline_segments = results["timeline_segments"]
        video_filename = processing_status.get(session_id, {}).get("video_filename", "Unknown")
        
        # Create exports directory
        exports_dir = Path("exports")
        exports_dir.mkdir(exist_ok=True)
        
        # Generate PDF
        pdf_filename = f"timeline_analysis_{session_id}.pdf"
        pdf_path = exports_dir / pdf_filename
        
        # Convert dict segments back to TimelineSegment objects for PDF export
        from core.content_correlator import TimelineSegment
        
        timeline_objects = []
        for seg_dict in timeline_segments:
            timeline_obj = TimelineSegment(
                id=seg_dict.get('id', 0),
                start_time=seg_dict.get('start_time', 0.0),
                end_time=seg_dict.get('end_time', 0.0),
                screenshot_path=seg_dict.get('screenshot_path', ''),
                transcript=seg_dict.get('transcript', ''),
                summary=seg_dict.get('summary', ''),
                key_topics=seg_dict.get('key_topics', []),
                screen_description=seg_dict.get('screen_description', ''),
                confidence_score=seg_dict.get('confidence_score', 0.0)
            )
            timeline_objects.append(timeline_obj)
        
        # Export PDF with detailed logging
        logger.info(f"Exporting PDF for session {session_id} with {len(timeline_objects)} segments")
        pdf_result = pdf_exporter.export_timeline_pdf(timeline_objects, str(pdf_path), video_filename)
        
        # Verify PDF was created
        if not pdf_path.exists():
            raise Exception(f"PDF file was not created at {pdf_path}")
        
        file_size = pdf_path.stat().st_size
        logger.info(f"PDF created successfully: {pdf_path} ({file_size} bytes)")
        
        return {
            "message": "PDF exported successfully",
            "download_url": f"/exports/{pdf_filename}",
            "filename": pdf_filename,
            "file_size": file_size
        }
        
    except Exception as e:
        logger.error(f"Error exporting PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Error exporting PDF: {str(e)}")

@app.get("/download/{session_id}/{filename}")
async def download_file(session_id: str, filename: str):
    """Download exported files"""
    file_path = Path("exports") / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type='application/octet-stream'
    )

@app.delete("/session/{session_id}")
async def cleanup_session(session_id: str):
    """Clean up session data"""
    try:
        # Remove from memory
        if session_id in analysis_results:
            del analysis_results[session_id]
        if session_id in processing_status:
            del processing_status[session_id]
        
        # Clean up files (optional - you might want to keep them)
        session_dir = Path("uploads") / session_id
        if session_dir.exists():
            import shutil
            shutil.rmtree(session_dir)
        
        return {"message": "Session cleaned up successfully"}
        
    except Exception as e:
        logger.error(f"Error cleaning up session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error cleaning up session: {str(e)}")

@app.post("/configure/sensitivity")
async def configure_sensitivity(config: dict):
    """Configure video analysis sensitivity"""
    global video_analyzer
    
    similarity_threshold = config.get("similarity_threshold", 0.75)
    min_duration = config.get("min_duration", 0.5)
    frame_skip = config.get("frame_skip", 5)
    
    # Validate ranges
    similarity_threshold = max(0.1, min(0.99, similarity_threshold))
    min_duration = max(0.1, min(10.0, min_duration))
    frame_skip = max(1, min(60, frame_skip))
    
    # Create new analyzer with updated settings
    video_analyzer = VideoAnalyzer(
        similarity_threshold=similarity_threshold,
        min_duration=min_duration
    )
    video_analyzer.frame_skip = frame_skip
    
    return {
        "message": "Sensitivity configured successfully",
        "settings": {
            "similarity_threshold": similarity_threshold,
            "min_duration": min_duration,
            "frame_skip": frame_skip
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_sessions": len(processing_status),
        "analyzer_settings": {
            "similarity_threshold": video_analyzer.similarity_threshold,
            "min_duration": video_analyzer.min_duration,
            "frame_skip": video_analyzer.frame_skip
        }
    }

if __name__ == "__main__":
    # Create necessary directories
    for directory in ["uploads", "exports"]:
        Path(directory).mkdir(exist_ok=True)
    
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
