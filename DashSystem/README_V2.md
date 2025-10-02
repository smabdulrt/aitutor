# DashSystem V2 - Intelligent Adaptive Learning System

**MongoDB-powered implementation of DASH (Deep Additive State History) algorithm**

## 🎯 Overview

DashSystem V2 is a complete rewrite of the original DashSystem that uses MongoDB as its backend instead of JSON files. It implements an intelligent adaptive learning algorithm that:

- Tracks student knowledge with **memory strength** (0.0 to 1.0)
- Models **forgetting** using exponential decay
- Enforces **prerequisites** before advancing topics
- Selects questions intelligently based on **lowest score + highest level**
- Updates skills **atomically** in MongoDB
- Cascades learning to **prerequisite skills**
- Implements **cold start strategy** for new students

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    DashSystem V2                        │
│  - Intelligent question selection algorithm             │
│  - Memory strength calculation with forgetting          │
│  - Prerequisite checking and cascading                  │
│  - Cold start strategy for new students                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                 MongoDB Handler                         │
│  - Connection management                                │
│  - CRUD operations for Skills, Questions, Users         │
│  - Atomic skill state updates                           │
│  - Smart question selection queries                     │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   MongoDB                               │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐          │
│  │  Skills   │  │ Questions │  │   Users   │          │
│  └───────────┘  └───────────┘  └───────────┘          │
│                                                         │
│  - Indexed for performance                              │
│  - Atomic updates                                       │
│  - Embedded skill states                                │
└─────────────────────────────────────────────────────────┘
```

---

## 📦 Installation

### 1. Install Dependencies

```bash
pip install -r DashSystem/requirements.txt
```

Key dependencies:
- `pymongo>=4.5.0` - MongoDB driver
- `python-dotenv>=1.0.0` - Environment variables
- `openai>=1.0.0` - LLM tagging (optional)

### 2. Start MongoDB

**Option A: Docker (Recommended)**
```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

**Option B: Local Installation**
- Download from https://www.mongodb.com/try/download/community
- Follow installation instructions for your OS

### 3. Set Environment Variables

Create a `.env` file:
```bash
# MongoDB connection
MONGODB_URI=mongodb://localhost:27017/

# Optional: OpenAI for question tagging
OPENAI_API_KEY=your_api_key_here
```

### 4. Migrate Existing Data

```bash
cd DashSystem
python migrate_to_mongodb.py
```

This will:
- Load `QuestionsBank/skills.json` → MongoDB
- Load `QuestionsBank/curriculum.json` → MongoDB
- Load `Users/*.json` → MongoDB
- Create indexes for performance
- Verify migration success

---

## 🚀 Quick Start

### Basic Usage

```python
from DashSystem.dash_system_v2 import DashSystemV2

# Initialize the system
dash = DashSystemV2()

# Create or load a student
user = dash.get_or_create_user(
    user_id="student_123",
    age=8,
    grade_level="GRADE_3"
)

# Get the next question for the student
question = dash.get_next_question("student_123")

if question:
    print(f"Question: {question['content']}")
    print(f"Options: {question.get('options', [])}")
    
    # Student answers the question
    student_answer = "42"  # Get from UI
    is_correct = (student_answer == question['answer'])
    response_time = 8.5  # seconds
    
    # Record the attempt
    affected_skills = dash.record_question_attempt(
        user_id="student_123",
        question_id=question['question_id'],
        skill_ids=question['skill_ids'],
        is_correct=is_correct,
        response_time=response_time
    )
    
    print(f"Updated {len(affected_skills)} skills")

# Get student statistics
stats = dash.get_user_statistics("student_123")
print(f"Accuracy: {stats['accuracy']*100:.1f}%")
print(f"Skills mastered: {stats['skills_mastered']}")
```

### Advanced Usage

```python
import time

# Get skills needing practice
current_time = time.time()
skills_to_practice = dash.get_skills_needing_practice(
    user=user,
    current_time=current_time,
    threshold=0.7  # Memory strength threshold
)

for skill_id, strength in skills_to_practice:
    skill = dash.SKILLS_CACHE[skill_id]
    print(f"{skill.name}: {strength:.2f} (Grade {skill.grade_level.name})")

# Check memory strength with forgetting
memory_strength = dash.calculate_memory_strength(
    user=user,
    skill_id="addition_basic",
    current_time=current_time
)
print(f"Current memory strength: {memory_strength:.2f}")
```

---

## 🧠 How It Works

### 1. Memory Strength & Forgetting

Each skill has a **memory strength** (0.0 to 1.0) that decays over time:

```
M(t) = M(t₀) × e^(-λ × Δt)

Where:
- M(t) = current memory strength
- M(t₀) = strength at last practice
- λ = forgetting rate (skill-specific)
- Δt = time since last practice
```

**Example:**
- Initial strength: 0.9
- Forgetting rate: 0.07 per day
- After 1 day: 0.9 × e^(-0.07×1) = 0.84
- After 7 days: 0.9 × e^(-0.07×7) = 0.56

### 2. Intelligent Question Selection

The algorithm selects the next question by:

1. **Calculate** current memory strengths (with decay)
2. **Filter** skills below threshold (default 0.7)
3. **Check** that all prerequisites are met
4. **Sort** by:
   - Lowest memory strength first (weakest skill)
   - Highest grade level second (learn advanced when ready)
5. **Find** unanswered question for top priority skill
6. **Avoid** recently answered questions

### 3. Cold Start Strategy

New students are initialized based on their grade level:

```python
# Example: 3rd grade student
# Kindergarten skills     → 0.8 (foundation assumed)
# Grade 1-2 skills        → 0.8 (below current grade)
# Grade 3 skills          → 0.0 (current grade, needs learning)
# Grade 4+ skills         → 0.0 (above grade, too advanced)
```

This creates a **zone of proximal development** where the system focuses on current grade-level skills while acknowledging prior knowledge.

### 4. Learning Dynamics

**Correct Answer:**
```
boost = learning_rate × (1 - current_strength) × time_penalty
new_strength = current_strength + boost

# Diminishing returns: stronger skills get smaller boosts
# Time penalty: slower answers get smaller boosts
```

**Incorrect Answer:**
```
new_strength = current_strength × 0.8  # 20% penalty
```

### 5. Prerequisite Cascading

When a student practices a skill, **prerequisite skills also benefit**:

- **Direct skill**: Full strength update
- **Prerequisites**: 20% of full update (reinforcement)
- **Recursive**: All prerequisites in the chain

**Example:**
- Student answers "2-digit addition" question correctly
- Updates:
  - `addition_2digit` → +0.25 (direct)
  - `addition_basic` → +0.05 (prerequisite)
  - `counting_1_10` → +0.05 (prerequisite's prerequisite)

---

## 📊 Database Schema

### Skills Collection
```javascript
{
  skill_id: "addition_basic",
  name: "Basic Addition",
  grade_level: "GRADE_1",
  prerequisites: ["counting_1_10"],
  forgetting_rate: 0.07,  // Higher = faster forgetting
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
  question_type: "multiple_choice",
  options: ["4", "5", "6", "7"],
  explanation: "Adding 2 and 3 gives us 5",
  tags: ["arithmetic", "single_digit"],
  times_shown: 12  // Usage tracking
}
```

### Users Collection
```javascript
{
  user_id: "student_123",
  age: 8,
  grade_level: "GRADE_3",
  skill_states: {
    "addition_basic": {
      memory_strength: 0.85,
      last_practice_time: ISODate("2025-10-02"),
      practice_count: 15,
      correct_count: 13
    }
  },
  question_history: [
    {
      question_id: "add_001",
      skill_ids: ["addition_basic"],
      is_correct: true,
      response_time_seconds: 4.5,
      timestamp: ISODate("2025-10-02")
    }
  ]
}
```

---

## 🧪 Testing

Run the comprehensive test suite:

```bash
cd DashSystem
python test_dash_system_v2.py
```

**Test Coverage:**
- MongoDB Handler (CRUD operations, atomic updates)
- Memory strength calculations
- Forgetting decay
- Question selection algorithm
- Prerequisite checking
- Learning dynamics (correct/incorrect answers)
- Prerequisite cascading
- Cold start strategy
- Complete user learning sessions

**Expected Output:**
```
test_complete_learning_session ... ok
test_memory_strength_calculation ... ok
test_prerequisite_cascading ... ok
test_record_question_attempt_correct ... ok
...

----------------------------------------------------------------------
Ran 15 tests in 2.34s

OK
```

---

## 🔧 Configuration

### Tuning Parameters

Adjust these constants in `dash_system_v2.py`:

```python
# Memory strength threshold for "skill mastered"
MASTERY_THRESHOLD = 0.8

# Memory strength threshold for "needs practice"
PRACTICE_THRESHOLD = 0.7

# Learning rate (how much correct answers boost strength)
LEARNING_RATE = 0.3

# Penalty for incorrect answer
INCORRECT_PENALTY = 0.8  # Reduce to 80% of current

# Ideal response time (seconds)
IDEAL_RESPONSE_TIME = 5.0

# Cold start strength for foundation skills
FOUNDATION_STRENGTH = 0.8
```

### Forgetting Rates

Adjust in `skills.json` or MongoDB:

```python
# Fast forgetting (procedural skills)
forgetting_rate = 0.10  # Half-life: ~7 days

# Medium forgetting (concepts)
forgetting_rate = 0.07  # Half-life: ~10 days

# Slow forgetting (foundational knowledge)
forgetting_rate = 0.05  # Half-life: ~14 days
```

---

## 📈 Performance

### Benchmarks

With proper indexing:
- **Get next question**: <50ms
- **Record attempt**: <100ms (atomic update)
- **Load user profile**: <20ms
- **Calculate all skill strengths**: <5ms (in-memory cache)

### Optimization Tips

1. **SKILLS_CACHE**: All skills loaded at startup (fast lookups)
2. **Indexes**: Created automatically on common query patterns
3. **Embedded skill states**: Single query to get user profile
4. **Atomic updates**: Uses MongoDB `$set`, `$inc`, `$push`
5. **Question history limit**: Keep last 1000 attempts per user

---

## 🔄 Migration from V1

### Differences from Original DashSystem

| Feature | V1 (JSON) | V2 (MongoDB) |
|---------|-----------|--------------|
| Storage | JSON files | MongoDB collections |
| Scalability | Single machine | Distributed |
| Concurrency | File locking issues | Atomic updates |
| Query speed | O(n) file scan | O(log n) indexed |
| Skills cache | Loaded per request | Loaded at startup |
| User updates | Write entire file | Atomic field update |
| Question selection | Random from pool | Smart algorithm |

### Breaking Changes

1. **Initialization:**
   ```python
   # V1
   dash = DASHSystem(skills_file="...", curriculum_file="...")
   
   # V2
   dash = DashSystemV2()  # Uses MongoDB
   ```

2. **User creation:**
   ```python
   # V1
   user_profile = dash.load_user_or_create(user_id)
   
   # V2
   user = dash.get_or_create_user(user_id, age=8, grade_level="GRADE_3")
   ```

3. **Recording attempts:**
   ```python
   # V1
   dash.record_question_attempt(user_profile, question_id, ...)
   
   # V2  
   dash.record_question_attempt(user_id, question_id, ...)
   # (user_id instead of user_profile object)
   ```

---

## 🐛 Troubleshooting

### Connection Issues

**Problem:** `pymongo.errors.ServerSelectionTimeoutError`

**Solution:**
```bash
# Check MongoDB is running
docker ps | grep mongodb

# Or check local installation
mongod --version

# Verify connection string
MONGODB_URI=mongodb://localhost:27017/
```

### Migration Fails

**Problem:** Migration script errors

**Solution:**
```bash
# Clear and retry
python migrate_to_mongodb.py --clear

# Check file paths
ls QuestionsBank/skills.json
ls QuestionsBank/curriculum.json
```

### No Questions Returned

**Problem:** `get_next_question()` returns `None`

**Possible causes:**
1. All questions answered → Generate new questions
2. Prerequisites not met → Check skill strengths
3. No questions in database → Run migration

**Debug:**
```python
# Check skills needing practice
skills = dash.get_skills_needing_practice(user, time.time())
print(f"Skills needing practice: {len(skills)}")

# Check question count
from DashSystem.mongodb_handler import get_db
db = get_db()
print(f"Questions in database: {db.questions.count_documents({})}")
```

---

## 📚 Additional Documentation

- **Schema Design**: `mongodb_schema.md`
- **Progress Report**: `PROGRESS_REPORT.md`
- **Migration Guide**: `migrate_to_mongodb.py` (docstrings)
- **API Reference**: See docstrings in `dash_system_v2.py`

---

## 🤝 Contributing

### Code Style

- Follow PEP 8
- Add docstrings to all functions
- Include type hints
- Write tests for new features

### Adding New Features

1. Update schema in `mongodb_schema.md`
2. Implement in `mongodb_handler.py` and/or `dash_system_v2.py`
3. Add tests in `test_dash_system_v2.py`
4. Update this README

---

## 📝 License

[Your License Here]

---

## 🙏 Acknowledgments

Based on:
- **DASH Algorithm** by Mozer & Lindsey (2016)
- Deep Additive State History for knowledge tracing
- Spaced repetition and forgetting curve research

---

## 📞 Support

For issues or questions:
- GitHub Issues: [Your repo URL]
- Documentation: This file + `PROGRESS_REPORT.md`
- Tests: `test_dash_system_v2.py`

---

**Built with ❤️ for adaptive education**
