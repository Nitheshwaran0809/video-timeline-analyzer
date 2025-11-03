import time
from datetime import datetime, timedelta
from typing import Union

class TimeUtils:
    """Utility functions for time formatting and conversion"""
    
    @staticmethod
    def seconds_to_mmss(seconds: float) -> str:
        """Convert seconds to MM:SS format"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
    
    @staticmethod
    def seconds_to_hhmmss(seconds: float) -> str:
        """Convert seconds to HH:MM:SS format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    
    @staticmethod
    def mmss_to_seconds(time_str: str) -> float:
        """Convert MM:SS or HH:MM:SS format to seconds"""
        parts = time_str.split(':')
        
        if len(parts) == 2:  # MM:SS
            minutes, seconds = map(int, parts)
            return minutes * 60 + seconds
        elif len(parts) == 3:  # HH:MM:SS
            hours, minutes, seconds = map(int, parts)
            return hours * 3600 + minutes * 60 + seconds
        else:
            raise ValueError("Invalid time format. Use MM:SS or HH:MM:SS")
    
    @staticmethod
    def format_duration(seconds: float, include_ms: bool = False) -> str:
        """Format duration in human readable format"""
        if seconds < 60:
            if include_ms:
                return f"{seconds:.1f}s"
            else:
                return f"{int(seconds)}s"
        elif seconds < 3600:
            return TimeUtils.seconds_to_mmss(seconds)
        else:
            return TimeUtils.seconds_to_hhmmss(seconds)
    
    @staticmethod
    def get_timestamp() -> str:
        """Get current timestamp in ISO format"""
        return datetime.now().isoformat()
    
    @staticmethod
    def get_formatted_timestamp(format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Get formatted timestamp"""
        return datetime.now().strftime(format_str)
    
    @staticmethod
    def time_ago(timestamp: Union[str, datetime]) -> str:
        """Get human readable time ago string"""
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        
        now = datetime.now()
        if timestamp.tzinfo is not None:
            now = now.replace(tzinfo=timestamp.tzinfo)
        
        diff = now - timestamp
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "Just now"
    
    @staticmethod
    def estimate_processing_time(file_size_mb: float, complexity_factor: float = 1.0) -> int:
        """Estimate processing time in seconds based on file size"""
        # Base estimation: ~30 seconds per 100MB for standard processing
        base_time = (file_size_mb / 100) * 30
        
        # Apply complexity factor (e.g., higher for detailed analysis)
        estimated_time = base_time * complexity_factor
        
        # Add minimum time and cap maximum
        estimated_time = max(30, min(estimated_time, 1800))  # 30s to 30min
        
        return int(estimated_time)
    
    @staticmethod
    def create_time_ranges(start_time: float, end_time: float, num_segments: int) -> list:
        """Create evenly spaced time ranges"""
        if num_segments <= 0:
            return []
        
        duration = end_time - start_time
        segment_duration = duration / num_segments
        
        ranges = []
        for i in range(num_segments):
            segment_start = start_time + (i * segment_duration)
            segment_end = start_time + ((i + 1) * segment_duration)
            ranges.append((segment_start, segment_end))
        
        return ranges
    
    @staticmethod
    def overlap_duration(range1: tuple, range2: tuple) -> float:
        """Calculate overlap duration between two time ranges"""
        start1, end1 = range1
        start2, end2 = range2
        
        overlap_start = max(start1, start2)
        overlap_end = min(end1, end2)
        
        if overlap_start < overlap_end:
            return overlap_end - overlap_start
        else:
            return 0.0
    
    @staticmethod
    def merge_overlapping_ranges(ranges: list, min_gap: float = 1.0) -> list:
        """Merge overlapping or close time ranges"""
        if not ranges:
            return []
        
        # Sort ranges by start time
        sorted_ranges = sorted(ranges, key=lambda x: x[0])
        merged = [sorted_ranges[0]]
        
        for current in sorted_ranges[1:]:
            last_merged = merged[-1]
            
            # Check if ranges overlap or are close enough to merge
            if current[0] <= last_merged[1] + min_gap:
                # Merge ranges
                merged[-1] = (last_merged[0], max(last_merged[1], current[1]))
            else:
                # Add as new range
                merged.append(current)
        
        return merged
    
    @staticmethod
    def performance_timer():
        """Context manager for timing code execution"""
        class Timer:
            def __enter__(self):
                self.start = time.perf_counter()
                return self
            
            def __exit__(self, *args):
                self.end = time.perf_counter()
                self.duration = self.end - self.start
            
            def elapsed(self):
                return time.perf_counter() - self.start
        
        return Timer()
