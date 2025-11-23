from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

app = FastAPI(title="Interview Practice Partner API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Groq API Keys
GROQ_API_KEY_1 = os.getenv("GROQ_API_KEY_1")
GROQ_API_KEY_2 = os.getenv("GROQ_API_KEY_2")
GROQ_API_KEY_3 = os.getenv("GROQ_API_KEY_3")
GROQ_API_KEY_4 = os.getenv("GROQ_API_KEY_4")

if not all([GROQ_API_KEY_1, GROQ_API_KEY_2, GROQ_API_KEY_3, GROQ_API_KEY_4]):
    print("WARNING: Groq API keys not found in environment variables")

# ==================== Data Models ====================

class UserSession(BaseModel):
    role: str
    experience: str
    difficulty: str
    resume_text: Optional[str] = None

class InterviewRequest(BaseModel):
    role: str
    experience: str
    difficulty: str
    resume_text: Optional[str] = None
    question_count: int = 6

class AnswerEvaluation(BaseModel):
    role: str
    experience: str
    question: str
    answer: str
    resume_text: Optional[str] = None

class ConversationalInterviewRequest(BaseModel):
    role: str
    experience: str
    difficulty: str
    resume_text: Optional[str] = None
    user_message: str
    conversation_history: Optional[List[dict]] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class CrewInterviewStartRequest(BaseModel):
    session_id: str
    role: str
    experience: str
    difficulty: str
    resume_text: Optional[str] = None

class CrewInterviewAnswerRequest(BaseModel):
    session_id: str
    role: str
    experience: str
    difficulty: str
    resume_text: Optional[str] = None
    user_message: str
    conversation_history: Optional[List[dict]] = None

class CrewInterviewRequest(BaseModel):
    session_id: str

# ==================== Session Storage ====================
# In production, use a database. For now, in-memory storage.
sessions = {}

# ==================== Helper Functions ====================

def get_difficulty_level(experience: str) -> str:
    """Map experience to difficulty if not explicitly set"""
    experience_to_difficulty = {
        "0": "Easy",
        "0-1": "Easy",
        "1-2": "Medium",
        "2-3": "Medium",
        "3-5": "Hard",
        "5+": "Expert"
    }
    return experience_to_difficulty.get(experience, "Medium")

# ==================== OLD GEMINI FUNCTIONS - REMOVED ====================
# All old Gemini-based functions have been removed
# System now uses CrewAI with Groq (llama-3.1-8b-instant)
# =========================================================================

# Placeholder for removed functions
def get_fallback_questions(role: str, experience: str, difficulty: str) -> List[str]:
    """Fallback questions if Gemini fails"""
    
    base_questions = {
        "Software Engineer": [
            "Tell me about yourself and your software development experience.",
            "Describe your most challenging project and how you solved it.",
            "How do you approach debugging a complex issue?",
            "What design patterns are you familiar with?",
            "How do you handle code reviews and feedback?",
            "What's your experience with testing and CI/CD?"
        ],
        "Data Scientist": [
            "Tell me about your experience with machine learning.",
            "Walk me through a data science project you've worked on.",
            "How do you handle missing data in a dataset?",
            "Explain the difference between supervised and unsupervised learning.",
            "What metrics do you use to evaluate model performance?",
            "How do you prevent overfitting in your models?"
        ],
        "Product Manager": [
            "Tell me about your product management experience.",
            "Describe a product you've worked on and its impact.",
            "How do you prioritize features?",
            "What's your approach to user research?",
            "How do you measure product success?",
            "Tell me about a difficult stakeholder situation you handled."
        ]
    }
    
    return base_questions.get(role, [
        "Tell me about yourself.",
        "Why are you interested in this role?",
        "Describe your greatest strength.",
        "Tell me about a challenge you overcame.",
        "Where do you see yourself in 5 years?",
        "Why should we hire you?"
    ])

def evaluate_answer(
    role: str,
    experience: str,
    question: str,
    answer: str,
    resume_text: Optional[str] = None
) -> dict:
    """
    Use Gemini to evaluate the user's answer
    """
    
    prompt = f"""You are an expert technical interviewer evaluating a candidate's response.

Position: {role}
Experience Level: {experience}
Question: {question}
Candidate's Answer: {answer}

Resume Context:
{resume_text if resume_text else "No resume provided"}

Evaluate the answer and provide:
1. A score from 0-100
2. Strengths (list 2-3 points)
3. Areas for improvement (list 2-3 points)
4. Specific feedback

Return as JSON with keys: "score", "strengths", "improvements", "feedback"

Example:
{{"score": 75, "strengths": ["Point 1", "Point 2"], "improvements": ["Point 1", "Point 2"], "feedback": "Overall feedback..."}}

Evaluate now:"""

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        
        response_text = response.text.strip()
        
        # Extract JSON
        if "{" in response_text and "}" in response_text:
            start = response_text.index("{")
            end = response_text.rindex("}") + 1
            json_str = response_text[start:end]
            evaluation = json.loads(json_str)
            return evaluation
        else:
            return {
                "score": 70,
                "strengths": ["Good effort"],
                "improvements": ["Could be more detailed"],
                "feedback": response_text
            }
    
    except Exception as e:
        print(f"Error evaluating answer: {e}")
        return {
            "score": 50,
            "strengths": ["Attempted to answer"],
            "improvements": ["More detail needed"],
            "feedback": "Unable to evaluate at this time"
        }

def parse_resume(resume_text: Optional[str]) -> dict:
    """
    Parse resume to extract skills, projects, and experience
    Uses Gemini to intelligently extract key information
    """
    if not resume_text or resume_text.lower() in ["no resume", "none", ""]:
        print("\n" + "="*80)
        print("📄 RESUME EXTRACTION")
        print("="*80)
        print("⚠️  No resume provided\n")
        return {
            "skills": [],
            "projects": [],
            "experience": [],
            "summary": "No resume provided"
        }
    
    if not GEMINI_API_KEY:
        print("\n" + "="*80)
        print("📄 RESUME EXTRACTION")
        print("="*80)
        print("⚠️  API key not configured - using fallback\n")
        return {
            "skills": [],
            "projects": [],
            "experience": [],
            "summary": resume_text[:500]  # Return first 500 chars as fallback
        }
    
    prompt = f"""Analyze this resume and extract key information in JSON format.

RESUME:
{resume_text}

Extract and return ONLY a JSON object with these keys:
{{
    "skills": ["skill1", "skill2", "skill3", ...],  (top 10 technical skills)
    "projects": ["project1: brief description", "project2: brief description", ...],  (top 5 projects/achievements)
    "experience": ["role1: company, duration", "role2: company, duration", ...],  (top 5 roles)
    "summary": "2-3 sentence summary of candidate's background"
}}

Focus on:
- Technical skills and technologies
- Significant projects and achievements
- Relevant work experience
- Key accomplishments

Return ONLY the JSON, no other text."""

    try:
        print("\n" + "="*80)
        print("📄 RESUME EXTRACTION")
        print("="*80)
        print(f"📥 Resume received ({len(resume_text)} characters)\n")
        
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        
        response_text = response.text.strip()
        
        # Extract JSON
        if "{" in response_text and "}" in response_text:
            start = response_text.index("{")
            end = response_text.rindex("}") + 1
            json_str = response_text[start:end]
            parsed = json.loads(json_str)
            
            # Print extracted content
            print("✅ EXTRACTED CONTENT:\n")
            
            # Summary
            print("📝 SUMMARY:")
            print(f"   {parsed.get('summary', 'N/A')}\n")
            
            # Skills
            print("🛠️  TOP SKILLS:")
            skills = parsed.get('skills', [])
            if skills:
                for i, skill in enumerate(skills, 1):
                    print(f"   {i}. {skill}")
            else:
                print("   (No skills extracted)")
            print()
            
            # Projects
            print("🚀 TOP PROJECTS:")
            projects = parsed.get('projects', [])
            if projects:
                for i, project in enumerate(projects, 1):
                    print(f"   {i}. {project}")
            else:
                print("   (No projects extracted)")
            print()
            
            # Experience
            print("💼 WORK EXPERIENCE:")
            experience = parsed.get('experience', [])
            if experience:
                for i, exp in enumerate(experience, 1):
                    print(f"   {i}. {exp}")
            else:
                print("   (No experience extracted)")
            print()
            
            print("="*80)
            print("✓ Resume extraction complete!\n")
            
            return parsed
        else:
            print("⚠️  Could not parse JSON response\n")
            return {
                "skills": [],
                "projects": [],
                "experience": [],
                "summary": response_text[:500]
            }
    
    except Exception as e:
        print(f"\n❌ Error parsing resume: {e}\n")
        return {
            "skills": [],
            "projects": [],
            "experience": [],
            "summary": resume_text[:500]
        }

def conversational_interview(
    role: str,
    experience: str,
    difficulty: str,
    user_message: str,
    resume_text: Optional[str] = None,
    conversation_history: Optional[List[dict]] = None
) -> dict:
    """
    Conversational interview that can ask follow-ups and provide feedback
    First message should be "start" to begin, then user answers
    """
    
    if conversation_history is None:
        conversation_history = []
    
    # If this is the start, ask for introduction
    if user_message.lower() == "start":
        return {
            "success": True,
            "question": "Tell me about yourself. Please share your background, experience, and what interests you about this role.",
            "is_followup": False,
            "conversation_history": []
        }
    
    # Build context for the interviewer
    difficulty_descriptions = {
        "Easy": "simple, foundational, beginner-friendly",
        "Medium": "moderate complexity, intermediate level",
        "Hard": "challenging, advanced concepts",
        "Expert": "very challenging, expert-level, edge cases"
    }
    
    difficulty_desc = difficulty_descriptions.get(difficulty, "moderate")
    
    # Format conversation history for context
    history_text = ""
    if conversation_history:
        for msg in conversation_history[-4:]:  # Keep last 4 messages for context
            role_name = msg.get("role", "unknown")
            content = msg.get("content", "")
            history_text += f"{role_name}: {content}\n"
    
    # Count how many exchanges have happened
    exchange_count = len(conversation_history) // 2 if conversation_history else 0
    
    # Parse resume to extract skills and projects
    parsed_resume = parse_resume(resume_text)
    
    # Format parsed resume data
    resume_context = f"""
CANDIDATE'S RESUME SUMMARY:
{parsed_resume.get('summary', 'No resume provided')}

KEY SKILLS:
{', '.join(parsed_resume.get('skills', [])) if parsed_resume.get('skills') else 'Not provided'}

PROJECTS & ACHIEVEMENTS:
{chr(10).join([f"- {p}" for p in parsed_resume.get('projects', [])]) if parsed_resume.get('projects') else 'Not provided'}

WORK EXPERIENCE:
{chr(10).join([f"- {e}" for e in parsed_resume.get('experience', [])]) if parsed_resume.get('experience') else 'Not provided'}
"""
    
    prompt = f"""You are an expert technical interviewer conducting a {role} interview.

INTERVIEW CONTEXT:
- Position: {role}
- Candidate Experience Level: {experience}
- Difficulty Level: {difficulty} (questions should be {difficulty_desc})
- Exchange Count: {exchange_count}

{resume_context}

CONVERSATION HISTORY (last few exchanges):
{history_text}

CANDIDATE'S LATEST RESPONSE:
{user_message}

YOUR TASK:
1. Evaluate the candidate's response
2. Provide constructive feedback
3. Ask the NEXT question (follow-up OR new topic)
4. Be conversational - acknowledge their answer before asking next question

CRITICAL RULES FOR QUESTION FLOW:
1. NEVER ask the same question twice (even in different wording)
2. NEVER ask similar questions about the same topic in succession
3. TRACK TOPICS: If last 2 messages were about Project X, ask about something else
4. INTERVIEW FLOW:
   - Questions 1-2: Role fit, background, why this position
   - Questions 3-4: Deep dive into ONE project from resume
   - Questions 5-6: Different project or technical skills
   - Questions 7+: Behavioral, system design, problem-solving, career goals

FOLLOW-UP RULES:
- Ask follow-ups ONLY if answer was incomplete or vague
- Maximum 1 follow-up per topic before moving on
- If answer was good/complete, move to NEW topic immediately
- NEVER ask about same project twice

TOPIC ROTATION (for {role}):
Topics to cover (in order):
1. Role fit and background
2. First project from resume (ask about challenges, learnings, impact)
3. Different project or technical skill
4. Problem-solving approach
5. System design or architecture
6. Teamwork and communication
7. Conflict resolution
8. Career goals and growth

RESUME CONTENT TO USE:
Projects: {', '.join([p.split(':')[0] for p in parsed_resume.get('projects', [])])}
Skills: {', '.join(parsed_resume.get('skills', [])[:5])}
Experience: {', '.join([e.split(':')[0] for e in parsed_resume.get('experience', [])])}

WHAT TO AVOID:
- ❌ Asking "Tell me about your projects" then later "What projects have you worked on?"
- ❌ Asking about same project multiple times
- ❌ Asking "How did you handle challenges in Project X?" then "What challenges did you face in Project X?"
- ❌ Only asking about resume (mix in behavioral and role-specific questions)
- ❌ Repeating question structure even if topic is different

WHAT TO DO:
- ✅ Ask about different aspects of different projects
- ✅ Mix technical, behavioral, and role-specific questions
- ✅ Reference specific project names when asking
- ✅ Move to new topics after 1-2 exchanges
- ✅ Vary question types and formats

Respond in JSON format:
{{
    "feedback": "Your feedback on their answer (acknowledge what they said well, what could be improved)",
    "score": 0-100 (score for this answer),
    "next_question": "The next question to ask (different topic/project than before)",
    "is_followup": false (only true if absolutely necessary for clarification)
}}

Respond now:"""

    try:
        if not GEMINI_API_KEY:
            return {
                "success": False,
                "error": "API key not configured"
            }
        
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        
        response_text = response.text.strip()
        
        # Extract JSON
        if "{" in response_text and "}" in response_text:
            start = response_text.index("{")
            end = response_text.rindex("}") + 1
            json_str = response_text[start:end]
            result = json.loads(json_str)
            
            # Add to conversation history
            new_history = conversation_history + [
                {"role": "candidate", "content": user_message},
                {"role": "interviewer", "content": result.get("next_question", "")}
            ]
            
            return {
                "success": True,
                "feedback": result.get("feedback", ""),
                "score": result.get("score", 70),
                "question": result.get("next_question", ""),
                "is_followup": result.get("is_followup", False),
                "conversation_history": new_history
            }
        else:
            return {
                "success": False,
                "error": "Invalid response format"
            }
    
    except Exception as e:
        print(f"Error in conversational interview: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }

# ==================== API Endpoints ====================

@app.get("/")
async def root():
    return {"message": "Interview Practice Partner API", "status": "running"}

@app.post("/login")
async def login(request: LoginRequest):
    """
    Authenticate user (simplified for now)
    In production, use proper authentication
    """
    # For demo: accept any email/password
    if request.email and request.password:
        session_id = request.email.replace("@", "_").replace(".", "_")
        sessions[session_id] = {"email": request.email}
        return {
            "success": True,
            "message": "Login successful",
            "session_id": session_id
        }
    return {
        "success": False,
        "message": "Invalid credentials"
    }

@app.post("/set-role")
async def set_role(request: dict):
    """Store user's selected role"""
    role = request.get("role")
    if not role:
        raise HTTPException(status_code=400, detail="Role is required")
    return {"success": True, "role": role}

@app.post("/set-experience")
async def set_experience(request: dict):
    """Store user's experience level"""
    experience = request.get("experience")
    if not experience:
        raise HTTPException(status_code=400, detail="Experience is required")
    return {"success": True, "experience": experience}

@app.post("/set-difficulty")
async def set_difficulty(request: dict):
    """Store user's difficulty preference"""
    difficulty = request.get("difficulty")
    if not difficulty:
        raise HTTPException(status_code=400, detail="Difficulty is required")
    return {"success": True, "difficulty": difficulty}

# COMMENTED OUT - Using new crew-based system instead
# @app.post("/generate-questions")
# async def generate_questions(request: InterviewRequest):
#     """
#     Generate interview questions based on role, experience, difficulty, and resume
#     """
#     try:
#         questions = generate_interview_questions(
#             role=request.role,
#             experience=request.experience,
#             difficulty=request.difficulty,
#             resume_text=request.resume_text,
#             question_count=request.question_count
#         )
#         return {
#             "success": True,
#             "questions": questions,
#             "count": len(questions)
#         }
#     except Exception as e:
#         print(f"Error: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# COMMENTED OUT - Using new crew-based system instead
# @app.post("/preview-interview")
# async def preview_interview(request: ConversationalInterviewRequest):
#     """
#     Preview what the interview will look like based on resume and role
#     Shows extracted resume content and what questions will be asked
#     """
#     try:
#         print("\n" + "="*80)
#         print("🔍 INTERVIEW PREVIEW")
#         print("="*80)
#         print(f"Role: {request.role}")
#         print(f"Experience: {request.experience}")
#         print(f"Difficulty: {request.difficulty}\n")
#         
#         # Parse resume
#         parsed_resume = parse_resume(request.resume_text)
#         
#         # Get first question
#         first_question_response = conversational_interview(
#             role=request.role,
#             experience=request.experience,
#             difficulty=request.difficulty,
#             user_message="start",
#             resume_text=request.resume_text,
#             conversation_history=None
#         )
#         
#         print("\n" + "="*80)
#         print("📋 INTERVIEW PREVIEW COMPLETE")
#         print("="*80 + "\n")
#         
#         return {
#             "success": True,
#             "resume_summary": parsed_resume.get('summary', ''),
#             "skills": parsed_resume.get('skills', []),
#             "projects": parsed_resume.get('projects', []),
#             "experience": parsed_resume.get('experience', []),
#             "first_question": first_question_response.get('question', ''),
#             "message": "This is what the AI extracted from your resume and the first question it will ask"
#         }
#     except Exception as e:
#         print(f"Error in preview: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# COMMENTED OUT - Using new crew-based system instead
# @app.post("/conversational-interview")
# async def conversational_interview_endpoint(request: ConversationalInterviewRequest):
#     """
#     Conversational interview endpoint that handles dynamic Q&A with follow-ups
#     First call with user_message="start" to begin the interview
#     """
#     try:
#         result = conversational_interview(
#             role=request.role,
#             experience=request.experience,
#             difficulty=request.difficulty,
#             user_message=request.user_message,
#             resume_text=request.resume_text,
#             conversation_history=request.conversation_history
#         )
#         return result
#     except Exception as e:
#         print(f"Error: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# COMMENTED OUT - Using new crew-based system instead
# @app.post("/evaluate-answer")
# async def evaluate_answer_endpoint(request: AnswerEvaluation):
#     """
#     Evaluate a user's answer to an interview question
#     """
#     try:
#         evaluation = evaluate_answer(
#             role=request.role,
#             experience=request.experience,
#             question=request.question,
#             answer=request.answer,
#             resume_text=request.resume_text
#         )
#         return {
#             "success": True,
#             "evaluation": evaluation
#         }
#     except Exception as e:
#         print(f"Error: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-speech")
async def analyze_speech(request: dict):
    """
    Analyze speech quality (filler words, pace, clarity)
    """
    transcript = request.get("transcript", "")
    
    # Simple analysis
    filler_words = ["um", "uh", "like", "you know", "so", "actually", "basically", "right", "kind of"]
    words = transcript.lower().split()
    filler_count = sum(1 for word in words if word.strip(".,!?;:") in filler_words)
    total_words = len(words)
    
    filler_ratio = (filler_count / total_words * 100) if total_words > 0 else 0
    wpm = max(80, min(160, len(words) // 2))  # Estimate WPM
    
    clarity_score = 100 - min(filler_ratio * 2, 50)
    confidence_score = 100 - min(filler_ratio, 30)
    
    return {
        "success": True,
        "filler_words": filler_count,
        "filler_ratio": filler_ratio,
        "words_per_minute": wpm,
        "clarity_score": clarity_score,
        "confidence_score": confidence_score
    }

@app.post("/generate-report")
async def generate_report(request: dict):
    """
    Generate a comprehensive interview report
    """
    try:
        role = request.get("role")
        chat_history = request.get("chat", [])
        scores = request.get("scores", {})
        
        prompt = f"""Generate a professional interview feedback report for a {role} candidate.

Chat History:
{json.dumps(chat_history, indent=2)}

Performance Scores:
{json.dumps(scores, indent=2)}

Provide:
1. Overall assessment
2. Strengths
3. Areas for improvement
4. Recommendations for practice

Return as JSON with keys: "assessment", "strengths", "improvements", "recommendations"

Generate report:"""
        
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        
        response_text = response.text.strip()
        
        if "{" in response_text and "}" in response_text:
            start = response_text.index("{")
            end = response_text.rindex("}") + 1
            json_str = response_text[start:end]
            report = json.loads(json_str)
            return {"success": True, "report": report}
        
        return {"success": True, "report": {"assessment": response_text}}
    
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== CREW AI ORCHESTRATOR ====================

from models.schemas import CrewInterviewRequest, CrewInterviewResponse
from agents.interview_crew import InterviewCrew as CrewAIInterviewCrew

# Initialize crew
interview_crew = CrewAIInterviewCrew()

# Using CrewAI-based implementation above

# ==================== CREW ENDPOINTS ====================

@app.post("/crew-interview-start")
async def crew_interview_start(request: CrewInterviewStartRequest):
    """Start a new interview with the crew"""
    try:
        question = interview_crew.start_interview(
            session_id=request.session_id,
            role=request.role,
            experience=request.experience,
            difficulty=request.difficulty,
            resume_text=request.resume_text or ""
        )
        
        return CrewInterviewResponse(
            success=True,
            question=question,
            session_id=request.session_id
        ).model_dump()
    
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/crew-interview-answer")
async def crew_interview_answer(request: CrewInterviewAnswerRequest):
    """Process user answer through the crew"""
    try:
        result = interview_crew.process_answer(
            session_id=request.session_id,
            user_answer=request.user_message,
            role=request.role,
            experience=request.experience,
            difficulty=request.difficulty,
            resume_text=request.resume_text or "",
            conversation_history=request.conversation_history or []
        )
        
        return result
    
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/crew-interview-end")
async def crew_interview_end(request: CrewInterviewRequest):
    """End interview and get final report"""
    try:
        print(f"\n🛑 /crew-interview-end called with session_id: {request.session_id}")
        result = interview_crew.end_interview(request.session_id)
        print(f"✅ end_interview returned: {type(result)}")
        print(f"   Keys: {result.keys() if isinstance(result, dict) else 'N/A'}")
        print(f"   Success: {result.get('success', 'N/A')}")
        print(f"   Has report: {bool(result.get('report'))}")
        print(f"   Has summary: {bool(result.get('summary'))}")
        print(f"   Has pdf_filename: {bool(result.get('pdf_filename'))}")
        return result
    
    except Exception as e:
        print(f"❌ Error in /crew-interview-end: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download-report")
async def download_report(filepath: str = None):
    """Download interview report PDF"""
    try:
        if not filepath:
            raise HTTPException(status_code=400, detail="filepath parameter required")
        
        # If filepath is just filename, look in reports directory
        if not os.path.isabs(filepath):
            report_dir = os.path.join(os.path.dirname(__file__), 'reports')
            file_path = os.path.join(report_dir, filepath)
        else:
            file_path = filepath
        
        # Security check: ensure file exists and is accessible
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            raise HTTPException(status_code=404, detail=f"Report not found: {file_path}")
        
        # Get just the filename for the download
        filename = os.path.basename(file_path)
        
        print(f"✅ Downloading report: {file_path}")
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/pdf"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error downloading report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Interview Practice Partner API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
