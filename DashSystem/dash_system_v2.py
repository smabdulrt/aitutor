"""
DashSystem V2 - MongoDB-powered Intelligent Learning System
Implements DASH (Deep Additive State History) algorithm with MongoDB backend
"""

import math
import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from DashSystem.mongodb_handler import MongoDBHandler, get_db
from LLMBase.llm_client import LLMClient

class GradeLevel(Enum):
    """Grade level enumeration"""
    K = 0
    GRADE_1 = 1
    GRADE_2 = 2
    GRADE_3 = 3
    GRADE_4 = 4
    GRADE_5 = 5
    GRADE_6 = 6
    GRADE_7 = 7
    GRADE_8 = 8
    GRADE_9 = 9
    GRADE_10 = 10
    GRADE_11 = 11
    GRADE_12 = 12

@dataclass
class Skill:
    """Skill representation matching MongoDB schema"""
    skill_id: str
    name: str
    grade_level: GradeLevel
    prerequisites: List[str]
    forgetting_rate: float
    difficulty: float

@dataclass
class Question:
    """Question representation matching MongoDB schema"""
    question_id: str
    skill_ids: List[str]
    content: str
    answer: str
    difficulty: float
    question_type: str
    options: List[str]
    explanation: str
    tags: List[str]

class DashSystemV2:
    """
    MongoDB-powered Intelligent Learning System
    
    Features:
    - In-memory SKILLS_CACHE for fast lookups
    - Intelligent question selection algorithm
    - Atomic MongoDB updates for consistency
    - Real-time memory strength calculation with forgetting
    - Prerequisite cascading
    - LLM-powered question tagging
    """
    
    def __init__(self, db_handler: Optional[MongoDBHandler] = None):
        """
        Initialize DashSystem V2
        
        Args:
            db_handler: Optional MongoDB handler (creates new if None)
        """
        self.db = db_handler if db_handler else get_db()
        
        # In-memory cache of all skills for fast access
        self.SKILLS_CACHE: Dict[str, Skill] = {}
        
        # Initialize LLM client for question tagging
        try:
            self.llm_client = LLMClient()
            print("✅ LLM Client initialized for question tagging")
        except Exception as e:
            self.llm_client = None
            print(f"⚠️  LLM Client not available: {e}")
        
        # Load all skills into memory
        self._load_skills_cache()
        
        print("✅ DashSystem V2 initialized with MongoDB backend")
    
    def _load_skills_cache(self):
        """Load all skills from MongoDB into memory for fast access"""
        print("📚 Loading skills into SKILLS_CACHE...")
        
        skills_docs = self.db.get_all_skills()
        
        for skill_doc in skills_docs:
            try:
                grade_level = GradeLevel[skill_doc["grade_level"]]
                skill = Skill(
                    skill_id=skill_doc["skill_id"],
                    name=skill_doc["name"],
                    grade_level=grade_level,
                    prerequisites=skill_doc.get("prerequisites", []),
                    forgetting_rate=skill_doc.get("forgetting_rate", 0.1),
                    difficulty=skill_doc.get("difficulty", 0.0)
                )
                self.SKILLS_CACHE[skill.skill_id] = skill
            except Exception as e:
                print(f"⚠️  Error loading skill {skill_doc.get('skill_id', 'unknown')}: {e}")
        
        print(f"✅ Loaded {len(self.SKILLS_CACHE)} skills into SKILLS_CACHE")
    
    def get_or_create_user(self, user_id: str, age: Optional[int] = None, 
                           grade_level: Optional[str] = None) -> Dict:
        """
        Get existing user or create new one with cold start strategy
        
        Cold Start Strategy:
        - Skills below user's grade: memory_strength = 0.8 (assumed mastered)
        - Skills at user's grade: memory_strength = 0.0 (needs learning)
        - Skills above user's grade: memory_strength = 0.0 (too advanced)
        
        Args:
            user_id: Unique user identifier
            age: User's age (for cold start)
            grade_level: User's current grade level string (e.g., "GRADE_3")
        
        Returns:
            User document from MongoDB
        """
        # Check if user exists
        user = self.db.get_user(user_id)
        
        if user:
            print(f"📂 Loaded existing user: {user_id}")
            return user
        
        # Create new user
        print(f"👤 Creating new user: {user_id}")
        
        all_skill_ids = list(self.SKILLS_CACHE.keys())
        success = self.db.create_user(user_id, all_skill_ids, age, grade_level)
        
        if not success:
            raise Exception(f"Failed to create user: {user_id}")
        
        # Load the newly created user
        user = self.db.get_user(user_id)
        
        # Apply cold start strategy if grade level provided
        if grade_level and user:
            self._apply_cold_start_strategy(user_id, grade_level)
            user = self.db.get_user(user_id)  # Reload after updates
        
        return user
    
    def _apply_cold_start_strategy(self, user_id: str, grade_level_str: str):
        """
        Apply cold start strategy: initialize skill strengths based on grade level
        
        Skills below user's grade get 0.8 (assumed foundation mastery)
        Skills at or above user's grade get 0.0 (need to learn)
        """
        try:
            user_grade = GradeLevel[grade_level_str]
            print(f"🎯 Applying cold start strategy for grade {user_grade.name}")
            
            skill_updates = {}
            
            for skill_id, skill in self.SKILLS_CACHE.items():
                if skill.grade_level.value < user_grade.value:
                    # Skills below user's grade - assume mastered
                    skill_updates[skill_id] = 0.8
            
            # Batch update all foundation skills
            if skill_updates:
                # Create a dummy question attempt for the update
                question_attempt = {
                    "question_id": "cold_start_init",
                    "skill_ids": list(skill_updates.keys()),
                    "is_correct": True,
                    "response_time_seconds": 0.0,
                    "time_penalty_applied": False
                }
                
                self.db.bulk_update_skill_states(user_id, skill_updates, question_attempt)
                print(f"✅ Initialized {len(skill_updates)} foundation skills to 0.8")
                
        except Exception as e:
            print(f"⚠️  Error applying cold start strategy: {e}")
    
    def calculate_memory_strength(self, user: Dict, skill_id: str, current_time: float) -> float:
        """
        Calculate current memory strength with exponential decay (forgetting)
        
        Formula: M(t) = M(t0) * exp(-λ * Δt)
        where:
        - M(t) = memory strength at current time
        - M(t0) = memory strength at last practice
        - λ = forgetting rate
        - Δt = time elapsed since last practice
        
        Args:
            user: User document from MongoDB
            skill_id: Skill to calculate strength for
            current_time: Current timestamp (seconds since epoch)
        
        Returns:
            Current memory strength (0.0 to 1.0)
        """
        skill_state = user["skill_states"].get(skill_id)
        
        if not skill_state:
            return 0.0
        
        base_strength = skill_state["memory_strength"]
        last_practice = skill_state["last_practice_time"]
        
        # If never practiced, return base strength
        if last_practice is None:
            return base_strength
        
        # Convert datetime to timestamp if needed
        if isinstance(last_practice, datetime):
            last_practice = last_practice.timestamp()
        
        # Calculate time elapsed
        time_elapsed = current_time - last_practice
        
        # Get forgetting rate from SKILLS_CACHE
        skill = self.SKILLS_CACHE.get(skill_id)
        if not skill:
            return base_strength
        
        forgetting_rate = skill.forgetting_rate
        
        # Apply exponential decay
        decayed_strength = base_strength * math.exp(-forgetting_rate * time_elapsed)
        
        # Clamp to [0, 1]
        return max(0.0, min(1.0, decayed_strength))
    
    def predict_correctness(self, user: Dict, skill_id: str, current_time: float) -> float:
        """
        Predict probability of answering correctly using sigmoid function
        
        P(correct) = sigmoid(memory_strength + bias)
        
        Args:
            user: User document
            skill_id: Skill to predict
            current_time: Current timestamp
        
        Returns:
            Probability of correct answer (0.0 to 1.0)
        """
        memory_strength = self.calculate_memory_strength(user, skill_id, current_time)
        
        # Sigmoid transformation with bias
        # This maps memory_strength to probability
        bias = -2.0  # Adjust this to calibrate difficulty
        z = memory_strength + bias
        probability = 1.0 / (1.0 + math.exp(-z))
        
        return probability
    
    def get_skills_needing_practice(self, user: Dict, current_time: float, 
                                   threshold: float = 0.7) -> List[Tuple[str, float]]:
        """
        Get skills that need practice, checking prerequisites
        
        Algorithm:
        1. Calculate memory strength for all skills (with decay)
        2. Find skills below threshold
        3. Check prerequisites are met
        4. Return sorted by: lowest score first, highest grade second
        
        Args:
            user: User document
            current_time: Current timestamp
            threshold: Minimum acceptable memory strength
        
        Returns:
            List of (skill_id, memory_strength) tuples, sorted by priority
        """
        skill_scores = {}
        
        # Calculate current strength for all skills
        for skill_id in self.SKILLS_CACHE.keys():
            strength = self.calculate_memory_strength(user, skill_id, current_time)
            skill_scores[skill_id] = strength
        
        # Find skills needing practice
        weak_skills = []
        
        for skill_id, strength in skill_scores.items():
            if strength >= threshold:
                continue  # Skill is strong enough
            
            skill = self.SKILLS_CACHE[skill_id]
            
            # Check if all prerequisites are met
            prerequisites_met = True
            for prereq_id in skill.prerequisites:
                prereq_strength = skill_scores.get(prereq_id, 0.0)
                if prereq_strength < threshold:
                    prerequisites_met = False
                    break
            
            if prerequisites_met:
                weak_skills.append((skill_id, strength))
        
        # Sort by priority:
        # 1. Lower strength = higher priority (practice weakest first)
        # 2. Higher grade level = higher priority (learn advanced concepts when ready)
        weak_skills.sort(key=lambda x: (
            x[1],  # Memory strength (ascending - weakest first)
            -self.SKILLS_CACHE[x[0]].grade_level.value  # Grade level (descending)
        ))
        
        return weak_skills
    
    def get_next_question(self, user_id: str, current_time: Optional[float] = None) -> Optional[Dict]:
        """
        Get the next best question for the student
        
        Intelligent Selection Algorithm:
        1. Find skills needing practice (memory_strength < 0.7)
        2. Filter by prerequisites met
        3. Sort by: lowest score first, highest testable level second
        4. Find unanswered question for top skill
        5. If no questions available, try next skill
        6. If still no questions, return None (or generate new one)
        
        Args:
            user_id: User identifier
            current_time: Current timestamp (defaults to now)
        
        Returns:
            Question document from MongoDB, or None if no suitable question
        """
        if current_time is None:
            current_time = time.time()
        
        # Get user
        user = self.db.get_user(user_id)
        if not user:
            print(f"❌ User not found: {user_id}")
            return None
        
        # Get skills needing practice
        skills_to_practice = self.get_skills_needing_practice(user, current_time)
        
        if not skills_to_practice:
            print("✨ All skills are strong! No practice needed right now.")
            return None
        
        print(f"🎯 Found {len(skills_to_practice)} skills needing practice")
        
        # Get answered questions
        answered_ids = self.db.get_answered_question_ids(user_id)
        
        # Try to find question for each skill in priority order
        for skill_id, strength in skills_to_practice:
            skill = self.SKILLS_CACHE[skill_id]
            print(f"🔍 Looking for question in: {skill.name} (strength: {strength:.2f})")
            
            # Find unanswered question
            question_doc = self.db.find_unanswered_question(
                skill_ids=[skill_id],
                answered_question_ids=answered_ids,
                max_times_shown=100
            )
            
            if question_doc:
                print(f"✅ Found question: {question_doc['question_id']}")
                return question_doc
        
        # No questions found
        print("⚠️  No unanswered questions available for priority skills")
        return None
    
    def update_skill_from_answer(self, user_id: str, skill_id: str, is_correct: bool,
                                response_time: float, current_time: float) -> float:
        """
        Calculate new memory strength after answering question
        
        Learning dynamics:
        - Correct answer: Boost memory strength (with diminishing returns)
        - Incorrect answer: Decrease memory strength
        - Fast correct answer: Larger boost
        - Slow correct answer: Smaller boost
        
        Args:
            user_id: User identifier
            skill_id: Skill being practiced
            is_correct: Whether answer was correct
            response_time: Time taken to answer (seconds)
            current_time: Current timestamp
        
        Returns:
            New memory strength value
        """
        user = self.db.get_user(user_id)
        if not user:
            return 0.0
        
        # Get current (decayed) memory strength
        current_strength = self.calculate_memory_strength(user, skill_id, current_time)
        
        # Calculate time penalty (slower = smaller boost)
        # Ideal response time is 5 seconds, penalty increases for slower answers
        ideal_time = 5.0
        time_penalty = math.exp(-(response_time - ideal_time) / 10.0)
        time_penalty = max(0.5, min(1.0, time_penalty))  # Clamp to [0.5, 1.0]
        
        if is_correct:
            # Correct answer: boost strength with diminishing returns
            # When strength is low, boost is large
            # When strength is high, boost is small
            learning_rate = 0.3 * (1.0 - current_strength)
            boost = learning_rate * time_penalty
            new_strength = current_strength + boost
        else:
            # Incorrect answer: decrease strength
            new_strength = current_strength * 0.8  # Reduce by 20%
        
        # Clamp to [0, 1]
        new_strength = max(0.0, min(1.0, new_strength))
        
        return new_strength
    
    def get_affected_skills(self, skill_id: str) -> List[str]:
        """
        Get all skills affected by practicing this skill (including prerequisites)
        
        When a student practices a skill, both the skill and its prerequisites
        get reinforced (though prerequisites get smaller boosts)
        
        Args:
            skill_id: The skill being practiced
        
        Returns:
            List of skill IDs (including the original and all prerequisites)
        """
        affected = [skill_id]
        
        skill = self.SKILLS_CACHE.get(skill_id)
        if not skill:
            return affected
        
        # Add all prerequisites recursively
        for prereq_id in skill.prerequisites:
            if prereq_id not in affected:
                affected.append(prereq_id)
                # Recursively get prerequisites of prerequisites
                sub_prereqs = self.get_affected_skills(prereq_id)
                for sub_prereq in sub_prereqs:
                    if sub_prereq not in affected:
                        affected.append(sub_prereq)
        
        return affected
    
    def record_question_attempt(self, user_id: str, question_id: str, 
                               skill_ids: List[str], is_correct: bool,
                               response_time: float) -> List[str]:
        """
        Record a question attempt and update all affected skills atomically
        
        This is the main entry point for updating student state after answering.
        
        Process:
        1. Calculate new memory strengths for all affected skills
        2. Update MongoDB atomically (all skills + question history)
        3. Return list of affected skills
        
        Args:
            user_id: User identifier
            question_id: Question that was answered
            skill_ids: Skills tested by the question
            is_correct: Whether answer was correct
            response_time: Time taken to answer (seconds)
        
        Returns:
            List of skill IDs that were updated
        """
        current_time = time.time()
        
        # Get all affected skills (including prerequisites)
        all_affected = []
        for skill_id in skill_ids:
            affected = self.get_affected_skills(skill_id)
            for s in affected:
                if s not in all_affected:
                    all_affected.append(s)
        
        # Calculate new memory strengths
        skill_updates = {}
        
        for skill_id in all_affected:
            if skill_id in skill_ids:
                # Directly tested skill - full update
                new_strength = self.update_skill_from_answer(
                    user_id, skill_id, is_correct, response_time, current_time
                )
            else:
                # Prerequisite skill - smaller boost (only if answer was correct)
                if is_correct:
                    user = self.db.get_user(user_id)
                    current_strength = self.calculate_memory_strength(user, skill_id, current_time)
                    # Prerequisite boost is 20% of what direct practice would give
                    boost = 0.05 * (1.0 - current_strength)
                    new_strength = min(1.0, current_strength + boost)
                else:
                    # Don't penalize prerequisites for wrong answer
                    user = self.db.get_user(user_id)
                    new_strength = self.calculate_memory_strength(user, skill_id, current_time)
            
            skill_updates[skill_id] = new_strength
        
        # Create question attempt record
        question_attempt = {
            "question_id": question_id,
            "skill_ids": skill_ids,
            "is_correct": is_correct,
            "response_time_seconds": response_time,
            "time_penalty_applied": response_time > 15.0  # Flag slow answers
        }
        
        # Atomic update in MongoDB
        success = self.db.bulk_update_skill_states(
            user_id, skill_updates, question_attempt
        )
        
        if success:
            print(f"✅ Updated {len(all_affected)} skills for user {user_id}")
        else:
            print(f"❌ Failed to update skills for user {user_id}")
        
        return all_affected
    
    def generate_question_tags(self, question_id: str, content: str, 
                              answer: str, skill_name: str) -> List[str]:
        """
        Use LLM to generate descriptive tags for a question
        
        Tags help with:
        - Finding similar questions
        - Understanding question characteristics
        - Filtering by difficulty or topic
        
        Args:
            question_id: Question identifier
            content: Question text
            answer: Correct answer
            skill_name: Name of the skill being tested
        
        Returns:
            List of generated tags
        """
        if not self.llm_client:
            print("⚠️  LLM client not available, skipping tag generation")
            return []
        
        try:
            prompt = f"""Analyze this math question and generate 3-5 descriptive tags.

Question: {content}
Answer: {answer}
Skill: {skill_name}

Generate tags that describe:
- Topic (e.g., "arithmetic", "fractions", "geometry")
- Difficulty indicators (e.g., "single_digit", "multi_step", "word_problem")
- Special features (e.g., "requires_carry", "visual", "real_world")

Return only the tags as a comma-separated list, nothing else."""

            response = self.llm_client.generate(prompt, max_tokens=50)
            
            # Parse response
            tags_str = response.strip()
            tags = [tag.strip() for tag in tags_str.split(",")]
            
            # Update question in database
            self.db.update_question_tags(question_id, tags)
            
            print(f"🏷️  Generated tags for {question_id}: {tags}")
            return tags
            
        except Exception as e:
            print(f"❌ Error generating tags: {e}")
            return []
    
    def get_user_statistics(self, user_id: str) -> Dict:
        """
        Get comprehensive statistics for a user
        
        Returns:
            Dictionary with user stats including skill proficiency
        """
        user = self.db.get_user(user_id)
        if not user:
            return {}
        
        current_time = time.time()
        
        # Calculate overall statistics
        question_history = user.get("question_history", [])
        total_questions = len(question_history)
        correct_answers = sum(1 for q in question_history if q.get("is_correct", False))
        
        # Calculate skill proficiency
        skill_proficiency = {}
        for skill_id in self.SKILLS_CACHE.keys():
            strength = self.calculate_memory_strength(user, skill_id, current_time)
            skill = self.SKILLS_CACHE[skill_id]
            skill_proficiency[skill_id] = {
                "name": skill.name,
                "grade_level": skill.grade_level.name,
                "memory_strength": round(strength, 3),
                "needs_practice": strength < 0.7
            }
        
        return {
            "user_id": user_id,
            "total_questions_answered": total_questions,
            "correct_answers": correct_answers,
            "accuracy": correct_answers / total_questions if total_questions > 0 else 0.0,
            "skills_mastered": sum(1 for s in skill_proficiency.values() if s["memory_strength"] >= 0.8),
            "skills_needing_practice": sum(1 for s in skill_proficiency.values() if s["needs_practice"]),
            "skill_proficiency": skill_proficiency
        }


# Convenience function for easy access
def create_dash_system() -> DashSystemV2:
    """Create and return a new DashSystem V2 instance"""
    return DashSystemV2()
