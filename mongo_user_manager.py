"""
MongoDB User Manager

Manages user profiles in MongoDB instead of local JSON files.
"""
import time
from typing import Dict, List, Optional
from dataclasses import asdict
from db_config import mongodb
from user_manager import UserProfile, QuestionAttempt, SkillState

class MongoUserManager:
    """Manages user profiles in MongoDB"""

    def __init__(self):
        self.db = mongodb.db
        self.users_collection = self.db['users'] if self.db else None

    def is_mongodb_available(self) -> bool:
        """Check if MongoDB is available"""
        return mongodb.is_connected()

    def user_exists(self, user_id: str) -> bool:
        """Check if a user exists in MongoDB"""
        if not self.is_mongodb_available():
            return False

        try:
            return self.users_collection.find_one({'_id': user_id}) is not None
        except Exception as e:
            print(f"❌ Error checking user existence: {e}")
            return False

    def create_new_user(self, user_id: str, all_skill_ids: List[str]) -> UserProfile:
        """Create a new user in MongoDB"""
        if not self.is_mongodb_available():
            raise Exception("MongoDB not available")

        current_time = time.time()

        # Initialize all skills with default states
        skill_states = {}
        for skill_id in all_skill_ids:
            skill_states[skill_id] = SkillState(
                memory_strength=0.0,
                last_practice_time=None,
                practice_count=0,
                correct_count=0
            )

        user_profile = UserProfile(
            user_id=user_id,
            created_at=current_time,
            last_updated=current_time,
            skill_states=skill_states,
            question_history=[],
            student_notes={}
        )

        try:
            # Convert to MongoDB document
            user_doc = {
                '_id': user_id,
                'user_id': user_id,
                'created_at': current_time,
                'last_updated': current_time,
                'skill_states': {k: v.to_dict() for k, v in skill_states.items()},
                'question_history': [],
                'student_notes': {}
            }

            self.users_collection.insert_one(user_doc)
            print(f"👤 Created new user in MongoDB: {user_id}")

            return user_profile

        except Exception as e:
            print(f"❌ Error creating user in MongoDB: {e}")
            raise

    def load_user(self, user_id: str) -> Optional[UserProfile]:
        """Load a user profile from MongoDB"""
        if not self.is_mongodb_available():
            return None

        try:
            user_doc = self.users_collection.find_one({'_id': user_id})

            if not user_doc:
                return None

            # Convert MongoDB document to UserProfile
            skill_states = {
                k: SkillState.from_dict(v)
                for k, v in user_doc['skill_states'].items()
            }

            question_history = [
                QuestionAttempt(**attempt)
                for attempt in user_doc['question_history']
            ]

            user_profile = UserProfile(
                user_id=user_doc['user_id'],
                created_at=user_doc['created_at'],
                last_updated=user_doc['last_updated'],
                skill_states=skill_states,
                question_history=question_history,
                student_notes=user_doc.get('student_notes', {})
            )

            print(f"📂 Loaded user from MongoDB: {user_id}")
            return user_profile

        except Exception as e:
            print(f"❌ Error loading user from MongoDB: {e}")
            return None

    def save_user(self, user_profile: UserProfile):
        """Save a user profile to MongoDB"""
        if not self.is_mongodb_available():
            raise Exception("MongoDB not available")

        user_profile.last_updated = time.time()

        try:
            user_doc = {
                '_id': user_profile.user_id,
                'user_id': user_profile.user_id,
                'created_at': user_profile.created_at,
                'last_updated': user_profile.last_updated,
                'skill_states': {k: v.to_dict() for k, v in user_profile.skill_states.items()},
                'question_history': [asdict(attempt) for attempt in user_profile.question_history],
                'student_notes': user_profile.student_notes
            }

            self.users_collection.replace_one(
                {'_id': user_profile.user_id},
                user_doc,
                upsert=True
            )

            print(f"💾 Saved user to MongoDB: {user_profile.user_id}")

        except Exception as e:
            print(f"❌ Error saving user to MongoDB: {e}")
            raise

    def get_or_create_user(self, user_id: str, all_skill_ids: List[str]) -> UserProfile:
        """Get existing user or create new one if doesn't exist"""
        user_profile = self.load_user(user_id)

        if user_profile is None:
            user_profile = self.create_new_user(user_id, all_skill_ids)
        else:
            # Check if any new skills need to be added
            missing_skills = set(all_skill_ids) - set(user_profile.skill_states.keys())
            if missing_skills:
                for skill_id in missing_skills:
                    user_profile.skill_states[skill_id] = SkillState(
                        memory_strength=0.0,
                        last_practice_time=None,
                        practice_count=0,
                        correct_count=0
                    )
                print(f"➕ Added {len(missing_skills)} new skills to user {user_id}")
                self.save_user(user_profile)

        return user_profile

    def add_question_attempt(self, user_profile: UserProfile, question_id: str,
                           skill_ids: List[str], is_correct: bool,
                           response_time_seconds: float, time_penalty_applied: bool = False):
        """Add a question attempt to user's history"""
        attempt = QuestionAttempt(
            question_id=question_id,
            skill_ids=skill_ids,
            is_correct=is_correct,
            response_time_seconds=response_time_seconds,
            timestamp=time.time(),
            time_penalty_applied=time_penalty_applied
        )

        user_profile.question_history.append(attempt)
        self.save_user(user_profile)

    def get_user_stats(self, user_profile: UserProfile) -> Dict:
        """Get summary statistics for a user"""
        total_questions = len(user_profile.question_history)
        correct_answers = sum(1 for attempt in user_profile.question_history if attempt.is_correct)

        if total_questions == 0:
            return {
                'total_questions': 0,
                'correct_answers': 0,
                'accuracy': 0.0,
                'avg_response_time': 0.0,
                'time_penalties': 0,
                'skills_practiced': 0
            }

        avg_response_time = sum(attempt.response_time_seconds for attempt in user_profile.question_history) / total_questions
        time_penalties = sum(1 for attempt in user_profile.question_history if attempt.time_penalty_applied)
        skills_practiced = len([skill_id for skill_id, state in user_profile.skill_states.items() if state.practice_count > 0])

        return {
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'accuracy': correct_answers / total_questions,
            'avg_response_time': avg_response_time,
            'time_penalties': time_penalties,
            'skills_practiced': skills_practiced
        }

    def list_all_users(self) -> List[str]:
        """Get list of all user IDs from MongoDB"""
        if not self.is_mongodb_available():
            return []

        try:
            users = self.users_collection.find({}, {'_id': 1})
            return [user['_id'] for user in users]
        except Exception as e:
            print(f"❌ Error listing users: {e}")
            return []

# Global instance
mongo_user_manager = MongoUserManager()
