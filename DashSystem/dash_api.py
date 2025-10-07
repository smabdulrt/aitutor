import time
import sys
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from DashSystem.dash_system_v2 import DashSystemV2

# === REQUEST/RESPONSE MODELS ===

class CreateUserRequest(BaseModel):
    user_id: str
    age: Optional[int] = None
    grade_level: Optional[str] = None

class SubmitAnswerRequest(BaseModel):
    user_id: str
    question_id: str
    skill_ids: List[str]
    is_correct: bool
    response_time: float

# === UTILITY FUNCTIONS ===

def serialize_mongo_doc(doc):
    """Convert MongoDB document to JSON-serializable dict"""
    if doc is None:
        return None

    result = {}
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            result[key] = str(value)
        elif isinstance(value, datetime):
            result[key] = value.isoformat()
        elif isinstance(value, dict):
            result[key] = serialize_mongo_doc(value)
        elif isinstance(value, list):
            result[key] = [serialize_mongo_doc(item) if isinstance(item, dict) else item for item in value]
        else:
            result[key] = value
    return result

def convert_to_perseus_format(question: dict) -> dict:
    """
    Convert MongoDB question to Perseus-compatible format for frontend rendering

    Perseus is Khan Academy's math rendering engine that expects specific format
    """
    # Extract base fields
    perseus_question = {
        "question_id": question.get("question_id"),
        "content": question.get("content", ""),
        "question_type": question.get("question_type", "input-number"),
        "skill_ids": question.get("skill_ids", []),
        "difficulty": question.get("difficulty", 0.5),
    }

    # Convert based on question type
    if question.get("question_type") == "multiple_choice":
        perseus_question["type"] = "multiple-choice"
        perseus_question["choices"] = [
            {"content": choice, "correct": choice == question.get("answer")}
            for choice in question.get("options", [])
        ]
    elif question.get("question_type") == "numeric":
        perseus_question["type"] = "input-number"
        perseus_question["answer"] = question.get("answer")
    else:
        # Default to text input
        perseus_question["type"] = "input-number"
        perseus_question["answer"] = question.get("answer")

    # Add explanation/hints
    perseus_question["explanation"] = question.get("explanation", "")
    perseus_question["hints"] = question.get("hints", [])
    perseus_question["tags"] = question.get("tags", [])

    return perseus_question

# === FASTAPI APP ===

app = FastAPI(
    title="DashSystem V2 API",
    description="Adaptive learning system with intelligent question selection",
    version="2.0.0"
)

dash_system = DashSystemV2()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === ENDPOINTS ===

@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "DashSystem V2 API",
        "version": "2.0.0",
        "total_skills": len(dash_system.SKILLS_CACHE)
    }

@app.post("/users/create")
def create_user(request: CreateUserRequest):
    """
    Create a new user with cold start strategy

    Example:
    ```json
    {
        "user_id": "student_123",
        "age": 8,
        "grade_level": "GRADE_3"
    }
    ```
    """
    try:
        user = dash_system.get_or_create_user(
            user_id=request.user_id,
            age=request.age,
            grade_level=request.grade_level
        )

        if not user:
            raise HTTPException(status_code=500, detail="Failed to create user")

        return JSONResponse(content={
            "success": True,
            "user_id": user["user_id"],
            "grade_level": user.get("grade_level"),
            "total_skills": len(user.get("skill_states", {}))
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/next-question/{user_id}")
def get_next_question(user_id: str):
    """
    Get the next recommended question for a user

    Returns Perseus-formatted question ready for frontend rendering
    """
    try:
        # Ensure the user exists
        user = dash_system.get_or_create_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get the next question
        next_question = dash_system.get_next_question(user_id, time.time())

        if not next_question:
            raise HTTPException(
                status_code=404,
                detail="No questions available. Student may have mastered all available skills!"
            )

        # Convert to Perseus format for frontend
        perseus_question = convert_to_perseus_format(next_question)

        return JSONResponse(content=perseus_question)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/submit-answer")
def submit_answer(request: SubmitAnswerRequest):
    """
    Submit an answer and update skill states with breadcrumb cascade

    Example:
    ```json
    {
        "user_id": "student_123",
        "question_id": "q_12345",
        "skill_ids": ["math_3_1.2.3.4"],
        "is_correct": true,
        "response_time": 5.2
    }
    ```
    """
    try:
        # Get question content for logging
        question_doc = dash_system.db.questions.find_one({"question_id": request.question_id})
        question_content = ""
        if question_doc:
            question_content = question_doc.get("content", "")

        # Record the question attempt
        affected_skills = dash_system.record_question_attempt(
            user_id=request.user_id,
            question_id=request.question_id,
            skill_ids=request.skill_ids,
            is_correct=request.is_correct,
            response_time=request.response_time,
            question_content=question_content
        )

        # Get updated user stats
        user = dash_system.db.get_user(request.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Calculate streak
        recent_history = user.get("question_history", [])[-10:]
        current_streak = 0
        for q in reversed(recent_history):
            if q.get("is_correct"):
                current_streak += 1
            else:
                break

        return JSONResponse(content={
            "success": True,
            "is_correct": request.is_correct,
            "affected_skills_count": len(affected_skills),
            "current_streak": current_streak,
            "total_questions_answered": len(user.get("question_history", []))
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user/{user_id}/stats")
def get_user_stats(user_id: str):
    """
    Get comprehensive statistics for a user

    Returns skill proficiency, accuracy, mastery counts, etc.
    """
    try:
        stats = dash_system.get_user_statistics(user_id)

        if not stats:
            raise HTTPException(status_code=404, detail="User not found")

        return JSONResponse(content=serialize_mongo_doc(stats))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user/{user_id}/profile")
def get_user_profile(user_id: str):
    """Get user profile with grade level and learning progress"""
    try:
        user = dash_system.db.get_user(user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Calculate progress metrics
        skill_states = user.get("skill_states", {})
        total_skills = len(skill_states)
        mastered_skills = sum(1 for s in skill_states.values() if s.get("memory_strength", 0) >= 0.8)
        locked_skills = sum(1 for s in skill_states.values() if s.get("memory_strength", 0) < 0)

        question_history = user.get("question_history", [])
        total_questions = len(question_history)
        correct_answers = sum(1 for q in question_history if q.get("is_correct"))

        return JSONResponse(content={
            "user_id": user["user_id"],
            "grade_level": user.get("grade_level"),
            "age": user.get("age"),
            "total_skills": total_skills,
            "mastered_skills": mastered_skills,
            "locked_skills": locked_skills,
            "learning_skills": total_skills - mastered_skills - locked_skills,
            "total_questions_answered": total_questions,
            "correct_answers": correct_answers,
            "accuracy": correct_answers / total_questions if total_questions > 0 else 0.0,
            "created_at": user.get("created_at").isoformat() if user.get("created_at") else None
        })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*80)
    print("🚀 Starting DashSystem V2 API Server")
    print("="*80)
    print(f"📚 Loaded {len(dash_system.SKILLS_CACHE)} skills")
    print(f"🌐 API will be available at: http://localhost:8000")
    print(f"📖 API docs available at: http://localhost:8000/docs")
    print("="*80 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)
