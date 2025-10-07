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
from LLMBase.llm_client import OpenRouterClient

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
            self.llm_client = OpenRouterClient()
            print("✅ LLM Client initialized for question tagging")
        except Exception as e:
            self.llm_client = None
            print(f"⚠️  LLM Client not available: {e}")
        
        # Load all skills into memory
        self._load_skills_cache()
        
        print("✅ DashSystem V2 initialized with MongoDB backend")
    
    def _load_skills_cache(self):
        """
        Load all skills from MongoDB into memory for fast access

        Handles hierarchical skill structure:
        - MongoDB has ONE document per subject
        - Each subject has nested: skills[grade][topic][concept][exercise]
        - This method flattens the hierarchy into SKILLS_CACHE for fast lookup
        """
        print("📚 Loading skills into SKILLS_CACHE...")

        subject_docs = self.db.get_all_skills()

        for subject_doc in subject_docs:
            try:
                subject = subject_doc.get("subject", "unknown")
                skills_tree = subject_doc.get("skills", {})

                # Recursively flatten the hierarchical structure
                self._flatten_skills_tree(skills_tree, subject)

            except Exception as e:
                print(f"⚠️  Error loading skills for subject {subject_doc.get('subject', 'unknown')}: {e}")

        print(f"✅ Loaded {len(self.SKILLS_CACHE)} skills into SKILLS_CACHE")

    def _flatten_skills_tree(self, node: Dict, subject: str, parent_path: str = ""):
        """
        Recursively flatten hierarchical skill tree into SKILLS_CACHE

        Args:
            node: Current node in the tree (could be grade/topic/concept/exercise)
            subject: Subject name (e.g., "math")
            parent_path: Path from root (for tracking hierarchy)
        """
        for key, value in node.items():
            if not isinstance(value, dict):
                continue

            # Check if this is a leaf skill (has skill_id)
            if "skill_id" in value:
                # This is a leaf skill - add to cache
                skill_id = value["skill_id"]
                exercise_name = value.get("exercise_name", "Unknown Exercise")
                breadcrumb = value.get("breadcrumb", "")

                # Extract grade from skill_id (format: "math_3_1.1.1.1" -> grade=3)
                try:
                    parts = skill_id.split('_')
                    grade_num = int(parts[1]) if len(parts) > 1 else 0
                    grade_level = GradeLevel(grade_num)
                except:
                    grade_level = GradeLevel.K

                # Convert breadcrumb prerequisites to skill_ids
                # Prerequisites are stored as breadcrumbs like "1.1.1"
                # Need to convert to skill_ids like "math_3_1.1.1"
                prerequisite_breadcrumbs = value.get("prerequisites", [])
                prerequisite_skill_ids = []
                for prereq_breadcrumb in prerequisite_breadcrumbs:
                    # Build skill_id from breadcrumb: subject_grade_breadcrumb
                    prereq_skill_id = f"{subject}_{grade_num}_{prereq_breadcrumb}"
                    prerequisite_skill_ids.append(prereq_skill_id)

                skill = Skill(
                    skill_id=skill_id,
                    name=exercise_name,
                    grade_level=grade_level,
                    prerequisites=prerequisite_skill_ids,
                    forgetting_rate=value.get("forgetting_rate", 0.1),
                    difficulty=value.get("difficulty", 0.5)
                )
                self.SKILLS_CACHE[skill_id] = skill
            else:
                # This is an intermediate node - recurse deeper
                new_path = f"{parent_path}.{key}" if parent_path else key
                self._flatten_skills_tree(value, subject, new_path)
    
    def get_or_create_user(self, user_id: str, age: Optional[int] = None, 
                           grade_level: Optional[str] = None) -> Dict:
        """
        Get existing user or create new one with cold start strategy

        Cold Start Strategy (Three-State System):
        - Skills below user's grade: memory_strength = 0.9 (assumed mastered)
        - Skills at user's grade: memory_strength = 0.0 (ready to learn)
        - Skills above user's grade: memory_strength = -1 (locked)

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

        Three-state initialization:
        - Skills below user's grade: 0.9 (assumed mastery, can be revised down)
        - Skills at user's grade: 0.0 (ready to learn, start here)
        - Skills above user's grade: -1 (locked until current mastered)
        """
        try:
            user_grade = GradeLevel[grade_level_str]
            print(f"🎯 Applying cold start strategy for grade {user_grade.name}")

            skill_updates = {}
            below_grade_count = 0
            current_grade_count = 0
            above_grade_count = 0

            for skill_id, skill in self.SKILLS_CACHE.items():
                if skill.grade_level.value < user_grade.value:
                    # Skills below user's grade - assume mastered
                    skill_updates[skill_id] = 0.9
                    below_grade_count += 1
                elif skill.grade_level.value == user_grade.value:
                    # Current grade - ready to learn (already initialized to 0.0)
                    current_grade_count += 1
                else:
                    # Skills above user's grade - locked
                    skill_updates[skill_id] = -1
                    above_grade_count += 1

            # Batch update foundation and locked skills
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
                print(f"✅ Cold start complete:")
                print(f"   - Below grade (0.9): {below_grade_count} skills")
                print(f"   - Current grade (0.0): {current_grade_count} skills")
                print(f"   - Above grade (-1 locked): {above_grade_count} skills")

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

        Special handling:
        - Locked skills (strength < 0) return -1 without decay

        Args:
            user: User document from MongoDB
            skill_id: Skill to calculate strength for
            current_time: Current timestamp (seconds since epoch)

        Returns:
            Current memory strength (-1 for locked, 0.0 to 1.0 otherwise)
        """
        skill_state = user["skill_states"].get(skill_id)

        if not skill_state:
            print(f"  📊 CALC [{skill_id}]: No skill state found, returning 0.0")
            return 0.0

        base_strength = skill_state["memory_strength"]
        last_practice = skill_state["last_practice_time"]

        # Handle locked skills - return immediately
        if base_strength < 0:
            print(f"  📊 CALC [{skill_id}]: Locked skill (strength={base_strength:.1f})")
            return -1

        # If never practiced, return base strength
        if last_practice is None:
            print(f"  📊 CALC [{skill_id}]: Never practiced, base_strength={base_strength:.4f}")
            return base_strength

        # Convert datetime to timestamp if needed
        if isinstance(last_practice, datetime):
            last_practice = last_practice.timestamp()

        # Calculate time elapsed
        time_elapsed = current_time - last_practice

        # Get forgetting rate from SKILLS_CACHE
        skill = self.SKILLS_CACHE.get(skill_id)
        if not skill:
            print(f"  📊 CALC [{skill_id}]: Skill not in cache, returning base_strength={base_strength:.4f}")
            return base_strength

        forgetting_rate = skill.forgetting_rate

        # Apply exponential decay
        decayed_strength = base_strength * math.exp(-forgetting_rate * time_elapsed)

        # Clamp to [0, 1]
        clamped_strength = max(0.0, min(1.0, decayed_strength))

        print(f"  📊 CALC [{skill_id}]:")
        print(f"     - base_strength: {base_strength:.4f}")
        print(f"     - time_elapsed: {time_elapsed:.2f}s ({time_elapsed/3600:.2f}h)")
        print(f"     - forgetting_rate: {forgetting_rate:.6f}")
        print(f"     - exp(-λ*Δt): {math.exp(-forgetting_rate * time_elapsed):.6f}")
        print(f"     - decayed_strength: {decayed_strength:.4f}")
        print(f"     - final (clamped): {clamped_strength:.4f}")

        return clamped_strength
    
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
        print(f"\n  🎯 PREDICT [{skill_id}]:")
        memory_strength = self.calculate_memory_strength(user, skill_id, current_time)

        # Sigmoid transformation with bias
        # This maps memory_strength to probability
        bias = -2.0  # Adjust this to calibrate difficulty
        z = memory_strength + bias
        probability = 1.0 / (1.0 + math.exp(-z))

        print(f"     - memory_strength: {memory_strength:.4f}")
        print(f"     - bias: {bias:.2f}")
        print(f"     - z (strength + bias): {z:.4f}")
        print(f"     - P(correct) = sigmoid(z): {probability:.4f}")

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
        print(f"\n📋 GETTING SKILLS NEEDING PRACTICE (threshold={threshold}):")
        skill_scores = {}

        # Calculate current strength for all skills
        print(f"  Calculating strength for {len(self.SKILLS_CACHE)} skills...")
        for skill_id in self.SKILLS_CACHE.keys():
            strength = self.calculate_memory_strength(user, skill_id, current_time)
            skill_scores[skill_id] = strength

        # Find skills needing practice
        weak_skills = []
        skills_above_threshold = []
        locked_skills = []

        for skill_id, strength in skill_scores.items():
            # Skip locked skills
            if strength < 0:
                locked_skills.append((skill_id, strength))
                continue

            if strength >= threshold:
                skills_above_threshold.append((skill_id, strength))
                continue  # Skill is strong enough

            skill = self.SKILLS_CACHE[skill_id]

            # Check if all prerequisites are met
            prerequisites_met = True
            for prereq_id in skill.prerequisites:
                prereq_strength = skill_scores.get(prereq_id, 0.0)
                if prereq_strength < threshold:
                    prerequisites_met = False
                    print(f"  ❌ [{skill_id}] blocked by prerequisite [{prereq_id}] (strength={prereq_strength:.4f} < {threshold})")
                    break

            if prerequisites_met:
                weak_skills.append((skill_id, strength))
                print(f"  ✅ [{skill_id}] needs practice (strength={strength:.4f} < {threshold})")

        print(f"\n  📊 Summary:")
        print(f"     - Skills above threshold: {len(skills_above_threshold)}")
        print(f"     - Skills needing practice: {len(weak_skills)}")
        print(f"     - Locked skills: {len(locked_skills)}")

        # Check for grade unlock: If no weak skills and we have locked skills
        if not weak_skills and locked_skills:
            # Try to unlock next grade
            unlocked = self._try_unlock_next_grade(user, skill_scores, threshold)
            if unlocked:
                # Recalculate after unlocking
                print(f"\n🔓 Re-evaluating after grade unlock...")
                return self.get_skills_needing_practice(user, current_time, threshold)

        # Sort by priority:
        # 1. Lower strength = higher priority (practice weakest first)
        # 2. Higher grade level = higher priority (learn advanced concepts when ready)
        weak_skills.sort(key=lambda x: (
            x[1],  # Memory strength (ascending - weakest first)
            -self.SKILLS_CACHE[x[0]].grade_level.value  # Grade level (descending)
        ))

        if weak_skills:
            print(f"\n  🎯 Priority order (top 5):")
            for i, (skill_id, strength) in enumerate(weak_skills[:5], 1):
                skill = self.SKILLS_CACHE[skill_id]
                print(f"     {i}. [{skill_id}] {skill.name} - strength={strength:.4f}, grade={skill.grade_level.value}")

        return weak_skills

    def _try_unlock_next_grade(self, user: Dict, skill_scores: Dict[str, float], mastery_threshold: float = 0.8) -> bool:
        """
        Try to unlock the next grade if current grade is mastered

        Criteria for unlocking:
        - All skills in current grade must be ≥ mastery_threshold (0.8)
        - Next grade must have locked skills (-1)

        Args:
            user: User document
            skill_scores: Current skill scores for all skills
            mastery_threshold: Minimum strength to consider mastered (default 0.8)

        Returns:
            True if a grade was unlocked, False otherwise
        """
        user_grade_str = user.get("grade_level")
        if not user_grade_str:
            return False

        try:
            user_grade = GradeLevel[user_grade_str]
        except KeyError:
            return False

        # Check if all current-grade skills are mastered
        current_grade_skills = {
            skill_id: strength
            for skill_id, strength in skill_scores.items()
            if self.SKILLS_CACHE[skill_id].grade_level.value == user_grade.value
        }

        if not current_grade_skills:
            return False

        all_mastered = all(strength >= mastery_threshold for strength in current_grade_skills.values())

        if not all_mastered:
            mastered_count = sum(1 for s in current_grade_skills.values() if s >= mastery_threshold)
            print(f"\n  🔒 Grade {user_grade.value} not fully mastered: {mastered_count}/{len(current_grade_skills)} skills ≥ {mastery_threshold}")
            return False

        # Find locked skills in next grade
        next_grade = user_grade.value + 1
        next_grade_locked = [
            skill_id
            for skill_id, strength in skill_scores.items()
            if strength < 0 and self.SKILLS_CACHE[skill_id].grade_level.value == next_grade
        ]

        if not next_grade_locked:
            print(f"\n  🎓 No locked skills found in Grade {next_grade}")
            return False

        # Unlock next grade!
        print(f"\n  🎉 GRADE UNLOCK! All Grade {user_grade.value} skills mastered (≥{mastery_threshold})")
        print(f"  🔓 Unlocking Grade {next_grade} ({len(next_grade_locked)} skills)")

        skill_updates = {skill_id: 0.0 for skill_id in next_grade_locked}

        question_attempt = {
            "question_id": f"grade_unlock_{next_grade}",
            "skill_ids": next_grade_locked,
            "is_correct": True,
            "response_time_seconds": 0.0,
            "time_penalty_applied": False
        }

        self.db.bulk_update_skill_states(user["user_id"], skill_updates, question_attempt)
        return True

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

        print(f"\n" + "="*80)
        print(f"🎓 GET NEXT QUESTION FOR USER: {user_id}")
        print(f"="*80)

        # Get user
        user = self.db.get_user(user_id)
        if not user:
            print(f"❌ User not found: {user_id}")
            return None

        print(f"✅ User found: {user['user_id']}, Grade: {user.get('grade_level', 'Unknown')}")

        # Get skills needing practice
        skills_to_practice = self.get_skills_needing_practice(user, current_time)

        if not skills_to_practice:
            print("\n✨ All skills are strong! No practice needed right now.")
            return None

        print(f"\n🎯 Found {len(skills_to_practice)} skills needing practice")

        # Get answered questions
        answered_ids = self.db.get_answered_question_ids(user_id)
        print(f"📝 User has answered {len(answered_ids)} questions")

        # Try to find question for each skill in priority order
        print(f"\n🔍 SEARCHING FOR QUESTIONS:")
        for i, (skill_id, strength) in enumerate(skills_to_practice, 1):
            skill = self.SKILLS_CACHE[skill_id]
            print(f"\n  Try #{i}: [{skill_id}] {skill.name}")
            print(f"    Memory strength: {strength:.4f}")
            
            # Find unanswered question
            question_doc = self.db.find_unanswered_question(
                skill_ids=[skill_id],
                answered_question_ids=answered_ids,
                max_times_shown=100
            )

            if question_doc:
                print(f"    ✅ Found question: {question_doc['question_id']}")
                print(f"\n" + "="*80)
                print(f"📄 SELECTED QUESTION:")
                print(f"   ID: {question_doc['question_id']}")
                print(f"   Skills: {question_doc.get('skill_ids', [])}")
                print(f"   Difficulty: {question_doc.get('difficulty', 'N/A')}")
                print(f"   Type: {question_doc.get('question_type', 'N/A')}")
                print(f"=" * 80 + "\n")
                return question_doc
            else:
                print(f"    ❌ No unanswered questions found for this skill")

        # No questions found
        print("\n⚠️  No unanswered questions available for any priority skills")
        print(f"=" * 80 + "\n")
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

    def get_breadcrumb_related_skills(self, skill_id: str) -> Dict[str, float]:
        """
        Find related skills based on breadcrumb hierarchy

        Returns skills at different hierarchy levels with cascade rates:
        - Same concept (x.x.x.N.x): 3% cascade
        - Same topic (x.x.N.x.x): 2% cascade
        - Same grade (N.x.x.x.x): 1% cascade
        - Lower grades (same path): 3% cascade (for gap detection)

        Args:
            skill_id: The skill being practiced (e.g., "math_8_1.2.3.2")

        Returns:
            Dictionary of {skill_id: cascade_rate} for related skills
        """
        related = {}

        # Parse skill_id: format is "subject_grade_breadcrumb"
        # Example: "math_8_1.2.3.2" → subject="math", grade=8, breadcrumb="1.2.3.2"
        parts = skill_id.split('_')
        if len(parts) < 3:
            return related

        subject = parts[0]
        try:
            grade = int(parts[1])
        except ValueError:
            return related

        breadcrumb = '_'.join(parts[2:])  # Handle multi-part breadcrumbs
        breadcrumb_parts = breadcrumb.split('.')

        if len(breadcrumb_parts) < 4:
            return related

        # Extract hierarchy levels
        # Breadcrumb format: Grade.Topic.Concept.SubConcept.Exercise
        # But in skill_id, grade is separate, so: Topic.Concept.SubConcept.Exercise
        topic = breadcrumb_parts[0] if len(breadcrumb_parts) > 0 else None
        concept = breadcrumb_parts[1] if len(breadcrumb_parts) > 1 else None
        subconcept = breadcrumb_parts[2] if len(breadcrumb_parts) > 2 else None
        exercise = breadcrumb_parts[3] if len(breadcrumb_parts) > 3 else None

        # Search through all skills in cache
        for other_skill_id, other_skill in self.SKILLS_CACHE.items():
            if other_skill_id == skill_id:
                continue  # Skip self

            # Parse other skill
            other_parts = other_skill_id.split('_')
            if len(other_parts) < 3 or other_parts[0] != subject:
                continue

            try:
                other_grade = int(other_parts[1])
            except ValueError:
                continue

            other_breadcrumb = '_'.join(other_parts[2:])
            other_breadcrumb_parts = other_breadcrumb.split('.')

            if len(other_breadcrumb_parts) < 4:
                continue

            other_topic = other_breadcrumb_parts[0] if len(other_breadcrumb_parts) > 0 else None
            other_concept = other_breadcrumb_parts[1] if len(other_breadcrumb_parts) > 1 else None
            other_subconcept = other_breadcrumb_parts[2] if len(other_breadcrumb_parts) > 2 else None

            # Check hierarchy matches and assign cascade rates
            cascade_rate = None

            # Same grade, same topic, same concept, same subconcept (different exercise)
            if (other_grade == grade and other_topic == topic and
                other_concept == concept and other_subconcept == subconcept):
                cascade_rate = 0.03  # Same concept: 3%

            # Same grade, same topic, same concept (different subconcept)
            elif (other_grade == grade and other_topic == topic and other_concept == concept):
                cascade_rate = 0.02  # Same topic: 2%

            # Same grade (different topic)
            elif other_grade == grade:
                cascade_rate = 0.01  # Same grade: 1%

            # Lower grades with same path (for gap detection)
            elif (other_grade < grade and other_topic == topic and
                  other_concept == concept and other_subconcept == subconcept):
                cascade_rate = 0.03  # Lower grade, same path: 3%

            if cascade_rate is not None:
                related[other_skill_id] = cascade_rate

        return related

    def print_skill_context_table(self, user_id: str, current_skill_id: str, current_time: float, window: int = 5):
        """
        Print skill table showing ±window levels around the current skill being practiced

        Args:
            user_id: User identifier
            current_skill_id: The skill currently being practiced
            current_time: Current timestamp
            window: Number of levels to show above and below (default: 5)
        """
        user = self.db.get_user(user_id)
        if not user:
            return

        # Get all skills sorted by breadcrumb (hierarchical order)
        skill_strengths = []
        for skill_id, skill in self.SKILLS_CACHE.items():
            strength = self.calculate_memory_strength(user, skill_id, current_time)
            skill_strengths.append((skill_id, skill.name, skill.grade_level.name, strength))

        # Sort by grade level and breadcrumb
        skill_strengths.sort(key=lambda x: (x[2], x[0]))  # Sort by grade, then skill_id (which includes breadcrumb)

        # Find index of current skill
        current_index = -1
        for i, (skill_id, _, _, _) in enumerate(skill_strengths):
            if skill_id == current_skill_id:
                current_index = i
                break

        if current_index == -1:
            print(f"⚠️  Current skill {current_skill_id} not found in cache")
            return

        # Calculate window bounds
        start_index = max(0, current_index - window)
        end_index = min(len(skill_strengths), current_index + window + 1)

        # Print table header
        print("\n" + "="*120)
        print(f"{'SKILL CONTEXT (±' + str(window) + ' levels around current skill)':^120}")
        print("="*120)
        print(f"{'Skill':<35} {'Grade':<8} {'Memory':<8} {'Current':<8}")
        print("-"*120)

        # Print skills in window
        for i in range(start_index, end_index):
            skill_id, name, grade, strength = skill_strengths[i]
            marker = ">>> " if i == current_index else "    "
            print(f"{marker}{name:<31} {grade:<8} {strength:<8.3f} {'<---' if i == current_index else ''}")

        print("-"*120)

    def record_question_attempt(self, user_id: str, question_id: str,
                               skill_ids: List[str], is_correct: bool,
                               response_time: float, question_content: str = "") -> List[str]:
        """
        Record a question attempt and update all affected skills atomically

        This is the main entry point for updating student state after answering.

        Process:
        1. Calculate new memory strengths for directly tested skills
        2. Apply prerequisite cascade (small boost to prerequisites)
        3. Apply breadcrumb cascade (related skills in hierarchy)
        4. Update MongoDB atomically (all skills + question history)
        5. Return list of affected skills

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
        user = self.db.get_user(user_id)
        if not user:
            return []

        # Get question count for this user
        question_count = len(user.get('question_history', [])) + 1

        # Get skill names and breadcrumbs
        skill_names = [self.SKILLS_CACHE[sid].name for sid in skill_ids if sid in self.SKILLS_CACHE]

        # Get breadcrumb from first skill (primary skill for the question)
        breadcrumb = "N/A"
        if skill_ids and skill_ids[0] in self.SKILLS_CACHE:
            # skill_id format: "subject_grade_breadcrumb" (e.g., "math_3_1.2.3.4")
            parts = skill_ids[0].split('_', 2)
            if len(parts) >= 3:
                breadcrumb = parts[2]  # Get the breadcrumb part

        # Print question header with breadcrumb + question ID
        print(f"\n{'='*80}")
        print(f"🔢 Question {question_count}")
        print(f"📍 Breadcrumb: {breadcrumb} | Question ID: {question_id}")
        print(f"Skills tested: {', '.join(skill_names)}")
        if question_content:
            # Truncate long content
            content_preview = question_content[:100] + "..." if len(question_content) > 100 else question_content
            print(f"Question: {content_preview}")
        print(f"{'='*80}")

        # Calculate time penalty
        time_penalty = self.calculate_time_penalty(response_time)
        time_status = "⚠️ SLOW" if time_penalty < 1.0 else "✅ FAST"

        print(f"\n⏱️  Response time: {response_time:.1f} seconds ({time_status})")
        if time_penalty < 1.0:
            print(f"   Time penalty applied: {time_penalty}x reward")

        # Store previous strengths for comparison
        prev_strengths = {}
        for skill_id in self.SKILLS_CACHE.keys():
            prev_strengths[skill_id] = self.calculate_memory_strength(user, skill_id, current_time)

        # Track all affected skills
        skill_updates = {}
        all_affected = []

        # Step 1: Update directly tested skills (full update)
        for skill_id in skill_ids:
            new_strength = self.update_skill_from_answer(
                user_id, skill_id, is_correct, response_time, current_time
            )
            skill_updates[skill_id] = new_strength
            all_affected.append(skill_id)

        # Step 2: Update prerequisites (smaller boost)
        prereq_count = 0
        for skill_id in skill_ids:
            prereqs = self.get_affected_skills(skill_id)
            for prereq_id in prereqs:
                if prereq_id in skill_ids or prereq_id in skill_updates:
                    continue  # Skip direct skills and already updated

                if is_correct:
                    current_strength = self.calculate_memory_strength(user, prereq_id, current_time)
                    # Skip locked skills
                    if current_strength < 0:
                        continue
                    # Prerequisite boost: 5% of gap
                    boost = 0.05 * (1.0 - current_strength)
                    new_strength = min(1.0, current_strength + boost)
                else:
                    # Don't penalize prerequisites for wrong answer
                    current_strength = self.calculate_memory_strength(user, prereq_id, current_time)
                    new_strength = current_strength

                skill_updates[prereq_id] = new_strength
                all_affected.append(prereq_id)
                prereq_count += 1

        # Step 3: Apply breadcrumb cascade
        breadcrumb_updates = {}
        for skill_id in skill_ids:
            related_skills = self.get_breadcrumb_related_skills(skill_id)

            for related_id, cascade_rate in related_skills.items():
                if related_id in skill_updates:
                    continue  # Already updated

                current_strength = self.calculate_memory_strength(user, related_id, current_time)

                # Skip locked skills
                if current_strength < 0:
                    continue

                # Apply cascade formula
                if is_correct:
                    # Positive cascade (boost)
                    boost = cascade_rate * (1.0 - current_strength)
                    new_strength = current_strength + boost
                else:
                    # Negative cascade (penalty)
                    penalty = cascade_rate
                    new_strength = current_strength * (1.0 - penalty)

                # Clamp to [0, 1]
                new_strength = max(0.0, min(1.0, new_strength))

                breadcrumb_updates[related_id] = new_strength

        # Merge breadcrumb updates
        for skill_id, strength in breadcrumb_updates.items():
            skill_updates[skill_id] = strength
            all_affected.append(skill_id)

        # Print score changes table
        print(f"\n📊 SCORE CHANGES:")
        print(f"{'Skill':<35} {'Type':<12} {'Previous':<10} {'New':<10} {'Change':<10}")
        print("-"*80)

        for skill_id in all_affected:
            if skill_id not in self.SKILLS_CACHE:
                continue
            skill_name = self.SKILLS_CACHE[skill_id].name
            prev_prob = prev_strengths.get(skill_id, 0.0)
            new_prob = skill_updates.get(skill_id, prev_prob)
            change = new_prob - prev_prob
            change_str = f"{change:+.3f}"

            # Determine if this is a direct skill or other type
            if skill_id in skill_ids:
                skill_type = "Direct"
            elif skill_id in [pid for sid in skill_ids for pid in self.get_affected_skills(sid)]:
                skill_type = "Prerequisite"
            else:
                skill_type = "Breadcrumb"

            print(f"{skill_name:<35} {skill_type:<12} {prev_prob:<10.3f} {new_prob:<10.3f} {change_str:<10}")

        # Show periodic skill context table (every 3 questions)
        if question_count % 3 == 0 and skill_ids:
            self.print_skill_context_table(user_id, skill_ids[0], current_time, window=5)

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
            print(f"✅ Successfully updated {len(skill_updates)} skills for user {user_id}")
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
