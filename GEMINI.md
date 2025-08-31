
Always use: /Users/vandanchopra/Vandan_Personal_Folder/CODE_STUFF/Projects/venvs/aitutor/bin/python to run
lets look at the file for our To-dos and wrap then up one by one. Keep making the human test each task manually and getting an OK from them before you mark it [DONE] and decide to move on.

------ TO DO ------
1. QUESTIONS TEMPLATE: Look at /Users/vandanchopra/Vandan_Personal_Folder/CODE_STUFF/Projects/aitutor/prototypes/perseus -- This is khan academy's questions display template. It's a nice clean approach. However, i don't want to use their code base. I'd rather use this as a starting point and create my own code base. I like the clean formatting they use, so lets retain that. Lets crate our own version of this. 

    **Continuity Note (Self):** Phase 1 of the SherlockED system is complete and has been manually verified by the user. The core backend architecture, API, and frontend rendering system are in place for our initial three widget types (multiple-choice, free-response, numeric-input). The next step is to begin **Phase 2: Iterative Expansion with Advanced Widgets**, starting with **Sprint 1: Classification and Ordering Widgets**.

    Here is the detailed to-do list, in the order I will perform the work:
        
        [DONE]Phase 1: Build and Test the Core Widget & Skill System
            * Goal: To build a robust, reusable system for rendering basic interactive questions and processing their answers to update user skills. This phase will deliver a complete, end-to-end product for our three core
                question types.
            1. Architect the Backend for Multiple Widget Types:[DONE]
                * Action: I will update the Question data model in the DASH system to include a question_type field (e.g., "multiple-choice") and a flexible widget_data field to hold all the unique information a specific widget
                    needs.
            2. Populate a Rich, Multi-Type Curriculum:
                * Action: I will significantly expand the curriculum.json file. I will add 10 new `multiple-choice` questions, 10 new `free-response` questions, and 10 new `numeric-input` questions, distributing them across
                    various skills.
            3. Implement a Smart Answer-Validation API: [DONE]
                * Action: I will create a single, intelligent POST /submit-answer API endpoint. This endpoint will use a new check_answer method in the DASH system that reads the question's type and applies the correct validation
                    logic for our initial three types.
            4. Build the `SherlockED` Frontend Renderer: [DONE]
                * Action: I will create the main SherlockED React component. This component will act as a "widget dispatcher"—its primary job is to read the question_type from the API data and dynamically render the correct widget
                    component.
            5. Develop the Initial Set of Core Widgets: [DONE]
                * Action: I will build the first three fundamental interactive widgets: MultipleChoiceDisplay.tsx, FreeResponseDisplay.tsx, and NumericInputDisplay.tsx.
                * Action: I will implement the full user interaction loop within SherlockED, handling answer submission to the API and displaying "Correct" or "Incorrect" feedback.
            6. Integrate and Verify the Core System:[DONE]
                * Action: I will replace the old question display component with the new SherlockED component in the main app layout.
                * Action: I will ask you to perform a full manual test of the core system with our three initial widget types to ensure the entire loop is working perfectly.

[DONE] 2. IXL Skill Expansion:
here is what i want you to do. it's going to be a big task. I want you to read all the 
  files in @prototypes/IXL and @prototypes/KhanAcademy and create the skills and learning 
  path the the AI tutor needs to follow for math. make sure you think hard about the 
  prerequisites for each skill and also put a meaningful forgetting_rate and difficulty for 
  each skill. {'Math':"trigonometry_advanced": {
      "skill_id": "trigonometry_advanced",
      "name": "Advanced Trigonometry",
      "grade_level": "GRADE_11",
      "prerequisites": ["trigonometry_basic"],
      "forgetting_rate": 0.17,
      "difficulty": 0.0,
      "description": "Advanced trigonometric identities and equations"
    }} -- and then save it in a json for aiTutor. It might be a lot of thinking to do, so if 
  you need to break the task up into multiple smaller tasks please feel to do so.

  NOTES:
  There are skill names with \n in them
   even though it's not needed: eg. 2_step_subtraction_word_problem\ns_within_100 2) There 
  are skills with no pre-requisites. 3) and then there are skills with a long list of 
  prerequisites, and above_and_below has a pre-requisite called above_and_below, which 
  doesn't make any sense. 4) Also, above_and_below has a pre-requisite "classify_shapes" 
  which isn't even a skill in our list. 5) Both khan and IXL have their skills mentioned in 
  a certain order, which is reflective of a meaningful learning path. Our list doesn't have 
  any of that logic. I suggest, we do this extraction all over again and do it like this: 
  first extract the skills from the file by grade, eg grade 1 grade 2 etc. and add a field 
  that says 'IXL' or 'Khan'. then we use an LLM to make sense of it, remove all the 
  duplicates, create a meaningful order in which they are taught. Once all this is done, 
  then we have a last step where we add pre-requisites (which always comes from the skills 
  in our list...and are hopefully taught before the current skill. Also, since we're using a
   dict, and a dict is natively unorderd, we need some way field to suggest what ought to be
   taught first and what next.

3. Curriculum Builder:
We are going to build two python scripts that call two different LLMs. 
LLM 1 will look at the topic, look at our sherlockED (/Users/vandanchopra/Vandan_Personal_Folder/CODE_STUFF/Projects/aitutor/frontend/src/components/SherlockED) templates and create 5 questions in the format required by sherlockED. we're going to create 1 question per skill per template.
LLM 2: will look at the question and try and answer the question. if it gets the answer right, the question is retained, else it is junked. question bank.
QuestionBank will have a subfolder called Math, in which each skill will have it's own json file, which will have it's own questions.

This curriculum builder script will run one skill at a time. it will also keep a tab on which skills have already been processed in an input json. and will take a variable input of n, where n is the number of skills it needs to work on. if n = -1, then it will do ALL skills.

All junked questions will be put in the junked subfolder, again by skill.

4. SherlockED Template Expansion
        Phase 2: Iterative Expansion with Advanced Widgets
            * Goal: To iteratively build out the full suite of advanced, Perseus-style widgets, leveraging the proven foundation from Phase 1.
            Sprint 1: Classification and Ordering Widgets (categorizer, sorter, orderer, matcher)
            Sprint 2: Graphing and Data Visualization Widgets (grapher, plotter, interactive-graph, number-line)
            Sprint 3: Advanced Mathematical Input Widgets (expression, matrix)
            * Actions for Each Sprint:
                1. Backend: Add 10 new sample questions to curriculum.json for each of the new widget types in the sprint.
                2. Frontend: Create the corresponding React widget components.
                3. Integration: Update the SherlockED renderer and the backend check_answer method to support the new widgets.

        Phase 3: Final Polish
            7. Comprehensive System Review:
                * Action: After all sprints are complete, I will ask you to perform a final, comprehensive test of the entire system, verifying that every single widget type functions correctly from end to end.