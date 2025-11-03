import os
import subprocess
import tempfile
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

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

class SimpleAudioProcessor:
    """Simple audio processor using FFmpeg for audio extraction"""
    
    def __init__(self):
        self.chunk_duration = 30
        logger.info("Initialized Simple Audio Processor (FFmpeg-based)")
        
    def check_ffmpeg(self) -> bool:
        """Check if FFmpeg is available"""
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("FFmpeg not found. Please install FFmpeg to enable audio processing.")
            return False
    
    def extract_audio_with_ffmpeg(self, video_path: str, output_path: str) -> bool:
        """Extract audio using FFmpeg"""
        try:
            if not self.check_ffmpeg():
                return False
                
            logger.info(f"Extracting audio from {video_path} using FFmpeg")
            
            # Use FFmpeg to extract audio
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vn',  # No video
                '-acodec', 'pcm_s16le',  # PCM 16-bit
                '-ar', '16000',  # 16kHz sample rate
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
    
    def get_audio_duration(self, video_path: str) -> float:
        """Get audio duration using FFmpeg"""
        try:
            if not self.check_ffmpeg():
                return 0.0
                
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                duration = float(result.stdout.strip())
                logger.info(f"Audio duration: {duration:.2f} seconds")
                return duration
            else:
                logger.warning("Could not determine audio duration")
                return 0.0
                
        except Exception as e:
            logger.error(f"Error getting audio duration: {e}")
            return 0.0
    
    def try_basic_speech_recognition(self, audio_path: str, duration: float) -> List[TranscriptSegment]:
        """Try basic speech recognition using available libraries"""
        segments = []
        
        # Try using speech_recognition library if available
        try:
            import speech_recognition as sr
            
            logger.info("Attempting speech recognition with SpeechRecognition library")
            recognizer = sr.Recognizer()
            
            # Process audio in chunks for better results
            chunk_duration = 30.0  # 30-second chunks
            
            for start_time in range(0, int(duration), int(chunk_duration)):
                end_time = min(start_time + chunk_duration, duration)
                
                try:
                    # Extract chunk
                    chunk_path = self.extract_audio_chunk(audio_path, start_time, end_time)
                    
                    if chunk_path:
                        # Recognize speech in chunk
                        with sr.AudioFile(chunk_path) as source:
                            audio_data = recognizer.record(source)
                        
                        try:
                            # Try Google Speech Recognition (free, requires internet)
                            text = recognizer.recognize_google(audio_data)
                            
                            if text.strip():
                                segment = TranscriptSegment(
                                    start_time=float(start_time),
                                    end_time=float(end_time),
                                    text=text.strip(),
                                    confidence=0.8
                                )
                                segments.append(segment)
                                logger.info(f"Transcribed chunk {start_time}-{end_time}s: {text[:50]}...")
                        
                        except sr.UnknownValueError:
                            logger.debug(f"No speech detected in chunk {start_time}-{end_time}s")
                        except sr.RequestError as e:
                            logger.warning(f"Speech recognition service error: {e}")
                            break
                        
                        # Clean up chunk file
                        try:
                            os.unlink(chunk_path)
                        except:
                            pass
                
                except Exception as e:
                    logger.warning(f"Error processing chunk {start_time}-{end_time}s: {e}")
                    continue
            
            return segments
            
        except ImportError:
            logger.info("SpeechRecognition library not available")
        except Exception as e:
            logger.warning(f"Speech recognition failed: {e}")
        
        return []
    
    def extract_audio_chunk(self, audio_path: str, start_time: float, end_time: float) -> Optional[str]:
        """Extract a chunk of audio for processing"""
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_chunk:
                chunk_path = temp_chunk.name
            
            cmd = [
                'ffmpeg',
                '-i', audio_path,
                '-ss', str(start_time),
                '-t', str(end_time - start_time),
                '-acodec', 'pcm_s16le',
                '-ar', '16000',
                '-ac', '1',
                '-y',
                chunk_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return chunk_path
            else:
                logger.warning(f"Failed to extract audio chunk: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting audio chunk: {e}")
            return None
    
    def process_video_audio(self, video_path: str) -> List[TranscriptSegment]:
        """Process video audio and return empty segments with timing info"""
        try:
            logger.info("Processing video audio with Simple Audio Processor")
            
            # Get video duration
            duration = self.get_audio_duration(video_path)
            
            if duration <= 0:
                logger.warning("Could not determine video duration")
                return []
            
            # Extract audio to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
                audio_path = temp_audio.name
            
            if not self.extract_audio_with_ffmpeg(video_path, audio_path):
                logger.warning("Audio extraction failed")
                return []
            
            # Try to use basic speech recognition if available
            segments = self.try_basic_speech_recognition(audio_path, duration)
            
            # If no speech recognition available, return empty segments
            if not segments:
                logger.info("No speech recognition available - returning empty transcript segments")
                return []
            
            # Clean up temporary audio file
            try:
                os.unlink(audio_path)
            except:
                pass
            
            logger.info(f"Created {len(segments)} audio segments")
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
        
        return {
            'total_duration': total_duration,
            'speech_duration': total_speech_time,
            'silence_duration': max(0, total_duration - total_speech_time),
            'speech_ratio': total_speech_time / total_duration if total_duration > 0 else 0,
            'total_words': 0,  # Can't count words without actual transcription
            'speaking_rate_wpm': 0,
            'num_segments': len(transcript_segments),
            'num_pauses': 0,
            'long_pauses': []
        }
