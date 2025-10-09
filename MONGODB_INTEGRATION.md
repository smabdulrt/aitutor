# MongoDB Integration for DASH System

This document explains the MongoDB integration for the AI Tutor DASH system.

## Overview

The DASH system has been upgraded to use MongoDB for:
- **Skills Template**: Master skills curriculum stored in MongoDB
- **User Profiles**: Student progress and skill states stored in MongoDB
- **Cold-Start Problem**: Automatic skill initialization based on grade level

## Architecture

### Before (JSON Files)
```
DashSystem
├── skills.json (local file)
└── Users/
    ├── user1.json
    ├── user2.json
    └── ...
```

### After (MongoDB)
```
MongoDB Database: aitutor
├── skills_template (collection)
│   ├── skill_1 (document)
│   ├── skill_2 (document)
│   └── ...
└── users (collection)
    ├── user_1 (document)
    ├── user_2 (document)
    └── ...
```

## Setup Instructions

### 1. Install MongoDB

**macOS (with Homebrew):**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Ubuntu/Debian:**
```bash
sudo apt-get install -y mongodb-org
sudo systemctl start mongod
```

**Windows:**
Download from [MongoDB Download Center](https://www.mongodb.com/try/download/community)

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `pymongo` - MongoDB driver
- `python-dotenv` - Environment configuration

### 3. Configure Environment

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` with your MongoDB connection details:
```env
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=aitutor
```

For MongoDB Atlas (cloud):
```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=aitutor
```

### 4. Initialize MongoDB Database

Run the setup script to migrate skills from JSON to MongoDB:
```bash
python3 setup_mongodb.py
```

This will:
- ✅ Check MongoDB connection
- ✅ Load skills.json
- ✅ Create `skills_template` collection
- ✅ Insert all skills as documents

## Usage

### Starting the System

The system automatically detects MongoDB availability:

```python
# With MongoDB (preferred)
dash = DASHSystem(use_mongodb=True)

# Without MongoDB (fallback to JSON files)
dash = DASHSystem(use_mongodb=False)
```

If MongoDB is not available, the system gracefully falls back to JSON file storage.

### Creating a New Student

When creating a new student with a grade level:
```python
user_profile = dash.load_user_or_create("student_123", grade_level=GradeLevel.GRADE_5)
```

This will:
1. Create a user document in MongoDB
2. Initialize all skills from the template
3. Mark skills below Grade 5 as "mastered" (memory_strength = 3.0)
4. Mark skills at or above Grade 5 as "not started" (memory_strength = 0.0)

**Cold-Start Problem Solved!** 🎉

### Frontend Integration

The Next Question button now:
1. ✅ Calls DASH API: `GET /next-question/{user_id}`
2. ✅ Receives personalized question based on skill gaps
3. ✅ Renders with Perseus math widgets
4. ✅ Maintains rich question display

**No more hardcoded questions!** The button connects to the intelligent DASH system.

## Collections Schema

### skills_template Collection

```json
{
  "_id": "addition_basic",
  "skill_id": "addition_basic",
  "name": "Basic Addition",
  "grade_level": "GRADE_1",
  "prerequisites": ["counting_1_10"],
  "forgetting_rate": 0.07,
  "difficulty": 0.0
}
```

### users Collection

```json
{
  "_id": "student_123",
  "user_id": "student_123",
  "created_at": 1234567890.123,
  "last_updated": 1234567890.456,
  "skill_states": {
    "counting_1_10": {
      "memory_strength": 3.0,
      "last_practice_time": null,
      "practice_count": 0,
      "correct_count": 0
    },
    "addition_basic": {
      "memory_strength": 0.5,
      "last_practice_time": 1234567890.789,
      "practice_count": 5,
      "correct_count": 3
    }
  },
  "question_history": [
    {
      "question_id": "q_123",
      "skill_ids": ["addition_basic"],
      "is_correct": true,
      "response_time_seconds": 45.2,
      "timestamp": 1234567890.789,
      "time_penalty_applied": false
    }
  ],
  "student_notes": {}
}
```

## Advantages of MongoDB

1. **Scalability**: Handles thousands of students easily
2. **Flexibility**: Easy to add new fields without migration
3. **Performance**: Indexed queries for fast lookups
4. **Cloud-Ready**: Works with MongoDB Atlas for production
5. **Atomic Operations**: Safe concurrent updates
6. **Backup/Restore**: Built-in database backup tools

## Fallback Behavior

If MongoDB is unavailable, the system automatically falls back to:
- JSON files for skills (`QuestionsBank/skills.json`)
- JSON files for users (`Users/{user_id}.json`)

**No breaking changes!** The system works with or without MongoDB.

## Development vs Production

### Development (Local MongoDB)
```env
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=aitutor_dev
```

### Production (MongoDB Atlas)
```env
MONGODB_URI=mongodb+srv://prod_user:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=aitutor_prod
```

## Troubleshooting

### MongoDB Connection Failed
```
❌ Failed to connect to MongoDB: ServerSelectionTimeoutError
⚠️  Falling back to local file storage
```

**Solution**: Ensure MongoDB is running:
```bash
# Check if MongoDB is running
sudo systemctl status mongod  # Linux
brew services list            # macOS

# Start MongoDB
sudo systemctl start mongod   # Linux
brew services start mongodb-community  # macOS
```

### Skills Not Loading
```
⚠️  No skills found in MongoDB, initializing from JSON...
```

**Solution**: Run the setup script:
```bash
python3 setup_mongodb.py
```

## Files Added

- `db_config.py` - MongoDB connection manager
- `mongo_skills_manager.py` - Skills template operations
- `mongo_user_manager.py` - User profile operations
- `setup_mongodb.py` - Database initialization script
- `.env.example` - Environment configuration template
- `requirements.txt` - Python dependencies

## Migration Guide

If you have existing JSON user files:

1. **Backup**: Copy the `Users/` folder
2. **Setup MongoDB**: Run `python3 setup_mongodb.py`
3. **Migrate Users**: (Optional) Create a migration script to import existing users

For now, new users will be created in MongoDB, and old JSON files remain as backup.

## Next Steps

- [ ] Migrate existing user profiles from JSON to MongoDB
- [ ] Add MongoDB indexes for performance
- [ ] Implement question storage in MongoDB
- [ ] Add MongoDB monitoring and logging
- [ ] Set up automated backups

---

**Questions?** Check the [MongoDB Documentation](https://docs.mongodb.com/) or contact the dev team.
