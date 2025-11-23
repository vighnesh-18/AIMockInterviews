"""
Interview Crew - Orchestrates the CrewAI agents for interview flow
"""
from crewai import Crew
from .interviewer_agent import InterviewerAgent
from .followup_agent import FollowUpAgent
from .scoring_agent import ScoringAgent
from .feedback_agent import FeedbackAgent
from memory.session_memory import session_manager
from utils.pdf_generator import PDFReportGenerator
import json
import os

class InterviewCrew:
    """Orchestrates the interview crew of agents"""
    
    def __init__(self):
        self.interviewer = InterviewerAgent()
        self.followup = FollowUpAgent()
        self.scoring = ScoringAgent()
        self.feedback = FeedbackAgent()
    
    def start_interview(self, session_id: str, role: str, experience: str, 
                       difficulty: str, resume_text: str) -> str:
        """Start a new interview session"""
        
        # Debug: Print resume text
        print("\n" + "="*80)
        print("📄 INTERVIEW START - RESUME DEBUG")
        print("="*80)
        print(f"✅ Resume text length: {len(resume_text) if resume_text else 0} characters")
        print(f"✅ Resume is 'No resume': {resume_text == 'No resume'}")
        print(f"✅ Resume is valid: {resume_text and resume_text.strip() and resume_text.strip() != 'No resume' and len(resume_text.strip()) > 50}")
        print(f"\n📝 Resume content (first 1000 chars):\n{resume_text[:1000] if resume_text else 'EMPTY'}")
        print("="*80 + "\n")
        
        # Create session
        session_manager.create_session(session_id, role, experience, difficulty, resume_text)
        
        # Create crew for initial question
        crew = Crew(
            agents=[self.interviewer.agent],
            tasks=[
                self.interviewer.create_question_task(
                    role=role,
                    experience=experience,
                    difficulty=difficulty,
                    resume_text=resume_text,
                    asked_questions=[],
                    topics_covered=[]
                )
            ],
            verbose=True
        )
        
        # Get first question
        result = crew.kickoff()
        question = str(result).strip()
        
        # Track the question and topic
        session_manager.add_asked_question(session_id, question, "introduction", 1)
        session_manager.add_topic_covered(session_id, "introduction")
        
        print(f"\n❓ FIRST QUESTION:\n{question}\n")
        return question
    
    def process_answer(self, session_id: str, user_answer: str, role: str, 
                      experience: str, difficulty: str, resume_text: str,
                      conversation_history: list) -> dict:
        
        print(f"\n📝 PROCESS_ANSWER called with session_id: {session_id}")
        session = session_manager.get_session(session_id)
        if not session:
            print(f"❌ Session not found!")
            return {"success": False, "error": "Session not found"}
        
        print(f"✅ Session found, current interactions: {session.get('total_interactions', 0)}")
        
        # Get current question
        current_question = ""
        if conversation_history:
            for msg in reversed(conversation_history):
                if msg.get("role") == "interviewer":
                    current_question = msg.get("content", "")
                    break
        
        asked_questions = session_manager.get_asked_questions_list(session_id)
        topics_covered = session_manager.get_topics_covered(session_id)
        
        # Step 1: Follow-Up Agent evaluates
        print("\n🔍 EVALUATING ANSWER...")
        followup_crew = Crew(
            agents=[self.followup.agent],
            tasks=[
                self.followup.create_evaluation_task(
                    current_question=current_question,
                    user_answer=user_answer,
                    role=role,
                    experience=experience,
                    asked_questions=asked_questions,
                    resume_text=resume_text
                )
            ],
            verbose=True
        )
        
        followup_result = followup_crew.kickoff()
        followup_text = str(followup_result).strip()
        
        # Parse followup decision
        try:
            # Extract JSON from response
            if "{" in followup_text and "}" in followup_text:
                start = followup_text.index("{")
                end = followup_text.rindex("}") + 1
                followup_decision = json.loads(followup_text[start:end])
            else:
                followup_decision = {
                    "confidence": 50,
                    "decision": "followup",
                    "reasoning": "Could not parse response"
                }
        except:
            followup_decision = {
                "confidence": 50,
                "decision": "followup",
                "reasoning": "Error parsing response"
            }
                
        next_question_crew = Crew(
            agents=[self.interviewer.agent],
            tasks=[
                self.interviewer.create_question_task(
                    role=role,
                    experience=experience,
                    difficulty=difficulty,
                    resume_text=resume_text,
                    asked_questions=asked_questions,
                    topics_covered=topics_covered
                )
            ],
            verbose=True
        )
        
        next_question_result = next_question_crew.kickoff()
        next_question = str(next_question_result).strip()
        
        # Track the question and topic
        topic = followup_decision.get("decision", "followup")
        session_manager.add_asked_question(session_id, next_question, topic, session["question_count"] + 1)
        session_manager.add_topic_covered(session_id, topic)
        
        # Step 3: Scoring Agent scores the interaction
        scoring_crew = Crew(
            agents=[self.scoring.agent],
            tasks=[
                self.scoring.create_scoring_task(
                    role=role,
                    experience=experience,
                    main_question=current_question,
                    answers=[user_answer]
                )
            ],
            verbose=True
        )
        
        scoring_result = scoring_crew.kickoff()
        scoring_text = str(scoring_result).strip()
        
        # Parse scores
        scores = None
        try:
            if "{" in scoring_text and "}" in scoring_text:
                start = scoring_text.index("{")
                end = scoring_text.rindex("}") + 1
                json_str = scoring_text[start:end]
                scores = json.loads(json_str)
        except Exception as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"Raw scoring text: {scoring_text[:200]}")
        
        # Fallback if parsing failed
        if not scores or not isinstance(scores, dict):
            # Extract feedback from raw text if JSON parsing failed
            feedback_text = scoring_text[:300] if scoring_text else "Unable to generate feedback"
            scores = {
                "domain_knowledge": 75,
                "communication": 75,
                "confidence": 75,
                "depth": 75,
                "final_score": 75,
                "feedback": feedback_text
            }
        
        # Ensure all required fields exist
        scores.setdefault("domain_knowledge", 70)
        scores.setdefault("communication", 70)
        scores.setdefault("confidence", 70)
        scores.setdefault("depth", 70)
        scores.setdefault("final_score", 70)
        scores.setdefault("feedback", "Feedback generated")
        
        
        # Store interaction block
        interaction_block = {
            "question": current_question,
            "answer": user_answer,
            "feedback": scores.get("feedback", ""),
            "score": scores.get("final_score", 0),
            "scores": scores
        }
        session_manager.add_interaction_block(session_id, interaction_block)
        print(f"✅ Interaction stored. Total interactions now: {session.get('total_interactions', 0) + 1}")
        
        return {
            "success": True,
            "question": next_question,
            "feedback": scores.get("feedback", ""),
            "score": scores.get("final_score", 0),
            "is_followup": followup_decision.get("decision") == "followup",
            "confidence": followup_decision.get("confidence", 0),
            "session_id": session_id
        }
    
    def end_interview(self, session_id: str) -> dict:
        """End interview and generate final report + PDF"""
        
        print(f"\n🛑 END_INTERVIEW called with session_id: {session_id}")
        session_summary = session_manager.get_session_summary(session_id)
        
        if not session_summary:
            print(f"❌ Session not found in memory!")
            return {"success": False, "error": "Session not found"}
        
        print(f"✅ Session summary retrieved:")
        print(f"   Total questions: {session_summary.get('total_questions', 0)}")
        print(f"   Total interactions: {session_summary.get('total_interactions', 0)}")
        print(f"   Average score: {session_summary.get('average_score', 0)}")
        print(f"   Topics covered: {session_summary.get('topics_covered', [])}")
        print(f"   Interaction blocks count: {len(session_summary.get('interaction_blocks', []))}")
        
        # Generate final report
        print("\n📊 GENERATING FINAL REPORT...")
        report_crew = Crew(
            agents=[self.feedback.agent],
            tasks=[
                self.feedback.create_report_task(
                    role=session_summary["role"],
                    experience=session_summary["experience"],
                    difficulty=session_summary["difficulty"],
                    interaction_blocks=session_summary["interaction_blocks"],
                    topics_covered=session_summary["topics_covered"],
                    average_score=session_summary["average_score"]
                )
            ],
            verbose=True
        )
        
        report_result = report_crew.kickoff()
        report_text = str(report_result).strip()
        
        # Parse report
        try:
            if "{" in report_text and "}" in report_text:
                start = report_text.index("{")
                end = report_text.rindex("}") + 1
                report = json.loads(report_text[start:end])
            else:
                report = {
                    "overall_assessment": report_text[:500],
                    "strengths": [],
                    "weak_areas": [],
                    "communication_analysis": "N/A",
                    "technical_depth": "N/A",
                    "recommendations": [],
                    "hire_verdict": "N/A",
                    "confidence_level": "N/A",
                    "final_score": session_summary["average_score"]
                }
        except:
            report = {
                "overall_assessment": "Error generating report",
                "strengths": [],
                "weak_areas": [],
                "communication_analysis": "N/A",
                "technical_depth": "N/A",
                "recommendations": [],
                "hire_verdict": "N/A",
                "confidence_level": "N/A",
                "final_score": session_summary["average_score"]
            }
        
        # Generate PDF Report
        print("\n📄 GENERATING PDF REPORT...")
        pdf_filename = None
        try:
            pdf_generator = PDFReportGenerator()
            pdf_path = pdf_generator.generate_report(session_summary)
            # Extract just the filename for the response
            pdf_filename = os.path.basename(pdf_path)
            print(f"✅ PDF Report saved: {pdf_path}")
            print(f"✅ PDF filename: {pdf_filename}")
        except Exception as e:
            print(f"❌ Error generating PDF: {e}")
            import traceback
            traceback.print_exc()
            pdf_filename = None
        
        # Clean up session
        session_manager.delete_session(session_id)
        
        
        return {
            "success": True,
            "report": report,
            "pdf_filename": pdf_filename,
            "summary": {
                "total_questions": session_summary["total_questions"],
                "total_interactions": session_summary["total_interactions"],
                "average_score": session_summary["average_score"],
                "topics_covered": session_summary["topics_covered"]
            }
        }
