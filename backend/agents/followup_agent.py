"""
Follow-Up Agent - CrewAI Agent for evaluating answers and deciding follow-ups
"""
from crewai import Agent, Task
import os
import json

GROQ_API_KEY = os.getenv("GROQ_API_KEY_2")

# Set API key for litellm
os.environ['GROQ_API_KEY'] = GROQ_API_KEY

class FollowUpAgent:
    """CrewAI Agent that evaluates answers and decides on follow-up strategy"""
    
    def __init__(self):
        self.agent = Agent(
            role="Answer Evaluator",
            goal="Evaluate candidate answers and decide whether to ask follow-ups, harder questions, or move to new topics",
            backstory="""You are an expert at evaluating interview answers. You assess answer quality,
            identify gaps, and make smart decisions about follow-up strategy. You understand that:
            - Vague answers need clarification (ask follow-up)
            - Good answers can be challenged (ask harder follow-up)
            - Poor answers should move to new topics (different question)""",
            verbose=True,
            allow_delegation=False,
            llm="groq/llama-3.1-8b-instant"
        )
    
    def create_evaluation_task(self, current_question: str, user_answer: str, 
                              role: str, experience: str, asked_questions: list, resume_text: str = "") -> Task:
        """Create a task to evaluate the answer"""
        
        asked_questions_str = "\n".join([f"- {q}" for q in asked_questions[-5:]]) if asked_questions else "None yet"
        
        # Check if resume is valid
        is_valid_resume = (
            resume_text 
            and resume_text.strip() 
            and resume_text.strip() != "No resume"
            and len(resume_text.strip()) > 50
        )
        
        resume_context = ""
        if is_valid_resume:
            resume_context = f"""
CANDIDATE'S RESUME:
{resume_text}

IMPORTANT: If the answer relates to items in their resume, ask follow-up questions about those specific experiences."""
        
        task = Task(
            description=f"""Evaluate this interview answer and decide on follow-up strategy.

QUESTION ASKED: {current_question}

CANDIDATE ANSWER: {user_answer}

CONTEXT:
- Role: {role}
- Experience: {experience}
- Previously Asked Questions: {asked_questions_str}{resume_context}

EVALUATE:
1. Answer Quality (0-100 confidence score)
2. Completeness (is it thorough or vague?)
3. Technical Accuracy (is it correct?)
4. Relevance to resume (if resume provided, does answer relate to their background?)

DECIDE:
- If confidence < 30%: Answer is vague/wrong → "different_question"
- If confidence 30-70%: Answer is partial or needs clarification → "followup"
- If confidence > 70%: Answer is good → "hard_followup"

FOLLOW-UP STRATEGY:
- For "followup": Ask clarifying questions about the same topic
- For "hard_followup": Ask deeper/more challenging questions about the same topic
- For "different_question": Move to a completely different topic

Return JSON format:
{{
    "confidence": 0-100,
    "decision": "followup" or "hard_followup" or "different_question",
    "reasoning": "Why you made this decision"
}}""",
            expected_output="JSON with confidence, decision, and reasoning",
            agent=self.agent
        )
        
        return task
