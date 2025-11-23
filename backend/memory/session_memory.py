from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

class SessionMemoryManager:
    
    def __init__(self):
        self.sessions: Dict = {}
        self.session_timeout = 3600  # 1 hour
    
    def create_session(self, session_id: str, role: str, experience: str, difficulty: str, resume_text: str) -> Dict:
        """Create a new session"""
        self.sessions[session_id] = {
            "session_id": session_id,
            "role": role,
            "experience": experience,
            "difficulty": difficulty,
            "resume_text": resume_text,
            "created_at": datetime.now().isoformat(),
            "asked_questions": [],
            "topics_covered": [],
            "current_topic": None,
            "interaction_blocks": [],
            "total_interactions": 0,
            "total_score": 0.0,
            "question_count": 0
        }
        return self.sessions[session_id]
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by ID"""
        return self.sessions.get(session_id)
    
    def add_asked_question(self, session_id: str, question: str, topic: str, round_num: int):
        """Add a question to the asked questions list"""
        if session_id in self.sessions:
            self.sessions[session_id]["asked_questions"].append({
                "question": question,
                "topic": topic,
                "round": round_num,
                "timestamp": datetime.now().isoformat()
            })
            self.sessions[session_id]["question_count"] += 1
    
    def add_topic_covered(self, session_id: str, topic: str):
        """Add a topic to covered topics"""
        if session_id in self.sessions:
            if topic not in self.sessions[session_id]["topics_covered"]:
                self.sessions[session_id]["topics_covered"].append(topic)
    
    def set_current_topic(self, session_id: str, topic: str):
        """Set the current topic being discussed"""
        if session_id in self.sessions:
            self.sessions[session_id]["current_topic"] = topic
    
    def add_interaction_block(self, session_id: str, block: Dict):
        """Add a completed interaction block"""
        if session_id in self.sessions:
            self.sessions[session_id]["interaction_blocks"].append(block)
            self.sessions[session_id]["total_interactions"] += 1
            
            # Update total score
            if "scores" in block and "final_score" in block["scores"]:
                current_total = self.sessions[session_id]["total_score"]
                new_score = block["scores"]["final_score"]
                total_interactions = self.sessions[session_id]["total_interactions"]
                
                # Calculate running average
                self.sessions[session_id]["total_score"] = (
                    (current_total * (total_interactions - 1) + new_score) / total_interactions
                )
    
    def get_asked_questions_list(self, session_id: str) -> List[str]:
        """Get list of all asked questions"""
        if session_id in self.sessions:
            return [q["question"] for q in self.sessions[session_id]["asked_questions"]]
        return []
    
    def get_topics_covered(self, session_id: str) -> List[str]:
        """Get list of topics covered"""
        if session_id in self.sessions:
            return self.sessions[session_id]["topics_covered"]
        return []
    
    def get_current_topic(self, session_id: str) -> Optional[str]:
        """Get current topic"""
        if session_id in self.sessions:
            return self.sessions[session_id]["current_topic"]
        return None
    
    def get_interaction_blocks(self, session_id: str) -> List[Dict]:
        """Get all interaction blocks"""
        if session_id in self.sessions:
            return self.sessions[session_id]["interaction_blocks"]
        return []
    
    def get_total_score(self, session_id: str) -> float:
        """Get running total score"""
        if session_id in self.sessions:
            return self.sessions[session_id]["total_score"]
        return 0.0
    
    def get_session_summary(self, session_id: str) -> Dict:
        """Get session summary for final report"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            return {
                "session_id": session_id,
                "role": session["role"],
                "experience": session["experience"],
                "difficulty": session["difficulty"],
                "total_questions": session["question_count"],
                "total_interactions": session["total_interactions"],
                "topics_covered": session["topics_covered"],
                "average_score": session["total_score"],
                "interaction_blocks": session["interaction_blocks"]
            }
        return {}
    
    def delete_session(self, session_id: str):
        """Delete a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def cleanup_old_sessions(self):
        """Remove sessions older than timeout"""
        now = datetime.now()
        sessions_to_delete = []
        
        for session_id, session in self.sessions.items():
            created_at = datetime.fromisoformat(session["created_at"])
            if (now - created_at).seconds > self.session_timeout:
                sessions_to_delete.append(session_id)
        
        for session_id in sessions_to_delete:
            self.delete_session(session_id)

# Global session manager
session_manager = SessionMemoryManager()
