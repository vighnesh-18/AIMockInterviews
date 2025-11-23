"""
Data models for the interview crew system
"""
from typing import List, Dict, Optional
from pydantic import BaseModel

class FollowUpDecision(BaseModel):
    """Follow-Up Agent's decision output"""
    confidence: int  # 0-100
    decision: str  # "followup", "hard_followup", or "different_question"
    reasoning: str
    memory: Dict
    suggested_question: Optional[str] = None

class ScoreBlock(BaseModel):
    """Score for a single question block"""
    domain_knowledge: int  # 0-100
    communication: int  # 0-100
    confidence: int  # 0-100
    depth: int  # 0-100
    final_score: int  # 0-100
    feedback: str

class InteractionBlock(BaseModel):
    """A complete interaction: main question + follow-ups + answers"""
    main_question: str
    answers: List[str]
    follow_ups: int
    confidence: int
    scores: ScoreBlock

class SessionMemory(BaseModel):
    """Session memory tracking"""
    session_id: str
    asked_questions: List[Dict]  # {question, topic, round}
    topics_covered: List[str]
    current_topic: Optional[str] = None
    interaction_blocks: List[InteractionBlock] = []
    total_interactions: int = 0
    total_score: float = 0.0

class CrewInterviewRequest(BaseModel):
    """Request for crew-based interview"""
    role: str
    experience: str
    difficulty: str
    resume_text: Optional[str] = None
    user_message: Optional[str] = None
    session_id: str
    conversation_history: Optional[List[Dict]] = None

class CrewInterviewResponse(BaseModel):
    """Response from crew-based interview"""
    success: bool
    question: Optional[str] = None
    feedback: Optional[str] = None
    score: Optional[int] = None
    is_followup: bool = False
    session_id: str
    error: Optional[str] = None
