from google.adk.agents import Agent, SequentialAgent
from typing import List
import json
import os 
from time import sleep
from google.adk.runners import Runner
from google.genai import types
from google.adk.memory import InMemoryMemoryService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.sessions import InMemorySessionService
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
import uuid
import asyncio
from dotenv import load_dotenv 
from .prompt import generator_prompt, validator_prompt, descriptive_text_extractor_prompt, json_rebuilder_prompt
from google import genai 
from PIL import Image
from io import BytesIO
from pathlib import Path
from imagekitio import ImageKit 

BASE_URL=Path(__file__).resolve().parents[2]
USER_ID="sherlockED"
GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY")
load_dotenv()

def upload_to_imagekit(image_name,image_path):
    #  Put essential values of keys [UrlEndpoint, PrivateKey, PublicKey]
    print("Uploading..")
    imagekit = ImageKit(
        private_key=os.getenv("IMAGEKIT_PRIVATE_KEY"),
        public_key=os.getenv("IMAGEKIT_PUBLIC_KEY"),
        url_endpoint=os.getenv("IMAGEKIT_URL_ENDPOINT")
    )
    upload = imagekit.upload_file(
            file=image_path,
            file_name=image_name,
            options=UploadFileRequestOptions(
                response_fields=["is_private_file", "tags"],
                tags=["tag1", "tag2"]
            )
        )     
    image_url = imagekit.url({
                "path": f"/{image_name}"
            }
        )
    print(image_url)
    return image_url


def generate_image(prompts: List[str]) ->  List[str]:
    """
    Function for generating images with Nano Banana.

    Args:
        prompts(List[str])  -> A list of prompts for each image needed

    Return:
        List[str]           -> of image urls

    Example:
        resp = generate_image(["6 identical cartoon flowers in a grid, no stem, same colors, no borders, background color #f0f0f0"])
        print(resp)
        ...

        Output:
        ['https://ik.imagekit.io/20z1p1q07/7c96b3c3-2209-455d-9a34-b2b037b59073.png']
    """
    client = genai.Client(
        api_key=GOOGLE_API_KEY
    )
    urls = []
    for prompt in prompts:
        print(f"Generating image..for {prompt}")
        response = client.models.generate_content(
            model="gemini-2.0-flash-preview-image-generation",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"]
            ),)
        image_parts = response.candidates[0].content.parts[1].inline_data.data 
        if image_parts:
            image = Image.open(BytesIO(image_parts))
            image_name = f"{str(uuid.uuid4())}.png"
            image_path = f"{BASE_URL}/assets/{image_name}"
            image.save(image_path)
            sleep(5)
            url = upload_to_imagekit(image_name, image_path)
    return urls

from google.adk.tools import FunctionTool

generate_image_tool = FunctionTool(
    func=generate_image
)


questions_generator_agent = Agent(
    name="questions_generator_agent",
    description="Agent that generates new perseus format questions",
    model="gemini-2.0-flash",
    instruction=generator_prompt,
    output_key="question_json"
)

descriptive_text_extractor_agent = Agent(
    name="descriptive_text_extractor_agent",
    description="Extracts image URLs and generates descriptive text prompts.",
    model="gemini-2.0-flash",
    instruction=descriptive_text_extractor_prompt,
    output_key="image_data_with_prompts"
)

image_generator_agent = Agent(
    name="image_generator_agent",
    description="Generates new image URLs from descriptive text prompts.",
    model="gemini-2.0-flash",
    tools=[generate_image_tool],
    output_key="generated_image_urls"
)

json_rebuilder_agent = Agent(
    name="json_rebuilder_agent",
    description="Rebuilds the original JSON with new image URLs and alt texts.",
    model="gemini-2.0-flash",
    instruction=json_rebuilder_prompt,
    output_key="updated_json"
)

questions_agent = SequentialAgent(
    name="questions_agent",
    description="Generates, processes images, and validates perseus questions",
    sub_agents=[
        questions_generator_agent,
        descriptive_text_extractor_agent,
        image_generator_agent,
        json_rebuilder_agent
    ],
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

async def execute(data: json) -> json:
    msg = f"Generate new question from: {data}"
    final_response = None
    
    async for ev in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=types.Content(
            role="user",
            parts=[types.Part(text=msg)]
        )):
        
        # Print all event details for comprehensive debugging
        print(f"=== EVENT ===")
        print(f"Type: {type(ev).__name__}")
        print(f"is_final: {ev.is_final_response()}")
        
        if hasattr(ev, 'content') and ev.content and ev.content.parts:
            response_text = ev.content.parts[0].text
            print(f"Content: {response_text[:200]}...")  # First 200 chars
            if ev.is_final_response():
                final_response = response_text
                
        # Check for tool-related events
        if hasattr(ev, 'tool_calls') and ev.tool_calls:
            print(f"TOOL CALLS: {ev.tool_calls}")
            
        print("=============")
    
    return final_response
