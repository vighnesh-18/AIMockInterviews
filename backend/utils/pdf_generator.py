"""
PDF Report Generator for Interview Sessions
Generates comprehensive interview feedback reports with scores and recommendations
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import os
from typing import Dict, List, Any
import json

class PDFReportGenerator:
    """Generates professional PDF reports for interview sessions"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#283593'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='BodyText',
            parent=self.styles['BodyText'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=10
        ))
        
        self.styles.add(ParagraphStyle(
            name='ScoreLabel',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#424242'),
            fontName='Helvetica-Bold'
        ))
    
    def generate_report(self, session_data: Dict[str, Any], output_path: str = None) -> str:
        """
        Generate a comprehensive PDF report
        
        Args:
            session_data: Dictionary containing interview session data
            output_path: Optional custom output path
        
        Returns:
            Path to generated PDF file
        """
        if output_path is None:
            output_dir = os.path.join(os.path.dirname(__file__), '..', 'reports')
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(output_dir, f"interview_report_{timestamp}.pdf")
        
        print(f"\n📝 Generating PDF Report...")
        print(f"   Output path: {output_path}")
        print(f"   Directory exists: {os.path.exists(os.path.dirname(output_path))}")
        
        # Create PDF document
        doc = SimpleDocTemplate(output_path, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        
        # Add title
        story.append(Paragraph("Interview Performance Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))
        
        # Add session info
        story.extend(self._create_session_info(session_data))
        story.append(Spacer(1, 0.2*inch))
        
        # Add overall score summary
        story.extend(self._create_score_summary(session_data))
        story.append(Spacer(1, 0.2*inch))
        
        # Add detailed feedback
        story.extend(self._create_detailed_feedback(session_data))
        story.append(Spacer(1, 0.2*inch))
        
        # Add analysis and recommendations
        story.extend(self._create_analysis_and_recommendations(session_data))
        
        # Build PDF
        try:
            doc.build(story)
            
            # Verify file was created
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"✅ PDF Report generated successfully!")
                print(f"   File: {output_path}")
                print(f"   Size: {file_size} bytes")
                return output_path
            else:
                print(f"❌ PDF file was not created at {output_path}")
                raise Exception(f"PDF file not created at {output_path}")
        
        except Exception as e:
            print(f"❌ Error building PDF: {e}")
            raise
    
    def _create_session_info(self, session_data: Dict) -> List:
        """Create session information section"""
        elements = []
        
        elements.append(Paragraph("Session Information", self.styles['SectionHeading']))
        
        info_data = [
            ["Role", session_data.get('role', 'N/A')],
            ["Experience Level", session_data.get('experience', 'N/A')],
            ["Difficulty", session_data.get('difficulty', 'N/A')],
            ["Date", datetime.now().strftime("%B %d, %Y at %I:%M %p")],
            ["Total Questions", str(session_data.get('total_questions', 0))],
            ["Total Interactions", str(session_data.get('total_interactions', 0))],
        ]
        
        table = Table(info_data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8eaf6')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        elements.append(table)
        return elements
    
    def _create_score_summary(self, session_data: Dict) -> List:
        """Create overall score summary section"""
        elements = []
        
        elements.append(Paragraph("Overall Performance", self.styles['SectionHeading']))
        
        average_score = session_data.get('average_score', 0)
        
        # Score interpretation
        if average_score >= 85:
            performance = "Excellent"
            color = colors.HexColor('#2e7d32')
        elif average_score >= 70:
            performance = "Good"
            color = colors.HexColor('#558b2f')
        elif average_score >= 55:
            performance = "Average"
            color = colors.HexColor('#f57f17')
        else:
            performance = "Needs Improvement"
            color = colors.HexColor('#c62828')
        
        # Score box
        score_data = [
            ["Final Score", f"{average_score:.1f}/100"],
            ["Performance Level", performance],
        ]
        
        table = Table(score_data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8eaf6')),
            ('BACKGROUND', (1, 0), (1, 0), color),
            ('TEXTCOLOR', (1, 0), (1, 0), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('FONTSIZE', (1, 0), (1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        elements.append(table)
        return elements
    
    def _create_detailed_feedback(self, session_data: Dict) -> List:
        """Create detailed feedback for each interaction"""
        elements = []
        
        elements.append(Paragraph("Detailed Feedback by Question", self.styles['SectionHeading']))
        
        interactions = session_data.get('interaction_blocks', [])
        
        for idx, interaction in enumerate(interactions, 1):
            # Question
            question = interaction.get('main_question', 'N/A')
            elements.append(Paragraph(f"<b>Question {idx}:</b> {question}", self.styles['BodyText']))
            
            # Answer
            answers = interaction.get('answers', [])
            if answers:
                answer_text = answers[0][:200] + "..." if len(answers[0]) > 200 else answers[0]
                elements.append(Paragraph(f"<b>Your Answer:</b> {answer_text}", self.styles['BodyText']))
            
            # Scores
            scores = interaction.get('scores', {})
            if scores:
                score_items = [
                    f"Domain Knowledge: {scores.get('domain_knowledge', 0)}/100",
                    f"Communication: {scores.get('communication', 0)}/100",
                    f"Confidence: {scores.get('confidence', 0)}/100",
                    f"Depth: {scores.get('depth', 0)}/100",
                ]
                elements.append(Paragraph(f"<b>Scores:</b> {' | '.join(score_items)}", self.styles['ScoreLabel']))
            
            # Feedback
            feedback = scores.get('feedback', 'No feedback available')
            elements.append(Paragraph(f"<b>Feedback:</b> {feedback}", self.styles['BodyText']))
            
            elements.append(Spacer(1, 0.15*inch))
        
        return elements
    
    def _create_analysis_and_recommendations(self, session_data: Dict) -> List:
        """Create analysis and recommendations section"""
        elements = []
        
        elements.append(PageBreak())
        elements.append(Paragraph("Analysis & Recommendations", self.styles['SectionHeading']))
        
        # Calculate strengths and weaknesses
        analysis = self._analyze_performance(session_data)
        
        # Strengths
        elements.append(Paragraph("✓ Strengths", self.styles['SectionHeading']))
        for strength in analysis['strengths']:
            elements.append(Paragraph(f"• {strength}", self.styles['BodyText']))
        elements.append(Spacer(1, 0.1*inch))
        
        # Areas for Improvement
        elements.append(Paragraph("⚠ Areas for Improvement", self.styles['SectionHeading']))
        for weakness in analysis['weaknesses']:
            elements.append(Paragraph(f"• {weakness}", self.styles['BodyText']))
        elements.append(Spacer(1, 0.1*inch))
        
        # Recommendations
        elements.append(Paragraph("💡 Recommendations", self.styles['SectionHeading']))
        for recommendation in analysis['recommendations']:
            elements.append(Paragraph(f"• {recommendation}", self.styles['BodyText']))
        elements.append(Spacer(1, 0.1*inch))
        
        # Topics covered
        topics = session_data.get('topics_covered', [])
        if topics:
            elements.append(Paragraph("Topics Covered", self.styles['SectionHeading']))
            topics_text = ", ".join(topics)
            elements.append(Paragraph(topics_text, self.styles['BodyText']))
        
        return elements
    
    def _analyze_performance(self, session_data: Dict) -> Dict[str, List[str]]:
        """Analyze performance and generate insights"""
        interactions = session_data.get('interaction_blocks', [])
        
        strengths = []
        weaknesses = []
        recommendations = []
        
        # Calculate average scores by category
        domain_scores = []
        communication_scores = []
        confidence_scores = []
        depth_scores = []
        
        for interaction in interactions:
            scores = interaction.get('scores', {})
            domain_scores.append(scores.get('domain_knowledge', 0))
            communication_scores.append(scores.get('communication', 0))
            confidence_scores.append(scores.get('confidence', 0))
            depth_scores.append(scores.get('depth', 0))
        
        # Calculate averages
        avg_domain = sum(domain_scores) / len(domain_scores) if domain_scores else 0
        avg_communication = sum(communication_scores) / len(communication_scores) if communication_scores else 0
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        avg_depth = sum(depth_scores) / len(depth_scores) if depth_scores else 0
        
        # Identify strengths (scores > 75)
        if avg_domain > 75:
            strengths.append("Strong domain knowledge and technical understanding")
        if avg_communication > 75:
            strengths.append("Clear and effective communication skills")
        if avg_confidence > 75:
            strengths.append("High confidence and conviction in answers")
        if avg_depth > 75:
            strengths.append("Ability to provide detailed and comprehensive answers")
        
        # Identify weaknesses (scores < 65)
        if avg_domain < 65:
            weaknesses.append(f"Domain knowledge needs improvement (Current: {avg_domain:.0f}/100)")
            recommendations.append("Study core concepts and practice technical problems")
        if avg_communication < 65:
            weaknesses.append(f"Communication clarity could be enhanced (Current: {avg_communication:.0f}/100)")
            recommendations.append("Practice explaining concepts clearly and concisely")
        if avg_confidence < 65:
            weaknesses.append(f"Confidence level is lower than ideal (Current: {avg_confidence:.0f}/100)")
            recommendations.append("Build confidence through more practice and preparation")
        if avg_depth < 65:
            weaknesses.append(f"Answers lack sufficient depth (Current: {avg_depth:.0f}/100)")
            recommendations.append("Provide more detailed examples and explanations in your answers")
        
        # Add general recommendations
        if not recommendations:
            recommendations.append("Continue practicing to maintain and improve your performance")
            recommendations.append("Focus on explaining your thought process during interviews")
        
        recommendations.append("Review the feedback for each question and practice similar topics")
        recommendations.append("Record yourself answering questions to improve delivery")
        
        return {
            "strengths": strengths if strengths else ["Good effort in attempting all questions"],
            "weaknesses": weaknesses if weaknesses else ["No major weaknesses identified"],
            "recommendations": recommendations
        }
