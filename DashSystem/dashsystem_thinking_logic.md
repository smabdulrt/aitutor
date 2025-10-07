# DASH System V2: Core Logic & Design Decisions

## Table of Contents
1. [Cold-Start Problem & Solution](#1-cold-start-problem--solution)
2. [Next Question Selection Logic](#2-next-question-selection-logic)
3. [Score Update Logic (Breadcrumb Cascade)](#3-score-update-logic-breadcrumb-cascade)
4. [Grade Progression System](#4-grade-progression-system)
5. [Implementation Details](#5-implementation-details)

---

## 1. Cold-Start Problem & Solution

### The Problem
When a new student joins the platform, we face a fundamental challenge:

**Scenario**: 13-year-old student (8th grade) joins
**Challenge**: We don't know their actual knowledge level across 8 years of curriculum

**Naive approaches fail:**
- ❌ **Start from Grade 1**: Wastes time on content they already know
- ❌ **Start from Grade 8**: They might have foundational gaps
- ❌ **Diagnostic test**: Takes too long, frustrating for eager students

### Our Solution: Three-State Initialization

We use **age → grade mapping** with three distinct states:

| Grade Level | Memory Strength | Meaning | Can Practice? |
|-------------|----------------|---------|---------------|
| **Below student grade** | **0.9** | Assumed mastery | ✅ If cascade pulls it down |
| **Current grade** | **0.0** | Ready to learn | ✅ Yes |
| **Above student grade** | **-1** | Locked | ❌ Until current mastered |

#### Example: 8th Grade Student

```python
# Grade 1-7 skills
skill_states = {
    "math_7_1.1.1.1": {"memory_strength": 0.9},  # Assumed mastered
    "math_6_1.2.3.1": {"memory_strength": 0.9},
    # ... all below-grade = 0.9
}

# Grade 8 skills
skill_states = {
    "math_8_1.1.1.1": {"memory_strength": 0.0},  # Start here
    "math_8_2.3.1.1": {"memory_strength": 0.0},
    # ... all current-grade = 0.0
}

# Grade 9+ skills
skill_states = {
    "math_9_1.1.1.1": {"memory_strength": -1},  # Locked
    "math_10_1.1.1.1": {"memory_strength": -1},
    # ... all above-grade = -1
}
```

### Why This Works

**1. Students start at appropriate level**
- System immediately offers Grade 8 questions
- No wasted time on content they likely know

**2. Automatic gap detection via cascade**
- Student struggles with Grade 8 algebra
- Cascade system lowers related Grade 7 skills from 0.9 → 0.6
- Grade 7 falls below threshold (0.7)
- System automatically offers Grade 7 for remediation

**3. Prevents premature advancement**
- Can't jump to Grade 9 until Grade 8 is mastered (all skills ≥ 0.8)
- Locked state (-1) ensures proper progression

**4. Self-correcting over time**
- Initial 0.9 assumption is just a starting point
- Real performance data quickly replaces assumptions
- Within 10-20 questions, system has accurate profile

---

## 2. Next Question Selection Logic

### Algorithm Overview

The system selects the optimal question through a multi-step process:

```
┌─────────────────────────────────────┐
│ 1. Calculate Memory Strength        │
│    - Apply exponential decay        │
│    - M(t) = M(t0) * exp(-λ * Δt)   │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ 2. Filter Candidate Skills          │
│    - 0.0 ≤ strength < 0.7           │
│    - Prerequisites met (≥ 0.7)      │
│    - Exclude locked (-1)            │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ 3. Sort by Priority                 │
│    - Primary: Weakest first         │
│    - Secondary: Highest grade       │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ 4. Check for Grade Unlock           │
│    - If no weak skills found        │
│    - AND current grade mastered     │
│    - THEN unlock next grade         │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ 5. Find Unanswered Question         │
│    - For top priority skill         │
│    - That student hasn't seen       │
└─────────────────────────────────────┘
```

### Detailed Step-by-Step

#### Step 1: Calculate Memory Strength
```python
# For each skill, apply forgetting curve
M(t) = M(t0) * exp(-λ * Δt)

where:
  M(t0) = memory strength at last practice
  λ = forgetting rate (default: 0.1)
  Δt = time elapsed since last practice
```

**Special case for locked skills:**
```python
if base_strength < 0:
    return -1  # Don't apply decay, keep locked
```

#### Step 2: Filter Candidates
```python
candidates = []
for skill_id, strength in skill_scores.items():
    # Exclude locked skills
    if strength < 0:
        continue

    # Exclude mastered skills
    if strength >= 0.7:
        continue

    # Check prerequisites
    if not all_prerequisites_met(skill_id, threshold=0.7):
        continue

    candidates.append((skill_id, strength))
```

#### Step 3: Sort by Priority
```python
# Two-level sort:
candidates.sort(key=lambda x: (
    x[1],                                    # Memory strength (ascending)
    -SKILLS_CACHE[x[0]].grade_level.value   # Grade level (descending)
))
```

**Why this order?**
- **Weakest first**: Addresses most critical knowledge gaps
- **Higher grade tie-breaker**: When two skills equally weak, choose more advanced

**Example:**
```
Grade 8 skill (strength 0.3) vs Grade 7 skill (strength 0.3)
→ Choose Grade 8 (student is ready for grade-level content)

Grade 8 skill (strength 0.2) vs Grade 8 skill (strength 0.5)
→ Choose 0.2 (address weakest gap first)
```

#### Step 4: Grade Unlock Mechanism

**Condition**: No weak skills found AND all current-grade skills ≥ 0.8

```python
def should_unlock_next_grade(user, current_grade):
    # Check: Are all current-grade skills mastered?
    current_grade_skills = get_skills_by_grade(current_grade)
    all_mastered = all(
        strength >= 0.8
        for strength in current_grade_skills.values()
    )

    if all_mastered:
        # Unlock next grade
        unlock_grade(current_grade + 1)
        return True

    return False
```

**Implementation:**
```python
# Find all skills with strength = -1 in next grade
next_grade_skills = [
    skill_id for skill_id, strength in skill_scores.items()
    if strength == -1 and skill.grade_level.value == current_grade + 1
]

# Change them all from -1 to 0.0
for skill_id in next_grade_skills:
    update_skill_strength(skill_id, new_strength=0.0)
```

#### Step 5: Find Question

```python
# Try each candidate in priority order
for skill_id, strength in candidates:
    question = find_unanswered_question(
        skill_ids=[skill_id],
        answered_ids=user.answered_question_ids,
        max_times_shown=100
    )

    if question:
        return question  # Found!

# No questions available
return None
```

---

## 3. Score Update Logic (Breadcrumb Cascade)

### The Core Innovation

When a student answers a question, we update **multiple skills simultaneously** based on the **breadcrumb hierarchy**.

### Example Scenario

**Student answers question for**: `math_8_1.2.3.2`
**Breadcrumb**: `8.1.2.3.2` (Grade.Topic.Concept.SubConcept.Exercise)
**Answer**: ❌ WRONG

### Three Levels of Updates

#### Level 1: Direct Skill (Full Update)
```python
skill_id = "math_8_1.2.3.2"
current_strength = 0.5

if is_correct:
    # Boost: 30% of gap to perfection
    boost = 0.3 * (1.0 - current_strength)
    new_strength = 0.5 + (0.3 * 0.5) = 0.65
else:
    # Penalty: 20% reduction
    new_strength = 0.5 * 0.8 = 0.4
```

#### Level 2: Prerequisites (Future Feature)
```python
# Only the immediate prerequisite
prereq_id = "math_8_1.2.3.1"
prereq_strength = 0.7

if is_correct:
    # Small boost: 5% of gap
    boost = 0.05 * (1.0 - prereq_strength)
    new_strength = 0.7 + (0.05 * 0.3) = 0.715
else:
    # No penalty on wrong answer
    new_strength = 0.7  # unchanged
```

#### Level 3: Breadcrumb Cascade (NEW)

**Parse the breadcrumb**: `8.1.2.3.2`

**Find related skills at each hierarchy level:**

1. **Same concept** (8.1.2.3.x): ±3% cascade
   ```python
   related_skills = [
       "math_8_1.2.3.1",  # strength 0.7 → wrong answer → 0.679
       "math_8_1.2.3.3",  # strength 0.6 → wrong answer → 0.582
   ]
   cascade_rate = 0.03
   ```

2. **Same topic** (8.1.2.x.x): ±2% cascade
   ```python
   related_skills = [
       "math_8_1.2.1.1",  # strength 0.8 → wrong answer → 0.784
       "math_8_1.2.2.1",  # strength 0.75 → wrong answer → 0.735
   ]
   cascade_rate = 0.02
   ```

3. **Same grade** (8.x.x.x.x): ±1% cascade
   ```python
   related_skills = [
       "math_8_1.1.1.1",  # strength 0.9 → wrong answer → 0.891
       "math_8_2.1.1.1",  # strength 0.85 → wrong answer → 0.8415
   ]
   cascade_rate = 0.01
   ```

4. **Lower grades** (7.1.2.3.x): Small cascade for gap detection
   ```python
   # Critical for automatic remediation!
   related_skills = [
       "math_7_1.2.3.1",  # strength 0.9 → wrong answer → 0.873
       "math_7_1.2.3.2",  # strength 0.9 → wrong answer → 0.873
   ]
   cascade_rate = 0.03

   # After several wrong answers on Grade 8:
   # Grade 7 skills drop below 0.7 threshold
   # System automatically offers Grade 7 for remediation!
   ```

### Formula for Cascade Updates

```python
def apply_breadcrumb_cascade(skill_id, is_correct, current_strength, cascade_rate):
    if is_correct:
        # Positive cascade (boost)
        boost = cascade_rate * (1.0 - current_strength)
        new_strength = current_strength + boost
    else:
        # Negative cascade (penalty)
        penalty = cascade_rate
        new_strength = current_strength * (1.0 - penalty)

    return clamp(new_strength, 0.0, 1.0)
```

### Why This Works

**1. Natural Knowledge Reinforcement**
- Practicing algebra (8.1.2.3.2) reinforces related algebra skills (8.1.2.x.x)
- Practicing any math reinforces general math proficiency (8.x.x.x.x)
- Mirrors how human learning actually works

**2. Automatic Gap Detection**
- Student struggles with Grade 8
- Cascade lowers Grade 7 from 0.9 → 0.6
- System detects gap and offers remediation
- No explicit "diagnostic mode" needed

**3. Cross-Grade Adaptation**
- System seamlessly moves between grades based on performance
- Strong student: Grade 7 stays high, Grade 8 progresses quickly
- Struggling student: Grade 7 drops, system adapts

**4. Prevents Gaming**
- Can't artificially boost scores by practicing unrelated skills
- Cascade is small enough to require genuine mastery
- Prerequisite gates still enforce proper sequencing

---

## 4. Grade Progression System

### The Student Journey

```
Grade 7 (Assumed Mastered)
  strength = 0.9
  status = "Can review if cascade triggers"
         │
         ▼
Grade 8 (Current)
  strength = 0.0
  status = "Active learning"
         │
         ├─ Student practices ──> Strengths increase
         │
         ├─ Struggles? ──> Grade 7 cascade pulls it back
         │
         └─ All Grade 8 ≥ 0.8? ──> Unlock Grade 9
                                          │
                                          ▼
Grade 9 (Was Locked)
  strength = -1 → 0.0
  status = "Newly unlocked, ready to learn"
```

### Unlock Criteria

**Condition for unlocking Grade N+1:**
```python
# All skills in Grade N must be ≥ 0.8
all_skills_mastered = all(
    strength >= 0.8
    for skill_id, strength in grade_N_skills.items()
)

# AND no weak skills requiring practice
no_weak_skills = len(get_skills_needing_practice()) == 0

if all_skills_mastered and no_weak_skills:
    unlock_grade(N + 1)
```

### Preventing Premature Advancement

**Why 0.8 threshold instead of 0.7?**
- 0.7 = "acceptable" (can pass prerequisite check)
- 0.8 = "mastered" (ready to build on this foundation)
- Ensures solid foundation before advancing

**What if student has one weak skill at 0.75?**
```python
# Cannot unlock until ALL skills ≥ 0.8
Grade 8 skills:
  - Algebra: 0.95 ✓
  - Geometry: 0.85 ✓
  - Fractions: 0.75 ✗  ← Blocks advancement

# System keeps offering fraction questions
# Until student reaches 0.8
```

---

## 5. Implementation Details

### Key Functions

#### `_apply_cold_start_strategy(user_id, grade_level)`
```python
for skill_id, skill in SKILLS_CACHE.items():
    if skill.grade_level < user_grade:
        skill_updates[skill_id] = 0.9
    elif skill.grade_level == user_grade:
        skill_updates[skill_id] = 0.0
    else:  # Above user grade
        skill_updates[skill_id] = -1
```

#### `calculate_memory_strength(user, skill_id, current_time)`
```python
base_strength = skill_state["memory_strength"]

# Handle locked skills
if base_strength < 0:
    return -1

# Apply forgetting curve
if last_practice:
    strength = base_strength * exp(-λ * Δt)
else:
    strength = base_strength

return clamp(strength, 0.0, 1.0)
```

#### `get_skills_needing_practice(user, current_time)`
```python
candidates = []

for skill_id, strength in all_skills:
    # Filter locked
    if strength < 0:
        continue

    # Filter mastered
    if strength >= 0.7:
        continue

    # Check prerequisites
    if prerequisites_met(skill_id):
        candidates.append((skill_id, strength))

# Check unlock condition
if not candidates and current_grade_mastered():
    unlock_next_grade()
    # Re-run to get newly unlocked skills
    return get_skills_needing_practice(user, current_time)

return sorted(candidates, key=sort_priority)
```

#### `get_breadcrumb_related_skills(skill_id)` (NEW)
```python
# Parse: "math_8_1.2.3.2" → breadcrumb "8.1.2.3.2"
subject, grade, breadcrumb = parse_skill_id(skill_id)
parts = breadcrumb.split('.')  # ['8', '1', '2', '3', '2']

related = {}

# Same concept (8.1.2.3.x)
pattern = f"{subject}_{grade}_{'.'.join(parts[:4])}.*"
related[pattern] = 0.03

# Same topic (8.1.2.x.x)
pattern = f"{subject}_{grade}_{'.'.join(parts[:3])}.*"
related[pattern] = 0.02

# Same grade (8.x.x.x.x)
pattern = f"{subject}_{grade}_*"
related[pattern] = 0.01

# Lower grades (7.1.2.3.x) - for gap detection
if grade > 1:
    pattern = f"{subject}_{grade-1}_{'.'.join(parts[:4])}.*"
    related[pattern] = 0.03

return related
```

#### `record_question_attempt(user_id, question_id, skill_ids, is_correct)`
```python
affected_skills = {}

# 1. Direct skills
for skill_id in skill_ids:
    new_strength = update_skill_from_answer(skill_id, is_correct)
    affected_skills[skill_id] = new_strength

# 2. Prerequisites (future)
for skill_id in skill_ids:
    for prereq_id in get_prerequisites(skill_id):
        new_strength = apply_prerequisite_boost(prereq_id, is_correct)
        affected_skills[prereq_id] = new_strength

# 3. Breadcrumb cascade (NEW)
for skill_id in skill_ids:
    related = get_breadcrumb_related_skills(skill_id)
    for related_id, cascade_rate in related.items():
        new_strength = apply_cascade(related_id, is_correct, cascade_rate)
        affected_skills[related_id] = new_strength

# Atomic update to MongoDB
bulk_update_skill_states(user_id, affected_skills)
```

---

## Summary

### The Complete Picture

1. **Student joins** → Cold start initializes (0.9, 0.0, -1)
2. **Student practices** → DASH selects optimal question
3. **Student answers** → Breadcrumb cascade updates multiple skills
4. **Struggles detected** → Lower grades automatically pulled in
5. **Mastery achieved** → Next grade unlocks
6. **Cycle repeats** → Continuous adaptive learning

### Key Innovations

- **Three-state system**: Simple but effective cold start
- **Breadcrumb cascade**: Natural knowledge reinforcement
- **Automatic remediation**: No manual intervention needed
- **Seamless grade transition**: Student never "stuck" or "rushed"

### Future Enhancements

- Explicit prerequisite tracking (coming in future version)
- Multi-skill questions (combine multiple breadcrumbs)
- Difficulty-based question selection
- Time-of-day learning patterns
- Collaborative filtering ("students like you struggled with...")

---

*This document represents the core logic of DASH System V2 as of the hierarchical skill implementation.*
