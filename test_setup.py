#!/usr/bin/env python3
"""
Simple test script to verify the setup is working correctly.
"""

import sys
import os
from pathlib import Path

def test_python_version():
    """Test Python version"""
    print(f"Python version: {sys.version}")
    if sys.version_info >= (3, 8):
        print("✅ Python version OK")
        return True
    else:
        print("❌ Python 3.8+ required")
        return False

def test_imports():
    """Test core module imports"""
    try:
        from core import VideoAnalyzer, SpeechProcessor, ContentCorrelator, PDFExporter
        from utils import FileManager, TimeUtils
        print("✅ Core modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_dependencies():
    """Test key dependencies"""
    dependencies = [
        ('cv2', 'opencv-python'),
        ('numpy', 'numpy'),
        ('PIL', 'Pillow'),
        ('groq', 'groq'),
        ('fastapi', 'fastapi'),
        ('uvicorn', 'uvicorn'),
        ('reportlab', 'reportlab')
    ]
    
    all_good = True
    for module, package in dependencies:
        try:
            __import__(module)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - run: pip install {package}")
            all_good = False
    
    return all_good

def test_environment():
    """Test environment setup"""
    env_file = Path('.env')
    if env_file.exists():
        print("✅ .env file found")
        
        # Check for API key
        with open('.env', 'r') as f:
            content = f.read()
            if 'GROQ_API_KEY=' in content and 'your_groq_api_key_here' not in content:
                print("✅ Groq API key configured")
                return True
            else:
                print("⚠️  Groq API key needs to be set in .env file")
                return False
    else:
        print("⚠️  .env file not found - will be created on first run")
        return False

def test_directories():
    """Test directory structure"""
    required_dirs = ['core', 'utils', 'frontend']
    all_exist = True
    
    for directory in required_dirs:
        if Path(directory).exists():
            print(f"✅ {directory}/ directory")
        else:
            print(f"❌ {directory}/ directory missing")
            all_exist = False
    
    return all_exist

def main():
    """Run all tests"""
    print("🎥 Video Timeline Analyzer - Setup Test")
    print("=" * 50)
    
    tests = [
        ("Python Version", test_python_version),
        ("Module Imports", test_imports),
        ("Dependencies", test_dependencies),
        ("Environment", test_environment),
        ("Directory Structure", test_directories)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n📋 Testing {name}...")
        result = test_func()
        results.append(result)
    
    print("\n" + "=" * 50)
    print("📊 SETUP TEST SUMMARY")
    print("=" * 50)
    
    if all(results):
        print("🎉 All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Set your Groq API key in .env file (if not done)")
        print("2. Run: python start.py")
        print("3. Open http://localhost:8000 in your browser")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("- Install missing dependencies: pip install -r requirements.txt")
        print("- Set Groq API key in .env file")
        print("- Ensure Python 3.8+ is installed")

if __name__ == "__main__":
    main()
