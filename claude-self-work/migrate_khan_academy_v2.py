"""
Enhanced Khan Academy Migration: Hierarchical Skill Structure
Creates ONE skill document per subject with full breadcrumb hierarchy
"""

import json
import os
import sys
import re
import uuid
from pathlib import Path
from typing import Dict, List
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent))
from DashSystem.mongodb_handler import get_db


def transform_itemdata(item_data: dict) -> dict:
    """Apply modifications for frontend compatibility:
       1. Add unique 'id' field to choices in radio widgets
       2. Add/append alt text for images
       3. Update versions to {major: 2, minor: 0}
    """

    def process_widgets(widgets: dict):
        for widget_key, widget in widgets.items():
            # --- Radio widget: add unique IDs to choices
            if widget.get("type") == "radio":
                choices = widget.get("options", {}).get("choices", [])
                for choice in choices:
                    if "id" not in choice:
                        choice["id"] = str(uuid.uuid4())

            # --- Image widget: ensure alt text
            if widget.get("type") == "image":
                options = widget.get("options", {})
                alt_text = options.get("alt", "").strip()
                if not alt_text:
                    options["alt"] = "alt text placeholder!"
                else:
                    if not alt_text.endswith("!"):
                        options["alt"] = alt_text + " !"

            # --- Recursively process nested widgets
            if "widgets" in widget:
                process_widgets(widget["widgets"])

            # --- Update version to {2,0}
            if "version" in widget:
                widget["version"] = {"major": 2, "minor": 0}

    # --- Process question widgets
    if "question" in item_data and "widgets" in item_data["question"]:
        process_widgets(item_data["question"]["widgets"])

    # --- Process hints widgets
    if "hints" in item_data:
        for hint in item_data["hints"]:
            if "widgets" in hint:
                process_widgets(hint["widgets"])

            # --- Also handle hint["images"]
            if "images" in hint and isinstance(hint["images"], dict):
                for k, v in hint["images"].items():
                    if isinstance(v, dict):
                        alt_text = v.get("alt", "").strip()
                        if not alt_text:
                            v["alt"] = "alt text placeholder!"
                        else:
                            if not alt_text.endswith("!"):
                                v["alt"] = alt_text + " !"

    # --- Handle top-level question images
    if "question" in item_data and "images" in item_data["question"]:
        for k, v in item_data["question"]["images"].items():
            if isinstance(v, dict):
                alt_text = v.get("alt", "").strip()
                if not alt_text:
                    v["alt"] = "alt text placeholder!"
                else:
                    if not alt_text.endswith("!"):
                        v["alt"] = alt_text + " !"

    # --- Update itemDataVersion
    if "itemDataVersion" in item_data:
        item_data["itemDataVersion"] = {"major": 2, "minor": 0}

    return item_data


class HierarchicalSkillMigrator:
    """Build hierarchical skill tree and migrate to MongoDB"""

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.db = get_db()

        # Hierarchical structure: skills_by_subject[subject][grade][topic][concept][exercise]
        self.skills_by_subject = defaultdict(lambda: {
            "subject": None,
            "subject_name": None,
            "skills": {}
        })

        self.questions_list = []
        self.stats = {
            "subjects": 0,
            "skills_created": 0,
            "questions_migrated": 0,
            "errors": []
        }

    def parse_folder_structure(self):
        """Parse Khan Academy folder structure into hierarchical skill tree"""
        print("\n📂 Parsing folder structure...")

        # Find all grade folders
        for grade_folder in sorted(self.base_path.iterdir()):
            if not grade_folder.is_dir():
                continue

            # Extract: "1_3rd_grade_math" → order=1, grade="3", subject="math"
            grade_match = re.match(r'(\d+)_(\d+)(?:st|nd|rd|th)_grade_(\w+)', grade_folder.name)
            if not grade_match:
                print(f"⚠️  Skipping unexpected folder: {grade_folder.name}")
                continue

            order_num, grade_num, subject = grade_match.groups()

            print(f"\n📚 Processing: Grade {grade_num} ({subject.title()})")

            # Initialize subject if first time seeing it
            if self.skills_by_subject[subject]["subject"] is None:
                self.skills_by_subject[subject]["subject"] = subject
                self.skills_by_subject[subject]["subject_name"] = subject.title()

            # Process topics within this grade
            self._process_grade(grade_folder, grade_num, subject)

        print(f"\n✅ Built skill trees for {len(self.skills_by_subject)} subjects")

    def _process_grade(self, grade_folder: Path, grade_num: str, subject: str):
        """Process all topics within a grade"""
        grade_skills = {}

        for topic_folder in sorted(grade_folder.iterdir()):
            if not topic_folder.is_dir():
                continue

            # Extract: "1.1_Topic_name" → topic_num="1.1", name="Topic name"
            parts = topic_folder.name.split('_', 1)
            if len(parts) < 2:
                continue

            topic_num = parts[0]
            topic_name = parts[1].replace('_', ' ').title()

            topic_skills = self._process_topic(topic_folder, grade_num, subject, topic_num, topic_name)

            if topic_skills:
                grade_skills[topic_num] = {
                    "topic_id": topic_num,
                    "topic_name": topic_name,
                    "breadcrumb": topic_num,
                    **topic_skills
                }

        # Add grade to subject's skills
        if grade_skills:
            self.skills_by_subject[subject]["skills"][grade_num] = {
                "grade_name": f"{self._ordinal(grade_num)} Grade",
                "grade_level": f"GRADE_{grade_num}",
                **grade_skills
            }

    def _process_topic(self, topic_folder: Path, grade: str, subject: str, topic_num: str, topic_name: str) -> Dict:
        """Process all concepts within a topic"""
        concept_skills = {}

        for concept_folder in sorted(topic_folder.iterdir()):
            if not concept_folder.is_dir():
                continue

            # Extract: "1.1.1_Concept_name" → concept_num="1.1.1", name="Concept name"
            parts = concept_folder.name.split('_', 1)
            if len(parts) < 2:
                continue

            concept_num = parts[0]
            concept_name = parts[1].replace('_', ' ').title()

            # Look for exercises subfolder (skip if found directly, we want what's inside)
            exercises_folder = concept_folder / 'exercises'
            if exercises_folder.exists():
                exercise_skills = self._process_exercises(exercises_folder, grade, subject, concept_num, concept_name)

                if exercise_skills:
                    # Get just the last part for dict key
                    concept_key = concept_num.split('.')[-1]
                    concept_skills[concept_key] = {
                        "concept_id": concept_num,
                        "concept_name": concept_name,
                        "breadcrumb": concept_num,
                        **exercise_skills
                    }

        return concept_skills

    def _process_exercises(self, exercises_folder: Path, grade: str, subject: str, concept_num: str, concept_name: str) -> Dict:
        """Process all exercises within a concept"""
        exercise_skills = {}

        for exercise_folder in sorted(exercises_folder.iterdir()):
            if not exercise_folder.is_dir():
                continue

            # Extract: "1.1.1.1_Exercise_name" → exercise_num="1.1.1.1", name="Exercise name"
            parts = exercise_folder.name.split('_', 1)
            if len(parts) < 2:
                continue

            exercise_num = parts[0]
            exercise_name = parts[1].replace('_', ' ').title()

            # This is a leaf skill - create skill_id
            skill_id = f"{subject}_{grade}_{exercise_num}"

            # Count questions in items folder
            items_folder = exercise_folder / 'items'
            question_count = 0
            if items_folder.exists():
                question_count = len(list(items_folder.glob('*.json')))
                # Process questions
                self._process_questions(items_folder, skill_id, grade, subject, exercise_num, exercise_name, concept_name)

            # Infer prerequisites from breadcrumb
            prerequisites = self._infer_prerequisites(exercise_num)

            # Get just the last part for dict key
            exercise_key = exercise_num.split('.')[-1]
            exercise_skills[exercise_key] = {
                "skill_id": skill_id,
                "breadcrumb": exercise_num,
                "exercise_name": exercise_name,
                "description": f"{concept_name} - {exercise_name}",
                "forgetting_rate": 0.1,
                "difficulty": 0.5,
                "prerequisites": prerequisites,
                "question_count": question_count
            }

            self.stats["skills_created"] += 1

        return exercise_skills

    def _process_questions(self, items_folder: Path, skill_id: str, grade: str, subject: str, breadcrumb: str, exercise_name: str, concept_name: str):
        """Process all question JSON files in items folder"""
        for json_file in sorted(items_folder.glob('*.json')):
            try:
                # Extract question number from filename: "1.8.1.1.1_xabc123.json"
                question_breadcrumb = json_file.stem.split('_')[0]
                khan_id = json_file.stem.split('_')[1] if '_' in json_file.stem else json_file.stem

                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Navigate nested Perseus structure
                if ('data' in data and
                    'assessmentItem' in data['data'] and
                    data['data']['assessmentItem'] and
                    'item' in data['data']['assessmentItem'] and
                    data['data']['assessmentItem']['item'] and
                    'itemData' in data['data']['assessmentItem']['item']):

                    item_data_str = data['data']['assessmentItem']['item']['itemData']
                    item_data = json.loads(item_data_str)

                    # Apply transformations for frontend compatibility
                    item_data = transform_itemdata(item_data)

                    question_content = item_data.get('question', {}).get('content', '')

                    question_doc = {
                        "question_id": f"khan_{khan_id}",
                        "skill_ids": [skill_id],
                        "content": question_content,
                        "answer": "",
                        "difficulty": 0.5,
                        "question_type": "perseus",
                        "options": [],
                        "explanation": "",
                        "tags": [grade, subject, concept_name, exercise_name],
                        "metadata": {
                            "question_number_breadcrumb": question_breadcrumb,
                            "grade": grade,
                            "subject": subject,
                            "skill": exercise_name,
                            "topic": concept_name,
                            "breadcrumb": breadcrumb,
                            "khan_id": khan_id,
                            "perseus_data": item_data
                        },
                        "source": "khan_academy",
                        "parent_question_id": None
                    }

                    self.questions_list.append(question_doc)

            except Exception as e:
                error_msg = f"Error processing {json_file.name}: {e}"
                self.stats["errors"].append(error_msg)

    def _infer_prerequisites(self, breadcrumb: str) -> List[str]:
        """
        Infer prerequisites from breadcrumb numbering

        Strategy:
        - Exercise "1.1.1.2" → prerequisite: "1.1.1.1" (previous in sequence)
        - Exercise "1.1.1.1" → NO prerequisite (first in concept, entry point)

        This ensures:
        1. Students can always start learning (first exercises have no prereqs)
        2. Sequential learning within a concept
        3. No broken prerequisite chains
        """
        parts = breadcrumb.split('.')

        if len(parts) < 2:
            return []

        # Get previous exercise in sequence
        # "1.1.1.2" → prerequisite: "1.1.1.1"
        last_num = int(parts[-1])
        if last_num > 1:
            prev_parts = parts[:-1] + [str(last_num - 1)]
            return ['.'.join(prev_parts)]

        # First exercise in concept has NO prerequisites
        # This is an entry point for students
        return []

    def _ordinal(self, n: str) -> str:
        """Convert number to ordinal (1 → 1st, 2 → 2nd, etc.)"""
        n = int(n)
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
        if 11 <= (n % 100) <= 13:
            suffix = 'th'
        return f"{n}{suffix}"

    def insert_to_mongodb(self):
        """Insert hierarchical skills and questions into MongoDB"""
        print(f"\n📦 Inserting data into MongoDB...")

        # Insert skill documents (one per subject)
        for subject, subject_data in self.skills_by_subject.items():
            try:
                self.db.skills.insert_one(subject_data)
                self.stats["subjects"] += 1
                print(f"✅ Inserted {subject} skills tree")
            except Exception as e:
                error = f"Error inserting {subject} skills: {e}"
                print(f"❌ {error}")
                self.stats["errors"].append(error)

        # Merge duplicate questions (same Khan ID in multiple grade folders)
        if self.questions_list:
            print(f"\n📋 Pre-processing {len(self.questions_list)} question entries...")

            # Group by question_id and merge skill_ids
            questions_by_id = defaultdict(lambda: {
                "skill_ids": set(),
                "data": None
            })

            for q in self.questions_list:
                qid = q["question_id"]
                # Add all skill_ids to the set
                questions_by_id[qid]["skill_ids"].update(q["skill_ids"])
                # Keep first occurrence of question data
                if not questions_by_id[qid]["data"]:
                    questions_by_id[qid]["data"] = q

            # Convert to final list with merged skill_ids
            merged_questions = []
            for qid, q_data in questions_by_id.items():
                # Update skill_ids to merged list
                q_data["data"]["skill_ids"] = sorted(list(q_data["skill_ids"]))
                merged_questions.append(q_data["data"])

            print(f"✅ Merged into {len(merged_questions)} unique questions")
            print(f"   Total skill associations: {sum(len(q['skill_ids']) for q in merged_questions)}")

            # Insert merged questions
            try:
                result = self.db.bulk_insert_questions(merged_questions)
                self.stats["questions_migrated"] = len(merged_questions)
                actual_count = self.db.questions.count_documents({})
                print(f"✅ Inserted {actual_count} questions into MongoDB")
            except Exception as e:
                error = f"Error inserting questions: {e}"
                print(f"❌ {error}")
                self.stats["errors"].append(error)

    def print_summary(self):
        """Print migration summary"""
        print(f"\n" + "="*70)
        print(f"MIGRATION SUMMARY")
        print(f"="*70)
        print(f"Subjects: {self.stats['subjects']}")
        print(f"Skills created: {self.stats['skills_created']}")
        print(f"Questions migrated: {self.stats['questions_migrated']}")
        print(f"Errors: {len(self.stats['errors'])}")

        if self.stats['errors']:
            print(f"\n⚠️  First 5 errors:")
            for error in self.stats['errors'][:5]:
                print(f"  - {error}")

        print(f"="*70)


def main():
    print("🎓 Khan Academy → MongoDB Hierarchical Migration")
    print("="*70)

    base_path = Path(__file__).parent.parent / "QuestionsBank" / "sample_questions_data"

    if not base_path.exists():
        print(f"❌ Error: sample_questions_data folder not found at {base_path}")
        return

    print(f"📂 Source: {base_path}")

    # Run migration
    migrator = HierarchicalSkillMigrator(base_path)
    migrator.parse_folder_structure()
    migrator.insert_to_mongodb()
    migrator.print_summary()

    print(f"\n✨ Migration complete!")


if __name__ == "__main__":
    main()
