# Backend Directory Structure

```
backend/
├── main.py                          # FastAPI app & crew orchestrator
├── requirements.txt                 # Python dependencies
├── .env                            # Environment variables (4 API keys)
│
├── agents/                         # Agent implementations
│   ├── __init__.py
│   ├── interviewer_agent.py        # Asks role-specific questions
│   ├── followup_agent.py           # Evaluates answers, decides follow-ups
│   ├── scoring_agent.py            # Scores each interaction
│   └── feedback_agent.py           # Generates final report
│
├── memory/                         # Session memory management
│   ├── __init__.py
│   └── session_memory.py           # SessionMemoryManager class
│
└── models/                         # Data models
    ├── __init__.py
    └── schemas.py                  # Pydantic models
```

## Key Files

### Agents (backend/agents/)
- **interviewer_agent.py** - Asks questions based on interview flow
- **followup_agent.py** - Evaluates answer quality and decides strategy
- **scoring_agent.py** - Scores interactions on 4 dimensions
- **feedback_agent.py** - Generates comprehensive final report

### Memory (backend/memory/)
- **session_memory.py** - Manages per-session data:
  - Asked questions list
  - Topics covered
  - Interaction blocks
  - Running scores

### Models (backend/models/)
- **schemas.py** - Pydantic models:
  - CrewInterviewRequest
  - CrewInterviewResponse
  - FollowUpDecision
  - ScoreBlock
  - InteractionBlock
  - SessionMemory

## Imports

All imports use absolute paths from backend root:
```python
from models.schemas import CrewInterviewRequest
from memory.session_memory import session_manager
from agents.interviewer_agent import InterviewerAgent
```

## Environment Variables

```
GEMINI_API_KEY1=...  # Interviewer Agent
GEMINI_API_KEY2=...  # Follow-Up Agent
GEMINI_API_KEY3=...  # Scoring Agent
GEMINI_API_KEY4=...  # Feedback Agent
```

## API Endpoints

- `POST /crew-interview-start` - Start new interview
- `POST /crew-interview-answer` - Process answer through crew
- `POST /crew-interview-end` - End interview and get report
