import os
import shutil
import tempfile
from pathlib import Path
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class FileManager:
    """Utility class for file operations"""
    
    @staticmethod
    def ensure_directory(path: str) -> str:
        """Ensure directory exists, create if not"""
        Path(path).mkdir(parents=True, exist_ok=True)
        return path
    
    @staticmethod
    def clean_directory(path: str, keep_files: Optional[List[str]] = None) -> None:
        """Clean directory contents, optionally keeping specific files"""
        if not os.path.exists(path):
            return
        
        keep_files = keep_files or []
        
        for item in os.listdir(path):
            if item in keep_files:
                continue
                
            item_path = os.path.join(path, item)
            try:
                if os.path.isfile(item_path):
                    os.unlink(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            except Exception as e:
                logger.warning(f"Could not remove {item_path}: {e}")
    
    @staticmethod
    def get_file_size(path: str) -> int:
        """Get file size in bytes"""
        return os.path.getsize(path) if os.path.exists(path) else 0
    
    @staticmethod
    def get_file_extension(filename: str) -> str:
        """Get file extension"""
        return Path(filename).suffix.lower()
    
    @staticmethod
    def is_video_file(filename: str) -> bool:
        """Check if file is a supported video format"""
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'}
        return FileManager.get_file_extension(filename) in video_extensions
    
    @staticmethod
    def create_temp_file(suffix: str = '', prefix: str = 'tmp') -> str:
        """Create temporary file and return path"""
        temp_file = tempfile.NamedTemporaryFile(suffix=suffix, prefix=prefix, delete=False)
        temp_file.close()
        return temp_file.name
    
    @staticmethod
    def safe_filename(filename: str) -> str:
        """Create safe filename by removing/replacing invalid characters"""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        safe_name = filename
        
        for char in invalid_chars:
            safe_name = safe_name.replace(char, '_')
        
        # Remove leading/trailing spaces and dots
        safe_name = safe_name.strip('. ')
        
        # Limit length
        if len(safe_name) > 255:
            name, ext = os.path.splitext(safe_name)
            safe_name = name[:255-len(ext)] + ext
        
        return safe_name or 'unnamed_file'
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    @staticmethod
    def copy_file_with_progress(src: str, dst: str, chunk_size: int = 8192) -> None:
        """Copy file with progress tracking"""
        total_size = os.path.getsize(src)
        copied = 0
        
        with open(src, 'rb') as fsrc, open(dst, 'wb') as fdst:
            while True:
                chunk = fsrc.read(chunk_size)
                if not chunk:
                    break
                fdst.write(chunk)
                copied += len(chunk)
                
                # Could emit progress events here if needed
                progress = (copied / total_size) * 100
                logger.debug(f"Copy progress: {progress:.1f}%")
    
    @staticmethod
    def validate_video_file(file_path: str) -> dict:
        """Validate video file and return metadata"""
        if not os.path.exists(file_path):
            return {"valid": False, "error": "File does not exist"}
        
        if not FileManager.is_video_file(file_path):
            return {"valid": False, "error": "Not a supported video format"}
        
        file_size = FileManager.get_file_size(file_path)
        max_size = 500 * 1024 * 1024  # 500MB
        
        if file_size > max_size:
            return {
                "valid": False, 
                "error": f"File too large ({FileManager.format_file_size(file_size)}). Max size: {FileManager.format_file_size(max_size)}"
            }
        
        if file_size == 0:
            return {"valid": False, "error": "File is empty"}
        
        return {
            "valid": True,
            "size": file_size,
            "formatted_size": FileManager.format_file_size(file_size),
            "extension": FileManager.get_file_extension(file_path)
        }
