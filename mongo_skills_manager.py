"""
MongoDB Skills Template Manager

Manages the master skills template in MongoDB and creates per-student skill documents.
"""
import json
from typing import Dict, List, Optional
from db_config import mongodb

class MongoSkillsManager:
    """Manages skills template in MongoDB"""

    def __init__(self):
        self.db = mongodb.db
        self.skills_collection = self.db['skills_template'] if self.db else None
        self.student_skills_collection = self.db['student_skills'] if self.db else None

    def is_mongodb_available(self) -> bool:
        """Check if MongoDB is available"""
        return mongodb.is_connected()

    def initialize_skills_template_from_json(self, skills_json_path: str) -> bool:
        """
        Initialize the skills template collection from a JSON file.
        This should be run once to migrate from JSON to MongoDB.

        Args:
            skills_json_path: Path to skills.json file

        Returns:
            True if successful, False otherwise
        """
        if not self.is_mongodb_available():
            print("❌ MongoDB not available, cannot initialize skills template")
            return False

        try:
            with open(skills_json_path, 'r') as f:
                skills_data = json.load(f)

            # Clear existing template (if any)
            self.skills_collection.delete_many({})

            # Insert skills as individual documents
            skills_documents = []
            for skill_id, skill_data in skills_data.items():
                skill_doc = {
                    '_id': skill_id,  # Use skill_id as MongoDB _id
                    'skill_id': skill_data['skill_id'],
                    'name': skill_data['name'],
                    'grade_level': skill_data['grade_level'],
                    'prerequisites': skill_data['prerequisites'],
                    'forgetting_rate': skill_data['forgetting_rate'],
                    'difficulty': skill_data['difficulty']
                }
                skills_documents.append(skill_doc)

            if skills_documents:
                result = self.skills_collection.insert_many(skills_documents)
                print(f"✅ Initialized skills template with {len(result.inserted_ids)} skills")
                return True
            else:
                print("⚠️  No skills found in JSON file")
                return False

        except FileNotFoundError:
            print(f"❌ Skills JSON file not found: {skills_json_path}")
            return False
        except Exception as e:
            print(f"❌ Error initializing skills template: {e}")
            return False

    def get_all_skills(self) -> Dict[str, Dict]:
        """
        Get all skills from the template.

        Returns:
            Dictionary of skills (skill_id -> skill_data)
        """
        if not self.is_mongodb_available():
            return {}

        try:
            skills = {}
            for skill_doc in self.skills_collection.find():
                skill_id = skill_doc['skill_id']
                skills[skill_id] = {
                    'skill_id': skill_doc['skill_id'],
                    'name': skill_doc['name'],
                    'grade_level': skill_doc['grade_level'],
                    'prerequisites': skill_doc['prerequisites'],
                    'forgetting_rate': skill_doc['forgetting_rate'],
                    'difficulty': skill_doc['difficulty']
                }

            return skills

        except Exception as e:
            print(f"❌ Error loading skills from MongoDB: {e}")
            return {}

    def get_skill(self, skill_id: str) -> Optional[Dict]:
        """Get a single skill by ID"""
        if not self.is_mongodb_available():
            return None

        try:
            return self.skills_collection.find_one({'_id': skill_id})
        except Exception as e:
            print(f"❌ Error loading skill {skill_id}: {e}")
            return None

    def create_student_skills(self, student_id: str, grade_level: Optional[str] = None) -> bool:
        """
        Create a student's skill document based on the template.

        Args:
            student_id: Student identifier
            grade_level: Starting grade level (e.g., "GRADE_5")

        Returns:
            True if successful
        """
        if not self.is_mongodb_available():
            return False

        try:
            # Check if student skills already exist
            existing = self.student_skills_collection.find_one({'_id': student_id})
            if existing:
                print(f"⚠️  Student skills already exist for {student_id}")
                return True

            # Get all skills from template
            all_skills = self.get_all_skills()

            # Initialize student skill states
            skill_states = {}
            for skill_id, skill_data in all_skills.items():
                # Default: all skills start at 0
                skill_states[skill_id] = {
                    'memory_strength': 0.0,
                    'last_practice_time': None,
                    'practice_count': 0,
                    'correct_count': 0
                }

                # If grade_level provided, mark lower-grade skills as mastered
                if grade_level:
                    skill_grade_value = self._grade_to_value(skill_data['grade_level'])
                    student_grade_value = self._grade_to_value(grade_level)

                    if skill_grade_value < student_grade_value:
                        skill_states[skill_id]['memory_strength'] = 3.0

            # Create student skills document
            student_doc = {
                '_id': student_id,
                'student_id': student_id,
                'grade_level': grade_level,
                'skill_states': skill_states,
                'created_at': None,  # Will be set by user_manager
                'last_updated': None
            }

            self.student_skills_collection.insert_one(student_doc)
            print(f"✅ Created skill states for student: {student_id}")
            return True

        except Exception as e:
            print(f"❌ Error creating student skills: {e}")
            return False

    def get_student_skills(self, student_id: str) -> Optional[Dict]:
        """Get a student's skill states"""
        if not self.is_mongodb_available():
            return None

        try:
            return self.student_skills_collection.find_one({'_id': student_id})
        except Exception as e:
            print(f"❌ Error loading student skills: {e}")
            return None

    def update_student_skill(self, student_id: str, skill_id: str, skill_state: Dict) -> bool:
        """Update a single skill state for a student"""
        if not self.is_mongodb_available():
            return False

        try:
            result = self.student_skills_collection.update_one(
                {'_id': student_id},
                {'$set': {f'skill_states.{skill_id}': skill_state}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"❌ Error updating student skill: {e}")
            return False

    def _grade_to_value(self, grade_str: str) -> int:
        """Convert grade string to numeric value"""
        grade_map = {
            'K': 0, 'GRADE_1': 1, 'GRADE_2': 2, 'GRADE_3': 3,
            'GRADE_4': 4, 'GRADE_5': 5, 'GRADE_6': 6, 'GRADE_7': 7,
            'GRADE_8': 8, 'GRADE_9': 9, 'GRADE_10': 10, 'GRADE_11': 11,
            'GRADE_12': 12
        }
        return grade_map.get(grade_str, 0)

# Global instance
mongo_skills = MongoSkillsManager()
