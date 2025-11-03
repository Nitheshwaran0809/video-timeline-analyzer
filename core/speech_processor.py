import os
import tempfile
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from groq import Groq
from moviepy.editor import VideoFileClip
import librosa
import soundfile as sf
from dotenv import load_dotenv

load_dotenv()
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

class SpeechProcessor:
    """Handles audio extraction and speech-to-text conversion using Groq API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("Groq API key not found. Set GROQ_API_KEY environment variable.")
        
        try:
            # Initialize with minimal parameters to avoid compatibility issues
            os.environ['GROQ_API_KEY'] = self.api_key
            self.client = Groq()
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
            try:
                # Fallback: try direct initialization
                self.client = Groq(api_key=self.api_key)
            except Exception as e2:
                logger.error(f"Fallback initialization also failed: {e2}")
                raise ValueError(f"Could not initialize Groq client: {e2}")
        self.chunk_duration = 30  # Process audio in 30-second chunks
        
    def extract_audio(self, video_path: str, output_path: str) -> str:
        """Extract audio from video file"""
        try:
            logger.info(f"Extracting audio from {video_path}")
            
            # Load video and extract audio
            video = VideoFileClip(video_path)
            audio = video.audio
            
            # Write audio to file
            audio.write_audiofile(output_path, verbose=False, logger=None)
            
            # Clean up
            audio.close()
            video.close()
            
            logger.info(f"Audio extracted to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error extracting audio: {e}")
            raise
    
    def split_audio_chunks(self, audio_path: str, chunk_duration: int = 30) -> List[Tuple[str, float, float]]:
        """Split audio into chunks for processing"""
        try:
            # Load audio file
            y, sr = librosa.load(audio_path, sr=None)
            duration = len(y) / sr
            
            chunks = []
            chunk_files = []
            
            for start_time in range(0, int(duration), chunk_duration):
                end_time = min(start_time + chunk_duration, duration)
                
                # Extract chunk
                start_sample = int(start_time * sr)
                end_sample = int(end_time * sr)
                chunk_audio = y[start_sample:end_sample]
                
                # Save chunk to temporary file
                chunk_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                sf.write(chunk_file.name, chunk_audio, sr)
                
                chunks.append((chunk_file.name, start_time, end_time))
                chunk_files.append(chunk_file.name)
            
            logger.info(f"Split audio into {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Error splitting audio: {e}")
            raise
    
    def transcribe_audio_chunk(self, audio_path: str) -> Dict[str, Any]:
        """Transcribe a single audio chunk using Groq API"""
        try:
            with open(audio_path, 'rb') as audio_file:
                # Use Groq's Whisper model for transcription
                transcription = self.client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-large-v3",
                    response_format="verbose_json",
                    language="en"  # Can be made configurable
                )
                
            return transcription
            
        except Exception as e:
            logger.error(f"Error transcribing audio chunk {audio_path}: {e}")
            return {"text": "", "segments": []}
    
    def process_video_audio(self, video_path: str) -> List[TranscriptSegment]:
        """Process entire video audio and return transcript segments"""
        transcript_segments = []
        
        try:
            # Extract audio from video
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
                audio_path = self.extract_audio(video_path, temp_audio.name)
            
            # Split audio into chunks
            audio_chunks = self.split_audio_chunks(audio_path)
            
            logger.info(f"Processing {len(audio_chunks)} audio chunks...")
            
            for i, (chunk_path, chunk_start, chunk_end) in enumerate(audio_chunks):
                logger.info(f"Transcribing chunk {i+1}/{len(audio_chunks)} ({chunk_start:.1f}s - {chunk_end:.1f}s)")
                
                # Transcribe chunk
                transcription = self.transcribe_audio_chunk(chunk_path)
                
                if transcription and 'segments' in transcription:
                    # Process segments from Groq response
                    for segment in transcription['segments']:
                        # Adjust timestamps to global video time
                        global_start = chunk_start + segment.get('start', 0)
                        global_end = chunk_start + segment.get('end', 0)
                        
                        transcript_segment = TranscriptSegment(
                            start_time=global_start,
                            end_time=global_end,
                            text=segment.get('text', '').strip(),
                            confidence=segment.get('avg_logprob', 0.0)
                        )
                        
                        if transcript_segment.text:  # Only add non-empty segments
                            transcript_segments.append(transcript_segment)
                
                # Clean up chunk file
                try:
                    os.unlink(chunk_path)
                except:
                    pass
            
            # Clean up main audio file
            try:
                os.unlink(audio_path)
            except:
                pass
            
            logger.info(f"Transcription complete: {len(transcript_segments)} segments")
            return transcript_segments
            
        except Exception as e:
            logger.error(f"Error processing video audio: {e}")
            raise
    
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
        
        # Find pauses (gaps between segments)
        pauses = []
        for i in range(len(transcript_segments) - 1):
            gap = transcript_segments[i + 1].start_time - transcript_segments[i].end_time
            if gap > 1.0:  # Pauses longer than 1 second
                pauses.append({
                    'start': transcript_segments[i].end_time,
                    'end': transcript_segments[i + 1].start_time,
                    'duration': gap
                })
        
        return {
            'total_duration': total_duration,
            'speech_duration': total_speech_time,
            'silence_duration': total_duration - total_speech_time,
            'speech_ratio': total_speech_time / total_duration if total_duration > 0 else 0,
            'total_words': total_words,
            'speaking_rate_wpm': speaking_rate,
            'num_segments': len(transcript_segments),
            'num_pauses': len(pauses),
            'long_pauses': [p for p in pauses if p['duration'] > 3.0]
        }
