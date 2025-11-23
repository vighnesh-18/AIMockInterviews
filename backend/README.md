# Interview Practice Partner - Backend API

FastAPI backend with Gemini AI integration for generating dynamic, role-based interview questions and evaluating candidate responses.

## 🚀 Features

- **Dynamic Question Generation**: Uses Gemini AI to generate role-specific, experience-aware interview questions
- **Answer Evaluation**: AI-powered evaluation of candidate responses with detailed feedback
- **Resume Integration**: Analyzes resume to generate contextual questions
- **Experience-Based Difficulty**: Automatically adjusts question difficulty based on experience level
- **Speech Analysis**: Analyzes transcript for filler words, pace, and clarity
- **Report Generation**: Creates comprehensive interview feedback reports

## 📋 Prerequisites

- Python 3.9+
- Gemini API Key (get from [Google AI Studio](https://makersuite.google.com/app/apikey))

## 🔧 Installation

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

The API will be available at `http://localhost:8000`

## 📚 API Endpoints

### Authentication
- `POST /login` - User login
  - Request: `{ "email": "user@example.com", "password": "password" }`
  - Response: `{ "success": true, "session_id": "..." }`

### Session Management
- `POST /set-role` - Store selected role
- `POST /set-experience` - Store experience level
- `POST /set-difficulty` - Store difficulty preference

### Interview Generation
- `POST /generate-questions` - Generate interview questions
  - Request:
    ```json
    {
      "role": "Software Engineer",
      "experience": "2-3",
      "difficulty": "Medium",
      "resume_text": "...",
      "question_count": 6
    }
    ```
  - Response: `{ "success": true, "questions": [...], "count": 6 }`

### Answer Evaluation
- `POST /evaluate-answer` - Evaluate a candidate's answer
  - Request:
    ```json
    {
      "role": "Software Engineer",
      "experience": "2-3",
      "question": "Tell me about yourself",
      "answer": "I am a software engineer with...",
      "resume_text": "..."
    }
    ```
  - Response:
    ```json
    {
      "success": true,
      "evaluation": {
        "score": 85,
        "strengths": [...],
        "improvements": [...],
        "feedback": "..."
      }
    }
    ```

### Analysis
- `POST /analyze-speech` - Analyze speech quality
  - Request: `{ "transcript": "..." }`
  - Response: `{ "success": true, "filler_words": 3, "clarity_score": 85, ... }`

### Reports
- `POST /generate-report` - Generate comprehensive report
  - Request: `{ "role": "...", "chat": [...], "scores": {...} }`
  - Response: `{ "success": true, "report": {...} }`

## 🎯 How It Works

### Question Generation Flow
1. User selects role, experience level, and difficulty
2. Frontend sends `/generate-questions` request with resume (if provided)
3. Backend uses Gemini to generate contextual questions:
   - Tailored to the specific role
   - Adjusted for experience level
   - References resume skills/projects
   - Matches difficulty level
4. Questions returned to frontend for interview

### Answer Evaluation Flow
1. User answers a question (voice or text)
2. Frontend sends `/evaluate-answer` request
3. Backend uses Gemini to evaluate:
   - Technical accuracy
   - Communication clarity
   - Relevance to role
   - Alignment with resume
4. Detailed feedback returned with score

## 📦 Dependencies

- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **google-generativeai** - Gemini API client
- **pydantic** - Data validation
- **python-dotenv** - Environment management
- **python-multipart** - File upload support

## 📝 Notes

- Questions are generated dynamically using Gemini AI
- Fallback questions are provided if API fails
- All responses are validated with Pydantic models
- CORS is enabled for frontend communication
- Session storage is in-memory (use database in production)
