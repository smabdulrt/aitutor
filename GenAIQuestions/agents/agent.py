from google.adk.agents import Agent, SequentialAgent
from typing import List
import os 
from google.adk.runners import Runner
from google.genai import types
from google.adk.memory import InMemoryMemoryService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.sessions import InMemorySessionService
import uuid
import asyncio
from dotenv import load_dotenv 
from .prompt import generator_prompt, validator_prompt
from google import genai 
from PIL import Image
from io import BytesIO
from pathlib import Path

BASE_URL=Path(__file__).resolve().parents[2]
USER_ID="sherlockED"
GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY")
load_dotenv()
        

def generate_image(prompts: List[str]) ->  List[str]:
    """Function for generating images with Nano Banana.
    ARGS:
        prompts(List[str])  -> A list of prompts for each image needed
    RETURN:
        List[str]           -> of image urls
    """

    client = genai.Client(
        api_key=GOOGLE_API_KEY
    )
    urls = []
    for prompt in prompts:
        response = client.models.generate_content(
            model="gemini-2.5-flash-image-preview",
            contents=prompt
        )
        image_parts = [
            part.inline_data.data
            for part in response.candidates[0].content.parts
            if part.inline_data
        ]
        if image_parts:
            image = Image.open(BytesIO(image_parts[0]))
            url = f"{BASE_URL}/frontend/public/{str(uuid.uuid4())}.png"
            image.save(url)
            urls.append(url)
        return urls
    
questions_generator_agent = Agent(
    name="questions_generator_agent",
    description="Agent that generates new perseus format questions",
    model="gemini-2.0-flash",
    instruction=generator_prompt,
    output_key="question_json"
)

questions_validator_agent = Agent(
    name="questions_validator_agent",
    description="Validates generated json and adds image",
    model="gemini-2.5-flash-image-preview",
    instruction=validator_prompt,
    tools=[generate_image]
)

questions_agent = SequentialAgent(
    name="questions_agent",
    description="Generates and validates perseus questions",
    sub_agents=[questions_generator_agent, questions_validator_agent],
)

runner = Runner(
    app_name="QuestionsGenerator",
    agent=questions_agent,
    session_service=InMemorySessionService(),
    artifact_service=InMemoryArtifactService(),
    memory_service=InMemoryMemoryService()
)

session_service = runner.session_service

async def create_session():
    session = await session_service.create_session(
        app_name="QuestionsGenerator",
        user_id=USER_ID
    )
    return session.id

SESSION_ID = asyncio.run(create_session())


async def execute(data: str) -> str:
    msg = f"Generate new question from: {data}"
    async for ev in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=types.Content(
            role="user",
            parts=[types.Part(text=msg)]
        )):
        if ev.is_final_response() and ev.content and ev.content.parts:
            return ev.content.parts[0].text