from fastapi import APIRouter, Request
import asyncio
import json
import uuid
import pathlib
from pydantic import BaseModel, Field
from typing import List
from app.utils.khan_questions_loader import load_questions

router = APIRouter()


@router.get("/questions/{sample_size}")
async def get_questions(sample_size: int = 14):
    """Endpoint for retrieving questions"""
    data = load_questions(
        sample_size=sample_size
    )
    return data