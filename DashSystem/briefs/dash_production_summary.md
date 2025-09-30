Here is a short, actionable outline of the work required.

**A FastAPI based System:**

*   **DB Schema:** Define and create the `skills`, `questions`, and `users` collections in MongoDB.
*   **Data Migration:** Write scripts to move existing curriculum and user data into the new MongoDB collections.
*   **Code Refactor:** Rewrite the `DASHSystem` class to connect to MongoDB instead of loading local files.
*   **Skills Cache:** Implement the in-memory `SKILLS_CACHE` to load all skills on application startup.
*   **State Updates:** Build the Python function to calculate new skill states and perform the atomic MongoDB `updateOne` call.
*   **Skill Recommendation:** Code the logic to calculate skill probabilities and identify the next skills to practice.
*   **Question Fetching:** Implement the efficient MongoDB `findOne` query to select the next unseen question.
*   **LLM Tagging:** Integrate an LLM client to programmatically generate tags for new questions.
*   **Curriculum Workflow:** Develop the human-in-the-loop system for generating and approving new skills from `learning_path` data.
*   **System Testing:** Write unit and integration tests for all database functions and user-facing logic.