"""
Scoring Agent - CrewAI Agent for scoring interview interactions
"""
from crewai import Agent, Task
import os
import json

GROQ_API_KEY = os.getenv("GROQ_API_KEY_3")

# Set API key for litellm
os.environ['GROQ_API_KEY'] = GROQ_API_KEY

class ScoringAgent:
    """CrewAI Agent that scores candidate answers on multiple dimensions"""
    
    def __init__(self):
        self.agent = Agent(
            role="Interview Scorer",
            goal="Score candidate answers on domain knowledge, communication, confidence, and depth",
            backstory="""You are an expert at evaluating technical interviews. You score answers
            objectively on multiple dimensions and provide constructive feedback. You understand
            that good answers show both knowledge and clear communication.""",
            verbose=True,
            allow_delegation=False,
            llm="groq/llama-3.1-8b-instant"
        )
    
    def create_scoring_task(self, role: str, experience: str, 
                           main_question: str, answers: list) -> Task:
        """Create a task to score an interaction"""
        
        answers_str = "\n".join([f"A{i+1}: {a}" for i, a in enumerate(answers)])
        
        task = Task(
            description=f"""Score this interview interaction on multiple dimensions.

ROLE: {role}
EXPERIENCE LEVEL: {experience}

QUESTION ASKED: {main_question}

CANDIDATE'S ANSWER:
{answers_str}

SCORING CRITERIA (0-100 each):
1. Domain Knowledge: How accurately does the answer address the specific question? Does it show technical understanding?
2. Communication: Is the answer clear, well-structured, and easy to understand?
3. Confidence: Does the candidate speak with conviction? Are they uncertain or hesitant?
4. Depth: Does the answer go beyond surface level? Are there examples or explanations?

IMPORTANT INSTRUCTIONS:
- Feedback MUST be specific to the question asked and answer given
- Do NOT give generic feedback
- Address what was good and what could be improved about THIS specific answer
- Be constructive and actionable
- Return ONLY the JSON object, nothing else

Calculate final score as weighted average:
(domain_knowledge * 0.3) + (communication * 0.25) + (confidence * 0.2) + (depth * 0.25)

RETURN ONLY THIS JSON (no other text):
{{
    "domain_knowledge": <number 0-100>,
    "communication": <number 0-100>,
    "confidence": <number 0-100>,
    "depth": <number 0-100>,
    "final_score": <number 0-100>,
    "feedback": "<specific feedback about THIS answer to THIS question>"
}}""",
            expected_output='{"domain_knowledge": 0-100, "communication": 0-100, "confidence": 0-100, "depth": 0-100, "final_score": 0-100, "feedback": "specific feedback"}',
            agent=self.agent
        )
        
        return task
