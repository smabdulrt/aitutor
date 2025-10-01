from fastapi import APIRouter, Request
from .agent import execute
import asyncio
import json
import pathlib
from pydantic import BaseModel, Field
from typing import List
from .khan_questions_loader import load_questions

router = APIRouter()

class Question(BaseModel):
    question: dict = Field(description="The question data")
    answerArea: dict = Field(description="The answer area")
    hints: List = Field(description="List of question hints")

@router.get("/questions/{sample_size}", response_model=List[Question])
async def get_questions(sample_size: int = 14):
    """Endpoint for retrieving questions"""
    data = load_questions(
        sample_size=sample_size
    )
    return data

#endpoint to generate new questions using the agent
@router.post("/questions/generate") 
def generate_question(request: Request):
    json_data = request.json()
    response = asyncio.run(execute(json_data))  
    response = response.strip().strip("```json").strip("```").strip()
    print(f"Raw LLM response: {response}")
    try:
        question_json = json.loads(response)
        return question_json
    except json.JSONDecodeError as e:
        return {"error": "Failed to parse JSON", "details": str(e), "response": response}