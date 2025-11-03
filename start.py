#!/usr/bin/env python3
"""
Video Timeline Analyzer - Startup Script

This script provides an easy way to start the application with proper
environment setup and error handling.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        return False
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'opencv-python',
        'numpy', 
        'Pillow',
        'scikit-image',
        'groq',
        'python-dotenv',
        'fastapi',
        'uvicorn',
        'moviepy',
        'librosa',
        'reportlab'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing required packages: {', '.join(missing_packages)}")
        logger.info("Please install them using: pip install -r requirements.txt")
        return False
    
    return True

def check_environment():
    """Check environment setup"""
    env_file = Path('.env')
    if not env_file.exists():
        logger.warning(".env file not found. Creating template...")
        with open('.env', 'w') as f:
            f.write("GROQ_API_KEY=your_groq_api_key_here\n")
        logger.info("Please edit .env file and add your Groq API key")
        return False
    
    # Check if API key is set
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key or api_key == 'your_groq_api_key_here':
        logger.error("GROQ_API_KEY not set in .env file")
        return False
    
    return True

def check_ffmpeg():
    """Check if FFmpeg is available"""
    try:
        subprocess.run(['ffmpeg', '-version'], 
                      capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.warning("FFmpeg not found. Some video processing features may not work.")
        logger.info("Please install FFmpeg: https://ffmpeg.org/download.html")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ['uploads', 'exports']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        logger.info(f"Created directory: {directory}")

def start_application():
    """Start the FastAPI application"""
    logger.info("Starting Video Timeline Analyzer...")
    
    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Error starting application: {e}")
        sys.exit(1)

def main():
    """Main startup function"""
    print("=" * 60)
    print("🎥 Video Timeline Analyzer")
    print("   AI-Powered Video Analysis System")
    print("=" * 60)
    
    # Check system requirements
    logger.info("Checking system requirements...")
    
    if not check_python_version():
        sys.exit(1)
    
    if not check_dependencies():
        sys.exit(1)
    
    if not check_environment():
        sys.exit(1)
    
    # Check optional dependencies
    check_ffmpeg()
    
    # Setup directories
    create_directories()
    
    # Start application
    logger.info("All checks passed! Starting application...")
    print("\n🚀 Starting server...")
    print("📱 Web interface will be available at: http://localhost:8000")
    print("📚 API documentation at: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the server\n")
    
    start_application()

if __name__ == "__main__":
    main()
