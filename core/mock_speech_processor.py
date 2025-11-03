import os
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class TranscriptSegment:
    """Represents a transcribed speech segment"""
    start_time: float
    end_time: float
    text: str
    confidence: float = 0.8
    speaker: Optional[str] = None
    
    @property
    def duration(self) -> float:
        return self.end_time - self.start_time

class MockSpeechProcessor:
    """Mock speech processor for testing when Groq is not available"""
    
    def __init__(self, api_key: Optional[str] = None):
        logger.info("Using mock speech processor for demonstration")
        self.chunk_duration = 30
        
    def process_video_audio(self, video_path: str) -> List[TranscriptSegment]:
        """Generate mock transcript segments for demonstration"""
        logger.info("Generating mock transcript segments...")
        
        # Create realistic mock transcript segments
        mock_segments = [
            TranscriptSegment(
                start_time=0.0,
                end_time=15.5,
                text="Welcome everyone to today's meeting. Let's start by reviewing the agenda and discussing our project progress.",
                confidence=0.85
            ),
            TranscriptSegment(
                start_time=15.5,
                end_time=32.0,
                text="As you can see on the screen, we have made significant progress on the user interface. The new design is more intuitive and user-friendly.",
                confidence=0.82
            ),
            TranscriptSegment(
                start_time=32.0,
                end_time=48.3,
                text="Let's move to the next slide. Here we can see the performance metrics and analytics dashboard that we've been working on.",
                confidence=0.88
            ),
            TranscriptSegment(
                start_time=48.3,
                end_time=65.0,
                text="The implementation includes real-time data visualization and interactive charts that provide valuable insights to our users.",
                confidence=0.84
            ),
            TranscriptSegment(
                start_time=65.0,
                end_time=80.2,
                text="Now, let's discuss the technical architecture. We've adopted a microservices approach that ensures scalability and maintainability.",
                confidence=0.86
            ),
            TranscriptSegment(
                start_time=80.2,
                end_time=95.8,
                text="The backend services are built with FastAPI and the frontend uses React with modern hooks and state management.",
                confidence=0.83
            ),
            TranscriptSegment(
                start_time=95.8,
                end_time=112.0,
                text="For deployment, we're using containerization with Docker and orchestration with Kubernetes for better resource management.",
                confidence=0.87
            ),
            TranscriptSegment(
                start_time=112.0,
                end_time=128.5,
                text="Let's look at the testing strategy. We have comprehensive unit tests, integration tests, and end-to-end testing in place.",
                confidence=0.85
            ),
            TranscriptSegment(
                start_time=128.5,
                end_time=145.0,
                text="The CI/CD pipeline automatically runs all tests and deploys to staging environment for review before production release.",
                confidence=0.89
            ),
            TranscriptSegment(
                start_time=145.0,
                end_time=160.0,
                text="That concludes our technical overview. Are there any questions or concerns about the implementation approach?",
                confidence=0.86
            )
        ]
        
        logger.info(f"Generated {len(mock_segments)} mock transcript segments")
        return mock_segments
    
    def get_transcript_for_timerange(self, transcript_segments: List[TranscriptSegment], 
                                   start_time: float, end_time: float) -> str:
        """Get transcript text for a specific time range"""
        relevant_segments = []
        
        for segment in transcript_segments:
            # Check if segment overlaps with the time range
            if (segment.start_time < end_time and segment.end_time > start_time):
                relevant_segments.append(segment)
        
        # Sort by start time
        relevant_segments.sort(key=lambda x: x.start_time)
        
        # Combine text
        transcript_text = " ".join([seg.text for seg in relevant_segments])
        return transcript_text.strip()
    
    def analyze_speech_patterns(self, transcript_segments: List[TranscriptSegment]) -> Dict[str, Any]:
        """Analyze speech patterns for insights"""
        if not transcript_segments:
            return {}
        
        total_duration = max(seg.end_time for seg in transcript_segments)
        total_speech_time = sum(seg.duration for seg in transcript_segments)
        
        # Calculate speaking rate (words per minute)
        total_words = sum(len(seg.text.split()) for seg in transcript_segments)
        speaking_rate = (total_words / (total_speech_time / 60)) if total_speech_time > 0 else 0
        
        return {
            'total_duration': total_duration,
            'speech_duration': total_speech_time,
            'silence_duration': total_duration - total_speech_time,
            'speech_ratio': total_speech_time / total_duration if total_duration > 0 else 0,
            'total_words': total_words,
            'speaking_rate_wpm': speaking_rate,
            'num_segments': len(transcript_segments),
            'num_pauses': 0,
            'long_pauses': []
        }
