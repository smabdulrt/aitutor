from agents.agent import execute 
import glob 
import uuid
import json 
import asyncio
from pathlib import Path 

file_pattern = Path(__file__).parent.resolve() / "examples" / "*.json"
generated_json = Path(__file__).parent.resolve() / "new" / f"{str(uuid.uuid4())}.json"


# load examples 
async def main():
    # generate questions 
    async def generate_questions(data: str) -> str:
        print(f"Generating questions...")
        try:
            response = await execute(data)
            response = response.strip()
            if response.startswith("```json"):
                response = response.removeprefix("```json")
            if response.endswith("```"):
                response = response.removesuffix("```")
            response = response.strip()
            return response
        except Exception as e:
            print(f"The following error occured: {e}")

    for path in glob.glob(str(file_pattern)):
        try:
            print(f"Loading example: {path}")
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                response = await generate_questions(data)
            with open(generated_json, "w", encoding="utf-8") as f:
                json_response = json.loads(response)
                json.dump(json_response, f, indent=4) if response else None
                print(f"Generation completed for: {path}...\n ")
        except Exception as e:
            print(f"Failed to load example {path}: {e}")

if __name__ == "__main__":
    asyncio.run(main())