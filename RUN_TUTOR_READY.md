# ✅ run_tutor.sh is Ready!

## What Was Fixed

Updated `run_tutor.sh` to use the correct Python path:
```bash
PYTHON_BIN="/Users/vandanchopra/Vandan_Personal_Folder/CODE_STUFF/Projects/venvs/aitutor/bin/python"
```

This ensures all backend services (MediaMixer, DashSystem API, SherlockED API) use the correct virtual environment.

---

## 🚀 How to Test

### Start Everything:

```bash
./run_tutor.sh
```

### Watch DASH Calculations (New Terminal):

```bash
tail -f logs/dashsystem.log
```

### Open Frontend:

```
http://localhost:3000
```

---

## What You'll See

### 1. In Terminal (run_tutor.sh output):
```
Using Python: /Users/vandanchopra/.../venvs/aitutor/bin/python
Starting Python backend... Logs -> logs/mediamixer.log
Starting DASH API server... Logs -> logs/dashsystem.log
Starting SherlockED Exam API server... Logs -> logs/sherlocked_exam.log
Starting Node.js frontend... Logs -> logs/frontend.log

📡 Service URLs:
  🌐 Frontend:           http://localhost:3000
  🔧 DASH API:           http://localhost:8000
  🕵️  SherlockED API:     http://localhost:8001
  📹 MediaMixer Command: ws://localhost:8765
  📺 MediaMixer Video:   ws://localhost:8766

Press Ctrl+C to stop.
```

### 2. In logs/dashsystem.log:
```
================================================================================
🚀 Starting DashSystem V2 API Server
================================================================================
📚 Loaded 54 skills
🌐 API will be available at: http://localhost:8000
📖 API docs available at: http://localhost:8000/docs
================================================================================

🎯 Applying cold start strategy for grade GRADE_3
✅ Cold start complete:
   - Below grade (0.9): 20 skills
   - Current grade (0.0): 18 skills
   - Above grade (-1 locked): 16 skills

🔄 RECORDING QUESTION ATTEMPT:
   Question: q_12345
   Skills: ['math_3_1.2.3.4']
   Correct: True
   Response time: 5.20s

  📝 Direct skill updates:
     [math_3_1.2.3.4] → 0.3000

  🌳 Breadcrumb cascade:
     [math_3_1.2.3.4] → 25 related skills
     Updated 25 breadcrumb-related skills

  📊 Total skills affected: 29
     - Direct: 1
     - Prerequisites: 3
     - Breadcrumb cascade: 25

✅ Successfully updated 29 skills for user student_demo
```

### 3. In Browser Console (F12):
```
User created: {user_id: "student_demo", grade_level: "GRADE_3", total_skills: 54}
DASH API response: {question_id: "...", content: "...", skill_ids: [...]}
✅ Answer submitted to DASH: {...}
   Affected 29 skills via cascade
   Current streak: 3
```

---

## ✅ DashSystem Integration Checklist

When you test, verify:

- [ ] All 4 services start (MediaMixer, DASH API, SherlockED, Frontend)
- [ ] Frontend loads at http://localhost:3000
- [ ] User `student_demo` is created automatically (check console)
- [ ] First question appears from DASH API
- [ ] Logs show cold start with 3 states (0.9, 0.0, -1)
- [ ] Submit button triggers DASH API call
- [ ] Browser console shows "Affected X skills via cascade"
- [ ] logs/dashsystem.log shows breadcrumb cascade calculations
- [ ] Next button fetches new question from DASH algorithm
- [ ] Response time is tracked and logged

---

## 🐛 If Something Goes Wrong

### No Questions Appear
**Problem**: MongoDB might not have questions loaded.

**Check**:
```bash
mongosh aitutor --eval "db.questions.countDocuments()"
```

**Fix**: Load questions from Khan Academy scraper.

### Port Already in Use
**Problem**: Previous run didn't clean up.

**Fix**:
```bash
lsof -ti:8000 | xargs kill -9
lsof -ti:8765 | xargs kill -9
lsof -ti:8766 | xargs kill -9
./run_tutor.sh
```

### API Errors in Logs
**Check**:
```bash
grep "❌" logs/dashsystem.log
```

### Frontend Not Loading
**Check**:
```bash
tail -f logs/frontend.log
```

---

## 🎯 What to Look For (DASH Integration)

### Cold Start Working:
```
🎯 Applying cold start strategy for grade GRADE_3
✅ Cold start complete:
   - Below grade (0.9): 20 skills    ← Skills assumed mastered
   - Current grade (0.0): 18 skills  ← Ready to learn
   - Above grade (-1 locked): 16 skills  ← Locked until Grade 3 mastered
```

### Breadcrumb Cascade Working:
```
🌳 Breadcrumb cascade:
     [math_3_1.2.3.4] → 25 related skills  ← This means it's working!
     Updated 25 breadcrumb-related skills
```

### Response Time Tracking:
```
Response time: 5.20s  ← Browser console
```

### Skill Updates:
```
📊 Total skills affected: 29  ← More than just 1 skill = cascade is working!
```

---

## 📝 Testing Steps

1. **Start**: `./run_tutor.sh`
2. **Watch**: `tail -f logs/dashsystem.log` (new terminal)
3. **Open**: http://localhost:3000
4. **Answer** a question
5. **Submit** and check:
   - Browser console: "Affected X skills"
   - Log file: Breadcrumb cascade details
6. **Click Next**
7. **Repeat** 5-10 times to see the algorithm adapt

---

## 🎉 Success!

If you see:
- ✅ Questions loading from API
- ✅ Breadcrumb cascade (20+ skills affected)
- ✅ Response time tracked
- ✅ Skills updating in MongoDB
- ✅ Grade progression working

**Then DashSystem V2 is fully integrated!** 🚀

---

Ready to test? Run `./run_tutor.sh` and watch the DASH algorithm in action!
