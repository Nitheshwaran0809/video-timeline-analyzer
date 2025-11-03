"""
Core video analysis modules for the Video Timeline Analyzer.

This package contains the main analysis engines:
- VideoAnalyzer: Detects screen changes in video content
- SpeechProcessor: Converts speech to text using Groq API
- ContentCorrelator: Maps visual content to verbal discussion
- PDFExporter: Generates professional PDF reports
"""

from .video_analyzer import VideoAnalyzer, ScreenSegment
from .speech_processor import SpeechProcessor, TranscriptSegment
from .content_correlator import ContentCorrelator, TimelineSegment
from .pdf_exporter import PDFExporter

__all__ = [
    'VideoAnalyzer',
    'ScreenSegment',
    'SpeechProcessor', 
    'TranscriptSegment',
    'ContentCorrelator',
    'TimelineSegment',
    'PDFExporter'
]

__version__ = '1.0.0'
