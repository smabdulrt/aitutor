from fastapi import APIRouter
import json
import pathlib
from pydantic import BaseModel, Field
from typing import List
from .khan_questions_loader import load_questions

router = APIRouter()

class Question(BaseModel):
    question: dict = Field(description="The question data")
    answerArea: dict
    hints: List

@router.get("/questions/{sample_size}", response_model=List[Question])
def get_questions(sample_size: int = 14):
    data = load_questions(sample_size=sample_size)
    return data