from math import e
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.agent.agent import execute
import asyncio
import json
import uuid
import pathlib 

router = APIRouter()

base_dir=pathlib.Path(__file__).resolve().parents[3]

#endpoint to generate new questions using the agent
@router.post("/generate")  
async def generate_question(request: Request):
    """Endpoint for generating new questions"""
    json_data = await request.json()
    response = await execute(json_data) 
    # print(f"LLM response: {response}")
    response = response.strip()
    if response.startswith("```json"):
        response = response.removeprefix("```json")
    if response.endswith("```"):
        response = response.removesuffix("```")
    response = response.strip()
    try:
        question_json = json.loads(response)
        file_name = str(uuid.uuid4())
        with open(f"{base_dir}/new/{file_name}.json", "w") as f:
            json.dump(question_json, f, indent=4)
        return JSONResponse(content={"message":"Question generated successfully"}, status_code=201)
    except json.JSONDecodeError as e:
        return {"error": "Failed to parse JSON", "details": str(e), "response": response}