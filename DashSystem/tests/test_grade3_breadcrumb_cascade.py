"""
Test Grade 3 Student with Breadcrumb Cascade Logic
Tests the three-state system (0.9, 0.0, -1) and breadcrumb cascade
"""

import time
from DashSystem.dash_system_v2 import DashSystemV2, create_dash_system
from DashSystem.mongodb_handler import get_db

def test_grade3_student():
    """Test a Grade 3 student scenario"""

    print("\n" + "="*80)
    print("TESTING GRADE 3 STUDENT WITH BREADCRUMB CASCADE")
    print("="*80)

    # Create DashSystem with real database
    print("\n📚 Initializing DashSystem V2...")
    dash = create_dash_system()

    # Check if we have skills loaded
    print(f"✅ Loaded {len(dash.SKILLS_CACHE)} skills from database")

    if len(dash.SKILLS_CACHE) == 0:
        print("❌ ERROR: No skills found in database!")
        print("   Make sure MongoDB has Khan Academy skills loaded.")
        return False

    # Show sample of skill IDs to verify breadcrumb format
    print("\n📋 Sample skill IDs:")
    for i, skill_id in enumerate(list(dash.SKILLS_CACHE.keys())[:5]):
        skill = dash.SKILLS_CACHE[skill_id]
        print(f"   {i+1}. {skill_id} - {skill.name} (Grade {skill.grade_level.value})")

    # Create Grade 3 student
    print("\n👤 Creating Grade 3 student...")
    user = dash.get_or_create_user(
        user_id="grade3_test_student",
        age=8,
        grade_level="GRADE_3"
    )

    if not user:
        print("❌ Failed to create user")
        return False

    print(f"✅ User created: {user['user_id']}")
    print(f"   Grade level: {user.get('grade_level', 'Unknown')}")
    print(f"   Total skills: {len(user['skill_states'])}")

    # Check initial state distribution
    print("\n📊 Initial skill state distribution:")
    locked_count = 0
    foundation_count = 0
    learning_count = 0

    for skill_id, state in user['skill_states'].items():
        strength = state['memory_strength']
        if strength < 0:
            locked_count += 1
        elif strength > 0.8:
            foundation_count += 1
        else:
            learning_count += 1

    print(f"   Foundation (0.9): {foundation_count} skills (Grades K-2)")
    print(f"   Learning (0.0): {learning_count} skills (Grade 3)")
    print(f"   Locked (-1): {locked_count} skills (Grades 4+)")

    # Get next question
    print("\n🎯 Getting next question...")
    current_time = time.time()
    question = dash.get_next_question("grade3_test_student", current_time)

    if not question:
        print("⚠️  No questions available")
        return False

    print(f"✅ Question selected:")
    print(f"   ID: {question['question_id']}")
    print(f"   Skills: {question.get('skill_ids', [])}")
    print(f"   Content: {question.get('content', 'N/A')[:100]}...")

    # Test breadcrumb cascade with WRONG answer
    print("\n🔄 Recording WRONG answer (to test cascade)...")
    skill_ids = question.get('skill_ids', [])

    if not skill_ids:
        print("⚠️  Question has no skill_ids")
        return False

    # Show skill info before update
    print(f"\n📝 Analyzing skill: {skill_ids[0]}")
    skill = dash.SKILLS_CACHE.get(skill_ids[0])
    if skill:
        print(f"   Name: {skill.name}")
        print(f"   Grade: {skill.grade_level.value}")

    # Get breadcrumb related skills BEFORE update
    print(f"\n🌳 Finding breadcrumb-related skills...")
    related = dash.get_breadcrumb_related_skills(skill_ids[0])
    print(f"   Found {len(related)} related skills")

    if len(related) > 0:
        print(f"   Sample related skills (first 5):")
        for i, (rel_skill_id, cascade_rate) in enumerate(list(related.items())[:5]):
            rel_skill = dash.SKILLS_CACHE.get(rel_skill_id)
            if rel_skill:
                print(f"      {i+1}. {rel_skill_id} - {rel_skill.name}")
                print(f"         Cascade rate: {cascade_rate*100:.1f}%")

    # Record wrong answer
    affected_skills = dash.record_question_attempt(
        user_id="grade3_test_student",
        question_id=question['question_id'],
        skill_ids=skill_ids,
        is_correct=False,  # WRONG answer
        response_time=10.0
    )

    print(f"\n✅ Recorded question attempt")
    print(f"   Total skills affected: {len(affected_skills)}")

    # Verify cascade happened
    print(f"\n📊 Verifying breadcrumb cascade effect:")
    updated_user = dash.db.get_user("grade3_test_student")

    # Check direct skill
    direct_skill_state = updated_user['skill_states'][skill_ids[0]]
    print(f"   Direct skill [{skill_ids[0]}]:")
    print(f"      New strength: {direct_skill_state['memory_strength']:.4f}")
    print(f"      Practice count: {direct_skill_state['practice_count']}")

    # Check if any breadcrumb-related skills were updated
    if len(related) > 0:
        sample_related = list(related.keys())[0]
        related_state = updated_user['skill_states'].get(sample_related)
        if related_state:
            print(f"\n   Sample related skill [{sample_related}]:")
            print(f"      Strength: {related_state['memory_strength']:.4f}")
            print(f"      (Should be slightly reduced due to cascade)")

    # Test with CORRECT answer
    print("\n" + "="*80)
    print("🔄 Recording CORRECT answer (to test positive cascade)...")
    print("="*80)

    # Get another question
    question2 = dash.get_next_question("grade3_test_student", time.time())

    if question2:
        print(f"✅ Next question: {question2['question_id']}")
        print(f"   Skills: {question2.get('skill_ids', [])}")

        affected_skills2 = dash.record_question_attempt(
            user_id="grade3_test_student",
            question_id=question2['question_id'],
            skill_ids=question2.get('skill_ids', []),
            is_correct=True,  # CORRECT answer
            response_time=5.0
        )

        print(f"\n✅ Skills affected by correct answer: {len(affected_skills2)}")
    else:
        print("⚠️  No more questions available")

    # Final statistics
    print("\n" + "="*80)
    print("📈 FINAL STATISTICS")
    print("="*80)

    stats = dash.get_user_statistics("grade3_test_student")
    print(f"Total questions answered: {stats['total_questions_answered']}")
    print(f"Correct answers: {stats['correct_answers']}")
    print(f"Accuracy: {stats['accuracy']*100:.1f}%")
    print(f"Skills mastered (≥0.8): {stats['skills_mastered']}")
    print(f"Skills needing practice (<0.7): {stats['skills_needing_practice']}")

    print("\n" + "="*80)
    print("✅ GRADE 3 STUDENT TEST COMPLETE")
    print("="*80)

    return True

if __name__ == "__main__":
    try:
        success = test_grade3_student()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ TEST FAILED WITH ERROR:")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
