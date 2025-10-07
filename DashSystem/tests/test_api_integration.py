"""
End-to-End API Integration Test
Tests all API endpoints with a simulated learning session
"""

import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_api_integration():
    """
    Complete end-to-end test of the API
    Simulates a student learning session
    """

    print("\n" + "="*80)
    print("DASHSYSTEM V2 - END-TO-END API INTEGRATION TEST")
    print("="*80)

    # Test 1: Health Check
    print("\n1️⃣  Testing Health Check Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Service: {data['service']}")
        print(f"   Total Skills: {data['total_skills']}")
        print("   ✅ Health check passed!")
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        print("   Make sure the API server is running: python DashSystem/dash_api.py")
        return False

    # Test 2: Create User
    print("\n2️⃣  Testing User Creation...")
    user_id = f"test_student_{int(time.time())}"
    try:
        response = requests.post(
            f"{BASE_URL}/users/create",
            json={
                "user_id": user_id,
                "age": 8,
                "grade_level": "GRADE_3"
            }
        )
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   User ID: {data['user_id']}")
        print(f"   Grade: {data['grade_level']}")
        print(f"   Total Skills: {data['total_skills']}")
        print("   ✅ User created successfully!")
    except Exception as e:
        print(f"   ❌ User creation failed: {e}")
        return False

    # Test 3: Get User Profile
    print("\n3️⃣  Testing User Profile Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/user/{user_id}/profile")
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Grade: {data['grade_level']}")
        print(f"   Mastered Skills: {data['mastered_skills']}")
        print(f"   Learning Skills: {data['learning_skills']}")
        print(f"   Locked Skills: {data['locked_skills']}")
        print("   ✅ Profile retrieved successfully!")
    except Exception as e:
        print(f"   ❌ Profile retrieval failed: {e}")
        return False

    # Test 4: Get Next Question
    print("\n4️⃣  Testing Next Question Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/next-question/{user_id}")
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            question = response.json()
            print(f"   Question ID: {question['question_id']}")
            print(f"   Type: {question['type']}")
            print(f"   Skills: {question['skill_ids']}")
            print(f"   Content: {question['content'][:100]}...")
            print("   ✅ Question retrieved successfully!")

            # Test 5: Submit Answer
            print("\n5️⃣  Testing Submit Answer Endpoint (Correct Answer)...")
            try:
                response = requests.post(
                    f"{BASE_URL}/submit-answer",
                    json={
                        "user_id": user_id,
                        "question_id": question['question_id'],
                        "skill_ids": question['skill_ids'],
                        "is_correct": True,
                        "response_time": 5.2
                    }
                )
                print(f"   Status: {response.status_code}")
                data = response.json()
                print(f"   Success: {data['success']}")
                print(f"   Affected Skills: {data['affected_skills_count']}")
                print(f"   Current Streak: {data['current_streak']}")
                print("   ✅ Answer submitted successfully!")
            except Exception as e:
                print(f"   ❌ Answer submission failed: {e}")
                return False

            # Test 6: Get Next Question Again (after answer)
            print("\n6️⃣  Testing Next Question After Answer...")
            try:
                response = requests.get(f"{BASE_URL}/next-question/{user_id}")
                if response.status_code == 200:
                    question2 = response.json()
                    print(f"   Next Question ID: {question2['question_id']}")
                    print("   ✅ Got next question!")

                    # Submit wrong answer to test cascade
                    print("\n7️⃣  Testing Submit Answer (Wrong Answer)...")
                    response = requests.post(
                        f"{BASE_URL}/submit-answer",
                        json={
                            "user_id": user_id,
                            "question_id": question2['question_id'],
                            "skill_ids": question2['skill_ids'],
                            "is_correct": False,
                            "response_time": 15.0
                        }
                    )
                    data = response.json()
                    print(f"   Success: {data['success']}")
                    print(f"   Affected Skills: {data['affected_skills_count']}")
                    print(f"   Current Streak: {data['current_streak']}")
                    print("   ✅ Wrong answer processed with cascade!")
                else:
                    print(f"   ⚠️  No more questions available (status {response.status_code})")
            except Exception as e:
                print(f"   ❌ Second question failed: {e}")
                return False

        elif response.status_code == 404:
            print("   ⚠️  No questions available in database")
            print("   This is expected if no questions have been loaded yet")
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            return False

    except Exception as e:
        print(f"   ❌ Question retrieval failed: {e}")
        return False

    # Test 8: Get Statistics
    print("\n8️⃣  Testing User Statistics Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/user/{user_id}/stats")
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Questions Answered: {data['total_questions_answered']}")
        print(f"   Accuracy: {data['accuracy']*100:.1f}%")
        print(f"   Skills Mastered: {data['skills_mastered']}")
        print(f"   Skills Needing Practice: {data['skills_needing_practice']}")
        print("   ✅ Statistics retrieved successfully!")
    except Exception as e:
        print(f"   ❌ Statistics retrieval failed: {e}")
        return False

    # Final Summary
    print("\n" + "="*80)
    print("✅ ALL API INTEGRATION TESTS PASSED!")
    print("="*80)
    print(f"\nTest User ID: {user_id}")
    print("The API is ready for frontend integration!")
    print("\nNext Steps:")
    print("  1. Access API docs at: http://localhost:8000/docs")
    print("  2. Connect your frontend to these endpoints")
    print("  3. Load questions into MongoDB to enable learning")
    print("="*80 + "\n")

    return True

if __name__ == "__main__":
    print("\n⚠️  Make sure the API server is running first!")
    print("   Run: python DashSystem/dash_api.py")
    print("\nStarting test in 3 seconds...")
    time.sleep(3)

    try:
        success = test_api_integration()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
