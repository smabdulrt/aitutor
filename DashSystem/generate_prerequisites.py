import json
import os
from collections import OrderedDict

def generate_prerequisites():
    """
    Parses curriculum.json to establish prerequisite chains and updates skills.json.

    Assumes:
    1. Skills within a grade are ordered sequentially.
    2. The first skill of a grade is a prerequisite for the second, and so on.
    3. The last skill of a grade is a prerequisite for the first skill of the next grade.
    """

    # Define the order of grades
    grade_order = [
        "K", "GRADE_1", "GRADE_2", "GRADE_3", "GRADE_4", "GRADE_5",
        "GRADE_6", "GRADE_7", "GRADE_8", "GRADE_9", "GRADE_10",
        "GRADE_11", "GRADE_12"
    ]

    # Construct file paths relative to the script's location
    script_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.join(script_dir, '..'))
    curriculum_path = os.path.join(project_root, "QuestionsBank/curriculum.json")
    skills_path = os.path.join(project_root, "QuestionsBank/skills.json")

    try:
        # Load the curriculum and skills files
        with open(curriculum_path, 'r') as f:
            curriculum_data = json.load(f)

        with open(skills_path, 'r') as f:
            skills_data = json.load(f, object_pairs_hook=OrderedDict)

    except FileNotFoundError as e:
        print(f"Error: Could not find file {e.filename}")
        return
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format - {e}")
        return

    print("Generating prerequisites based on curriculum structure...")

    # Clear all existing prerequisites to start fresh
    for skill_id in skills_data:
        skills_data[skill_id]['prerequisites'] = []

    last_skill_of_previous_grade = None

    for grade_key in grade_order:
        if grade_key in curriculum_data['grades']:
            grade_info = curriculum_data['grades'][grade_key]

            # Sort skills by the 'order' field
            sorted_skills = sorted(grade_info['skills'], key=lambda s: s['order'])

            if not sorted_skills:
                continue

            # Handle prerequisite from the previous grade
            first_skill_id = sorted_skills[0]['skill_id']
            if last_skill_of_previous_grade and first_skill_id in skills_data:
                skills_data[first_skill_id]['prerequisites'].append(last_skill_of_previous_grade)

            # Handle prerequisites within the current grade
            for i in range(len(sorted_skills) - 1):
                current_skill_id = sorted_skills[i]['skill_id']
                next_skill_id = sorted_skills[i+1]['skill_id']

                if next_skill_id in skills_data:
                    skills_data[next_skill_id]['prerequisites'].append(current_skill_id)

            # Update the last skill for the next iteration
            last_skill_of_previous_grade = sorted_skills[-1]['skill_id']

    # Save the updated skills data back to skills.json
    try:
        with open(skills_path, 'w') as f:
            json.dump(skills_data, f, indent=2)
        print(f"✅ Successfully updated prerequisites in {skills_path}")

        # Log the changes for verification
        for skill_id, skill_info in skills_data.items():
            if skill_info['prerequisites']:
                print(f"  - Skill '{skill_id}' now has prerequisites: {skill_info['prerequisites']}")

    except IOError as e:
        print(f"Error: Could not write to file {skills_path} - {e}")

if __name__ == "__main__":
    generate_prerequisites()