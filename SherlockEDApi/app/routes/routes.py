from fastapi import APIRouter, Request
from app.agent.agent import execute
import asyncio
import json
import uuid
import pathlib
from pydantic import BaseModel, Field
from typing import List
from app.utils.khan_questions_loader import load_questions

router = APIRouter()

base_dir=pathlib.Path(__name__).resolve().parents[1]


# class Question(BaseModel):
#     question: dict = Field(description="The question data")
#     answerArea: dict = Field(description="The answer area")
#     hints: List = Field(description="List of question hints")

@router.get("/questions/{sample_size}", response_model=List[Question])
async def get_questions(sample_size: int = 14):
    """Endpoint for retrieving questions"""
    data = load_questions(
        sample_size=sample_size
    )
    return data

#endpoint to generate new questions using the agent
@router.post("/questions/generate")  
async def generate_question(request: Request):
    json_data = await request.json()
    response = await execute(json_data) 
    print(f"LLM response: {response}")
    response = response.strip().strip("```json").strip("```").strip()
    try:
        question_json = json.loads(response)
        file_name = str(uuid.uuid4())
        with open(f"{base_dir}/GenAIQuestions/{file_name}.json", "w") as f:
            json.dump(question_json, f, indent=4)
        return {"message":"Question generated successfully"},201
    except json.JSONDecodeError as e:
        return {"error": "Failed to parse JSON", "details": str(e), "response": response}