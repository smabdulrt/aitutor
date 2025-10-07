"""
Migrate Khan Academy Perseus Questions to MongoDB
Extracts skills and questions from sample_questions_data/ folder structure
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Set
import re

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from DashSystem.mongodb_handler import MongoDBHandler, get_db


class KhanAcademyMigrator:
    """Migrate Khan Academy data to MongoDB"""

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.db = get_db()
        self.skills_map: Dict[str, Dict] = {}
        self.questions_list: List[Dict] = []
        self.stats = {
            "skills_created": 0,
            "questions_migrated": 0,
            "errors": []
        }

    def parse_folder_structure(self):
        """Parse folder structure to extract skills"""
        print("\n📂 Parsing folder structure...")

        # Find all grade folders
        for grade_folder in sorted(self.base_path.iterdir()):
            if not grade_folder.is_dir():
                continue

            # Extract grade info: "1_3rd_grade_math" -> grade="3", subject="math"
            grade_match = re.match(r'(\d+)_(\d+(?:st|nd|rd|th))_grade_(\w+)', grade_folder.name)
            if not grade_match:
                print(f"⚠️  Skipping folder with unexpected name: {grade_folder.name}")
                continue

            order_num, grade_level, subject = grade_match.groups()
            grade_num = re.search(r'\d+', grade_level).group()

            print(f"\n  Processing Grade {grade_num} ({subject})...")

            # Process each topic folder
            for topic_folder in sorted(grade_folder.iterdir()):
                if not topic_folder.is_dir():
                    continue

                self._process_topic(topic_folder, grade_num, subject)

        print(f"\n✅ Extracted {len(self.skills_map)} unique skills")

    def _process_topic(self, topic_folder: Path, grade: str, subject: str):
        """Process a topic folder to extract concepts and skills"""
        # Parse topic: "1.8_Arithmetic_patterns_and_problem_solving"
        topic_name = topic_folder.name.split('_', 1)[1].replace('_', ' ') if '_' in topic_folder.name else topic_folder.name

        # Process concept folders
        for concept_folder in sorted(topic_folder.iterdir()):
            if not concept_folder.is_dir():
                continue

            concept_name = concept_folder.name.split('_', 1)[1].replace('_', ' ') if '_' in concept_folder.name else concept_folder.name

            # Look for exercises subfolder
            exercises_folder = concept_folder / 'exercises'
            if not exercises_folder.exists():
                continue

            # Process each exercise (sub-concept)
            for exercise_folder in sorted(exercises_folder.iterdir()):
                if not exercise_folder.is_dir():
                    continue

                exercise_name = exercise_folder.name.split('_', 1)[1].replace('_', ' ') if '_' in exercise_folder.name else exercise_folder.name

                # Create skill from exercise
                skill_id = self._create_skill_id(grade, topic_name, concept_name, exercise_name)

                if skill_id not in self.skills_map:
                    self.skills_map[skill_id] = {
                        "skill_id": skill_id,
                        "name": exercise_name.title(),
                        "grade_level": f"GRADE_{grade}",
                        "topic": topic_name.title(),
                        "concept": concept_name.title(),
                        "prerequisites": [],  # Will be inferred from numbering
                        "forgetting_rate": 0.1,  # Default
                        "difficulty": 0.5  # Default
                    }

                # Process questions in items folder
                items_folder = exercise_folder / 'items'
                if items_folder.exists():
                    self._process_questions(items_folder, skill_id, grade, topic_name, concept_name, exercise_name)

    def _create_skill_id(self, grade: str, topic: str, concept: str, exercise: str) -> str:
        """Create unique skill ID from components"""
        # Simplified ID: grade_topic_concept_exercise
        parts = [grade, topic, concept, exercise]
        skill_id = '_'.join([p.lower().replace(' ', '_').replace('-', '_')[:20] for p in parts])
        return skill_id[:100]  # Limit length

    def _process_questions(self, items_folder: Path, skill_id: str, grade: str, topic: str, concept: str, exercise: str):
        """Process all question JSON files in items folder"""
        for json_file in sorted(items_folder.glob('*.json')):
            try:
                # Extract question number from filename: "1.8.1.1.1_xc86f255983d3dafe.json"
                question_breadcrumb = json_file.stem.split('_')[0]
                khan_id = json_file.stem.split('_')[1] if '_' in json_file.stem else json_file.stem

                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Navigate nested structure
                if ('data' in data and
                    'assessmentItem' in data['data'] and
                    data['data']['assessmentItem'] and
                    'item' in data['data']['assessmentItem'] and
                    data['data']['assessmentItem']['item'] and
                    'itemData' in data['data']['assessmentItem']['item']):

                    item_data_str = data['data']['assessmentItem']['item']['itemData']
                    item_data = json.loads(item_data_str)

                    # Extract question content
                    question_content = item_data.get('question', {}).get('content', '')

                    # Create question document
                    question_doc = {
                        "question_id": f"khan_{khan_id}",
                        "skill_ids": [skill_id],
                        "content": question_content,
                        "answer": "",  # Will be extracted from widgets
                        "difficulty": 0.5,  # Default
                        "question_type": "perseus",
                        "options": [],
                        "explanation": "",
                        "tags": [grade, topic, concept, exercise],
                        "metadata": {
                            "question_number_breadcrumb": question_breadcrumb,
                            "grade": grade,
                            "skill": exercise,
                            "topic": topic,
                            "concept": concept,
                            "sub_concept": exercise,
                            "khan_id": khan_id,
                            "perseus_data": item_data  # Store full Perseus data
                        },
                        "source": "khan_academy",
                        "parent_question_id": None
                    }

                    self.questions_list.append(question_doc)

            except Exception as e:
                error_msg = f"Error processing {json_file.name}: {e}"
                print(f"    ❌ {error_msg}")
                self.stats["errors"].append(error_msg)

    def insert_to_mongodb(self):
        """Insert extracted skills and questions into MongoDB"""
        print(f"\n📦 Inserting data into MongoDB...")

        # Insert skills
        if self.skills_map:
            skills_list = list(self.skills_map.values())
            try:
                count = self.db.bulk_insert_skills(skills_list)
                self.stats["skills_created"] = count
                print(f"✅ Inserted {count} skills")
            except Exception as e:
                print(f"❌ Error inserting skills: {e}")
                self.stats["errors"].append(f"Skills insertion error: {e}")

        # Insert questions
        if self.questions_list:
            try:
                count = self.db.bulk_insert_questions(self.questions_list)
                self.stats["questions_migrated"] = count
                print(f"✅ Inserted {count} questions")
            except Exception as e:
                print(f"❌ Error inserting questions: {e}")
                self.stats["errors"].append(f"Questions insertion error: {e}")

    def print_summary(self):
        """Print migration summary"""
        print(f"\n" + "="*60)
        print(f"MIGRATION SUMMARY")
        print(f"="*60)
        print(f"Skills created: {self.stats['skills_created']}")
        print(f"Questions migrated: {self.stats['questions_migrated']}")
        print(f"Errors: {len(self.stats['errors'])}")

        if self.stats['errors']:
            print(f"\n⚠️  First 5 errors:")
            for error in self.stats['errors'][:5]:
                print(f"  - {error}")

        print(f"="*60)


def main():
    print("🎓 Khan Academy → MongoDB Migration")
    print("="*60)

    # Path to sample questions
    base_path = Path(__file__).parent.parent / "QuestionsBank" / "sample_questions_data"

    if not base_path.exists():
        print(f"❌ Error: sample_questions_data folder not found at {base_path}")
        return

    print(f"📂 Source: {base_path}")

    # Clear existing data (optional - comment out to append)
    print("\n⚠️  Clearing existing skills and questions from MongoDB...")
    db = get_db()
    db.skills.delete_many({})
    db.questions.delete_many({})
    print("✅ Collections cleared")

    # Run migration
    migrator = KhanAcademyMigrator(base_path)
    migrator.parse_folder_structure()
    migrator.insert_to_mongodb()
    migrator.print_summary()

    print(f"\n✨ Migration complete!")


if __name__ == "__main__":
    main()
