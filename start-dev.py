#!/usr/bin/env python3
"""
Development startup script for Video Timeline Analyzer
Starts both the FastAPI backend and React frontend in development mode
"""

import os
import sys
import subprocess
import threading
import time
from pathlib import Path

def start_backend():
    """Start the FastAPI backend server"""
    print("🚀 Starting FastAPI backend server...")
    try:
        subprocess.run([
            sys.executable, "main.py"
        ], cwd=Path(__file__).parent)
    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped")

def start_frontend():
    """Start the React frontend development server"""
    print("⚛️  Starting React frontend server...")
    frontend_dir = Path(__file__).parent / "frontend"
    
    # Check if node_modules exists, if not, install dependencies
    if not (frontend_dir / "node_modules").exists():
        print("📦 Installing frontend dependencies...")
        try:
            subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies. Make sure Node.js and npm are installed.")
            return
        except FileNotFoundError:
            print("❌ npm not found. Please install Node.js and npm first.")
            return
    
    try:
        subprocess.run(["npm", "start"], cwd=frontend_dir)
    except KeyboardInterrupt:
        print("\n🛑 Frontend server stopped")
    except FileNotFoundError:
        print("❌ npm not found. Please install Node.js and npm first.")

def main():
    """Main function to start both servers"""
    print("🎥 Video Timeline Analyzer - Development Mode")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ main.py not found. Please run this script from the project root directory.")
        sys.exit(1)
    
    # Create necessary directories
    for directory in ["uploads", "exports"]:
        Path(directory).mkdir(exist_ok=True)
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Give backend time to start
    time.sleep(3)
    
    print("\n" + "=" * 50)
    print("🌐 Servers will be available at:")
    print("   • FastAPI Backend: http://localhost:8000")
    print("   • React Frontend:  http://localhost:3000")
    print("   • API Docs:        http://localhost:8000/docs")
    print("=" * 50)
    
    # Start frontend (this will block until stopped)
    try:
        start_frontend()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down development servers...")

if __name__ == "__main__":
    main()
