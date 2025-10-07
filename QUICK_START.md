# Quick Start - 3 Commands

## 1. Start Everything

```bash
./run_tutor.sh
```

## 2. Watch Calculations (New Terminal)

```bash
tail -f logs/dashsystem.log
```

## 3. Open Frontend

```
http://localhost:3000
```

---

## What You'll See

### Terminal (logs/dashsystem.log):
```
🎯 Applying cold start strategy for grade GRADE_3
✅ Cold start complete:
   - Below grade (0.9): 450 skills
   - Current grade (0.0): 500 skills
   - Above grade (-1 locked): 550 skills

🔄 RECORDING QUESTION ATTEMPT:
   Correct: True
   Response time: 5.20s

  🌳 Breadcrumb cascade:
     Updated 25 breadcrumb-related skills

✅ Successfully updated 29 skills
```

### Browser Console (F12):
```
✅ Answer submitted to DASH: {...}
   Affected 29 skills via cascade
   Current streak: 3
```

---

## That's It!

Answer questions and watch the DASH algorithm work in real-time in the terminal.

For detailed testing instructions, see `TESTING_GUIDE.md`
