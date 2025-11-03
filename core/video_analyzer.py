import cv2
import numpy as np
from PIL import Image
import os
from typing import List, Tuple, Dict, Any
from dataclasses import dataclass
from skimage.metrics import structural_similarity as ssim
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ScreenSegment:
    """Represents a unique screen segment with its metadata"""
    id: int
    start_time: float
    end_time: float
    screenshot_path: str
    frame_number: int
    similarity_score: float = 0.0
    description: str = ""
    
    @property
    def duration(self) -> float:
        return self.end_time - self.start_time

class VideoAnalyzer:
    """Core video analysis engine for detecting screen changes"""
    
    def __init__(self, similarity_threshold: float = 0.85, min_duration: float = 2.0):
        self.similarity_threshold = similarity_threshold
        self.min_duration = min_duration  # Minimum duration for a screen segment
        self.frame_interval = 1.0  # Check every 1 second like reference code
        
    def extract_frames(self, video_path: str, output_dir: str) -> List[Tuple[int, float, str]]:
        """Extract frames from video and return frame info"""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        frames_info = []
        frame_count = 0
        frame_interval_frames = int(fps * self.frame_interval)
        
        logger.info(f"Processing video: {total_frames} frames at {fps} FPS, checking every {self.frame_interval}s")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Process frames at specified intervals (like reference code)
            if frame_count % frame_interval_frames == 0:
                timestamp = frame_count / fps
                frame_path = os.path.join(output_dir, f"frame_{frame_count:06d}.jpg")
                
                # Save frame
                cv2.imwrite(frame_path, frame)
                frames_info.append((frame_count, timestamp, frame_path))
                
            frame_count += 1
            
            # Progress logging
            if frame_count % 1000 == 0:
                progress = (frame_count / total_frames) * 100
                logger.info(f"Processed {frame_count}/{total_frames} frames ({progress:.1f}%)")
        
        cap.release()
        logger.info(f"Extracted {len(frames_info)} frames for analysis")
        return frames_info
    
    def calculate_frame_similarity(self, img1_path: str, img2_path: str) -> float:
        """Calculate structural similarity between two frames"""
        try:
            # Load images in grayscale
            img1 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE)
            img2 = cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)
            
            if img1 is None or img2 is None:
                return 0.0
            
            # Resize to standard size for comparison
            height, width = 480, 640
            img1 = cv2.resize(img1, (width, height))
            img2 = cv2.resize(img2, (width, height))
            
            # Calculate SSIM
            similarity = ssim(img1, img2)
            return similarity
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    def calculate_histogram_difference(self, img1_path: str, img2_path: str) -> float:
        """Calculate histogram difference between two frames for color change detection"""
        try:
            # Load images in color
            img1 = cv2.imread(img1_path)
            img2 = cv2.imread(img2_path)
            
            if img1 is None or img2 is None:
                return 0.0
            
            # Resize to standard size for comparison
            height, width = 480, 640
            img1 = cv2.resize(img1, (width, height))
            img2 = cv2.resize(img2, (width, height))
            
            # Calculate histograms for each color channel
            hist1_b = cv2.calcHist([img1], [0], None, [256], [0, 256])
            hist1_g = cv2.calcHist([img1], [1], None, [256], [0, 256])
            hist1_r = cv2.calcHist([img1], [2], None, [256], [0, 256])
            
            hist2_b = cv2.calcHist([img2], [0], None, [256], [0, 256])
            hist2_g = cv2.calcHist([img2], [1], None, [256], [0, 256])
            hist2_r = cv2.calcHist([img2], [2], None, [256], [0, 256])
            
            # Calculate correlation for each channel
            corr_b = cv2.compareHist(hist1_b, hist2_b, cv2.HISTCMP_CORREL)
            corr_g = cv2.compareHist(hist1_g, hist2_g, cv2.HISTCMP_CORREL)
            corr_r = cv2.compareHist(hist1_r, hist2_r, cv2.HISTCMP_CORREL)
            
            # Average correlation (higher = more similar)
            avg_correlation = (corr_b + corr_g + corr_r) / 3.0
            
            # Convert to difference (lower = more similar)
            difference = 1.0 - avg_correlation
            return difference
            
        except Exception as e:
            logger.error(f"Error calculating histogram difference: {e}")
            return 0.0
    
    def detect_screen_changes(self, frames_info: List[Tuple[int, float, str]]) -> List[ScreenSegment]:
        """Detect significant screen changes like reference code"""
        if len(frames_info) < 2:
            return []
        
        segments = []
        current_segment_start = 0
        segment_id = 1
        
        logger.info("🔍 Starting screen change detection...")
        
        for i in range(1, len(frames_info)):
            frame_num, timestamp, frame_path = frames_info[i]
            prev_frame_path = frames_info[i-1][2]
            
            # Calculate similarity with previous frame
            similarity = self.calculate_frame_similarity(prev_frame_path, frame_path)
            
            # If similarity is below threshold, we have a screen change
            if similarity < self.similarity_threshold:
                # Create segment for previous screen
                prev_timestamp = frames_info[current_segment_start][1]
                duration = timestamp - prev_timestamp
                
                # Only create segment if it meets minimum duration
                if duration >= self.min_duration:
                    segment = ScreenSegment(
                        id=segment_id,
                        start_time=prev_timestamp,
                        end_time=timestamp,
                        screenshot_path=frames_info[current_segment_start][2],
                        frame_number=frames_info[current_segment_start][0],
                        similarity_score=(1.0 - similarity) * 100,  # Convert to percentage
                        description=f"Screen {segment_id}"
                    )
                    segments.append(segment)
                    segment_id += 1
                    
                    logger.info(f"📸 Screen {segment_id-1}: Change detected at {timestamp:.1f}s (SSIM: {similarity:.3f})")
                
                current_segment_start = i
        
        # Add final segment
        if current_segment_start < len(frames_info) - 1:
            final_timestamp = frames_info[-1][1]
            duration = final_timestamp - frames_info[current_segment_start][1]
            
            if duration >= self.min_duration:
                segment = ScreenSegment(
                    id=segment_id,
                    start_time=frames_info[current_segment_start][1],
                    end_time=final_timestamp,
                    screenshot_path=frames_info[current_segment_start][2],
                    frame_number=frames_info[current_segment_start][0],
                    similarity_score=80.0,
                    description=f"Screen {segment_id}"
                )
                segments.append(segment)
        
        logger.info(f"✅ Detected {len(segments)} unique screen segments")
        return segments
    
    def analyze_video(self, video_path: str, output_dir: str) -> List[ScreenSegment]:
        """Main method to analyze video and detect screen changes"""
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Extract frames
        frames_info = self.extract_frames(video_path, output_dir)
        
        # Detect screen changes
        segments = self.detect_screen_changes(frames_info)
        
        return segments
    
    def get_high_quality_screenshot(self, video_path: str, timestamp: float, output_path: str) -> str:
        """Extract a high-quality screenshot at specific timestamp"""
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_number = int(timestamp * fps)
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()
        
        if ret:
            cv2.imwrite(output_path, frame)
            cap.release()
            return output_path
        else:
            cap.release()
            raise ValueError(f"Could not extract frame at timestamp {timestamp}")
