import time
import sys
import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from DashSystem.dash_system import DASHSystem, Question, GradeLevel

app = FastAPI()
dash_system = DASHSystem()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allows the React frontend to connect
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/next-question/{user_id}", response_model=Question)
def get_next_question(user_id: str, grade: Optional[str] = None):
    """
    Gets the next recommended question for a given user.
    If 'grade' is provided on the first call for a user, it sets their initial skill level.
    """
    # Convert grade string to GradeLevel enum if provided
    grade_level_enum: Optional[GradeLevel] = None
    if grade:
        try:
            # Normalize grade input (e.g., "grade_7" -> "GRADE_7")
            grade_upper = grade.upper()
            if not grade_upper.startswith("GRADE_"):
                # Accommodate inputs like "7" or "K"
                if grade_upper.isdigit() and grade_upper != '0':
                    grade_upper = f"GRADE_{grade_upper}"

            grade_level_enum = GradeLevel[grade_upper]
        except KeyError:
            valid_grades = [g.name for g in GradeLevel]
            raise HTTPException(
                status_code=400,
                detail=f"Invalid grade level '{grade}'. Valid options are: {valid_grades}"
            )

    # Ensure the user exists and is loaded, potentially initializing skills
    dash_system.load_user_or_create(user_id, grade_level=grade_level_enum)
    
    # Get the next question
    next_question = dash_system.get_next_question(user_id, time.time())
    
    if next_question:
        return next_question
    else:
        # If no specific question is recommended, you could return a default
        # or a message indicating the student is proficient in all areas.
        raise HTTPException(status_code=404, detail="No recommended question found for this user.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
