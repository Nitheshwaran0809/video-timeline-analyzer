import os
import logging
from typing import List, Dict, Any
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from PIL import Image as PILImage
from .content_correlator import TimelineSegment

logger = logging.getLogger(__name__)

class PDFExporter:
    """Export timeline analysis to professional PDF report"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2C3E50'),
            alignment=1  # Center alignment
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            textColor=colors.HexColor('#34495E'),
            borderWidth=1,
            borderColor=colors.HexColor('#BDC3C7'),
            borderPadding=10,
            backColor=colors.HexColor('#ECF0F1')
        ))
        
        # Segment header style
        self.styles.add(ParagraphStyle(
            name='SegmentHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=10,
            textColor=colors.HexColor('#2980B9'),
            borderWidth=1,
            borderColor=colors.HexColor('#3498DB'),
            borderPadding=5,
            backColor=colors.HexColor('#EBF5FB')
        ))
        
        # Summary style
        self.styles.add(ParagraphStyle(
            name='Summary',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=10,
            textColor=colors.HexColor('#2C3E50'),
            leftIndent=20,
            rightIndent=20,
            backColor=colors.HexColor('#F8F9FA'),
            borderWidth=1,
            borderColor=colors.HexColor('#DEE2E6'),
            borderPadding=10
        ))
        
        # Transcript style
        self.styles.add(ParagraphStyle(
            name='Transcript',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=10,
            textColor=colors.HexColor('#495057'),
            leftIndent=15,
            fontName='Helvetica'
        ))
        
        # Topics style
        self.styles.add(ParagraphStyle(
            name='Topics',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=5,
            textColor=colors.HexColor('#28A745'),
            leftIndent=20,
            bulletIndent=10
        ))
    
    def export_timeline_pdf(self, timeline_segments: List[TimelineSegment], 
                          output_path: str, video_filename: str = "Video") -> str:
        """Export timeline to PDF report"""
        try:
            logger.info(f"Exporting timeline to PDF: {output_path}")
            
            # Create PDF document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build story (content)
            story = []
            
            # Add title page
            story.extend(self._create_title_page(video_filename, timeline_segments))
            
            # Add summary page
            story.extend(self._create_summary_page(timeline_segments))
            
            # Add detailed timeline
            story.extend(self._create_detailed_timeline(timeline_segments))
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"PDF exported successfully to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error exporting PDF: {e}")
            raise
    
    def _create_title_page(self, video_filename: str, timeline_segments: List[TimelineSegment]) -> List:
        """Create title page content"""
        content = []
        
        # Main title
        title = Paragraph("Video Timeline Analysis Report", self.styles['CustomTitle'])
        content.append(title)
        content.append(Spacer(1, 20))
        
        # Video information
        video_info = f"<b>Video:</b> {video_filename}<br/>"
        video_info += f"<b>Analysis Date:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>"
        video_info += f"<b>Total Segments:</b> {len(timeline_segments)}<br/>"
        
        if timeline_segments:
            total_duration = max(seg.end_time for seg in timeline_segments)
            duration_min = int(total_duration // 60)
            duration_sec = int(total_duration % 60)
            video_info += f"<b>Total Duration:</b> {duration_min}:{duration_sec:02d}<br/>"
        
        info_para = Paragraph(video_info, self.styles['Normal'])
        content.append(info_para)
        content.append(Spacer(1, 30))
        
        # Executive summary
        exec_summary = self._generate_executive_summary(timeline_segments)
        content.append(Paragraph("<b>Executive Summary</b>", self.styles['CustomSubtitle']))
        content.append(Paragraph(exec_summary, self.styles['Summary']))
        
        content.append(PageBreak())
        return content
    
    def _create_summary_page(self, timeline_segments: List[TimelineSegment]) -> List:
        """Create summary statistics page"""
        content = []
        
        content.append(Paragraph("Analysis Summary", self.styles['CustomTitle']))
        content.append(Spacer(1, 20))
        
        # Statistics table
        stats_data = self._calculate_statistics(timeline_segments)
        
        table_data = [
            ['Metric', 'Value'],
            ['Total Segments', str(stats_data['total_segments'])],
            ['Average Segment Duration', f"{stats_data['avg_duration']:.1f} seconds"],
            ['Longest Segment', f"{stats_data['max_duration']:.1f} seconds"],
            ['Shortest Segment', f"{stats_data['min_duration']:.1f} seconds"],
            ['High Confidence Segments', str(stats_data['high_confidence_count'])],
            ['Most Common Content Type', stats_data['common_content_type']],
            ['Total Unique Topics', str(stats_data['unique_topics_count'])]
        ]
        
        table = Table(table_data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7'))
        ]))
        
        content.append(table)
        content.append(Spacer(1, 30))
        
        # Top topics
        if stats_data['top_topics']:
            content.append(Paragraph("Most Discussed Topics", self.styles['CustomSubtitle']))
            for i, topic in enumerate(stats_data['top_topics'][:10], 1):
                topic_text = f"{i}. {topic}"
                content.append(Paragraph(topic_text, self.styles['Topics']))
        
        content.append(PageBreak())
        return content
    
    def _create_detailed_timeline(self, timeline_segments: List[TimelineSegment]) -> List:
        """Create detailed timeline content"""
        content = []
        
        content.append(Paragraph("Detailed Timeline", self.styles['CustomTitle']))
        content.append(Spacer(1, 20))
        
        for i, segment in enumerate(timeline_segments):
            # Segment header
            header_text = f"Screen {segment.id} - {segment.formatted_time_range} ({segment.duration:.1f}s)"
            content.append(Paragraph(header_text, self.styles['SegmentHeader']))
            
            # Screen type
            type_text = f"<b>Type:</b> {segment.screen_description}"
            content.append(Paragraph(type_text, self.styles['Normal']))
            content.append(Spacer(1, 5))
            
            # Screenshot (if exists and accessible)
            if segment.screenshot_path and os.path.exists(segment.screenshot_path):
                try:
                    # Resize image to fit page
                    img = self._resize_image_for_pdf(segment.screenshot_path)
                    content.append(img)
                    content.append(Spacer(1, 10))
                except Exception as e:
                    logger.warning(f"Could not add screenshot for segment {segment.id}: {e}")
            
            # Discussion summary
            if segment.summary:
                content.append(Paragraph("<b>Discussion Summary:</b>", self.styles['Normal']))
                content.append(Paragraph(segment.summary, self.styles['Summary']))
            
            # Key topics
            if segment.key_topics:
                topics_text = "<b>Key Topics:</b><br/>"
                for topic in segment.key_topics:
                    topics_text += f"• {topic}<br/>"
                content.append(Paragraph(topics_text, self.styles['Topics']))
            
            # Full transcript
            if segment.transcript:
                content.append(Paragraph("<b>Full Transcript:</b>", self.styles['Normal']))
                # Truncate very long transcripts
                transcript_text = segment.transcript
                if len(transcript_text) > 1000:
                    transcript_text = transcript_text[:1000] + "... [truncated]"
                content.append(Paragraph(transcript_text, self.styles['Transcript']))
            
            # Add spacing between segments
            content.append(Spacer(1, 20))
            
            # Page break every 3 segments to avoid overcrowding
            if (i + 1) % 3 == 0 and i < len(timeline_segments) - 1:
                content.append(PageBreak())
        
        return content
    
    def _resize_image_for_pdf(self, image_path: str, max_width: int = 400, max_height: int = 300):
        """Resize image to fit in PDF"""
        try:
            # Open and resize image
            with PILImage.open(image_path) as pil_img:
                # Calculate new size maintaining aspect ratio
                width, height = pil_img.size
                aspect_ratio = width / height
                
                if width > max_width:
                    width = max_width
                    height = int(width / aspect_ratio)
                
                if height > max_height:
                    height = max_height
                    width = int(height * aspect_ratio)
                
                # Create ReportLab Image
                img = Image(image_path, width=width, height=height)
                return img
                
        except Exception as e:
            logger.error(f"Error resizing image {image_path}: {e}")
            return Paragraph(f"[Screenshot not available: {os.path.basename(image_path)}]", self.styles['Normal'])
    
    def _generate_executive_summary(self, timeline_segments: List[TimelineSegment]) -> str:
        """Generate executive summary"""
        if not timeline_segments:
            return "No timeline segments were detected in this video."
        
        total_duration = max(seg.end_time for seg in timeline_segments)
        avg_duration = sum(seg.duration for seg in timeline_segments) / len(timeline_segments)
        
        # Count content types
        content_types = {}
        all_topics = []
        
        for segment in timeline_segments:
            content_type = segment.screen_description
            content_types[content_type] = content_types.get(content_type, 0) + 1
            all_topics.extend(segment.key_topics)
        
        most_common_type = max(content_types.items(), key=lambda x: x[1])[0] if content_types else "Unknown"
        
        summary = f"This video analysis identified {len(timeline_segments)} distinct screen segments over "
        summary += f"{int(total_duration//60)}:{int(total_duration%60):02d} minutes. "
        summary += f"The average segment duration was {avg_duration:.1f} seconds. "
        summary += f"The most common screen type was '{most_common_type}'. "
        
        if all_topics:
            unique_topics = list(set(all_topics))
            summary += f"A total of {len(unique_topics)} unique topics were discussed throughout the video."
        
        return summary
    
    def _calculate_statistics(self, timeline_segments: List[TimelineSegment]) -> Dict[str, Any]:
        """Calculate statistics for summary page"""
        if not timeline_segments:
            return {}
        
        durations = [seg.duration for seg in timeline_segments]
        content_types = {}
        all_topics = []
        high_confidence_count = 0
        
        for segment in timeline_segments:
            # Content types
            content_type = segment.screen_description
            content_types[content_type] = content_types.get(content_type, 0) + 1
            
            # Topics
            all_topics.extend(segment.key_topics)
            
            # High confidence segments
            if segment.confidence_score > 0.7:
                high_confidence_count += 1
        
        # Most common content type
        most_common_type = max(content_types.items(), key=lambda x: x[1])[0] if content_types else "Unknown"
        
        # Top topics by frequency
        topic_freq = {}
        for topic in all_topics:
            topic_freq[topic] = topic_freq.get(topic, 0) + 1
        
        top_topics = sorted(topic_freq.items(), key=lambda x: x[1], reverse=True)
        top_topics = [topic for topic, freq in top_topics]
        
        return {
            'total_segments': len(timeline_segments),
            'avg_duration': sum(durations) / len(durations),
            'max_duration': max(durations),
            'min_duration': min(durations),
            'high_confidence_count': high_confidence_count,
            'common_content_type': most_common_type,
            'unique_topics_count': len(set(all_topics)),
            'top_topics': top_topics
        }
