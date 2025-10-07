# Testing Guide - DashSystem V2 with Frontend

## 🚀 Quick Start

### Step 1: Start Everything

```bash
cd /Users/vandanchopra/Vandan_Personal_Folder/CODE_STUFF/Projects/aitutor
./run_tutor.sh
```

You'll see:
```
Starting Python backend... Logs -> logs/mediamixer.log
Starting DASH API server... Logs -> logs/dashsystem.log
Starting SherlockED Exam API server... Logs -> logs/sherlocked_exam.log
Starting Node.js frontend... Logs -> logs/frontend.log
```

### Step 2: Watch the Calculations (In a New Terminal)

```bash
cd /Users/vandanchopra/Vandan_Personal_Folder/CODE_STUFF/Projects/aitutor
tail -f logs/dashsystem.log
```

You'll see **LIVE calculations** like:
```
📚 Loading skills into SKILLS_CACHE...
✅ Loaded 1500 skills into SKILLS_CACHE

🎯 Applying cold start strategy for grade GRADE_3
✅ Cold start complete:
   - Below grade (0.9): 450 skills
   - Current grade (0.0): 500 skills
   - Above grade (-1 locked): 550 skills

📋 GETTING SKILLS NEEDING PRACTICE (threshold=0.7):
  📊 CALC [math_3_1.2.3.4]:
     - base_strength: 0.0000
     - time_elapsed: 0.00s (0.00h)
     - final (clamped): 0.0000

🔄 RECORDING QUESTION ATTEMPT:
   Question: q_12345
   Skills: ['math_3_1.2.3.4']
   Correct: True
   Response time: 5.20s

  🌳 Breadcrumb cascade:
     [math_3_1.2.3.4] → 25 related skills
     Updated 25 breadcrumb-related skills

  📊 Total skills affected: 29
     - Direct: 1
     - Prerequisites: 3
     - Breadcrumb cascade: 25

✅ Successfully updated 29 skills for user student_demo
```

### Step 3: Open the Frontend

Open your browser to: **http://localhost:3000**

## 🧪 What to Test

### Test 1: Initial Load
- [ ] Frontend loads without errors
- [ ] User `student_demo` is created automatically
- [ ] First question appears
- [ ] Console shows: `User created: {user_id: "student_demo", grade_level: "GRADE_3"}`

### Test 2: Answer a Question Correctly
1. **Answer the question correctly**
2. **Click "Submit"**
3. **Check Browser Console** (F12 → Console):
   ```
   ✅ Answer submitted to DASH: {...}
      Affected 29 skills via cascade
      Current streak: 1
   ```
4. **Check Terminal** (logs/dashsystem.log):
   - See breadcrumb cascade updating 20-30 skills
   - See memory strength changes
5. **Click "Next"**
6. **Verify** you get a new question

### Test 3: Answer Incorrectly
1. **Answer the question incorrectly**
2. **Click "Submit"**
3. **Check Browser Console**:
   ```
   ✅ Answer submitted to DASH: {...}
      Affected 25 skills via cascade
      Current streak: 0
   ```
4. **Check Terminal**:
   - See **negative cascade** (skills going down by 1-3%)
   - See memory strength decrease
5. **Click "Next"**
6. **Verify** you might get a similar/easier question

### Test 4: Speed Test
1. **Answer quickly** (< 5 seconds)
2. **Submit**
3. **Check Console**: `Response time: 3.2 seconds`
4. **Answer slowly** (> 10 seconds)
5. **Submit**
6. **Check Console**: `Response time: 15.8 seconds`
7. **Verify** in logs that response time affects the boost

### Test 5: Grade Progression
After answering ~20-30 questions correctly:
1. **Watch logs for**:
   ```
   🎉 GRADE UNLOCK! All Grade 3 skills mastered (≥0.8)
   🔓 Unlocking Grade 4 (500 skills)
   ```
2. **Verify** you start getting Grade 4 questions

## 📊 What You're Seeing in the Logs

### Cold Start (First Load)
```
🎯 Applying cold start strategy for grade GRADE_3
✅ Cold start complete:
   - Below grade (0.9): 450 skills    ← Assumed mastery
   - Current grade (0.0): 500 skills  ← Ready to learn
   - Above grade (-1 locked): 550 skills  ← Locked
```

### Question Selection
```
📋 GETTING SKILLS NEEDING PRACTICE (threshold=0.7):
  ✅ [math_3_1.2.3.4] needs practice (strength=0.0000 < 0.7)

  🎯 Priority order (top 5):
     1. [math_3_1.2.3.4] Addition - strength=0.0000, grade=3
     2. [math_3_1.2.3.5] Subtraction - strength=0.0000, grade=3
     ...
```

### Answer Submission (Correct)
```
🔄 RECORDING QUESTION ATTEMPT:
   Correct: True
   Response time: 5.20s

  📝 Direct skill updates:
     [math_3_1.2.3.4] → 0.3000  ← 30% boost

  🔗 Prerequisite cascade:
     Updated 3 prerequisite skills

  🌳 Breadcrumb cascade:
     [math_3_1.2.3.4] → 25 related skills
     Same concept (3%): 8 skills
     Same topic (2%): 10 skills
     Same grade (1%): 5 skills
     Lower grades (3%): 2 skills
```

### Answer Submission (Wrong)
```
🔄 RECORDING QUESTION ATTEMPT:
   Correct: False
   Response time: 10.50s

  📝 Direct skill updates:
     [math_3_1.2.3.4] → 0.2400  ← 20% penalty (was 0.3, now 0.24)

  🌳 Breadcrumb cascade:
     [math_3_1.2.3.4] → 25 related skills
     Negative cascade: All related skills drop by 1-3%
```

## 🔍 Debugging

### No Questions Appear
**Check**: Are there questions in MongoDB?
```bash
mongosh aitutor --eval "db.questions.countDocuments()"
```

If 0, you need to load questions first.

### API Errors
**Check API logs**:
```bash
tail -f logs/dashsystem.log | grep "❌"
```

### Frontend Not Loading
**Check frontend logs**:
```bash
tail -f logs/frontend.log
```

### MongoDB Not Running
```bash
brew services start mongodb-community
```

## 📈 Success Criteria

You know it's working when:

✅ Questions load from the API
✅ Submit triggers cascade (25+ skills affected)
✅ Browser console shows skill counts and streak
✅ Terminal shows detailed calculations
✅ Wrong answers decrease strength
✅ Correct answers increase strength
✅ Related skills update via breadcrumb cascade
✅ Response time is tracked

## 🎯 Advanced Testing

### Test Different Students
Edit `RendererComponent.tsx` line 18:
```typescript
const [userId] = useState("student_alice"); // Different student
```

### Test Different Grades
Edit `RendererComponent.tsx` line 33:
```typescript
grade_level: 'GRADE_5' // Try different grade
```

### Watch Specific Skills
In logs, grep for specific skill:
```bash
tail -f logs/dashsystem.log | grep "math_3_1.2.3.4"
```

## 📝 Notes

- **First load** creates the user automatically
- **Each submit** updates 20-40 skills (cascade!)
- **Response time** affects the learning boost
- **Streaks** are tracked automatically
- **Grade unlock** happens automatically when mastered

---

**Ready to test!** 🚀

Run `./run_tutor.sh` and watch the magic happen in `tail -f logs/dashsystem.log`
