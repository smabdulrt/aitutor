"""
MongoDB Database Models and Connection Handler for DashSystem v2
"""

import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.collection import Collection
from pymongo.database import Database
from dataclasses import dataclass, asdict
import time

class MongoDBHandler:
    """Handles MongoDB connection and operations for DashSystem"""
    
    def __init__(self, connection_string: Optional[str] = None, database_name: str = "aitutor_db"):
        """
        Initialize MongoDB connection
        
        Args:
            connection_string: MongoDB connection string (default: from env or localhost)
            database_name: Name of the database to use
        """
        if connection_string is None:
            connection_string = os.getenv(
                "MONGODB_URI",
                "mongodb://localhost:27017/"
            )
        
        self.client = MongoClient(connection_string)
        self.db: Database = self.client[database_name]
        
        # Collections
        self.skills: Collection = self.db["skills"]
        self.questions: Collection = self.db["questions"]
        self.users: Collection = self.db["users"]
        
        # Ensure indexes are created
        self._create_indexes()
        
        print(f"✅ Connected to MongoDB database: {database_name}")
    
    def _create_indexes(self):
        """Create all necessary indexes for performance"""
        
        # Skills indexes
        self.skills.create_index([("skill_id", ASCENDING)], unique=True)
        self.skills.create_index([("grade_level", ASCENDING)])
        self.skills.create_index([("prerequisites", ASCENDING)])
        
        # Questions indexes
        self.questions.create_index([("question_id", ASCENDING)], unique=True)
        self.questions.create_index([("skill_ids", ASCENDING)])
        self.questions.create_index([("tags", ASCENDING)])
        self.questions.create_index([
            ("skill_ids", ASCENDING),
            ("times_shown", ASCENDING)
        ])
        
        # Users indexes
        self.users.create_index([("user_id", ASCENDING)], unique=True)
        self.users.create_index([("grade_level", ASCENDING)])
        self.users.create_index([("skill_states.last_practice_time", ASCENDING)])
        
        print("✅ MongoDB indexes created")
    
    def close(self):
        """Close MongoDB connection"""
        self.client.close()
        print("🔌 MongoDB connection closed")
    
    # === SKILLS OPERATIONS ===
    
    def insert_skill(self, skill_data: Dict) -> bool:
        """Insert a single skill"""
        try:
            skill_data["created_at"] = datetime.utcnow()
            skill_data["updated_at"] = datetime.utcnow()
            self.skills.insert_one(skill_data)
            return True
        except Exception as e:
            print(f"❌ Error inserting skill: {e}")
            return False
    
    def bulk_insert_skills(self, skills_list: List[Dict]) -> int:
        """Bulk insert multiple skills"""
        try:
            now = datetime.utcnow()
            for skill in skills_list:
                skill["created_at"] = now
                skill["updated_at"] = now
            
            result = self.skills.insert_many(skills_list, ordered=False)
            return len(result.inserted_ids)
        except Exception as e:
            print(f"❌ Error bulk inserting skills: {e}")
            return 0
    
    def get_all_skills(self) -> List[Dict]:
        """Get all skills for SKILLS_CACHE"""
        return list(self.skills.find({}))
    
    def get_skill_by_id(self, skill_id: str) -> Optional[Dict]:
        """Get a single skill by ID"""
        return self.skills.find_one({"skill_id": skill_id})
    
    # === QUESTIONS OPERATIONS ===
    
    def insert_question(self, question_data: Dict) -> bool:
        """Insert a single question"""
        try:
            question_data["created_at"] = datetime.utcnow()
            question_data["updated_at"] = datetime.utcnow()
            question_data["times_shown"] = question_data.get("times_shown", 0)
            question_data["avg_correctness"] = question_data.get("avg_correctness", 0.0)
            
            self.questions.insert_one(question_data)
            return True
        except Exception as e:
            print(f"❌ Error inserting question: {e}")
            return False
    
    def bulk_insert_questions(self, questions_list: List[Dict]) -> int:
        """Bulk insert multiple questions"""
        try:
            now = datetime.utcnow()
            for question in questions_list:
                question["created_at"] = now
                question["updated_at"] = now
                question["times_shown"] = question.get("times_shown", 0)
                question["avg_correctness"] = question.get("avg_correctness", 0.0)
            
            result = self.questions.insert_many(questions_list, ordered=False)
            return len(result.inserted_ids)
        except Exception as e:
            print(f"❌ Error bulk inserting questions: {e}")
            return 0
    
    def find_unanswered_question(
        self, 
        skill_ids: List[str], 
        answered_question_ids: List[str],
        max_times_shown: int = 100
    ) -> Optional[Dict]:
        """
        Find an unanswered question for given skills
        
        Prioritizes questions that:
        1. Haven't been answered by this user
        2. Test the required skills
        3. Haven't been shown too many times
        4. Are shown least frequently overall
        """
        query = {
            "skill_ids": {"$in": skill_ids},
            "question_id": {"$nin": answered_question_ids},
            "times_shown": {"$lt": max_times_shown}
        }
        
        # Sort by times_shown (ascending) to prefer fresh questions
        result = self.questions.find_one(
            query,
            sort=[("times_shown", ASCENDING)]
        )
        
        # Increment times_shown counter
        if result:
            self.questions.update_one(
                {"_id": result["_id"]},
                {"$inc": {"times_shown": 1}}
            )
        
        return result
    
    def get_all_questions_for_skill(self, skill_id: str) -> List[Dict]:
        """Get all questions testing a specific skill"""
        return list(self.questions.find({"skill_ids": skill_id}))
    
    def update_question_tags(self, question_id: str, tags: List[str]) -> bool:
        """Update tags for a question (LLM-generated)"""
        try:
            result = self.questions.update_one(
                {"question_id": question_id},
                {
                    "$set": {
                        "tags": tags,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"❌ Error updating question tags: {e}")
            return False
    
    # === USER OPERATIONS ===
    
    def create_user(
        self, 
        user_id: str, 
        all_skill_ids: List[str],
        age: Optional[int] = None,
        grade_level: Optional[str] = None
    ) -> bool:
        """
        Create a new user with initialized skill states
        
        Implements cold start strategy:
        - Skills below user's grade: memory_strength = 0.8
        - Skills at user's grade: memory_strength = 0.0
        - Skills above user's grade: memory_strength = 0.0
        """
        try:
            now = datetime.utcnow()
            
            # Initialize skill states
            skill_states = {}
            for skill_id in all_skill_ids:
                skill_states[skill_id] = {
                    "memory_strength": 0.0,  # Will be adjusted by cold start logic
                    "last_practice_time": None,
                    "practice_count": 0,
                    "correct_count": 0,
                    "last_updated": now
                }
            
            user_doc = {
                "user_id": user_id,
                "created_at": now,
                "last_updated": now,
                "age": age,
                "grade_level": grade_level,
                "skill_states": skill_states,
                "question_history": [],
                "student_notes": {}
            }
            
            self.users.insert_one(user_doc)
            print(f"👤 Created new user: {user_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating user: {e}")
            return False
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user profile with all skill states"""
        return self.users.find_one({"user_id": user_id})
    
    def user_exists(self, user_id: str) -> bool:
        """Check if user exists"""
        return self.users.count_documents({"user_id": user_id}, limit=1) > 0
    
    def update_skill_state(
        self,
        user_id: str,
        skill_id: str,
        memory_strength: float,
        is_correct: bool,
        question_attempt: Dict
    ) -> bool:
        """
        Atomically update a skill state and add question attempt
        
        This is the critical atomic operation that ensures consistency
        """
        try:
            now = datetime.utcnow()
            
            update_query = {
                "$set": {
                    f"skill_states.{skill_id}.memory_strength": memory_strength,
                    f"skill_states.{skill_id}.last_practice_time": now,
                    f"skill_states.{skill_id}.last_updated": now,
                    "last_updated": now
                },
                "$inc": {
                    f"skill_states.{skill_id}.practice_count": 1
                }
            }
            
            # Only increment correct_count if answer was correct
            if is_correct:
                update_query["$inc"][f"skill_states.{skill_id}.correct_count"] = 1
            
            # Add question attempt to history (keep last 1000)
            question_attempt["timestamp"] = now
            update_query["$push"] = {
                "question_history": {
                    "$each": [question_attempt],
                    "$slice": -1000  # Keep last 1000 attempts
                }
            }
            
            result = self.users.update_one(
                {"user_id": user_id},
                update_query
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"❌ Error updating skill state: {e}")
            return False
    
    def bulk_update_skill_states(
        self,
        user_id: str,
        skill_updates: Dict[str, float],  # skill_id -> new_memory_strength
        question_attempt: Dict
    ) -> bool:
        """
        Update multiple skills at once (for prerequisite updates)
        This handles the cascading updates when a question affects multiple skills
        """
        try:
            now = datetime.utcnow()
            
            # Build update operations
            set_operations = {}
            inc_operations = {}
            
            for skill_id, memory_strength in skill_updates.items():
                set_operations[f"skill_states.{skill_id}.memory_strength"] = memory_strength
                set_operations[f"skill_states.{skill_id}.last_practice_time"] = now
                set_operations[f"skill_states.{skill_id}.last_updated"] = now
                inc_operations[f"skill_states.{skill_id}.practice_count"] = 1
                
                # Increment correct count only for directly tested skills
                if skill_id in question_attempt.get("skill_ids", []):
                    if question_attempt.get("is_correct", False):
                        inc_operations[f"skill_states.{skill_id}.correct_count"] = 1
            
            set_operations["last_updated"] = now
            
            # Add question to history
            question_attempt["timestamp"] = now
            
            update_query = {
                "$set": set_operations,
                "$inc": inc_operations,
                "$push": {
                    "question_history": {
                        "$each": [question_attempt],
                        "$slice": -1000
                    }
                }
            }
            
            result = self.users.update_one(
                {"user_id": user_id},
                update_query
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"❌ Error bulk updating skill states: {e}")
            return False
    
    def get_answered_question_ids(self, user_id: str) -> List[str]:
        """Get list of all question IDs the user has answered"""
        user = self.users.find_one(
            {"user_id": user_id},
            {"question_history.question_id": 1}
        )
        
        if not user or "question_history" not in user:
            return []
        
        return [attempt["question_id"] for attempt in user["question_history"]]
    
    def get_user_skill_state(self, user_id: str, skill_id: str) -> Optional[Dict]:
        """Get a single skill state for a user"""
        user = self.users.find_one(
            {"user_id": user_id},
            {f"skill_states.{skill_id}": 1}
        )
        
        if not user or "skill_states" not in user:
            return None
        
        return user["skill_states"].get(skill_id)
    
    # === UTILITY OPERATIONS ===
    
    def get_database_stats(self) -> Dict[str, int]:
        """Get counts of documents in each collection"""
        return {
            "skills": self.skills.count_documents({}),
            "questions": self.questions.count_documents({}),
            "users": self.users.count_documents({})
        }
    
    def clear_all_collections(self):
        """DANGEROUS: Clear all collections - use only for testing"""
        self.skills.delete_many({})
        self.questions.delete_many({})
        self.users.delete_many({})
        print("⚠️  All collections cleared")


# Global singleton instance
_db_handler: Optional[MongoDBHandler] = None

def get_db() -> MongoDBHandler:
    """Get or create MongoDB handler singleton"""
    global _db_handler
    if _db_handler is None:
        _db_handler = MongoDBHandler()
    return _db_handler

def close_db():
    """Close MongoDB connection"""
    global _db_handler
    if _db_handler is not None:
        _db_handler.close()
        _db_handler = None
