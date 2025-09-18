# MVP components to build
# Load from /CurriculumBuilder/khan_academy_json/
import json
import os
import random
import glob
import pathlib

path = pathlib.Path(__file__).parent.parent.resolve() / "CurriculumBuilder" 

def load_json_objects_from_dir(directory: str, pattern: str = "*.json") -> list:
    """Load all JSON objects from files in a directory matching a pattern."""
    all_objects = []
    # Build file pattern
    file_pattern = os.path.join(directory, pattern)
    # Iterate through matching files
    for file_path in glob.glob(file_pattern):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # If the file contains a list, extend; if dict, append
                if isinstance(data, list):
                    all_objects.extend(data)
                else:
                    all_objects.append(data)
        except Exception as e:
            print(f"⚠️ Failed to load {file_path}: {e}")
    return all_objects

def load_questions(sample_size: int = 20):
    all_questions = load_json_objects_from_dir(path)
    return random.sample(all_questions, sample_size)

if __name__ == "__main__":
    questions = load_questions()
    print(f"Loaded {len(questions)} questions.")
    for q in questions:
        print(json.dumps(q, indent=2))  # Pretty-print each question