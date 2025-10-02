"""
Data Migration Script: JSON files → MongoDB
Migrates skills, questions, and users from JSON format to MongoDB
"""

import json
import os
from typing import Dict, List
from mongodb_handler import MongoDBHandler

class DataMigrator:
    """Handles migration of data from JSON files to MongoDB"""
    
    def __init__(self, mongodb_handler: MongoDBHandler):
        self.db = mongodb_handler
        self.stats = {
            "skills_migrated": 0,
            "questions_migrated": 0,
            "users_migrated": 0,
            "errors": []
        }
    
    def migrate_skills(self, skills_file_path: str = "QuestionsBank/skills.json") -> bool:
        """Migrate skills from JSON to MongoDB"""
        print(f"\n📦 Migrating skills from {skills_file_path}...")
        
        try:
            with open(skills_file_path, 'r') as f:
                skills_data = json.load(f)
            
            skills_list = []
            for skill_id, skill_info in skills_data.items():
                skill_doc = {
                    "skill_id": skill_info["skill_id"],
                    "name": skill_info["name"],
                    "grade_level": skill_info["grade_level"],
                    "prerequisites": skill_info.get("prerequisites", []),
                    "forgetting_rate": skill_info.get("forgetting_rate", 0.1),
                    "difficulty": skill_info.get("difficulty", 0.0)
                }
                skills_list.append(skill_doc)
            
            count = self.db.bulk_insert_skills(skills_list)
            self.stats["skills_migrated"] = count
            print(f"✅ Migrated {count} skills")
            return True
            
        except FileNotFoundError:
            error = f"Skills file not found: {skills_file_path}"
            print(f"❌ {error}")
            self.stats["errors"].append(error)
            return False
        except Exception as e:
            error = f"Error migrating skills: {e}"
            print(f"❌ {error}")
            self.stats["errors"].append(error)
            return False
    
    def migrate_questions(self, curriculum_file_path: str = "QuestionsBank/curriculum.json") -> bool:
        """Migrate questions from curriculum JSON to MongoDB"""
        print(f"\n📦 Migrating questions from {curriculum_file_path}...")
        
        try:
            with open(curriculum_file_path, 'r') as f:
                curriculum_data = json.load(f)
            
            questions_list = []
            
            # Navigate the nested structure: grades -> skills -> questions
            for grade_key, grade_data in curriculum_data.get("grades", {}).items():
                for skill_data in grade_data.get("skills", []):
                    skill_id = skill_data.get("skill_id")
                    
                    for question_data in skill_data.get("questions", []):
                        question_doc = {
                            "question_id": question_data["question_id"],
                            "skill_ids": [skill_id],  # Single skill for now
                            "content": question_data.get("content", ""),
                            "answer": question_data.get("answer", ""),
                            "difficulty": question_data.get("difficulty", 0.0),
                            "question_type": question_data.get("question_type", "open_ended"),
                            "options": question_data.get("options", []),
                            "explanation": question_data.get("explanation", ""),
                            "tags": question_data.get("tags", []),
                            "source": "curriculum",
                            "parent_question_id": None
                        }
                        questions_list.append(question_doc)
            
            count = self.db.bulk_insert_questions(questions_list)
            self.stats["questions_migrated"] = count
            print(f"✅ Migrated {count} questions")
            return True
            
        except FileNotFoundError:
            error = f"Curriculum file not found: {curriculum_file_path}"
            print(f"❌ {error}")
            self.stats["errors"].append(error)
            return False
        except Exception as e:
            error = f"Error migrating questions: {e}"
            print(f"❌ {error}")
            self.stats["errors"].append(error)
            return False
    
    def migrate_users(self, users_folder: str = "Users") -> bool:
        """Migrate user profiles from JSON files to MongoDB"""
        print(f"\n📦 Migrating users from {users_folder}/...")
        
        try:
            if not os.path.exists(users_folder):
                print(f"⚠️  Users folder not found: {users_folder}")
                return True  # Not an error, just no users to migrate
            
            user_files = [f for f in os.listdir(users_folder) if f.endswith('.json')]
            
            if not user_files:
                print("ℹ️  No user files to migrate")
                return True
            
            migrated_count = 0
            
            for user_file in user_files:
                user_path = os.path.join(users_folder, user_file)
                
                try:
                    with open(user_path, 'r') as f:
                        user_data = json.load(f)
                    
                    # Transform skill_states format
                    skill_states = {}
                    for skill_id, state_data in user_data.get("skill_states", {}).items():
                        skill_states[skill_id] = {
                            "memory_strength": state_data.get("memory_strength", 0.0),
                            "last_practice_time": state_data.get("last_practice_time"),
                            "practice_count": state_data.get("practice_count", 0),
                            "correct_count": state_data.get("correct_count", 0),
                            "last_updated": None  # Will be set during first update
                        }
                    
                    # Transform question_history format
                    question_history = []
                    for attempt in user_data.get("question_history", []):
                        question_history.append({
                            "question_id": attempt["question_id"],
                            "skill_ids": attempt.get("skill_ids", []),
                            "is_correct": attempt.get("is_correct", False),
                            "response_time_seconds": attempt.get("response_time_seconds", 0.0),
                            "time_penalty_applied": attempt.get("time_penalty_applied", False),
                            # timestamp will be added by MongoDB handler
                        })
                    
                    # Create user document
                    user_doc = {
                        "user_id": user_data["user_id"],
                        "created_at": user_data.get("created_at"),
                        "last_updated": user_data.get("last_updated"),
                        "age": user_data.get("age"),
                        "grade_level": user_data.get("grade_level"),
                        "skill_states": skill_states,
                        "question_history": question_history,
                        "student_notes": user_data.get("student_notes", {})
                    }
                    
                    # Insert into MongoDB
                    self.db.users.insert_one(user_doc)
                    migrated_count += 1
                    print(f"✅ Migrated user: {user_data['user_id']}")
                    
                except Exception as e:
                    error = f"Error migrating user from {user_file}: {e}"
                    print(f"❌ {error}")
                    self.stats["errors"].append(error)
                    continue
            
            self.stats["users_migrated"] = migrated_count
            print(f"✅ Migrated {migrated_count} users")
            return True
            
        except Exception as e:
            error = f"Error accessing users folder: {e}"
            print(f"❌ {error}")
            self.stats["errors"].append(error)
            return False
    
    def verify_migration(self) -> bool:
        """Verify the migration was successful"""
        print("\n🔍 Verifying migration...")
        
        stats = self.db.get_database_stats()
        
        print(f"   Skills in MongoDB: {stats['skills']}")
        print(f"   Questions in MongoDB: {stats['questions']}")
        print(f"   Users in MongoDB: {stats['users']}")
        
        all_good = True
        
        if stats['skills'] == 0:
            print("⚠️  Warning: No skills found in MongoDB")
            all_good = False
        
        if stats['questions'] == 0:
            print("⚠️  Warning: No questions found in MongoDB")
            all_good = False
        
        if self.stats["errors"]:
            print(f"\n❌ Migration completed with {len(self.stats['errors'])} errors:")
            for error in self.stats["errors"]:
                print(f"   - {error}")
            all_good = False
        
        if all_good:
            print("✅ Migration verification passed!")
        
        return all_good
    
    def print_summary(self):
        """Print migration summary"""
        print("\n" + "=" * 50)
        print("MIGRATION SUMMARY")
        print("=" * 50)
        print(f"Skills migrated:    {self.stats['skills_migrated']}")
        print(f"Questions migrated: {self.stats['questions_migrated']}")
        print(f"Users migrated:     {self.stats['users_migrated']}")
        print(f"Errors encountered: {len(self.stats['errors'])}")
        print("=" * 50)


def run_migration(
    clear_existing: bool = False,
    skills_file: str = "QuestionsBank/skills.json",
    curriculum_file: str = "QuestionsBank/curriculum.json",
    users_folder: str = "Users"
):
    """
    Run the complete migration process
    
    Args:
        clear_existing: If True, clear existing MongoDB data before migration
        skills_file: Path to skills.json
        curriculum_file: Path to curriculum.json
        users_folder: Path to Users folder
    """
    print("=" * 50)
    print("DATA MIGRATION: JSON → MongoDB")
    print("=" * 50)
    
    # Initialize MongoDB handler
    db = MongoDBHandler()
    
    # Clear existing data if requested
    if clear_existing:
        print("\n⚠️  Clearing existing MongoDB data...")
        response = input("Are you sure? This cannot be undone! (yes/no): ")
        if response.lower() == "yes":
            db.clear_all_collections()
        else:
            print("❌ Migration cancelled")
            return
    
    # Create migrator and run migration
    migrator = DataMigrator(db)
    
    # Migrate in order: skills → questions → users
    success = True
    success = migrator.migrate_skills(skills_file) and success
    success = migrator.migrate_questions(curriculum_file) and success
    success = migrator.migrate_users(users_folder) and success
    
    # Verify migration
    success = migrator.verify_migration() and success
    
    # Print summary
    migrator.print_summary()
    
    # Close connection
    db.close()
    
    if success:
        print("\n🎉 Migration completed successfully!")
    else:
        print("\n⚠️  Migration completed with errors. Please review the output above.")
    
    return success


if __name__ == "__main__":
    import sys
    
    # Check for --clear flag
    clear_existing = "--clear" in sys.argv
    
    if clear_existing:
        print("⚠️  Running with --clear flag: existing data will be deleted!")
    
    run_migration(clear_existing=clear_existing)
