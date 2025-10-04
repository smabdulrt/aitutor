# Teaching Assistant System - Project Requirements

## Project Overview
Build a proactive Teaching Assistant (TA) that works alongside Gemini 2.0 (Adam) to enhance the AI tutoring experience. The TA provides historical context, emotional intelligence, and performance tracking to make Adam the best teacher in the world.

## Current System Architecture
- **Frontend**: React app with Gemini Live API via WebSocket
- **Gemini Integration**: genai-live-client.ts handles streaming text/audio
- **Backend**: DashSystem (adaptive learning), MediaMixer (video streaming), QuestionGenerator
- **No TA, Vector DB, or Knowledge Graph currently exists**

## Functional Requirements

### Requirement 1: Gemini Stream Capture
- **Description**: Capture all streaming text from Gemini's WebSocket responses
- **Input**: Text content from genai-live-client.ts `content` events
- **Output**: Real-time text stream to Python backend via WebSocket
- **Example**:
  ```
  Input: Gemini says "Let's start with a simpler question..."
  Output: Text captured in Python backend, logged with timestamp
  ```

### Requirement 2: Vector Database (Long-term Memory)
- **Description**: Store all tutoring interactions for semantic retrieval
- **Input**: Gemini responses, student questions, conversation context
- **Output**: ChromaDB vector store with embedding-based retrieval
- **Technical Details**:
  - Embeddings: sentence-transformers (all-MiniLM-L6-v2)
  - Index by: session_id, timestamp, topic, emotional_state
  - Retrieval: Similarity search with k=3 default
- **Example**:
  ```
  Input: Store("Student struggled with 2x+4=10")
  Query: "Find similar fraction struggles"
  Output: [Previous session on 2x+3=7, Session on x/2=5, ...]
  ```

### Requirement 3: Knowledge Graph
- **Description**: Graph-based representation of skills, topics, and learning paths
- **Input**: Skills from DashSystem, student progress, topic relationships
- **Output**: NetworkX graph with Neo4j persistence (optional)
- **Graph Structure**:
  - Nodes: Topics, Skills, Questions, Student Progress States
  - Edges: Prerequisites, Similarities, Learning Paths
- **Example**:
  ```
  Query: find_prerequisite_gaps(student_id="adam", skill="fractions")
  Output: [Missing: "division basics", Weak: "number sense"]
  ```

### Requirement 4: Basic TA Core Features
- **Description**: Fundamental proactive tutoring features
- **Features**:
  1. **Greet on Startup**: Inject warm greeting prompt to Gemini
  2. **Greet on Close**: Inject session summary and closure prompt
  3. **Inactivity Monitor**: Detect 60s of no questions → nudge student
- **Input**: Session events, activity timestamps
- **Output**: Prompts injected to Gemini via WebSocket
- **Example**:
  ```
  Session Start:
  TA → Gemini: "Adam, greet Emma warmly and ask about her day"

  60s silence:
  TA → Gemini: "Adam, student seems quiet. Check if they're still there"
  ```

### Requirement 5: Emotional Intelligence
- **Description**: Detect student emotions and consult Adam for response strategy
- **Input**: Camera frames, student transcript, voice tone (optional)
- **Output**: Emotional state + Adam's recommended approach
- **Process**:
  1. TA detects emotion (frustrated, confused, confident, disengaged)
  2. TA asks Adam: "Student appears frustrated. How would you handle this?"
  3. TA forwards Adam's strategy (no additional TA intelligence)
- **Example**:
  ```
  Detected: Student frustrated (3 wrong answers, sighing)
  TA → Adam: "Student seems frustrated after 3 errors. Your approach?"
  Adam → TA: "Simplify to prerequisite skill, offer encouragement"
  TA → Gemini: "Adam, proceed with your approach: [strategy]"
  ```

### Requirement 6: Historical Context Provider
- **Description**: Surface relevant past context from vector DB and knowledge graph
- **Input**: Current topic, student_id
- **Output**: Past struggles + skill gaps injected to Adam before response
- **Retrieval Strategy**:
  - Vector DB: Similarity search for past struggles with current topic
  - Knowledge Graph: Find prerequisite gaps for current skill
- **Example**:
  ```
  Current Topic: "Solving 3x+5=20"

  TA → Adam (before Adam responds):
  "Historical Context:
   - Past Struggles: Student struggled with 2x+4=10 (Session 2024-01-15)
   - Skill Gaps: Weak on 'inverse operations' prerequisite
   Consider this when crafting your response."
  ```

### Requirement 7: Performance Tracking
- **Description**: Track student metrics and suggest improvements to Adam
- **Metrics**:
  - Questions answered (total, per session)
  - Accuracy rate (%)
  - Time per question (avg, median)
  - Hints needed
  - Emotional state trends
  - Skill mastery delta (improvement rate)
- **Output**: Real-time metrics + suggestions to Adam
- **Example**:
  ```
  Session Metrics:
  - Accuracy: 45% (below baseline 65%)
  - Avg time/question: 180s (above baseline 120s)
  - Hints needed: 8 (high)

  TA → Adam:
  "Performance Alert: Student struggling (45% accuracy vs 65% baseline).
   Suggest: Reduce difficulty, increase scaffolding, check for prerequisite gaps"
  ```

## Technical Specifications

### Project Structure
```
backend/
├── teaching_assistant/
│   ├── __init__.py
│   ├── ta_core.py              # Main TA orchestrator
│   ├── emotional_intelligence.py
│   ├── context_provider.py
│   ├── performance_tracker.py
│   └── activity_monitor.py
├── memory/
│   ├── __init__.py
│   ├── vector_store.py         # ChromaDB interface
│   └── knowledge_graph.py      # NetworkX/Neo4j interface
├── stream_capture/
│   ├── __init__.py
│   └── gemini_capture.py       # WebSocket bridge
└── tests/
    ├── test_ta_core.py
    ├── test_emotional_intelligence.py
    ├── test_context_provider.py
    ├── test_performance_tracker.py
    ├── test_vector_store.py
    └── test_knowledge_graph.py
```

### Dependencies
- `chromadb>=0.4.0` - Vector database
- `networkx>=3.0` - Knowledge graph
- `neo4j>=5.0` - Graph persistence (optional)
- `sentence-transformers>=2.2.0` - Embeddings
- `websockets>=12.0` - Stream capture
- `pytest>=7.0` - Testing
- `pytest-asyncio>=0.21.0` - Async testing

### API Interfaces

#### TA Core API
```python
class TeachingAssistant:
    async def greet_on_startup(student_name: str) -> None
    async def greet_on_close(session_summary: dict) -> None
    async def monitor_activity() -> None  # Runs every 10s
    async def inject_prompt(prompt: str) -> None
```

#### Vector Store API
```python
class VectorStore:
    def store(text: str, metadata: dict) -> str
    def similarity_search(query: str, k: int, filter: dict) -> List[dict]
    def get_by_session(session_id: str) -> List[dict]
```

#### Knowledge Graph API
```python
class KnowledgeGraph:
    def add_skill_node(skill_id: str, data: dict) -> None
    def add_prerequisite_edge(from_skill: str, to_skill: str) -> None
    def find_prerequisite_gaps(student_id: str, current_skill: str) -> List[dict]
    def get_learning_path(start_skill: str, end_skill: str) -> List[str]
```

## Testing & Validation

### Test Checkpoint A (End of Step 1)
**What Should Work:**
- Documentation cleaned (no Gemini setup, logging sections)
- Only architecture essentials remain

**Tests:**
1. Review README.md - no Gemini setup instructions
2. Review GEMINI.md - streamlined content
3. Verify essential docs intact

---

### Test Checkpoint B (End of Step 2)
**What Should Work:**
- Gemini text streaming captured in real-time
- WebSocket bridge: Frontend → Python backend
- All text logged with timestamps

**Tests:**
1. Start tutoring session
2. Verify all Adam responses in backend logs
3. Check WebSocket connection stable
4. Confirm zero data loss

---

### Test Checkpoint C (End of Step 3)
**What Should Work:**
- ChromaDB storing all interactions
- Knowledge graph with skill relationships
- Retrieval API functional (latency < 200ms)

**Tests:**
1. Run 3 tutoring sessions
2. Query: "Find similar past struggles with fractions"
3. Verify knowledge graph shows skill prerequisites
4. Measure retrieval latency

---

### Test Checkpoint D (End of Step 4)
**What Should Work:**
- TA greets on startup
- TA wraps up on close
- TA nudges after 60s inactivity

**Tests:**
1. Start session → verify greeting
2. Stay silent 60s → verify nudge
3. End session → verify closure
4. Check all prompts in logs

---

### Test Checkpoint E (End of Step 5)
**What Should Work:**
- Emotion detection active
- Adam consulted for emotional strategy
- Adam's approach executed

**Tests:**
1. Simulate frustration (wrong answers, delays)
2. Verify TA detects emotion
3. Check TA asks Adam for guidance
4. Confirm Adam's strategy executed

---

### Test Checkpoint F (End of Step 6)
**What Should Work:**
- Vector DB retrieves past struggles
- Knowledge graph identifies skill gaps
- Context injected to Adam before responses

**Tests:**
1. Create session with known struggle topic
2. Start new session on same topic
3. Verify TA surfaces past context
4. Check Adam uses context in responses
5. Measure context retrieval < 300ms

---

### Test Checkpoint G (End of Step 7)
**What Should Work:**
- All metrics calculated correctly
- Baseline comparisons accurate
- Suggestions sent to Adam
- Performance dashboard visible

**Tests:**
1. Complete 5-question session
2. Verify accuracy calculation
3. Check TA suggests difficulty adjustment if accuracy >90% or <50%
4. View performance dashboard
5. Confirm metrics persist across sessions

---

### Integration Test (Final)
**Full System Test:**
1. Start fresh tutoring session
2. TA greets student warmly
3. Student struggles with topic
4. TA detects frustration
5. TA surfaces past similar struggles
6. TA provides performance insights to Adam
7. Adam adjusts approach based on TA context
8. Student improves
9. TA tracks improvement metrics
10. Session ends with TA-prompted closure

**Success Criteria:**
- All components work together seamlessly
- No errors in logs
- Performance metrics accurate
- Adam's responses show TA-enhanced intelligence

## Success Criteria

### Overall System Success:
- ✅ All 7 steps implemented
- ✅ All test checkpoints pass (A-G)
- ✅ Code coverage > 85%
- ✅ Tests import from codebase (zero hardcoding)
- ✅ Integration test passes
- ✅ Documentation complete
- ✅ Latency benchmarks met:
  - Vector retrieval < 200ms
  - Context injection < 300ms
  - Emotion detection < 500ms
- ✅ Ready for production deployment

## Non-Functional Requirements

### Performance
- Vector DB queries < 200ms (p95)
- Knowledge graph traversal < 100ms
- Real-time streaming latency < 50ms
- TA prompt injection < 100ms

### Reliability
- 99.9% uptime for TA services
- Graceful degradation if vector DB unavailable
- Automatic reconnection for WebSocket failures

### Security
- Student data encrypted at rest
- Secure WebSocket connections (WSS)
- No PII in logs

### Scalability
- Support 100+ concurrent sessions
- Vector DB handles 1M+ interactions
- Knowledge graph scales to 10K+ skills

## Notes for Autonomous Development

- Write tests FIRST (imports only, no hardcoding)
- Implement code to pass tests
- Run pytest automatically
- Debug failures autonomously
- Iterate until 100% pass rate
- Mark checkpoints complete only when all tests pass
