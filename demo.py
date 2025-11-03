#!/usr/bin/env python3
"""
Video Timeline Analyzer - Demo Script

This script demonstrates the core functionality of the video analysis system
without the web interface.
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from core import VideoAnalyzer, SpeechProcessor, ContentCorrelator, PDFExporter
from utils import FileManager, TimeUtils

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def demo_analysis(video_path: str):
    """Run a complete analysis demo"""
    
    # Validate input file
    if not os.path.exists(video_path):
        logger.error(f"Video file not found: {video_path}")
        return
    
    validation = FileManager.validate_video_file(video_path)
    if not validation['valid']:
        logger.error(f"Invalid video file: {validation['error']}")
        return
    
    logger.info(f"Processing video: {video_path}")
    logger.info(f"File size: {validation['formatted_size']}")
    
    # Create output directory
    output_dir = Path("demo_output")
    FileManager.ensure_directory(str(output_dir))
    
    try:
        # Step 1: Analyze video for screen changes
        logger.info("🎬 Step 1: Analyzing screen changes...")
        video_analyzer = VideoAnalyzer(similarity_threshold=0.85, min_duration=2.0)
        
        frames_dir = output_dir / "frames"
        screen_segments = video_analyzer.analyze_video(video_path, str(frames_dir))
        
        logger.info(f"✅ Found {len(screen_segments)} screen segments")
        for i, segment in enumerate(screen_segments[:3]):  # Show first 3
            logger.info(f"   Segment {segment.id}: {TimeUtils.format_duration(segment.start_time)} - {TimeUtils.format_duration(segment.end_time)}")
        
        # Step 2: Process speech
        logger.info("🎤 Step 2: Processing speech...")
        speech_processor = SpeechProcessor()
        transcript_segments = speech_processor.process_video_audio(video_path)
        
        logger.info(f"✅ Generated {len(transcript_segments)} transcript segments")
        
        # Show some transcript samples
        for i, segment in enumerate(transcript_segments[:3]):
            logger.info(f"   Transcript {i+1}: '{segment.text[:50]}...'")
        
        # Step 3: Correlate content
        logger.info("🔗 Step 3: Correlating content...")
        content_correlator = ContentCorrelator()
        timeline_segments = content_correlator.correlate_content(screen_segments, transcript_segments)
        
        logger.info(f"✅ Created {len(timeline_segments)} timeline segments")
        
        # Step 4: Generate reports
        logger.info("📄 Step 4: Generating reports...")
        
        # Export JSON
        json_path = output_dir / "timeline_analysis.json"
        timeline_data = content_correlator.export_timeline_data(timeline_segments)
        
        import json
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(timeline_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ JSON report saved: {json_path}")
        
        # Export PDF
        pdf_path = output_dir / "timeline_analysis.pdf"
        pdf_exporter = PDFExporter()
        video_filename = Path(video_path).name
        pdf_exporter.export_timeline_pdf(timeline_segments, str(pdf_path), video_filename)
        
        logger.info(f"✅ PDF report saved: {pdf_path}")
        
        # Summary
        logger.info("\n" + "="*50)
        logger.info("📊 ANALYSIS SUMMARY")
        logger.info("="*50)
        logger.info(f"Video: {video_filename}")
        logger.info(f"Duration: {TimeUtils.format_duration(max(seg.end_time for seg in timeline_segments))}")
        logger.info(f"Screen segments: {len(screen_segments)}")
        logger.info(f"Transcript segments: {len(transcript_segments)}")
        logger.info(f"Timeline segments: {len(timeline_segments)}")
        
        # Show timeline overview
        logger.info("\n📋 TIMELINE OVERVIEW:")
        for segment in timeline_segments:
            confidence_bar = "█" * int(segment.confidence_score * 10) + "░" * (10 - int(segment.confidence_score * 10))
            logger.info(f"   {segment.formatted_time_range} | {confidence_bar} | {segment.screen_description}")
            if segment.key_topics:
                logger.info(f"      Topics: {', '.join(segment.key_topics)}")
        
        logger.info(f"\n✅ Demo completed! Check output in: {output_dir}")
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        raise

def main():
    """Main demo function"""
    print("🎥 Video Timeline Analyzer - Demo")
    print("="*40)
    
    # Load environment
    load_dotenv()
    
    # Check API key
    if not os.getenv('GROQ_API_KEY'):
        logger.error("GROQ_API_KEY not found in environment")
        logger.info("Please set your Groq API key in .env file")
        return
    
    # Get video file path
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
    else:
        video_path = input("Enter path to video file: ").strip()
    
    if not video_path:
        logger.error("No video file specified")
        return
    
    # Run demo
    try:
        demo_analysis(video_path)
    except KeyboardInterrupt:
        logger.info("Demo interrupted by user")
    except Exception as e:
        logger.error(f"Demo error: {e}")

if __name__ == "__main__":
    main()
