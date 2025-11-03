import os
import subprocess
import tempfile
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import json

logger = logging.getLogger(__name__)

@dataclass
class TranscriptSegment:
    """Represents a transcribed speech segment"""
    start_time: float
    end_time: float
    text: str
    confidence: float = 0.0
    speaker: Optional[str] = None
    
    @property
    def duration(self) -> float:
        return self.end_time - self.start_time

class WhisperSpeechProcessor:
    """Speech processor using OpenAI Whisper for offline speech recognition"""
    
    def __init__(self):
        self.chunk_duration = 30
        self.whisper_available = self.check_whisper()
        logger.info(f"Initialized Whisper Speech Processor (Available: {self.whisper_available})")
        
    def check_whisper(self) -> bool:
        """Check if Whisper is available"""
        try:
            import whisper
            return True
        except ImportError:
            logger.warning("Whisper not installed. Install with: pip install openai-whisper")
            return False
    
    def check_ffmpeg(self) -> bool:
        """Check if FFmpeg is available"""
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("FFmpeg not found. Please install FFmpeg.")
            return False
    
    def extract_audio_with_ffmpeg(self, video_path: str, output_path: str) -> bool:
        """Extract audio using FFmpeg"""
        try:
            if not self.check_ffmpeg():
                return False
                
            logger.info(f"Extracting audio from {video_path} using FFmpeg")
            
            # Use FFmpeg to extract audio optimized for speech recognition
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vn',  # No video
                '-acodec', 'pcm_s16le',  # PCM 16-bit
                '-ar', '16000',  # 16kHz sample rate (optimal for speech)
                '-ac', '1',  # Mono
                '-y',  # Overwrite output file
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Audio extracted successfully to {output_path}")
                return True
            else:
                logger.error(f"FFmpeg error: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error extracting audio with FFmpeg: {e}")
            return False
    
    def transcribe_with_whisper(self, audio_path: str) -> List[Dict[str, Any]]:
        """Transcribe audio using Whisper"""
        try:
            if not self.whisper_available:
                return []
            
            import whisper
            
            logger.info("Loading Whisper model...")
            # Use base model for good balance of speed and accuracy
            model = whisper.load_model("base")
            
            logger.info(f"Transcribing audio: {audio_path}")
            result = model.transcribe(
                audio_path,
                word_timestamps=True,
                verbose=False
            )
            
            segments = []
            if 'segments' in result:
                for segment in result['segments']:
                    segments.append({
                        'start': segment.get('start', 0.0),
                        'end': segment.get('end', 0.0),
                        'text': segment.get('text', '').strip(),
                        'confidence': segment.get('avg_logprob', 0.0)
                    })
            
            logger.info(f"Whisper transcription complete: {len(segments)} segments")
            return segments
            
        except Exception as e:
            logger.error(f"Error with Whisper transcription: {e}")
            return []
    
    def transcribe_with_speech_recognition(self, audio_path: str) -> List[Dict[str, Any]]:
        """Fallback transcription using speech_recognition library"""
        try:
            import speech_recognition as sr
            
            logger.info("Using speech_recognition library as fallback")
            
            recognizer = sr.Recognizer()
            
            # Load audio file
            with sr.AudioFile(audio_path) as source:
                audio_data = recognizer.record(source)
            
            # Try Google Speech Recognition (free)
            try:
                text = recognizer.recognize_google(audio_data)
                logger.info("Google Speech Recognition successful")
                
                # Create a single segment for the entire audio
                return [{
                    'start': 0.0,
                    'end': 30.0,  # Approximate
                    'text': text,
                    'confidence': 0.8
                }]
            except sr.UnknownValueError:
                logger.warning("Speech recognition could not understand audio")
                return []
            except sr.RequestError as e:
                logger.error(f"Speech recognition service error: {e}")
                return []
                
        except ImportError:
            logger.warning("speech_recognition library not installed")
            return []
        except Exception as e:
            logger.error(f"Error with speech_recognition: {e}")
            return []
    
    def process_video_audio(self, video_path: str) -> List[TranscriptSegment]:
        """Process video audio and return transcript segments"""
        try:
            logger.info("Processing video audio with Whisper Speech Processor")
            
            # Extract audio to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
                audio_path = temp_audio.name
            
            if not self.extract_audio_with_ffmpeg(video_path, audio_path):
                logger.error("Audio extraction failed")
                return []
            
            # Try Whisper first, then fallback to speech_recognition
            transcript_data = []
            
            if self.whisper_available:
                transcript_data = self.transcribe_with_whisper(audio_path)
            
            if not transcript_data:
                logger.info("Trying speech_recognition as fallback...")
                transcript_data = self.transcribe_with_speech_recognition(audio_path)
            
            # Convert to TranscriptSegment objects
            segments = []
            for data in transcript_data:
                if data.get('text', '').strip():
                    segment = TranscriptSegment(
                        start_time=float(data.get('start', 0.0)),
                        end_time=float(data.get('end', 0.0)),
                        text=data.get('text', '').strip(),
                        confidence=float(data.get('confidence', 0.0))
                    )
                    segments.append(segment)
            
            # Clean up temporary audio file
            try:
                os.unlink(audio_path)
            except:
                pass
            
            logger.info(f"Speech processing complete: {len(segments)} segments with transcripts")
            return segments
            
        except Exception as e:
            logger.error(f"Error processing video audio: {e}")
            return []
    
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
        
        total_duration = max(seg.end_time for seg in transcript_segments) if transcript_segments else 0
        total_speech_time = sum(seg.duration for seg in transcript_segments)
        
        # Calculate speaking rate (words per minute)
        total_words = sum(len(seg.text.split()) for seg in transcript_segments)
        speaking_rate = (total_words / (total_speech_time / 60)) if total_speech_time > 0 else 0
        
        return {
            'total_duration': total_duration,
            'speech_duration': total_speech_time,
            'silence_duration': max(0, total_duration - total_speech_time),
            'speech_ratio': total_speech_time / total_duration if total_duration > 0 else 0,
            'total_words': total_words,
            'speaking_rate_wpm': speaking_rate,
            'num_segments': len(transcript_segments),
            'num_pauses': 0,
            'long_pauses': []
        }
