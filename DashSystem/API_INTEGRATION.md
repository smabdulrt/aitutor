# API Integration Guide for DashSystem V2

This guide shows how to update existing API endpoints to use the new DashSystem V2.

---

## 🔄 Updating Existing API Endpoints

### Step 1: Update `dash_api.py`

The existing `DashSystem/dash_api.py` needs to be updated to use V2.

```python
"""
Updated API using DashSystem V2
"""

from flask import Flask, request, jsonify
from DashSystem.dash_system_v2 import DashSystemV2
import time

app = Flask(__name__)

# Initialize DashSystem V2 (singleton)
dash_system = DashSystemV2()

@app.route('/api/v2/user/create', methods=['POST'])
def create_user():
    """
    Create a new user with cold start strategy
    
    POST /api/v2/user/create
    Body: {
        "user_id": "student_123",
        "age": 8,
        "grade_level": "GRADE_3"
    }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        age = data.get('age')
        grade_level = data.get('grade_level')
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        # Create user
        user = dash_system.get_or_create_user(user_id, age, grade_level)
        
        return jsonify({
            "success": True,
            "user_id": user["user_id"],
            "created_at": str(user["created_at"]),
            "grade_level": user.get("grade_level"),
            "skills_initialized": len(user["skill_states"])
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/v2/user/<user_id>', methods=['GET'])
def get_user(user_id):
    """
    Get user profile with statistics
    
    GET /api/v2/user/{user_id}
    """
    try:
        # Get user statistics
        stats = dash_system.get_user_statistics(user_id)
        
        if not stats:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/v2/question/next', methods=['POST'])
def get_next_question():
    """
    Get next question for a student
    
    POST /api/v2/question/next
    Body: {
        "user_id": "student_123"
    }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        # Get next question
        question = dash_system.get_next_question(user_id)
        
        if not question:
            return jsonify({
                "message": "No questions available",
                "suggestion": "All skills are mastered or need question generation"
            }), 200
        
        # Format response
        response = {
            "question_id": question["question_id"],
            "content": question["content"],
            "question_type": question["question_type"],
            "difficulty": question["difficulty"],
            "skill_ids": question["skill_ids"],
            "skill_names": [
                dash_system.SKILLS_CACHE[sid].name 
                for sid in question["skill_ids"]
                if sid in dash_system.SKILLS_CACHE
            ]
        }
        
        # Add options if multiple choice
        if question["question_type"] == "multiple_choice":
            response["options"] = question.get("options", [])
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/v2/question/answer', methods=['POST'])
def submit_answer():
    """
    Submit answer to a question
    
    POST /api/v2/question/answer
    Body: {
        "user_id": "student_123",
        "question_id": "q_123",
        "skill_ids": ["addition_basic"],
        "answer": "5",
        "response_time": 8.5
    }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        question_id = data.get('question_id')
        skill_ids = data.get('skill_ids', [])
        student_answer = data.get('answer')
        response_time = data.get('response_time', 0.0)
        
        # Validate required fields
        if not all([user_id, question_id, student_answer]):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Get correct answer from database
        from DashSystem.mongodb_handler import get_db
        db = get_db()
        question_doc = db.questions.find_one({"question_id": question_id})
        
        if not question_doc:
            return jsonify({"error": "Question not found"}), 404
        
        # Check if answer is correct
        is_correct = (str(student_answer).strip().lower() == 
                     str(question_doc["answer"]).strip().lower())
        
        # Record the attempt
        affected_skills = dash_system.record_question_attempt(
            user_id=user_id,
            question_id=question_id,
            skill_ids=skill_ids,
            is_correct=is_correct,
            response_time=response_time
        )
        
        # Get updated skill strengths
        user = db.get_user(user_id)
        current_time = time.time()
        
        skill_updates = {}
        for skill_id in affected_skills:
            strength = dash_system.calculate_memory_strength(
                user, skill_id, current_time
            )
            skill_updates[skill_id] = {
                "name": dash_system.SKILLS_CACHE[skill_id].name,
                "memory_strength": round(strength, 3)
            }
        
        return jsonify({
            "success": True,
            "is_correct": is_correct,
            "correct_answer": question_doc["answer"],
            "explanation": question_doc.get("explanation", ""),
            "affected_skills_count": len(affected_skills),
            "skill_updates": skill_updates
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/v2/skills/weak', methods=['POST'])
def get_weak_skills():
    """
    Get skills that need practice
    
    POST /api/v2/skills/weak
    Body: {
        "user_id": "student_123",
        "threshold": 0.7
    }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        threshold = data.get('threshold', 0.7)
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        # Get user
        from DashSystem.mongodb_handler import get_db
        db = get_db()
        user = db.get_user(user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Get skills needing practice
        current_time = time.time()
        weak_skills = dash_system.get_skills_needing_practice(
            user, current_time, threshold
        )
        
        # Format response
        skills_list = []
        for skill_id, strength in weak_skills:
            skill = dash_system.SKILLS_CACHE[skill_id]
            skills_list.append({
                "skill_id": skill_id,
                "name": skill.name,
                "grade_level": skill.grade_level.name,
                "memory_strength": round(strength, 3),
                "priority": "high" if strength < 0.5 else "medium"
            })
        
        return jsonify({
            "count": len(skills_list),
            "skills": skills_list
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/v2/health', methods=['GET'])
def health_check():
    """Check API and database health"""
    try:
        from DashSystem.mongodb_handler import get_db
        db = get_db()
        stats = db.get_database_stats()
        
        return jsonify({
            "status": "healthy",
            "version": "2.0",
            "database": {
                "skills": stats["skills"],
                "questions": stats["questions"],
                "users": stats["users"]
            },
            "skills_cache_loaded": len(dash_system.SKILLS_CACHE)
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 503


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

---

## 📝 API Endpoint Reference

### 1. Create User
**POST** `/api/v2/user/create`

Request:
```json
{
  "user_id": "student_123",
  "age": 8,
  "grade_level": "GRADE_3"
}
```

Response:
```json
{
  "success": true,
  "user_id": "student_123",
  "created_at": "2025-10-02T19:00:00",
  "grade_level": "GRADE_3",
  "skills_initialized": 50
}
```

### 2. Get User Profile
**GET** `/api/v2/user/{user_id}`

Response:
```json
{
  "user_id": "student_123",
  "total_questions_answered": 15,
  "correct_answers": 12,
  "accuracy": 0.8,
  "skills_mastered": 5,
  "skills_needing_practice": 10,
  "skill_proficiency": {
    "addition_basic": {
      "name": "Basic Addition",
      "grade_level": "GRADE_1",
      "memory_strength": 0.85,
      "needs_practice": false
    }
  }
}
```

### 3. Get Next Question
**POST** `/api/v2/question/next`

Request:
```json
{
  "user_id": "student_123"
}
```

Response:
```json
{
  "question_id": "add_123",
  "content": "What is 7 + 5?",
  "question_type": "multiple_choice",
  "difficulty": 0.3,
  "skill_ids": ["addition_basic"],
  "skill_names": ["Basic Addition"],
  "options": ["10", "11", "12", "13"]
}
```

### 4. Submit Answer
**POST** `/api/v2/question/answer`

Request:
```json
{
  "user_id": "student_123",
  "question_id": "add_123",
  "skill_ids": ["addition_basic"],
  "answer": "12",
  "response_time": 5.5
}
```

Response:
```json
{
  "success": true,
  "is_correct": true,
  "correct_answer": "12",
  "explanation": "7 + 5 = 12",
  "affected_skills_count": 2,
  "skill_updates": {
    "addition_basic": {
      "name": "Basic Addition",
      "memory_strength": 0.87
    },
    "counting_1_10": {
      "name": "Counting 1-10",
      "memory_strength": 0.81
    }
  }
}
```

### 5. Get Weak Skills
**POST** `/api/v2/skills/weak`

Request:
```json
{
  "user_id": "student_123",
  "threshold": 0.7
}
```

Response:
```json
{
  "count": 3,
  "skills": [
    {
      "skill_id": "fractions_intro",
      "name": "Introduction to Fractions",
      "grade_level": "GRADE_3",
      "memory_strength": 0.45,
      "priority": "high"
    }
  ]
}
```

### 6. Health Check
**GET** `/api/v2/health`

Response:
```json
{
  "status": "healthy",
  "version": "2.0",
  "database": {
    "skills": 50,
    "questions": 500,
    "users": 25
  },
  "skills_cache_loaded": 50
}
```

---

## 🔌 Frontend Integration Example

### React Component Example

```typescript
// api/dashSystem.ts
const API_BASE = 'http://localhost:5000/api/v2';

export async function createUser(userId: string, age: number, gradeLevel: string) {
  const response = await fetch(`${API_BASE}/user/create`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId, age, grade_level: gradeLevel })
  });
  return response.json();
}

export async function getNextQuestion(userId: string) {
  const response = await fetch(`${API_BASE}/question/next`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId })
  });
  return response.json();
}

export async function submitAnswer(
  userId: string,
  questionId: string,
  skillIds: string[],
  answer: string,
  responseTime: number
) {
  const response = await fetch(`${API_BASE}/question/answer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: userId,
      question_id: questionId,
      skill_ids: skillIds,
      answer,
      response_time: responseTime
    })
  });
  return response.json();
}

export async function getUserStats(userId: string) {
  const response = await fetch(`${API_BASE}/user/${userId}`);
  return response.json();
}
```

### React Component Usage

```typescript
// components/QuestionView.tsx
import { useState, useEffect } from 'react';
import { getNextQuestion, submitAnswer } from '../api/dashSystem';

export function QuestionView({ userId }: { userId: string }) {
  const [question, setQuestion] = useState(null);
  const [answer, setAnswer] = useState('');
  const [startTime, setStartTime] = useState(Date.now());
  const [feedback, setFeedback] = useState(null);

  useEffect(() => {
    loadNextQuestion();
  }, []);

  async function loadNextQuestion() {
    const q = await getNextQuestion(userId);
    setQuestion(q);
    setStartTime(Date.now());
    setAnswer('');
    setFeedback(null);
  }

  async function handleSubmit() {
    const responseTime = (Date.now() - startTime) / 1000; // seconds
    
    const result = await submitAnswer(
      userId,
      question.question_id,
      question.skill_ids,
      answer,
      responseTime
    );
    
    setFeedback(result);
    
    // Load next question after 3 seconds
    setTimeout(loadNextQuestion, 3000);
  }

  if (!question) return <div>Loading...</div>;

  return (
    <div className="question-view">
      <h2>{question.content}</h2>
      
      {question.question_type === 'multiple_choice' ? (
        <div>
          {question.options.map(option => (
            <button
              key={option}
              onClick={() => setAnswer(option)}
              className={answer === option ? 'selected' : ''}
            >
              {option}
            </button>
          ))}
        </div>
      ) : (
        <input
          type="text"
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          placeholder="Your answer"
        />
      )}
      
      <button onClick={handleSubmit} disabled={!answer}>
        Submit
      </button>
      
      {feedback && (
        <div className={`feedback ${feedback.is_correct ? 'correct' : 'incorrect'}`}>
          <p>{feedback.is_correct ? '✅ Correct!' : '❌ Incorrect'}</p>
          <p>Answer: {feedback.correct_answer}</p>
          <p>{feedback.explanation}</p>
          <p>Skills updated: {feedback.affected_skills_count}</p>
        </div>
      )}
    </div>
  );
}
```

---

## 🚀 Deployment Checklist

### 1. Environment Setup
```bash
# Install dependencies
pip install -r DashSystem/requirements.txt

# Set environment variables
export MONGODB_URI=mongodb://your-prod-server:27017/
export OPENAI_API_KEY=your_key_here  # For LLM tagging
```

### 2. Database Migration
```bash
# Run migration to populate MongoDB
python DashSystem/migrate_to_mongodb.py

# Verify data
python -c "
from DashSystem.mongodb_handler import get_db
db = get_db()
print(db.get_database_stats())
"
```

### 3. Run Tests
```bash
# Run test suite
python DashSystem/test_dash_system_v2.py

# All tests should pass
```

### 4. Start API Server
```bash
# Development
python DashSystem/dash_api.py

# Production (with gunicorn)
gunicorn -w 4 -b 0.0.0.0:5000 DashSystem.dash_api:app
```

### 5. Health Check
```bash
curl http://localhost:5000/api/v2/health
```

---

## 🔒 Security Considerations

1. **Authentication**: Add JWT or session-based auth to all endpoints
2. **Rate Limiting**: Prevent abuse with rate limiting middleware
3. **Input Validation**: Validate all user inputs before processing
4. **MongoDB Security**: Use authentication, TLS, and network restrictions
5. **CORS**: Configure appropriate CORS headers for frontend

---

## 📊 Monitoring

### Key Metrics to Track

1. **Response Times**
   - `/question/next`: Should be <50ms
   - `/question/answer`: Should be <100ms

2. **Database Performance**
   - Query times
   - Connection pool usage
   - Index hit rates

3. **User Metrics**
   - Active users
   - Questions per session
   - Average accuracy
   - Skills mastered per week

### Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add to endpoints
logger = logging.getLogger('dash_api')
logger.info(f'User {user_id} answered question {question_id}: {is_correct}')
```

---

## 🎯 Next Steps

1. ✅ Implement API endpoints (use code above)
2. ✅ Test API with Postman/curl
3. ✅ Connect frontend to API
4. ✅ Deploy to staging environment
5. ✅ Run production tests
6. ✅ Deploy to production
7. ✅ Monitor and iterate

---

**API Integration Complete!** 🚀
