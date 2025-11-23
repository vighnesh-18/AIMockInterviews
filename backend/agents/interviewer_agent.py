from crewai import Agent, Task
import os

GROQ_API_KEY = os.getenv('GROQ_API_KEY_1')

class InterviewerAgent:
    def __init__(self):
        self.agent = Agent(
            role='Expert Technical Interviewer',
            goal='Ask insightful, role-specific interview questions that deeply explore the candidate\'s resume, skills, and experience',
            backstory='You are an expert technical interviewer with 15+ years of experience. You specialize in asking targeted questions about a candidate\'s resume, skills, and past projects. You dig deep into their experience and ask follow-up questions to understand their technical depth.',
            verbose=True,
            allow_delegation=False,
            llm='groq/llama-3.1-8b-instant'
        )
    
    def create_question_task(self, role, experience, difficulty, resume_text, asked_questions, topics_covered):
        asked_questions_str = '\n'.join([f'- {q}' for q in asked_questions[-5:]]) if asked_questions else 'None yet'
        topics_str = ', '.join(topics_covered) if topics_covered else 'None yet'
        
        is_valid_resume = (
            resume_text 
            and resume_text.strip() 
            and resume_text.strip() != "No resume"
            and len(resume_text.strip()) > 50
        )
        
        resume_section = ""
        if is_valid_resume:
            resume_section = f"""
CANDIDATE'S RESUME AND BACKGROUND:
{resume_text}

IMPORTANT INSTRUCTIONS FOR RESUME-BASED QUESTIONS:
1. PRIORITIZE asking about specific skills, technologies, and projects mentioned in the resume
2. Ask about their experience with specific tools/frameworks listed
3. Ask about their past projects - what they built, challenges they faced, technologies used
4. Ask about their work experience - responsibilities, achievements, technical contributions
5. Ask follow-up questions about their resume items to understand depth and expertise
6. Reference specific items from their resume to make questions personal and relevant
7. If they mention a project or skill, dig deeper into it in follow-up questions
8. Ask about how their resume experience relates to the {role} position"""
        else:
            resume_section = f"""
NO RESUME PROVIDED - Ask generic role-based questions about {role} position."""
        
        task = Task(
            description=f"""You are interviewing a candidate for a {role} position.

CANDIDATE DETAILS:
- Role: {role}
- Experience Level: {experience}
- Difficulty Level: {difficulty}

TOPICS ALREADY COVERED:
{topics_str}

PREVIOUSLY ASKED QUESTIONS (DO NOT REPEAT):
{asked_questions_str}

{resume_section}

CRITICAL RULES:
1. DO NOT repeat any previously asked questions
2. DO NOT ask about topics already covered
3. Ask about DIFFERENT aspects and areas each time
4. If resume is provided, ALWAYS prioritize resume-based questions over generic ones
5. Ask ONE clear, specific question
6. Make the question relevant to their background and the {role} role
7. Return ONLY the question text, nothing else - no explanations or preamble

Generate the next interview question now:""",
            expected_output='A single, clear, specific interview question (nothing else)',
            agent=self.agent
        )
        return task
