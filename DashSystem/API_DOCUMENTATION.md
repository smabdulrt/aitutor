# DashSystem V2 API Documentation

Complete REST API for the DashSystem V2 adaptive learning platform.

## Base URL

```
http://localhost:8000
```

## Interactive Documentation

Once the server is running, access the auto-generated interactive docs:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Endpoints

### 1. Health Check

**GET** `/`

Check if the API is running and get basic info.

**Response:**
```json
{
  "status": "ok",
  "service": "DashSystem V2 API",
  "version": "2.0.0",
  "total_skills": 1500
}
```

---

### 2. Create User

**POST** `/users/create`

Create a new user with three-state cold start strategy (0.9, 0.0, -1).

**Request Body:**
```json
{
  "user_id": "student_demo",
  "age": 8,
  "grade_level": "GRADE_3"
}
```

**Response:**
```json
{
  "success": true,
  "user_id": "student_demo",
  "grade_level": "GRADE_3",
  "total_skills": 1500
}
```

**Cold Start Behavior:**
- Skills below Grade 3: Set to 0.9 (assumed mastery)
- Skills at Grade 3: Set to 0.0 (ready to learn)
- Skills above Grade 3: Set to -1 (locked)

---

### 3. Get Next Question

**GET** `/next-question/{user_id}`

Get the next recommended question using intelligent DASH algorithm.

**Example Request:**
```
GET /next-question/student_demo
```

**Response (Perseus Format):**
```json
{
  "question_id": "q_12345",
  "content": "What is 7 + 8?",
  "type": "input-number",
  "answer": "15",
  "skill_ids": ["math_3_1.2.3.4"],
  "difficulty": 0.3,
  "explanation": "Add the ones place: 7 + 8 = 15",
  "hints": ["Try using your fingers", "7 + 3 = 10, then add 5 more"],
  "tags": ["addition", "single_digit", "basic"]
}
```

**Question Types:**
- `input-number`: Numeric answer
- `multiple-choice`: Multiple choice with options
- `input-text`: Text answer

---

### 4. Submit Answer

**POST** `/submit-answer`

Submit a student's answer and trigger breadcrumb cascade updates.

**Request Body:**
```json
{
  "user_id": "student_demo",
  "question_id": "q_12345",
  "skill_ids": ["math_3_1.2.3.4"],
  "is_correct": true,
  "response_time": 5.2
}
```

**Response:**
```json
{
  "success": true,
  "is_correct": true,
  "affected_skills_count": 25,
  "current_streak": 5,
  "total_questions_answered": 42
}
```

**Cascade Behavior:**
- Direct skill: Full update (30% boost or 20% penalty)
- Prerequisites: 5% boost if correct
- Breadcrumb-related skills:
  - Same concept: ±3%
  - Same topic: ±2%
  - Same grade: ±1%
  - Lower grades: ±3% (gap detection)

---

### 5. Get User Statistics

**GET** `/user/{user_id}/stats`

Get comprehensive statistics including skill proficiency.

**Example Request:**
```
GET /user/student_demo/stats
```

**Response:**
```json
{
  "user_id": "student_demo",
  "total_questions_answered": 42,
  "correct_answers": 35,
  "accuracy": 0.833,
  "skills_mastered": 120,
  "skills_needing_practice": 45,
  "skill_proficiency": {
    "math_3_1.2.3.4": {
      "name": "Single-digit addition",
      "grade_level": "GRADE_3",
      "memory_strength": 0.85,
      "needs_practice": false
    }
    // ... more skills
  }
}
```

---

### 6. Get User Profile

**GET** `/user/{user_id}/profile`

Get user profile with learning progress summary.

**Example Request:**
```
GET /user/student_demo/profile
```

**Response:**
```json
{
  "user_id": "student_demo",
  "grade_level": "GRADE_3",
  "age": 8,
  "total_skills": 1500,
  "mastered_skills": 120,
  "locked_skills": 800,
  "learning_skills": 580,
  "total_questions_answered": 42,
  "correct_answers": 35,
  "accuracy": 0.833,
  "created_at": "2025-10-05T10:30:00"
}
```

---

## Running the Server

### Start the API server:

```bash
python DashSystem/dash_api.py
```

### Or with auto-reload for development:

```bash
uvicorn DashSystem.dash_api:app --reload --port 8000
```

---

## Frontend Integration Example

### React/Next.js Example:

```typescript
// Create user
const createUser = async (userId: string, gradeLevel: string) => {
  const response = await fetch('http://localhost:8000/users/create', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: userId,
      grade_level: gradeLevel,
      age: parseInt(gradeLevel.split('_')[1]) + 5
    })
  });
  return response.json();
};

// Get next question
const getNextQuestion = async (userId: string) => {
  const response = await fetch(`http://localhost:8000/next-question/${userId}`);
  return response.json();
};

// Submit answer
const submitAnswer = async (data: AnswerData) => {
  const response = await fetch('http://localhost:8000/submit-answer', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  return response.json();
};
```

---

## Error Responses

All endpoints return standard HTTP error codes:

- `404`: Resource not found (user or question)
- `500`: Internal server error
- `422`: Validation error (malformed request)

**Example Error:**
```json
{
  "detail": "User not found"
}
```

---

## Testing

### Quick Test with curl:

```bash
# Health check
curl http://localhost:8000/

# Create user
curl -X POST http://localhost:8000/users/create \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test_student","grade_level":"GRADE_3","age":8}'

# Get next question
curl http://localhost:8000/next-question/test_student

# Get user profile
curl http://localhost:8000/user/test_student/profile
```

---

## CORS Configuration

The API allows requests from:
- `http://localhost:3000` (React default)
- `http://localhost:3001`

To add more origins, edit `dash_api.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://your-domain.com"],
    ...
)
```
