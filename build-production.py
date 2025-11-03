#!/usr/bin/env python3
"""
Production build script for Video Timeline Analyzer
Builds the React frontend and configures FastAPI to serve it
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_frontend():
    """Build the React frontend for production"""
    print("⚛️  Building React frontend for production...")
    frontend_dir = Path(__file__).parent / "frontend"
    
    if not frontend_dir.exists():
        print("❌ Frontend directory not found!")
        return False
    
    # Install dependencies if needed
    if not (frontend_dir / "node_modules").exists():
        print("📦 Installing frontend dependencies...")
        try:
            subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    # Build the frontend
    try:
        subprocess.run(["npm", "run", "build"], cwd=frontend_dir, check=True)
        print("✅ Frontend build completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Frontend build failed: {e}")
        return False
    except FileNotFoundError:
        print("❌ npm not found. Please install Node.js and npm first.")
        return False

def setup_static_files():
    """Copy built frontend files to static directory"""
    print("📁 Setting up static files...")
    
    frontend_build = Path(__file__).parent / "frontend" / "build"
    static_dir = Path(__file__).parent / "static"
    
    if not frontend_build.exists():
        print("❌ Frontend build directory not found!")
        return False
    
    # Remove existing static files
    if static_dir.exists():
        shutil.rmtree(static_dir)
    
    # Copy build files to static directory
    try:
        shutil.copytree(frontend_build, static_dir)
        print("✅ Static files copied successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to copy static files: {e}")
        return False

def create_production_main():
    """Create a production version of main.py that serves the React app"""
    print("🔧 Creating production configuration...")
    
    # Read the current main.py
    main_file = Path(__file__).parent / "main.py"
    if not main_file.exists():
        print("❌ main.py not found!")
        return False
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Add route to serve React app
    react_route = '''
# Serve React app for all frontend routes
@app.get("/{full_path:path}", response_class=HTMLResponse)
async def serve_react_app(request: Request, full_path: str):
    """Serve React app for all frontend routes"""
    # API routes should be handled by existing endpoints
    if full_path.startswith(('api/', 'upload', 'status/', 'results/', 'timeline/', 'export/', 'download/', 'session/', 'health', 'docs', 'redoc', 'openapi.json')):
        raise HTTPException(status_code=404, detail="Not found")
    
    # Serve React app
    return FileResponse('static/index.html')
'''
    
    # Insert the route before the main block
    if 'if __name__ == "__main__":' in content:
        content = content.replace('if __name__ == "__main__":', react_route + '\nif __name__ == "__main__":')
    
    # Write production main file
    prod_main_file = Path(__file__).parent / "main_production.py"
    with open(prod_main_file, 'w') as f:
        f.write(content)
    
    print("✅ Production configuration created!")
    return True

def main():
    """Main function to build for production"""
    print("🎥 Video Timeline Analyzer - Production Build")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ main.py not found. Please run this script from the project root directory.")
        sys.exit(1)
    
    # Build frontend
    if not build_frontend():
        print("❌ Production build failed!")
        sys.exit(1)
    
    # Setup static files
    if not setup_static_files():
        print("❌ Static file setup failed!")
        sys.exit(1)
    
    # Create production main file
    if not create_production_main():
        print("❌ Production configuration failed!")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Production build completed successfully!")
    print("\nTo run in production mode:")
    print("   python main_production.py")
    print("\nOr with gunicorn:")
    print("   pip install gunicorn")
    print("   gunicorn main_production:app -w 4 -k uvicorn.workers.UvicornWorker")
    print("=" * 50)

if __name__ == "__main__":
    main()
