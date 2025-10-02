# MongoDB Schema Design for DashSystem v2

## Collections

### 1. Skills Collection
Stores all available skills in the curriculum with their properties.

```javascript
{
  "_id": ObjectId,
  "skill_id": "addition_basic",  // Unique identifier
  "name": "Basic Addition",
  "grade_level": "GRADE_1",
  "prerequisites": ["counting_1_10"],  // Array of skill_id strings
  "forgetting_rate": 0.07,
  "difficulty": 0.3,
  "created_at": ISODate,
  "updated_at": ISODate
}
```

**Indexes:**
- `skill_id`: unique index for fast lookups
- `grade_level`: for filtering by grade
- `prerequisites`: multi-key index for prerequisite queries

---

### 2. Questions Collection
Stores all questions with their associated skills and metadata.

```javascript
{
  "_id": ObjectId,
  "question_id": "add_basic_001",  // Unique identifier
  "skill_ids": ["addition_basic"],  // Array of skill IDs this question tests
  "content": "What is 2 + 3?",
  "answer": "5",
  "difficulty": 0.3,
  "question_type": "multiple_choice",  // or "open_ended", "true_false"
  "options": ["4", "5", "6", "7"],  // For multiple choice
  "explanation": "Adding 2 and 3 gives us 5",
  "tags": ["arithmetic", "single_digit", "no_carry"],  // LLM-generated tags
  "source": "curriculum",  // or "generated"
  "parent_question_id": null,  // For variations, points to original
  "created_at": ISODate,
  "updated_at": ISODate,
  "times_shown": 0,  // Track usage
  "avg_correctness": 0.0  // Track difficulty calibration
}
```

**Indexes:**
- `question_id`: unique index
- `skill_ids`: multi-key index for finding questions by skill
- `tags`: multi-key index for tag-based queries
- `{skill_ids: 1, times_shown: 1}`: compound index for smart selection

---

### 3. Users Collection
Stores user profiles, skill states, and question history.

```javascript
{
  "_id": ObjectId,
  "user_id": "student_123",  // Unique identifier
  "created_at": ISODate,
  "last_updated": ISODate,
  "age": 8,  // For cold start problem
  "grade_level": "GRADE_3",  // Current grade
  
  // Embedded skill states for fast access
  "skill_states": {
    "addition_basic": {
      "memory_strength": 0.85,
      "last_practice_time": ISODate,
      "practice_count": 15,
      "correct_count": 13,
      "last_updated": ISODate
    },
    "subtraction_basic": {
      "memory_strength": 0.72,
      "last_practice_time": ISODate,
      "practice_count": 10,
      "correct_count": 7,
      "last_updated": ISODate
    }
    // ... one entry per skill
  },
  
  // Question history stored as array
  "question_history": [
    {
      "question_id": "add_basic_001",
      "skill_ids": ["addition_basic"],
      "is_correct": true,
      "response_time_seconds": 4.5,
      "timestamp": ISODate,
      "time_penalty_applied": false
    }
  ],
  
  // Student notes and metadata
  "student_notes": {
    "learning_style": "visual",
    "struggles_with": ["word_problems"],
    "excels_at": ["mental_math"]
  }
}
```

**Indexes:**
- `user_id`: unique index
- `{"skill_states.last_practice_time": 1}`: for finding skills needing review
- `{"question_history.question_id": 1}`: for checking if question was answered
- `grade_level`: for cohort analysis

---

## Query Patterns

### 1. Load All Skills (Startup - populate SKILLS_CACHE)
```javascript
db.skills.find({})
```

### 2. Get User with Skill States
```javascript
db.users.findOne({user_id: "student_123"})
```

### 3. Find Next Question
```javascript
// Find unanswered question for a skill
db.questions.findOne({
  skill_ids: "addition_basic",
  question_id: {$nin: user.question_history.map(h => h.question_id)},
  times_shown: {$lt: 100}  // Avoid overused questions
}).sort({times_shown: 1})  // Prefer less-shown questions
```

### 4. Update Skill State (Atomic)
```javascript
db.users.updateOne(
  {user_id: "student_123"},
  {
    $set: {
      "skill_states.addition_basic.memory_strength": 0.90,
      "skill_states.addition_basic.last_practice_time": ISODate(),
      "skill_states.addition_basic.last_updated": ISODate(),
      last_updated: ISODate()
    },
    $inc: {
      "skill_states.addition_basic.practice_count": 1,
      "skill_states.addition_basic.correct_count": 1
    },
    $push: {
      question_history: {
        $each: [questionAttempt],
        $slice: -1000  // Keep last 1000 attempts
      }
    }
  }
)
```

### 5. Find Skills Needing Review
```javascript
// This would be done in Python using current_time calculations
// MongoDB query finds all skill states for a user
db.users.findOne(
  {user_id: "student_123"},
  {"skill_states": 1}
)
```

---

## Data Migration Strategy

### Phase 1: Export Existing Data
1. Read `skills.json` → transform → insert into MongoDB `skills` collection
2. Read `curriculum.json` → extract questions → insert into `questions` collection
3. Read `Users/*.json` → transform → insert into `users` collection

### Phase 2: Validate
1. Count documents in each collection
2. Verify indexes created
3. Test sample queries

### Phase 3: Switch Code
1. Update DashSystem to use MongoDB instead of JSON files
2. Keep JSON files as backup

---

## Cold Start Strategy

When a new user is created:
1. Get user's age/grade level
2. Initialize all skills with `memory_strength = 0.0`
3. For skills below user's grade: set `memory_strength = 0.8` (8/10)
4. For skills at user's grade: set `memory_strength = 0.0` (needs assessment)
5. For skills above user's grade: set `memory_strength = 0.0` (too advanced)

This creates a "zone of proximal development" where the system focuses on current grade-level skills while acknowledging mastery of prerequisite skills.

---

## Forgetting Implementation

The forgetting calculation happens in Python, not in MongoDB:

```python
def calculate_memory_strength(user_id: str, skill_id: str, current_time: float) -> float:
    """Calculate current memory strength with decay"""
    state = user.skill_states[skill_id]
    
    if state.last_practice_time is None:
        return state.memory_strength
    
    time_elapsed = current_time - state.last_practice_time
    forgetting_rate = skills[skill_id].forgetting_rate
    
    # Exponential decay
    decayed_strength = state.memory_strength * math.exp(-forgetting_rate * time_elapsed)
    
    return decayed_strength
```

This allows us to query MongoDB for the base memory strength, then calculate decay in real-time without storing decayed values.

---

## Performance Considerations

1. **SKILLS_CACHE**: Load all skills into memory at startup (< 1000 skills, ~100KB)
2. **User Skill States**: Embedded in user document for single-query access
3. **Question History**: Limited to last 1000 attempts per user
4. **Indexes**: Carefully chosen to support common query patterns
5. **Atomic Updates**: Use `updateOne` with `$set`, `$inc`, `$push` for consistency

---

## Future Enhancements

1. **Sharding**: Shard by `user_id` if user base grows large
2. **Question Analytics Collection**: Track question performance across all users
3. **Learning Path Recommendations**: Pre-compute recommended paths
4. **Caching Layer**: Redis for frequently accessed user states
