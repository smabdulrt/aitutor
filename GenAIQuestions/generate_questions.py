from agents.agent import execute 
import glob 
import json 
import asyncio
from pathlib import Path 

file_pattern = Path(__file__).resolve() / "examples" / "*.json"

# generate questions 
async def generate_questions(data: json) -> json:
    response = await execute(data)
    response = response.strip()
    # if response.startswith()
    return response


# load examples 
async def load_examples():
    for path in glob.glob(file_pattern):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                response = await generate_questions(data) 
                print(response)
        except Exception as e:
            print(f"Failed to load example {path}: {e}")

if __name__ == "__main__":
    asyncio.run(load_examples())