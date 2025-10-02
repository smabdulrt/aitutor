# DashSystem v2 - Progress Report
**Date:** October 2, 2025  
**Branch:** dashsystem_v2  
**Status:** Phase 1 Complete (MongoDB Foundation)

---

## ✅ COMPLETED - Phase 1: MongoDB Foundation

### 1. MongoDB Schema Design (`mongodb_schema.md`)
**What:** Comprehensive database schema for the entire system

**Collections Designed:**
- **Skills Collection**: Stores all curriculum skills with prerequisites, forgetting rates, difficulty
- **Questions Collection**: Stores all questions with metadata, tags, usage tracking
- **Users Collection**: Stores user profiles with embedded skill states and question history

**Key Features:**
- Indexes optimized for common query patterns
- Atomic update patterns for consistency
- Cold start strategy for new users
- Forgetting calculation approach
- Question selection algorithm design

---

### 2. MongoDB Handler (`mongodb_handler.py`)
**What:** Complete database interface with all CRUD operations

**Skills Operations:**
- `insert_skill()` - Add single skill
- `bulk_insert_skills()` - Batch insert for migration
- `get_all_skills()` - Load entire SKILLS_CACHE
- `get_skill_by_id()` - Single skill lookup

**Questions Operations:**
- `insert_question()` - Add single question
- `bulk_insert_questions()` - Batch insert
- `find_unanswered_question()` - Smart question selection
  * Avoids repeated questions
  * Prioritizes less-shown questions
  * Filters by skill
  * Auto-increments usage counter
- `get_all_questions_for_skill()` - Get question pool
- `update_question_tags()` - For LLM tagging

**User Operations:**
- `create_user()` - Initialize new student with all skills
- `get_user()` - Retrieve full profile
- `update_skill_state()` - **Atomic single-skill update**
- `bulk_update_skill_states()` - **Atomic multi-skill update** (for prerequisites)
- `get_answered_question_ids()` - Track history
- `get_user_skill_state()` - Single skill query

**Performance Features:**
- Connection pooling via singleton pattern
- Bulk operations for data loading
- Compound indexes for complex queries
- Atomic updates prevent race conditions

---

### 3. Data Migration Script (`migrate_to_mongodb.py`)
**What:** Migrates all existing JSON data to MongoDB

**Capabilities:**
- Migrates `skills.json` → MongoDB Skills collection
- Migrates `curriculum.json` → MongoDB Questions collection
- Migrates `Users/*.json` → MongoDB Users collection
- Automatic data transformation
- Error handling and reporting
- Verification step
- Summary statistics

**Usage:**
```bash
# Normal migration (keeps existing MongoDB data)
python migrate_to_mongodb.py

# Clear and fresh migration
python migrate_to_mongodb.py --clear
```

---

## 🔄 IN PROGRESS - What's Currently Happening

The foundation is complete. Next up:

1. **Create DashSystem v2 class** that uses MongoDB instead of JSON
2. **Implement intelligent question selection algorithm**
3. **Add LLM tagging integration**
4. **Write comprehensive tests**
5. **Update API endpoints**

---

## 📋 NEXT STEPS - Phase 2: DashSystem v2 Class

### Task 1: Refactor DashSystem to use MongoDB
**File:** `DashSystem/dash_system_v2.py`

**Changes Needed:**
1. Replace `_load_from_files()` with MongoDB queries
2. Implement `SKILLS_CACHE` - load all skills at startup
3. Update `get_next_question()` to use MongoDB queries
4. Modify `update_with_prerequisites()` to use atomic MongoDB updates
5. Remove JSON file dependencies

**Key Methods to Refactor:**
```python
class DashSystemV2:
    def __init__(self):
        self.db = get_db()
        self.SKILLS_CACHE = {}  # Load from MongoDB
        self._load_skills_cache()
    
    def _load_skills_cache(self):
        """Load all skills into memory for fast access"""
        skills_list = self.db.get_all_skills()
        for skill_doc in skills_list:
            self.SKILLS_CACHE[skill_doc['skill_id']] = Skill(...)
    
    def get_next_question(self, user_id, current_time):
        """Use MongoDB to find next question"""
        # 1. Calculate which skills need practice
        # 2. Get answered questions from MongoDB
        # 3. Find unanswered question using db.find_unanswered_question()
        # 4. Return question
    
    def record_question_attempt(self, user_id, question_id, is_correct, ...):
        """Use atomic MongoDB update"""
        # 1. Calculate new memory strengths
        # 2. Get all affected skills (with prerequisites)
        # 3. Call db.bulk_update_skill_states() atomically
```

---

### Task 2: Intelligent Next Question Algorithm
**Location:** Inside `DashSystemV2.get_next_question()`

**Algorithm Requirements (from Asana):**

1. **Cold Start Problem:**
   - New student starts with memory_strength = 0 for all skills
   - Based on age/grade, set foundation skills to 0.8 (mastered)
   - Current grade skills stay at 0.0 (need to learn)

2. **Next Question Selection:**
   - Find skill with **lowest score**
   - But at **highest possible level** student can handle
   - Ensure **prerequisites are met** (>= 0.7 threshold)
   - Don't give questions they obviously don't know

3. **Learning Path Logic:**
   - Right answer boosts current skill AND underlying prerequisites
   - Wrong answer slightly decreases current skill
   - Track when each skill was last practiced
   - Avoid repeating same question types

4. **Forgetting Factor:**
   - Memory strength decays over time: `M(t) = M(t0) * exp(-λ * Δt)`
   - Calculate in real-time, don't store decayed values
   - Use this for determining which skills need review

**Pseudocode:**
```python
def get_next_question(user_id, current_time):
    # 1. Get user from MongoDB
    user = db.get_user(user_id)
    
    # 2. Calculate current memory strengths (with decay)
    skill_scores = {}
    for skill_id in SKILLS_CACHE:
        skill_scores[skill_id] = calculate_memory_strength(
            user, skill_id, current_time
        )
    
    # 3. Find skills needing practice (score < 0.7)
    weak_skills = [s for s, score in skill_scores.items() if score < 0.7]
    
    # 4. Filter by prerequisites met
    ready_skills = []
    for skill_id in weak_skills:
        prereqs = SKILLS_CACHE[skill_id].prerequisites
        if all(skill_scores[p] >= 0.7 for p in prereqs):
            ready_skills.append(skill_id)
    
    # 5. Sort by: lowest score first, then highest grade level
    ready_skills.sort(key=lambda s: (
        skill_scores[s],  # Lower score = higher priority
        -SKILLS_CACHE[s].grade_level.value  # Higher grade = higher priority
    ))
    
    # 6. Try to find question for top skill
    for skill_id in ready_skills:
        answered_ids = db.get_answered_question_ids(user_id)
        question = db.find_unanswered_question(
            skill_ids=[skill_id],
            answered_question_ids=answered_ids
        )
        if question:
            return question
    
    # 7. No questions found - generate new one
    return generate_new_question(ready_skills[0])
```

---

### Task 3: LLM Question Tagging
**Purpose:** Auto-generate descriptive tags for questions

**Integration Point:** `QuestionGeneratorAgent`

**Flow:**
1. When new question is generated
2. Pass question content + answer to LLM
3. LLM returns tags like: ["arithmetic", "single_digit", "no_carry", "word_problem"]
4. Store tags in MongoDB: `db.update_question_tags(question_id, tags)`

**LLM Prompt Template:**
```
Analyze this math question and generate 3-5 descriptive tags.

Question: {question_content}
Answer: {answer}
Skill: {skill_name}

Generate tags that describe:
- Topic (e.g., "arithmetic", "fractions", "geometry")
- Difficulty indicators (e.g., "single_digit", "multi_step", "word_problem")
- Special features (e.g., "requires_carry", "visual", "real_world")

Return only the tags as a comma-separated list.
```

---

## 🧪 Phase 3: Testing

### Unit Tests Needed
- MongoDB Handler tests
  * Connection/disconnection
  * CRUD operations
  * Atomic updates
  * Error handling
  
- DashSystem V2 tests
  * Skills cache loading
  * Memory strength calculations
  * Forgetting decay
  * Question selection algorithm
  * Prerequisite checking

### Integration Tests Needed
- Full user flow:
  1. Create new user
  2. Get first question
  3. Answer question (correct)
  4. Verify skill state updated
  5. Get next question
  6. Answer question (incorrect)
  7. Verify skill state updated
  8. Check prerequisite skills also updated

- Migration tests:
  * Verify data integrity after migration
  * Compare JSON vs MongoDB user states
  * Performance benchmarks

---

## 📊 Current Database Schema

### Skills Collection
```javascript
{
  skill_id: "addition_basic",
  name: "Basic Addition",
  grade_level: "GRADE_1",
  prerequisites: ["counting_1_10"],
  forgetting_rate: 0.07,
  difficulty: 0.3
}
```

### Questions Collection
```javascript
{
  question_id: "add_001",
  skill_ids: ["addition_basic"],
  content: "What is 2 + 3?",
  answer: "5",
  difficulty: 0.3,
  tags: ["arithmetic", "single_digit"],
  times_shown: 12,
  avg_correctness: 0.85
}
```

### Users Collection
```javascript
{
  user_id: "student_123",
  age: 7,
  grade_level: "GRADE_2",
  skill_states: {
    "addition_basic": {
      memory_strength: 0.85,
      last_practice_time: ISODate("2025-10-01"),
      practice_count: 15,
      correct_count: 13
    }
  },
  question_history: [...]
}
```

---

## 🎯 Success Criteria

The DashSystem v2 implementation will be complete when:

1. ✅ MongoDB schema designed and documented
2. ✅ MongoDB handler implemented with all operations
3. ✅ Data migration script working
4. ⏳ DashSystem v2 class uses MongoDB (not JSON)
5. ⏳ Intelligent question selection algorithm implemented
6. ⏳ LLM tagging integrated
7. ⏳ All tests passing
8. ⏳ API endpoints updated
9. ⏳ Documentation updated

**Current Progress:** 3/9 complete (33%)

---

## 🚀 How to Use What's Been Built

### 1. Install Dependencies
```bash
pip install pymongo  # MongoDB driver
```

### 2. Start MongoDB
```bash
# Docker (recommended)
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Or install MongoDB locally
```

### 3. Run Migration
```bash
cd DashSystem
python migrate_to_mongodb.py
```

### 4. Verify Migration
Check that data was migrated:
```python
from mongodb_handler import get_db

db = get_db()
stats = db.get_database_stats()
print(f"Skills: {stats['skills']}")
print(f"Questions: {stats['questions']}")
print(f"Users: {stats['users']}")
```

---

## 📝 Files Created So Far

1. `DashSystem/mongodb_schema.md` - Complete schema documentation
2. `DashSystem/mongodb_handler.py` - Database interface (966 lines total)
3. `DashSystem/migrate_to_mongodb.py` - Migration script

**Git Commit:** `fe324e4` - "feat: Add MongoDB integration for DashSystem v2"

---

## 🔗 Related Resources

- **Asana Task:** DashSystem: Next Question Generator (Intelligent)
- **GitHub Branch:** dashsystem_v2
- **Repository:** https://github.com/vandanchopra/aitutor
- **Original Algorithm:** DASH (Deep Additive State History) by Mozer & Lindsey

---

## ⏭️ Immediate Next Action

**Create `DashSystem/dash_system_v2.py`** - the new MongoDB-powered DashSystem class that implements the intelligent question selection algorithm described above.

This will be approximately 400-500 lines of code that:
- Loads skills into SKILLS_CACHE
- Calculates memory strength with forgetting
- Implements the smart question selection algorithm
- Uses atomic MongoDB updates for skill states
- Handles prerequisite cascading
- Integrates with question generation

Would you like me to implement this next phase?
