import time
import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Union, List

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from DashSystem.dash_system import DASHSystem, Question

app = FastAPI()
dash_system = DASHSystem()

# Pydantic model for the answer submission
class AnswerRequest(BaseModel):
    user_id: str
    question_id: str
    answer: Union[str, int, float, List[str]]
    response_time_seconds: float

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allows the React frontend to connect
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/next-question/{user_id}", response_model=Question)
def get_next_question(user_id: str):
    """
    Gets the next recommended question for a given user.
    """
    # Ensure the user exists and is loaded
    dash_system.load_user_or_create(user_id)
    
    # Get the next question
    next_question = dash_system.get_next_question(user_id, time.time())
    
    if next_question:
        return next_question
    else:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="No recommended question found.")

@app.post("/submit-answer")
def submit_answer(answer_request: AnswerRequest):
    """
    Submits an answer for a question and updates the user's skill profile.
    """
    is_correct = dash_system.check_answer(
        answer_request.question_id, answer_request.answer
    )
    
    user_profile = dash_system.load_user_or_create(answer_request.user_id)
    question = dash_system.questions.get(answer_request.question_id)
    
    if question:
        dash_system.record_question_attempt(
            user_profile=user_profile,
            question_id=answer_request.question_id,
            skill_ids=question.skill_ids,
            is_correct=is_correct,
            response_time_seconds=answer_request.response_time_seconds,
        )
    
    return {"correct": is_correct}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
