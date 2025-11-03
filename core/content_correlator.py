import re
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from .video_analyzer import ScreenSegment
from .speech_processor import TranscriptSegment

logger = logging.getLogger(__name__)

@dataclass
class TimelineSegment:
    """Combined timeline segment with visual and audio content"""
    id: int
    start_time: float
    end_time: float
    screenshot_path: str
    transcript: str
    summary: str
    key_topics: List[str]
    screen_description: str
    confidence_score: float = 0.0
    
    @property
    def duration(self) -> float:
        return self.end_time - self.start_time
    
    @property
    def formatted_time_range(self) -> str:
        """Format time range as MM:SS - MM:SS"""
        start_min, start_sec = divmod(int(self.start_time), 60)
        end_min, end_sec = divmod(int(self.end_time), 60)
        return f"{start_min:02d}:{start_sec:02d} - {end_min:02d}:{end_sec:02d}"

class ContentCorrelator:
    """Correlates visual screen changes with speech transcription"""
    
    def __init__(self):
        # Keywords that indicate visual references
        self.visual_reference_keywords = [
            "see", "look", "here", "this", "that", "click", "button", "screen",
            "page", "window", "menu", "tab", "panel", "section", "area",
            "right", "left", "top", "bottom", "above", "below", "next to"
        ]
        
        # Keywords for different content types
        self.content_type_keywords = {
            "presentation": ["slide", "presentation", "deck", "powerpoint"],
            "code": ["code", "function", "variable", "class", "method", "script"],
            "browser": ["website", "page", "url", "browser", "chrome", "firefox"],
            "document": ["document", "file", "text", "word", "pdf"],
            "application": ["app", "application", "software", "program", "tool"],
            "demo": ["demo", "demonstration", "example", "show", "tutorial"]
        }
    
    def correlate_content(self, screen_segments: List[ScreenSegment], 
                         transcript_segments: List[TranscriptSegment]) -> List[TimelineSegment]:
        """Correlate screen segments with transcript segments"""
        timeline_segments = []
        
        logger.info(f"Correlating {len(screen_segments)} screen segments with {len(transcript_segments)} transcript segments")
        
        for screen_segment in screen_segments:
            # Get transcript for this screen's time range
            transcript_text = self._get_transcript_for_timerange(
                transcript_segments, 
                screen_segment.start_time, 
                screen_segment.end_time
            )
            
            # Analyze content
            summary = self._generate_summary(transcript_text)
            key_topics = self._extract_key_topics(transcript_text)
            screen_description = self._describe_screen_content(transcript_text)
            confidence_score = self._calculate_confidence_score(transcript_text, screen_segment)
            
            timeline_segment = TimelineSegment(
                id=screen_segment.id,
                start_time=screen_segment.start_time,
                end_time=screen_segment.end_time,
                screenshot_path=screen_segment.screenshot_path,
                transcript=transcript_text,
                summary=summary,
                key_topics=key_topics,
                screen_description=screen_description,
                confidence_score=confidence_score
            )
            
            timeline_segments.append(timeline_segment)
        
        logger.info(f"Created {len(timeline_segments)} timeline segments")
        return timeline_segments
    
    def _get_transcript_for_timerange(self, transcript_segments: List[TranscriptSegment], 
                                    start_time: float, end_time: float) -> str:
        """Get transcript text for a specific time range without overlaps"""
        relevant_segments = []
        
        for segment in transcript_segments:
            # Check if segment is primarily within this time range
            segment_center = (segment.start_time + segment.end_time) / 2
            if start_time <= segment_center < end_time:
                relevant_segments.append(segment)
        
        # If no segments found with center method, fall back to overlap method
        if not relevant_segments:
            for segment in transcript_segments:
                # Check for significant overlap (at least 50% of segment duration)
                overlap_start = max(segment.start_time, start_time)
                overlap_end = min(segment.end_time, end_time)
                overlap_duration = max(0, overlap_end - overlap_start)
                segment_duration = segment.end_time - segment.start_time
                
                if segment_duration > 0 and overlap_duration / segment_duration >= 0.5:
                    relevant_segments.append(segment)
        
        # Sort by start time and remove duplicates
        relevant_segments.sort(key=lambda x: x.start_time)
        seen_texts = set()
        unique_segments = []
        
        for segment in relevant_segments:
            if segment.text not in seen_texts:
                unique_segments.append(segment)
                seen_texts.add(segment.text)
        
        # Combine text
        transcript_text = " ".join([seg.text for seg in unique_segments])
        return transcript_text.strip()
    
    def _generate_summary(self, transcript_text: str) -> str:
        """Generate a concise summary of the discussion"""
        if not transcript_text:
            return "No discussion - Visual only"
        
        # Simple extractive summary - take first and key sentences
        sentences = re.split(r'[.!?]+', transcript_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return "No clear discussion points"
        
        # Take first sentence and any sentence with visual references
        summary_sentences = [sentences[0]]
        
        for sentence in sentences[1:]:
            if any(keyword in sentence.lower() for keyword in self.visual_reference_keywords):
                if sentence not in summary_sentences:
                    summary_sentences.append(sentence)
        
        # Limit to 2-3 sentences
        summary = ". ".join(summary_sentences[:3])
        if not summary.endswith('.'):
            summary += '.'
        
        return summary
    
    def _extract_key_topics(self, transcript_text: str) -> List[str]:
        """Extract key topics from transcript"""
        if not transcript_text:
            return []
        
        topics = []
        text_lower = transcript_text.lower()
        
        # Check for content type keywords
        for content_type, keywords in self.content_type_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(content_type.title())
        
        # Extract potential topics using simple NLP
        # Look for repeated important words (nouns/verbs)
        words = re.findall(r'\b[a-zA-Z]{4,}\b', transcript_text.lower())
        word_freq = {}
        
        # Common stop words to ignore
        stop_words = {
            'this', 'that', 'with', 'have', 'will', 'from', 'they', 'been',
            'were', 'said', 'each', 'which', 'their', 'time', 'about', 'would',
            'there', 'could', 'other', 'more', 'very', 'what', 'know', 'just',
            'first', 'into', 'over', 'think', 'also', 'your', 'work', 'life'
        }
        
        for word in words:
            if word not in stop_words and len(word) > 4:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get most frequent words as topics
        frequent_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:3]
        for word, freq in frequent_words:
            if freq > 1:  # Only include words mentioned multiple times
                topics.append(word.title())
        
        return topics[:5]  # Limit to 5 topics
    
    def _describe_screen_content(self, transcript_text: str) -> str:
        """Describe what type of screen content is being shown"""
        if not transcript_text:
            return "Unknown screen content"
        
        text_lower = transcript_text.lower()
        
        # Check for specific application mentions
        if any(word in text_lower for word in ["powerpoint", "slide", "presentation"]):
            return "PowerPoint presentation"
        elif any(word in text_lower for word in ["code", "editor", "vscode", "programming"]):
            return "Code editor"
        elif any(word in text_lower for word in ["browser", "website", "chrome", "firefox", "url"]):
            return "Web browser"
        elif any(word in text_lower for word in ["document", "word", "text", "file"]):
            return "Document viewer"
        elif any(word in text_lower for word in ["terminal", "command", "console"]):
            return "Terminal/Command line"
        elif any(word in text_lower for word in ["dashboard", "analytics", "chart", "graph"]):
            return "Dashboard/Analytics"
        elif any(word in text_lower for word in ["email", "outlook", "message"]):
            return "Email application"
        elif any(word in text_lower for word in ["video", "player", "media"]):
            return "Media player"
        else:
            return "Application screen"
    
    def _calculate_confidence_score(self, transcript_text: str, screen_segment: ScreenSegment) -> float:
        """Calculate confidence score for the correlation"""
        if not transcript_text:
            return 0.3  # Low confidence for visual-only segments
        
        score = 0.5  # Base score
        
        # Boost score for visual references
        visual_refs = sum(1 for keyword in self.visual_reference_keywords 
                         if keyword in transcript_text.lower())
        score += min(visual_refs * 0.1, 0.3)
        
        # Boost score for longer discussions
        word_count = len(transcript_text.split())
        if word_count > 50:
            score += 0.1
        elif word_count > 100:
            score += 0.2
        
        # Boost score for longer screen duration (more stable screen)
        if screen_segment.duration > 10:
            score += 0.1
        elif screen_segment.duration > 30:
            score += 0.2
        
        return min(score, 1.0)
    
    def export_timeline_data(self, timeline_segments: List[TimelineSegment]) -> Dict[str, Any]:
        """Export timeline data for JSON serialization"""
        return {
            'segments': [asdict(segment) for segment in timeline_segments],
            'metadata': {
                'total_segments': len(timeline_segments),
                'total_duration': max(seg.end_time for seg in timeline_segments) if timeline_segments else 0,
                'avg_segment_duration': sum(seg.duration for seg in timeline_segments) / len(timeline_segments) if timeline_segments else 0
            }
        }
    
    def filter_segments_by_confidence(self, timeline_segments: List[TimelineSegment], 
                                    min_confidence: float = 0.5) -> List[TimelineSegment]:
        """Filter segments by confidence score"""
        filtered = [seg for seg in timeline_segments if seg.confidence_score >= min_confidence]
        logger.info(f"Filtered {len(timeline_segments)} segments to {len(filtered)} with confidence >= {min_confidence}")
        return filtered
