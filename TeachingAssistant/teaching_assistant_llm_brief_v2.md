# Teaching Assistant LLM Brief v2.0
## Hybrid Architecture Implementation Plan

### **System Overview**

The AI Tutor Teaching Assistant (TA) is a hybrid system that combines:
- **Python-based deterministic processing** for performance tracking, historical analysis, and intervention logic
- **Gemini Live API** for multimodal emotional state assessment and natural tutoring interactions
- **Real-time monitoring** with 30-second analysis cycles
- **Prompt injection system** to guide ADAM's teaching behavior

### **Architecture Components**

```
┌─────────────────────────────────────────────────────────────┐
│                    ADAM (Gemini Live)                       │
│                  - AI Tutor Interface                       │
│                  - Multimodal Understanding                 │
│                  - Natural Conversations                    │
└─────────────────┬───────────────────────────────────────────┘
                  │ Voice Transcript + JSON Response    │ Prompt Injection
                  │                                     │
┌─────────────────▼─────────────────────────────────────▼─────────────┐
│                    Teaching Assistant (Python)                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│  │ Conversation    │  │ Memory Systems  │  │ Analysis Engine │     │
│  │ Intelligence    │  │                 │  │                 │     │
│  │ - Transcription │  │ - Vector DB     │  │ - Performance   │     │
│  │ - NLP Analysis  │  │ - Knowledge     │  │ - Emotional     │     │
│  │ - Topic Extract │  │   Graph         │  │ - Intervention  │     │
│  │ - Context Track │  │ - Semantic Mem  │  │ - Composite     │     │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘     │
│                                                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│  │ Short-term      │  │ Medium-term     │  │ Long-term       │     │
│  │ Memory          │  │ Memory          │  │ Memory          │     │
│  │ - Session Context│  │ - Recent Patterns│ │ - Learning Style│     │
│  │ - Active Topics │  │ - Weekly Trends │  │ - Preferences   │     │
│  │ - Current State │  │ - Skill Progress│  │ - Success Patterns│  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘     │
└─────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     External Data Sources                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│  │ Vector Database │  │ Knowledge Graph │  │ Student Profile │     │
│  │ (ChromaDB)      │  │ (Neo4j/NetworkX)│  │ Database        │     │
│  │ - Embeddings    │  │ - Relationships │  │ - Demographics  │     │
│  │ - Similarities  │  │ - Concepts      │  │ - History       │     │
│  │ - Patterns      │  │ - Progressions  │  │ - Preferences   │     │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## **DEVELOPMENT PLAN**

### **Step 1: Foundation Setup**
**Objective**: Set up basic project structure and core dependencies

**Tasks**:
1. Initialize Python project with proper structure
2. Set up Gemini Live API connection
3. Create basic configuration management
4. Implement logging system

**Pseudo Code**:
```python
# Project Structure
teaching_assistant/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── logger.py
│   ├── adam_interface/
│   │   ├── __init__.py
│   │   └── gemini_client.py
│   ├── performance/
│   │   ├── __init__.py
│   │   └── tracker.py
│   ├── emotional/
│   │   ├── __init__.py
│   │   └── skills.py
│   └── main.py
├── tests/
├── requirements.txt
└── README.md

# src/core/config.py
class Config:
    def __init__(self):
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.analysis_interval = 30  # seconds
        self.log_level = "INFO"
        self.database_url = os.getenv('DATABASE_URL')

# src/adam_interface/gemini_client.py
class GeminiClient:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.session = None

    async def initialize_session(self):
        """Initialize Gemini Live session"""
        pass

    async def send_analysis_request(self, prompt):
        """Send emotional analysis request to ADAM"""
        pass

    async def inject_teaching_prompt(self, intervention):
        """Inject intervention prompt to guide ADAM"""
        pass
```

**Deliverables**:
- Working Python project structure
- Gemini Live API connection established
- Basic configuration and logging

---

### **Step 2: Conversation Intelligence System**
**Objective**: Build real-time conversation transcription and analysis

**Tasks**:
1. Implement real-time speech-to-text for student voice
2. Capture and store ADAM's voice responses
3. Create conversation transcript storage
4. Build basic NLP analysis pipeline

**Pseudo Code**:
```python
# src/conversation/transcription.py
import speech_recognition as sr
import asyncio
from collections import deque

class ConversationTranscriber:
    def __init__(self, language='en-US'):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.language = language
        self.is_listening = False

        # Conversation storage
        self.student_transcript = deque(maxlen=1000)  # Last 1000 utterances
        self.adam_transcript = deque(maxlen=1000)

        # Real-time processing
        self.transcript_buffer = []
        self.last_speech_time = 0

    async def start_continuous_listening(self):
        """Start continuous speech recognition for student"""
        self.is_listening = True

        # Adjust for ambient noise
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)

        while self.is_listening:
            try:
                await self._process_audio_chunk()
                await asyncio.sleep(0.1)  # Small delay to prevent CPU overload
            except Exception as e:
                logger.error(f"Transcription error: {e}")

    async def _process_audio_chunk(self):
        """Process single audio chunk"""
        try:
            with self.microphone as source:
                # Listen for 1 second chunks
                audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)

            # Use Google's speech recognition (could be replaced with Whisper)
            text = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.recognizer.recognize_google(audio, language=self.language)
            )

            if text.strip():
                timestamp = time.time()
                utterance = {
                    'speaker': 'student',
                    'text': text,
                    'timestamp': timestamp,
                    'confidence': 0.8,  # Google doesn't provide confidence
                    'duration': time.time() - self.last_speech_time
                }

                self.student_transcript.append(utterance)
                self.last_speech_time = timestamp

                # Trigger NLP analysis
                await self._trigger_nlp_analysis(utterance)

        except sr.UnknownValueError:
            # No speech detected, continue
            pass
        except sr.RequestError as e:
            logger.error(f"Speech recognition error: {e}")

    def record_adam_response(self, adam_text, timestamp=None):
        """Record ADAM's spoken response"""
        if timestamp is None:
            timestamp = time.time()

        utterance = {
            'speaker': 'adam',
            'text': adam_text,
            'timestamp': timestamp,
            'confidence': 1.0,  # ADAM's responses are known
            'response_to': self._get_last_student_utterance()
        }

        self.adam_transcript.append(utterance)

    async def _trigger_nlp_analysis(self, utterance):
        """Trigger NLP analysis for new utterance"""
        # This will be connected to the NLP processor
        pass

    def get_recent_conversation(self, minutes=5):
        """Get recent conversation transcript"""
        cutoff_time = time.time() - (minutes * 60)

        # Combine student and ADAM transcripts
        all_utterances = []
        all_utterances.extend([u for u in self.student_transcript if u['timestamp'] > cutoff_time])
        all_utterances.extend([u for u in self.adam_transcript if u['timestamp'] > cutoff_time])

        # Sort by timestamp
        all_utterances.sort(key=lambda x: x['timestamp'])

        return all_utterances

    def get_conversation_summary(self):
        """Get summary statistics of conversation"""
        recent_conversation = self.get_recent_conversation(10)  # Last 10 minutes

        student_utterances = [u for u in recent_conversation if u['speaker'] == 'student']
        adam_utterances = [u for u in recent_conversation if u['speaker'] == 'adam']

        return {
            'total_student_words': sum(len(u['text'].split()) for u in student_utterances),
            'total_adam_words': sum(len(u['text'].split()) for u in adam_utterances),
            'student_utterances': len(student_utterances),
            'adam_utterances': len(adam_utterances),
            'conversation_turns': len(recent_conversation),
            'avg_student_response_length': np.mean([len(u['text'].split()) for u in student_utterances]) if student_utterances else 0,
            'silence_periods': self._detect_silence_periods(recent_conversation)
        }

    def _detect_silence_periods(self, conversation):
        """Detect periods of silence in conversation"""
        silence_periods = []

        for i in range(1, len(conversation)):
            gap = conversation[i]['timestamp'] - conversation[i-1]['timestamp']
            if gap > 10:  # 10+ seconds of silence
                silence_periods.append({
                    'start': conversation[i-1]['timestamp'],
                    'end': conversation[i]['timestamp'],
                    'duration': gap
                })

        return silence_periods

# src/conversation/nlp_processor.py
from transformers import pipeline, AutoTokenizer, AutoModel
import torch

class ConversationNLPProcessor:
    def __init__(self):
        # Initialize models
        self.sentiment_analyzer = pipeline("sentiment-analysis",
                                         model="cardiffnlp/twitter-roberta-base-sentiment-latest")
        self.emotion_classifier = pipeline("text-classification",
                                         model="j-hartmann/emotion-english-distilroberta-base")
        self.topic_model = pipeline("zero-shot-classification",
                                  model="facebook/bart-large-mnli")

        # Educational topics for classification
        self.educational_topics = [
            "mathematics", "science", "reading", "writing", "history",
            "problem solving", "confusion", "understanding", "help request",
            "frustration", "excitement", "boredom", "difficulty"
        ]

    async def analyze_utterance(self, utterance):
        """Comprehensive NLP analysis of student utterance"""
        text = utterance['text']

        # Sentiment analysis
        sentiment_result = self.sentiment_analyzer(text)[0]

        # Emotion classification
        emotion_result = self.emotion_classifier(text)[0]

        # Topic classification
        topic_result = self.topic_model(text, self.educational_topics)

        # Linguistic features
        linguistic_features = self._extract_linguistic_features(text)

        # Educational markers
        educational_markers = self._identify_educational_markers(text)

        analysis = {
            'utterance_id': f"{utterance['timestamp']:.3f}",
            'timestamp': utterance['timestamp'],
            'sentiment': {
                'label': sentiment_result['label'],
                'score': sentiment_result['score']
            },
            'emotion': {
                'label': emotion_result['label'],
                'score': emotion_result['score']
            },
            'topic': {
                'label': topic_result['labels'][0],
                'score': topic_result['scores'][0]
            },
            'linguistic_features': linguistic_features,
            'educational_markers': educational_markers,
            'complexity_score': self._calculate_complexity_score(text)
        }

        return analysis

    def _extract_linguistic_features(self, text):
        """Extract linguistic features from text"""
        words = text.split()

        return {
            'word_count': len(words),
            'avg_word_length': np.mean([len(w) for w in words]) if words else 0,
            'question_marks': text.count('?'),
            'exclamation_marks': text.count('!'),
            'hesitation_markers': len([w for w in words if w.lower() in ['um', 'uh', 'like', 'you know']]),
            'certainty_markers': len([w for w in words if w.lower() in ['definitely', 'sure', 'certain', 'obviously']]),
            'uncertainty_markers': len([w for w in words if w.lower() in ['maybe', 'perhaps', 'might', 'possibly']]),
            'negative_markers': len([w for w in words if w.lower() in ['no', 'not', 'never', 'cannot', "can't", "don't"]])
        }

    def _identify_educational_markers(self, text):
        """Identify educational context markers"""
        text_lower = text.lower()

        markers = {
            'help_request': any(phrase in text_lower for phrase in ['help me', 'i need help', 'can you help', "i don't understand"]),
            'confusion_expression': any(phrase in text_lower for phrase in ['confused', 'lost', "don't get it", 'unclear']),
            'understanding_claim': any(phrase in text_lower for phrase in ['i understand', 'i get it', 'makes sense', 'i see']),
            'difficulty_statement': any(phrase in text_lower for phrase in ['too hard', 'difficult', 'challenging', 'tough']),
            'confidence_expression': any(phrase in text_lower for phrase in ['i know', 'i think', 'i believe', 'sure']),
            'engagement_markers': any(phrase in text_lower for phrase in ['interesting', 'cool', 'wow', 'amazing']),
            'disengagement_markers': any(phrase in text_lower for phrase in ['boring', 'tired', 'bored', 'whatever'])
        }

        return markers

    def _calculate_complexity_score(self, text):
        """Calculate linguistic complexity score"""
        words = text.split()
        if not words:
            return 0

        # Simple complexity based on word length and sentence structure
        avg_word_length = np.mean([len(w) for w in words])
        sentence_count = len([s for s in text.split('.') if s.strip()])
        avg_sentence_length = len(words) / max(1, sentence_count)

        complexity = (avg_word_length / 10) + (avg_sentence_length / 20)
        return min(complexity, 1.0)  # Normalize to 0-1

# src/conversation/context_tracker.py
class ConversationContextTracker:
    def __init__(self):
        self.active_topics = {}
        self.conversation_flow = []
        self.context_switches = []
        self.engagement_timeline = []

    def update_context(self, utterance_analysis):
        """Update conversation context with new utterance analysis"""
        timestamp = utterance_analysis['timestamp']
        topic = utterance_analysis['topic']['label']

        # Track topic progression
        if topic not in self.active_topics:
            self.active_topics[topic] = {
                'first_mention': timestamp,
                'last_mention': timestamp,
                'mention_count': 0,
                'engagement_level': 0
            }

        self.active_topics[topic]['last_mention'] = timestamp
        self.active_topics[topic]['mention_count'] += 1

        # Track conversation flow
        flow_entry = {
            'timestamp': timestamp,
            'topic': topic,
            'sentiment': utterance_analysis['sentiment']['label'],
            'emotion': utterance_analysis['emotion']['label'],
            'educational_markers': utterance_analysis['educational_markers']
        }

        self.conversation_flow.append(flow_entry)

        # Detect context switches
        if len(self.conversation_flow) > 1:
            prev_topic = self.conversation_flow[-2]['topic']
            if prev_topic != topic:
                self.context_switches.append({
                    'timestamp': timestamp,
                    'from_topic': prev_topic,
                    'to_topic': topic,
                    'switch_type': self._classify_topic_switch(prev_topic, topic)
                })

    def _classify_topic_switch(self, from_topic, to_topic):
        """Classify the type of topic switch"""
        # Educational topic hierarchies
        math_topics = ['mathematics', 'problem solving']
        emotional_topics = ['confusion', 'frustration', 'excitement']
        help_topics = ['help request', 'difficulty']

        if from_topic in math_topics and to_topic in emotional_topics:
            return 'academic_to_emotional'
        elif from_topic in emotional_topics and to_topic in math_topics:
            return 'emotional_to_academic'
        elif from_topic in help_topics or to_topic in help_topics:
            return 'help_seeking'
        else:
            return 'general_shift'

    def get_context_summary(self):
        """Get current conversation context summary"""
        recent_flow = self.conversation_flow[-10:]  # Last 10 exchanges

        return {
            'active_topics': dict(sorted(self.active_topics.items(),
                                       key=lambda x: x[1]['last_mention'], reverse=True)),
            'recent_context_switches': self.context_switches[-5:],
            'dominant_emotion': self._get_dominant_emotion(recent_flow),
            'engagement_trend': self._calculate_engagement_trend(),
            'conversation_coherence': self._calculate_coherence_score()
        }

    def _get_dominant_emotion(self, recent_flow):
        """Get the dominant emotion from recent conversation"""
        emotions = [entry['emotion'] for entry in recent_flow]
        if emotions:
            return max(set(emotions), key=emotions.count)
        return 'neutral'

    def _calculate_engagement_trend(self):
        """Calculate engagement trend over conversation"""
        # Simple implementation - can be enhanced
        recent_markers = []
        for entry in self.conversation_flow[-10:]:
            markers = entry['educational_markers']
            engagement_score = 0
            if markers['engagement_markers']:
                engagement_score += 1
            if markers['disengagement_markers']:
                engagement_score -= 1
            recent_markers.append(engagement_score)

        if len(recent_markers) > 1:
            return np.mean(recent_markers[-5:]) - np.mean(recent_markers[-10:-5])
        return 0

    def _calculate_coherence_score(self):
        """Calculate how coherent the conversation flow is"""
        if len(self.context_switches) < 2:
            return 1.0

        # Fewer abrupt switches = higher coherence
        recent_switches = len([s for s in self.context_switches[-5:]
                             if s['switch_type'] in ['academic_to_emotional', 'emotional_to_academic']])

        return max(0, 1.0 - (recent_switches / 5))
```

**Deliverables**:
- Real-time speech-to-text transcription system
- Conversation storage and retrieval
- Basic NLP analysis pipeline
- Conversation context tracking

---

### **Step 3: Performance Tracking System**
**Objective**: Build deterministic performance monitoring

**Tasks**:
1. Create question response tracking
2. Implement accuracy calculations
3. Build response time analysis
4. Add session duration monitoring

**Pseudo Code**:
```python
# src/performance/tracker.py
class PerformanceTracker:
    def __init__(self):
        self.questions_history = []
        self.session_start_time = time.time()
        self.current_question_start = None

    def record_question_start(self, question_id, difficulty_level):
        """Record when student starts a question"""
        self.current_question_start = {
            'question_id': question_id,
            'start_time': time.time(),
            'difficulty': difficulty_level
        }

    def record_answer_submission(self, answer, is_correct, attempts=1):
        """Record answer submission and accuracy"""
        end_time = time.time()
        response_time = end_time - self.current_question_start['start_time']

        question_record = {
            'question_id': self.current_question_start['question_id'],
            'response_time': response_time,
            'is_correct': is_correct,
            'attempts': attempts,
            'difficulty': self.current_question_start['difficulty'],
            'timestamp': end_time
        }

        self.questions_history.append(question_record)

    def get_recent_metrics(self, window_minutes=5):
        """Get performance metrics for recent time window"""
        cutoff_time = time.time() - (window_minutes * 60)
        recent_questions = [q for q in self.questions_history if q['timestamp'] > cutoff_time]

        if not recent_questions:
            return self._get_baseline_metrics()

        return {
            'accuracy_rate': sum(q['is_correct'] for q in recent_questions) / len(recent_questions),
            'avg_response_time': sum(q['response_time'] for q in recent_questions) / len(recent_questions),
            'consecutive_errors': self._count_consecutive_errors(),
            'questions_attempted': len(recent_questions),
            'difficulty_trend': self._calculate_difficulty_trend(recent_questions),
            'session_duration_minutes': (time.time() - self.session_start_time) / 60
        }

    def _count_consecutive_errors(self):
        """Count consecutive wrong answers from end of history"""
        consecutive = 0
        for question in reversed(self.questions_history):
            if not question['is_correct']:
                consecutive += 1
            else:
                break
        return consecutive

    def _calculate_difficulty_trend(self, recent_questions):
        """Calculate if difficulty is increasing/decreasing"""
        if len(recent_questions) < 2:
            return 0

        difficulties = [q['difficulty'] for q in recent_questions]
        return (difficulties[-1] - difficulties[0]) / len(difficulties)

    def get_performance_indicators(self):
        """Get indicators for emotional state correlation"""
        recent = self.get_recent_metrics()
        baseline = self.get_baseline_performance()

        return {
            'accuracy_decline': max(0, baseline['accuracy'] - recent['accuracy_rate']),
            'response_time_increase': recent['avg_response_time'] / baseline['avg_response_time'] if baseline['avg_response_time'] > 0 else 1,
            'consecutive_errors': recent['consecutive_errors'],
            'performance_trend': self._calculate_performance_trend()
        }
```

**Deliverables**:
- Working performance tracking system
- Accuracy and timing calculations
- Performance trend analysis

---

### **Step 4: Vector Database System**
**Objective**: Build vector storage and similarity search for conversations and behaviors

**Tasks**:
1. Set up ChromaDB for conversation embeddings
2. Create conversation-to-vector encoding
3. Implement behavioral pattern storage
4. Build similarity search functionality

**Pseudo Code**:
```python
# src/memory/vector_database.py
import chromadb
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Any

class ConversationVectorStore:
    def __init__(self, collection_name="conversations", model_name="all-MiniLM-L6-v2"):
        self.client = chromadb.Client()
        self.collection = self.client.create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

        # Sentence transformer for encoding conversations
        self.encoder = SentenceTransformer(model_name)

        # Conversation storage
        self.conversation_cache = {}

    def store_conversation_segment(self, student_id: str, segment: Dict[str, Any],
                                 emotional_context: Dict[str, Any],
                                 performance_context: Dict[str, Any]):
        """Store conversation segment with context"""

        # Create composite text for embedding
        conversation_text = self._create_conversation_text(segment)

        # Generate embedding
        embedding = self.encoder.encode(conversation_text).tolist()

        # Create metadata
        metadata = {
            'student_id': student_id,
            'timestamp': segment['timestamp'],
            'conversation_length': len(segment['utterances']),
            'dominant_emotion': emotional_context.get('primary_emotion', 'neutral'),
            'emotion_confidence': emotional_context.get('confidence', 0.5),
            'performance_accuracy': performance_context.get('accuracy_rate', 0.0),
            'response_time': performance_context.get('avg_response_time', 0.0),
            'topics': ','.join(segment.get('topics', [])),
            'educational_markers': self._encode_educational_markers(segment),
            'intervention_triggered': segment.get('intervention_triggered', False)
        }

        # Store in vector database
        document_id = f"{student_id}_{int(segment['timestamp'])}"

        self.collection.add(
            embeddings=[embedding],
            documents=[conversation_text],
            metadatas=[metadata],
            ids=[document_id]
        )

    def _create_conversation_text(self, segment: Dict[str, Any]) -> str:
        """Create searchable text representation of conversation segment"""
        utterances = segment['utterances']

        # Combine student and ADAM utterances with context
        text_parts = []

        for utterance in utterances:
            speaker = utterance['speaker']
            text = utterance['text']

            # Add speaker context
            if speaker == 'student':
                text_parts.append(f"Student: {text}")
            else:
                text_parts.append(f"ADAM: {text}")

        # Add emotional and educational context
        if 'emotional_markers' in segment:
            emotional_text = ' '.join([f"{k}:{v}" for k, v in segment['emotional_markers'].items() if v])
            text_parts.append(f"Emotional context: {emotional_text}")

        if 'topics' in segment:
            topics_text = ' '.join(segment['topics'])
            text_parts.append(f"Topics: {topics_text}")

        return ' '.join(text_parts)

    def _encode_educational_markers(self, segment: Dict[str, Any]) -> str:
        """Encode educational markers as searchable string"""
        markers = []

        for utterance in segment['utterances']:
            if 'educational_markers' in utterance:
                for marker, present in utterance['educational_markers'].items():
                    if present:
                        markers.append(marker)

        return ','.join(set(markers))

    def find_similar_conversations(self, current_segment: Dict[str, Any],
                                 student_id: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Find similar conversation segments"""

        # Create embedding for current segment
        current_text = self._create_conversation_text(current_segment)
        current_embedding = self.encoder.encode(current_text).tolist()

        # Build query filters
        where_clause = {}
        if student_id:
            where_clause['student_id'] = student_id

        # Query vector database
        results = self.collection.query(
            query_embeddings=[current_embedding],
            where=where_clause if where_clause else None,
            n_results=limit,
            include=['documents', 'metadatas', 'distances']
        )

        # Process results
        similar_conversations = []

        for i, (document, metadata, distance) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        )):
            similarity_score = 1 - distance  # Convert distance to similarity

            similar_conversations.append({
                'similarity_score': similarity_score,
                'conversation_text': document,
                'metadata': metadata,
                'emotional_context': {
                    'emotion': metadata['dominant_emotion'],
                    'confidence': metadata['emotion_confidence']
                },
                'performance_context': {
                    'accuracy': metadata['performance_accuracy'],
                    'response_time': metadata['response_time']
                },
                'topics': metadata['topics'].split(',') if metadata['topics'] else [],
                'educational_markers': metadata['educational_markers'].split(',') if metadata['educational_markers'] else [],
                'intervention_triggered': metadata['intervention_triggered']
            })

        return similar_conversations

    def store_behavioral_pattern(self, student_id: str, pattern_type: str,
                               pattern_data: Dict[str, Any], context: Dict[str, Any]):
        """Store behavioral patterns for pattern recognition"""

        # Create pattern embedding
        pattern_text = self._create_pattern_text(pattern_type, pattern_data, context)
        embedding = self.encoder.encode(pattern_text).tolist()

        metadata = {
            'student_id': student_id,
            'pattern_type': pattern_type,
            'timestamp': context.get('timestamp', time.time()),
            'session_id': context.get('session_id', ''),
            'frequency': pattern_data.get('frequency', 1),
            'confidence': pattern_data.get('confidence', 0.5),
            'associated_emotion': pattern_data.get('emotion', 'neutral'),
            'intervention_success': context.get('intervention_success')
        }

        document_id = f"{student_id}_{pattern_type}_{int(metadata['timestamp'])}"

        self.collection.add(
            embeddings=[embedding],
            documents=[pattern_text],
            metadatas=[metadata],
            ids=[document_id]
        )

    def _create_pattern_text(self, pattern_type: str, pattern_data: Dict[str, Any],
                           context: Dict[str, Any]) -> str:
        """Create searchable text for behavioral patterns"""

        text_parts = [f"Pattern: {pattern_type}"]

        # Add pattern details
        for key, value in pattern_data.items():
            text_parts.append(f"{key}: {value}")

        # Add context
        for key, value in context.items():
            if key not in ['timestamp', 'session_id']:
                text_parts.append(f"{key}: {value}")

        return ' '.join(text_parts)

    def get_student_conversation_history(self, student_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get conversation history for a specific student"""

        results = self.collection.query(
            query_embeddings=None,
            where={'student_id': student_id},
            n_results=limit,
            include=['documents', 'metadatas']
        )

        history = []
        for document, metadata in zip(results['documents'][0], results['metadatas'][0]):
            history.append({
                'conversation_text': document,
                'metadata': metadata
            })

        # Sort by timestamp
        history.sort(key=lambda x: x['metadata']['timestamp'])

        return history

# src/memory/behavioral_embeddings.py
class BehavioralEmbeddingSystem:
    def __init__(self, vector_store: ConversationVectorStore):
        self.vector_store = vector_store
        self.behavior_patterns = {}

    def create_session_embedding(self, session_data: Dict[str, Any]) -> np.ndarray:
        """Create embedding for entire session"""

        # Combine all conversation segments
        all_conversations = []

        for segment in session_data['conversation_segments']:
            conversation_text = self.vector_store._create_conversation_text(segment)
            all_conversations.append(conversation_text)

        # Combine with performance and emotional data
        session_text = ' '.join(all_conversations)

        # Add session-level context
        context_parts = []

        if 'performance_summary' in session_data:
            perf = session_data['performance_summary']
            context_parts.append(f"Accuracy: {perf.get('overall_accuracy', 0):.2f}")
            context_parts.append(f"Questions: {perf.get('total_questions', 0)}")
            context_parts.append(f"Duration: {perf.get('session_duration', 0):.1f} minutes")

        if 'emotional_summary' in session_data:
            emotions = session_data['emotional_summary']
            dominant_emotions = emotions.get('dominant_emotions', [])
            context_parts.append(f"Emotions: {','.join(dominant_emotions)}")

        full_text = session_text + ' ' + ' '.join(context_parts)

        return self.vector_store.encoder.encode(full_text)

    def find_similar_sessions(self, current_session: Dict[str, Any],
                            student_id: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Find sessions with similar behavioral patterns"""

        current_embedding = self.create_session_embedding(current_session)

        # This would require storing session-level embeddings
        # For now, use conversation similarity as proxy

        recent_segments = current_session.get('conversation_segments', [])
        if not recent_segments:
            return []

        # Use most recent segment to find similar conversations
        latest_segment = recent_segments[-1]

        return self.vector_store.find_similar_conversations(
            latest_segment, student_id, limit
        )

    def detect_recurring_patterns(self, student_id: str, pattern_window_days: int = 30) -> List[Dict[str, Any]]:
        """Detect recurring behavioral patterns for a student"""

        # Get recent conversation history
        history = self.vector_store.get_student_conversation_history(student_id, limit=200)

        # Filter by time window
        cutoff_time = time.time() - (pattern_window_days * 24 * 3600)
        recent_history = [h for h in history if h['metadata']['timestamp'] > cutoff_time]

        # Group by similar patterns
        pattern_groups = self._cluster_similar_conversations(recent_history)

        # Identify recurring patterns
        recurring_patterns = []

        for group in pattern_groups:
            if len(group) >= 3:  # Pattern appears at least 3 times
                pattern_summary = self._summarize_pattern_group(group)
                recurring_patterns.append(pattern_summary)

        return recurring_patterns

    def _cluster_similar_conversations(self, conversations: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Cluster conversations by similarity"""
        # Simple clustering implementation
        # In production, could use more sophisticated clustering algorithms

        if len(conversations) < 2:
            return [conversations]

        # Create embeddings for all conversations
        embeddings = []
        for conv in conversations:
            embedding = self.vector_store.encoder.encode(conv['conversation_text'])
            embeddings.append(embedding)

        # Simple threshold-based clustering
        clusters = []
        used_indices = set()

        for i, embedding in enumerate(embeddings):
            if i in used_indices:
                continue

            cluster = [conversations[i]]
            used_indices.add(i)

            for j, other_embedding in enumerate(embeddings):
                if j <= i or j in used_indices:
                    continue

                similarity = np.dot(embedding, other_embedding) / (
                    np.linalg.norm(embedding) * np.linalg.norm(other_embedding)
                )

                if similarity > 0.7:  # Similarity threshold
                    cluster.append(conversations[j])
                    used_indices.add(j)

            clusters.append(cluster)

        return clusters

    def _summarize_pattern_group(self, group: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize a group of similar conversations"""

        # Extract common elements
        all_emotions = [conv['metadata']['dominant_emotion'] for conv in group]
        all_topics = []

        for conv in group:
            topics = conv['metadata']['topics'].split(',') if conv['metadata']['topics'] else []
            all_topics.extend(topics)

        # Calculate pattern statistics
        return {
            'pattern_id': f"pattern_{hash(str(group[0]['conversation_text']))}",
            'frequency': len(group),
            'common_emotions': list(set(all_emotions)),
            'common_topics': list(set(all_topics)),
            'avg_accuracy': np.mean([conv['metadata']['performance_accuracy'] for conv in group]),
            'intervention_success_rate': np.mean([conv['metadata']['intervention_triggered'] for conv in group]),
            'first_occurrence': min(conv['metadata']['timestamp'] for conv in group),
            'last_occurrence': max(conv['metadata']['timestamp'] for conv in group),
            'sample_conversation': group[0]['conversation_text'][:200] + '...'
        }
```

**Deliverables**:
- ChromaDB setup for conversation storage
- Conversation-to-vector encoding system
- Behavioral pattern recognition
- Similarity search functionality

---

### **Step 5: Knowledge Graph System**
**Objective**: Build relationship mapping for learning concepts and student interactions

**Tasks**:
1. Set up NetworkX knowledge graph
2. Create student-concept relationship mapping
3. Implement learning progression tracking
4. Build intervention effectiveness relationships

**Pseudo Code**:
```python
# src/memory/knowledge_graph.py
import networkx as nx
from typing import Dict, List, Any, Tuple
import json
import time

class EducationalKnowledgeGraph:
    def __init__(self):
        self.graph = nx.MultiDiGraph()

        # Node types
        self.node_types = {
            'student': 'person',
            'concept': 'knowledge',
            'topic': 'subject',
            'skill': 'ability',
            'emotion': 'state',
            'intervention': 'action',
            'conversation': 'interaction'
        }

        # Initialize with base educational concepts
        self._initialize_base_concepts()

    def _initialize_base_concepts(self):
        """Initialize graph with fundamental educational concepts"""

        # Core subject areas
        subjects = ['mathematics', 'science', 'reading', 'writing', 'history']
        for subject in subjects:
            self.add_concept_node(subject, 'subject', {'difficulty': 0.5, 'fundamental': True})

        # Mathematical concepts hierarchy
        math_concepts = [
            ('arithmetic', 'mathematics', 0.3),
            ('algebra', 'arithmetic', 0.6),
            ('geometry', 'mathematics', 0.5),
            ('calculus', 'algebra', 0.9)
        ]

        for concept, prerequisite, difficulty in math_concepts:
            self.add_concept_node(concept, 'concept', {'difficulty': difficulty})
            self.add_relationship(prerequisite, concept, 'prerequisite_for', {'strength': 0.8})

        # Emotional states
        emotions = ['confusion', 'frustration', 'engagement', 'boredom', 'anxiety', 'excitement']
        for emotion in emotions:
            self.add_concept_node(emotion, 'emotion', {'valence': self._get_emotion_valence(emotion)})

    def _get_emotion_valence(self, emotion: str) -> float:
        """Get emotional valence (-1 to 1)"""
        positive_emotions = ['engagement', 'excitement']
        negative_emotions = ['confusion', 'frustration', 'boredom', 'anxiety']

        if emotion in positive_emotions:
            return 0.8
        elif emotion in negative_emotions:
            return -0.6
        else:
            return 0.0

    def add_student_node(self, student_id: str, profile: Dict[str, Any]):
        """Add student node with profile information"""

        self.graph.add_node(
            student_id,
            node_type='student',
            **profile,
            created_at=time.time(),
            last_updated=time.time()
        )

        # Connect to interests
        for interest in profile.get('interests', []):
            if interest not in self.graph:
                self.add_concept_node(interest, 'interest', {'personal': True})

            self.add_relationship(student_id, interest, 'interested_in', {'strength': 0.7})

    def add_concept_node(self, concept_id: str, concept_type: str, attributes: Dict[str, Any]):
        """Add educational concept node"""

        self.graph.add_node(
            concept_id,
            node_type=concept_type,
            **attributes,
            created_at=time.time()
        )

    def add_relationship(self, from_node: str, to_node: str, relationship_type: str,
                        attributes: Dict[str, Any] = None):
        """Add relationship between nodes"""

        if attributes is None:
            attributes = {}

        self.graph.add_edge(
            from_node,
            to_node,
            relationship=relationship_type,
            created_at=time.time(),
            **attributes
        )

    def record_learning_interaction(self, student_id: str, concept: str,
                                  interaction_data: Dict[str, Any]):
        """Record student interaction with educational concept"""

        # Create interaction node
        interaction_id = f"interaction_{student_id}_{concept}_{int(time.time())}"

        self.graph.add_node(
            interaction_id,
            node_type='interaction',
            **interaction_data,
            timestamp=time.time()
        )

        # Connect student to interaction
        self.add_relationship(student_id, interaction_id, 'participated_in')

        # Connect interaction to concept
        self.add_relationship(interaction_id, concept, 'focused_on')

        # Update student-concept relationship
        self._update_student_concept_relationship(student_id, concept, interaction_data)

    def _update_student_concept_relationship(self, student_id: str, concept: str,
                                           interaction_data: Dict[str, Any]):
        """Update direct student-concept relationship based on interaction"""

        # Check if direct relationship exists
        if self.graph.has_edge(student_id, concept):
            # Update existing relationship
            edge_data = self.graph[student_id][concept]

            # Update mastery level based on performance
            current_mastery = edge_data.get('mastery_level', 0.5)
            performance = interaction_data.get('accuracy', 0.5)

            # Simple learning curve update
            new_mastery = current_mastery + 0.1 * (performance - current_mastery)

            edge_data['mastery_level'] = max(0, min(1, new_mastery))
            edge_data['last_interaction'] = time.time()
            edge_data['interaction_count'] = edge_data.get('interaction_count', 0) + 1

        else:
            # Create new relationship
            initial_mastery = interaction_data.get('accuracy', 0.5)

            self.add_relationship(
                student_id, concept, 'learning',
                {
                    'mastery_level': initial_mastery,
                    'last_interaction': time.time(),
                    'interaction_count': 1,
                    'learning_rate': 0.1
                }
            )

    def record_emotional_state(self, student_id: str, emotion: str, context: Dict[str, Any]):
        """Record student's emotional state in specific context"""

        emotion_instance_id = f"emotion_{student_id}_{emotion}_{int(time.time())}"

        self.graph.add_node(
            emotion_instance_id,
            node_type='emotion_instance',
            emotion=emotion,
            confidence=context.get('confidence', 0.5),
            intensity=context.get('intensity', 0.5),
            timestamp=time.time(),
            context=context
        )

        # Connect to student
        self.add_relationship(student_id, emotion_instance_id, 'experienced')

        # Connect to concept if applicable
        if 'current_concept' in context:
            self.add_relationship(emotion_instance_id, context['current_concept'], 'triggered_by')

    def record_intervention(self, student_id: str, intervention_type: str,
                          context: Dict[str, Any], outcome: Dict[str, Any]):
        """Record intervention and its effectiveness"""

        intervention_id = f"intervention_{student_id}_{intervention_type}_{int(time.time())}"

        self.graph.add_node(
            intervention_id,
            node_type='intervention',
            intervention_type=intervention_type,
            context=context,
            outcome=outcome,
            success=outcome.get('success', False),
            timestamp=time.time()
        )

        # Connect to student
        self.add_relationship(student_id, intervention_id, 'received')

        # Connect to emotional context
        if 'emotional_state' in context:
            emotion = context['emotional_state']
            self.add_relationship(intervention_id, emotion, 'addressed_emotion')

    def get_student_learning_path(self, student_id: str) -> List[Dict[str, Any]]:
        """Get student's learning progression path"""

        if student_id not in self.graph:
            return []

        # Get all concepts student has interacted with
        learning_edges = [(student_id, concept, data)
                         for concept, data in self.graph[student_id].items()
                         if data.get('relationship') == 'learning']

        # Sort by mastery level and last interaction
        learning_path = []

        for _, concept, edge_data in learning_edges:
            concept_data = self.graph.nodes[concept]

            learning_path.append({
                'concept': concept,
                'concept_type': concept_data.get('node_type', 'unknown'),
                'mastery_level': edge_data.get('mastery_level', 0),
                'interaction_count': edge_data.get('interaction_count', 0),
                'last_interaction': edge_data.get('last_interaction', 0),
                'difficulty': concept_data.get('difficulty', 0.5)
            })

        # Sort by last interaction time
        learning_path.sort(key=lambda x: x['last_interaction'], reverse=True)

        return learning_path

    def get_effective_interventions(self, student_id: str, emotional_state: str) -> List[Dict[str, Any]]:
        """Get historically effective interventions for student's emotional state"""

        effective_interventions = []

        # Find all intervention nodes for this student
        if student_id in self.graph:
            for neighbor in self.graph[student_id]:
                edge_data = self.graph[student_id][neighbor]

                if edge_data.get('relationship') == 'received':
                    intervention_data = self.graph.nodes[neighbor]

                    if (intervention_data.get('node_type') == 'intervention' and
                        intervention_data.get('success', False)):

                        # Check if intervention addressed similar emotional state
                        intervention_context = intervention_data.get('context', {})

                        if intervention_context.get('emotional_state') == emotional_state:
                            effective_interventions.append({
                                'intervention_type': intervention_data.get('intervention_type'),
                                'success_rate': 1.0,  # This student had success
                                'context': intervention_context,
                                'outcome': intervention_data.get('outcome', {}),
                                'timestamp': intervention_data.get('timestamp', 0)
                            })

        # Sort by recency
        effective_interventions.sort(key=lambda x: x['timestamp'], reverse=True)

        return effective_interventions

    def get_concept_prerequisites(self, concept: str) -> List[str]:
        """Get prerequisites for a concept"""

        prerequisites = []

        if concept in self.graph:
            # Find incoming 'prerequisite_for' relationships
            for pred in self.graph.predecessors(concept):
                edge_data = self.graph[pred][concept]

                if edge_data.get('relationship') == 'prerequisite_for':
                    prerequisites.append(pred)

        return prerequisites

    def recommend_next_concepts(self, student_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Recommend next concepts for student to learn"""

        if student_id not in self.graph:
            return []

        # Get student's current mastery levels
        current_mastery = {}
        learning_path = self.get_student_learning_path(student_id)

        for item in learning_path:
            current_mastery[item['concept']] = item['mastery_level']

        # Find concepts with satisfied prerequisites
        candidates = []

        for node in self.graph.nodes():
            node_data = self.graph.nodes[node]

            if (node_data.get('node_type') in ['concept', 'skill'] and
                node not in current_mastery):

                # Check prerequisites
                prerequisites = self.get_concept_prerequisites(node)
                prerequisites_satisfied = all(
                    current_mastery.get(prereq, 0) >= 0.7 for prereq in prerequisites
                )

                if prerequisites_satisfied or not prerequisites:
                    difficulty = node_data.get('difficulty', 0.5)

                    candidates.append({
                        'concept': node,
                        'difficulty': difficulty,
                        'prerequisites': prerequisites,
                        'estimated_readiness': self._calculate_readiness_score(
                            student_id, node, current_mastery
                        )
                    })

        # Sort by readiness score
        candidates.sort(key=lambda x: x['estimated_readiness'], reverse=True)

        return candidates[:limit]

    def _calculate_readiness_score(self, student_id: str, concept: str,
                                 current_mastery: Dict[str, float]) -> float:
        """Calculate student's readiness for a concept"""

        # Base score from prerequisite mastery
        prerequisites = self.get_concept_prerequisites(concept)

        if prerequisites:
            prereq_mastery = np.mean([current_mastery.get(prereq, 0) for prereq in prerequisites])
        else:
            prereq_mastery = 0.5  # No prerequisites

        # Adjust for concept difficulty
        concept_data = self.graph.nodes[concept]
        difficulty = concept_data.get('difficulty', 0.5)

        # Adjust for student's learning rate (from past interactions)
        avg_learning_rate = self._get_student_learning_rate(student_id)

        # Combine factors
        readiness_score = (
            0.5 * prereq_mastery +
            0.3 * (1 - difficulty) +  # Easier concepts get higher score
            0.2 * avg_learning_rate
        )

        return max(0, min(1, readiness_score))

    def _get_student_learning_rate(self, student_id: str) -> float:
        """Calculate student's average learning rate"""

        learning_path = self.get_student_learning_path(student_id)

        if not learning_path:
            return 0.5  # Default

        learning_rates = []

        for item in learning_path:
            interactions = item['interaction_count']
            mastery = item['mastery_level']

            if interactions > 0:
                rate = mastery / interactions  # Simple rate calculation
                learning_rates.append(rate)

        if learning_rates:
            return np.mean(learning_rates)
        else:
            return 0.5

    def export_graph_data(self, student_id: str = None) -> Dict[str, Any]:
        """Export graph data for visualization or analysis"""

        if student_id:
            # Export subgraph related to specific student
            student_nodes = set([student_id])

            # Add connected nodes (up to 2 hops)
            for neighbor in self.graph[student_id]:
                student_nodes.add(neighbor)

                for second_neighbor in self.graph[neighbor]:
                    student_nodes.add(second_neighbor)

            subgraph = self.graph.subgraph(student_nodes)

            return {
                'nodes': [{'id': node, **data} for node, data in subgraph.nodes(data=True)],
                'edges': [{'source': u, 'target': v, **data} for u, v, data in subgraph.edges(data=True)]
            }

        else:
            # Export full graph
            return {
                'nodes': [{'id': node, **data} for node, data in self.graph.nodes(data=True)],
                'edges': [{'source': u, 'target': v, **data} for u, v, data in self.graph.edges(data=True)]
            }
```

**Deliverables**:
- NetworkX knowledge graph setup
- Student learning progression tracking
- Concept relationship mapping
- Intervention effectiveness tracking

---

### **Step 6: Testing & Evaluation Phase A**
**Objective**: Validate foundation, conversation intelligence, performance tracking, and memory systems

**Unit Tests**:
```python
# tests/test_performance_tracker.py
import pytest
from src.performance.tracker import PerformanceTracker

class TestPerformanceTracker:
    def test_question_recording(self):
        tracker = PerformanceTracker()
        tracker.record_question_start("q1", 0.5)
        tracker.record_answer_submission("answer", True, 1)

        assert len(tracker.questions_history) == 1
        assert tracker.questions_history[0]['is_correct'] == True

    def test_accuracy_calculation(self):
        tracker = PerformanceTracker()
        # Simulate 5 questions: 3 correct, 2 wrong
        for i in range(3):
            tracker.record_question_start(f"q{i}", 0.5)
            tracker.record_answer_submission("answer", True)
        for i in range(2):
            tracker.record_question_start(f"q{i+3}", 0.5)
            tracker.record_answer_submission("answer", False)

        metrics = tracker.get_recent_metrics()
        assert metrics['accuracy_rate'] == 0.6

    def test_consecutive_errors(self):
        tracker = PerformanceTracker()
        # Correct, Wrong, Wrong, Wrong
        tracker.record_question_start("q1", 0.5)
        tracker.record_answer_submission("answer", True)
        for i in range(3):
            tracker.record_question_start(f"q{i+2}", 0.5)
            tracker.record_answer_submission("answer", False)

        metrics = tracker.get_recent_metrics()
        assert metrics['consecutive_errors'] == 3

# tests/test_gemini_client.py
class TestGeminiClient:
    @pytest.mark.asyncio
    async def test_session_initialization(self):
        client = GeminiClient("test_api_key")
        # Mock test for session initialization
        assert client is not None

    @pytest.mark.asyncio
    async def test_analysis_request_format(self):
        client = GeminiClient("test_api_key")
        # Test that analysis requests are properly formatted
        prompt = "Test emotional analysis"
        # Mock the response and verify format
        pass
```

**Integration Tests**:
```python
# tests/test_integration.py
class TestSystemIntegration:
    def test_config_loading(self):
        config = Config()
        assert config.analysis_interval == 30
        assert config.gemini_api_key is not None

    def test_performance_tracker_integration(self):
        tracker = PerformanceTracker()
        # Simulate realistic session
        for i in range(10):
            tracker.record_question_start(f"q{i}", random.uniform(0.3, 0.8))
            is_correct = random.choice([True, False])
            tracker.record_answer_submission(f"answer{i}", is_correct)

        metrics = tracker.get_recent_metrics()
        assert 'accuracy_rate' in metrics
        assert 'avg_response_time' in metrics
```

**Success Criteria**:
- All unit tests pass (100% coverage for core functions)
- Performance tracking accurately calculates metrics
- Gemini client establishes connection
- Configuration management works properly

---

### **Step 4: Emotional State Analysis System**
**Objective**: Implement emotion detection and skill mapping

**Tasks**:
1. Create emotional skill definitions
2. Build ADAM communication for emotional analysis
3. Implement JSON response parsing
4. Add confidence scoring

**Pseudo Code**:
```python
# src/emotional/skills.py
class EmotionalSkill:
    def __init__(self, name, category, triggers, recommended_action, priority="medium"):
        self.name = name
        self.category = category
        self.triggers = triggers
        self.recommended_action = recommended_action
        self.priority = priority
        self.activation_count = 0
        self.success_rate = 0.0

class EmotionalSkillSystem:
    def __init__(self):
        self.skills = self._initialize_skills()
        self.activation_history = []

    def _initialize_skills(self):
        """Initialize all 23 emotional skills from brief"""
        return {
            'high_engagement': EmotionalSkill(
                name="High Engagement",
                category="engaged",
                triggers=["quick_responses", "direct_eye_contact", "upright_posture"],
                recommended_action="Keep momentum going! Ask follow-up questions or introduce slight challenge",
                priority="low"
            ),
            'deep_confusion': EmotionalSkill(
                name="Deep Confusion",
                category="confused",
                triggers=["explicit_confusion", "blank_stare", "multiple_wrong_answers"],
                recommended_action="Back up to fundamentals, break problem into smaller steps",
                priority="high"
            ),
            'building_frustration': EmotionalSkill(
                name="Building Frustration",
                category="frustrated",
                triggers=["sighing", "tense_body_language", "irritated_tone"],
                recommended_action="Acknowledge difficulty, suggest different approach or break",
                priority="high"
            ),
            # ... all 23 skills
        }

    def analyze_emotional_state(self, adam_response, performance_data):
        """Combine ADAM's emotional assessment with performance data"""
        try:
            emotional_data = json.loads(adam_response)
        except json.JSONDecodeError:
            return None

        # Map ADAM's response to our skill system
        primary_skill = self._map_emotion_to_skill(emotional_data['primary_emotion'])

        # Enhance with performance correlation
        enhanced_analysis = {
            'primary_skill': primary_skill,
            'confidence': emotional_data.get('confidence', 0.5),
            'supporting_evidence': self._correlate_with_performance(emotional_data, performance_data),
            'intervention_needed': self._determine_intervention_need(primary_skill, performance_data),
            'timestamp': time.time()
        }

        return enhanced_analysis

    def _correlate_with_performance(self, emotional_data, performance_data):
        """Correlate emotional signals with performance indicators"""
        correlations = []

        # Check if emotional state matches performance patterns
        if emotional_data['primary_emotion'] == 'frustrated' and performance_data['accuracy_decline'] > 0.2:
            correlations.append("performance_decline_supports_frustration")

        if emotional_data['primary_emotion'] == 'confused' and performance_data['response_time_increase'] > 1.5:
            correlations.append("slow_responses_support_confusion")

        if emotional_data['primary_emotion'] == 'bored' and performance_data['accuracy_rate'] > 0.9:
            correlations.append("high_accuracy_supports_boredom")

        return correlations

# src/emotional/analyzer.py
class EmotionalAnalyzer:
    def __init__(self, gemini_client, skill_system):
        self.gemini_client = gemini_client
        self.skill_system = skill_system
        self.analysis_history = []

    async def request_emotional_analysis(self, performance_context):
        """Ask ADAM for emotional state assessment"""
        prompt = self._build_analysis_prompt(performance_context)

        try:
            response = await self.gemini_client.send_analysis_request(prompt)
            analysis = self.skill_system.analyze_emotional_state(response, performance_context)

            if analysis:
                self.analysis_history.append(analysis)
                return analysis

        except Exception as e:
            logger.error(f"Emotional analysis failed: {e}")
            return None

    def _build_analysis_prompt(self, performance_context):
        """Build focused prompt for ADAM emotional analysis"""
        return f"""
        Based on the student's recent speech patterns, facial expressions, body language, and interactions, assess their current emotional state.

        Recent performance context:
        - Accuracy: {performance_context['accuracy_rate']:.1%}
        - Response time trend: {performance_context['response_time_increase']:.1f}x baseline
        - Consecutive errors: {performance_context['consecutive_errors']}
        - Session duration: {performance_context.get('session_duration_minutes', 0):.1f} minutes

        Respond with JSON only in this exact format:
        {{
          "primary_emotion": "engaged|confused|frustrated|bored|anxious|tired|overwhelmed",
          "confidence": 0.85,
          "observed_behaviors": ["specific", "behaviors", "seen"],
          "emotional_intensity": 0.7,
          "speech_indicators": "description of speech patterns",
          "visual_cues": "description of visual observations",
          "energy_level": 0.6
        }}

        Focus on what you can directly observe in the multimodal input.
        """
```

**Deliverables**:
- Complete emotional skill system
- ADAM integration for emotional analysis
- JSON response parsing and validation
- Performance-emotion correlation logic

---

### **Step 5: Intervention System**
**Objective**: Build prompt injection and intervention logic

**Tasks**:
1. Create intervention decision engine
2. Implement prompt injection mechanism
3. Add intervention tracking and success measurement
4. Build adaptive threshold system

**Pseudo Code**:
```python
# src/intervention/engine.py
class InterventionEngine:
    def __init__(self, gemini_client, skill_system):
        self.gemini_client = gemini_client
        self.skill_system = skill_system
        self.intervention_history = []
        self.success_tracker = {}
        self.adaptive_thresholds = self._initialize_thresholds()

    def _initialize_thresholds(self):
        """Initialize intervention thresholds"""
        return {
            'high_priority': 0.8,    # Immediate intervention needed
            'medium_priority': 0.6,  # Schedule intervention
            'low_priority': 0.4,     # Monitor only
            'consecutive_errors': 3,  # Trigger confusion intervention
            'accuracy_decline': 0.25, # Trigger frustration intervention
            'session_duration': 45   # Trigger fatigue check (minutes)
        }

    async def evaluate_intervention_need(self, emotional_analysis, performance_data):
        """Determine if intervention is needed and execute"""
        if not emotional_analysis:
            return False

        intervention_score = self._calculate_intervention_score(emotional_analysis, performance_data)

        if intervention_score >= self.adaptive_thresholds['high_priority']:
            await self._execute_immediate_intervention(emotional_analysis, performance_data)
            return True
        elif intervention_score >= self.adaptive_thresholds['medium_priority']:
            await self._schedule_intervention(emotional_analysis, performance_data)
            return True

        return False

    def _calculate_intervention_score(self, emotional_analysis, performance_data):
        """Calculate composite intervention urgency score"""
        base_score = emotional_analysis['confidence']

        # Boost score based on performance correlations
        if len(emotional_analysis['supporting_evidence']) > 0:
            base_score += 0.2

        # Critical situations get immediate boost
        critical_emotions = ['overwhelmed', 'deep_confusion', 'building_frustration']
        if emotional_analysis['primary_skill'].name.lower().replace(' ', '_') in critical_emotions:
            base_score += 0.3

        # Performance indicators
        if performance_data['consecutive_errors'] >= 3:
            base_score += 0.2
        if performance_data['accuracy_decline'] > 0.2:
            base_score += 0.15

        return min(base_score, 1.0)

    async def _execute_immediate_intervention(self, emotional_analysis, performance_data):
        """Execute high-priority intervention immediately"""
        intervention_prompt = self._generate_intervention_prompt(emotional_analysis, performance_data)

        try:
            await self.gemini_client.inject_teaching_prompt(intervention_prompt)

            # Record intervention
            intervention_record = {
                'timestamp': time.time(),
                'emotional_state': emotional_analysis['primary_skill'].name,
                'intervention_type': 'immediate',
                'prompt': intervention_prompt,
                'performance_context': performance_data,
                'success': None  # Will be updated later
            }

            self.intervention_history.append(intervention_record)

        except Exception as e:
            logger.error(f"Failed to execute intervention: {e}")

    def _generate_intervention_prompt(self, emotional_analysis, performance_data):
        """Generate specific intervention prompt for ADAM"""
        skill = emotional_analysis['primary_skill']
        base_action = skill.recommended_action

        # Customize based on performance context
        if performance_data['consecutive_errors'] >= 3:
            if 'confusion' in skill.name.lower():
                return f"The student has gotten {performance_data['consecutive_errors']} questions wrong in a row and appears confused. {base_action} Ask them to explain their thinking process so you can identify where they're getting stuck."

        if performance_data['accuracy_decline'] > 0.2:
            if 'frustration' in skill.name.lower():
                return f"The student's accuracy has dropped by {performance_data['accuracy_decline']:.1%} and they seem frustrated. {base_action} Remind them that mistakes are part of learning."

        if performance_data.get('session_duration_minutes', 0) > 45:
            if 'fatigue' in skill.name.lower() or 'tired' in skill.name.lower():
                return f"The student has been working for {performance_data['session_duration_minutes']:.0f} minutes and appears tired. {base_action} Suggest a 5-minute break to recharge."

        # Default intervention
        return f"Based on the student's current state, {base_action.lower()}"

    def track_intervention_success(self, intervention_id, success_metrics):
        """Track whether interventions were successful"""
        # Implementation for measuring intervention effectiveness
        pass

# src/intervention/adaptive_system.py
class AdaptiveThresholdSystem:
    def __init__(self):
        self.student_baselines = {}
        self.intervention_effectiveness = {}

    def learn_student_baseline(self, student_id, behavioral_data):
        """Learn individual student's baseline behavior"""
        if student_id not in self.student_baselines:
            self.student_baselines[student_id] = {}

        baseline = self.student_baselines[student_id]
        baseline.update({
            'avg_response_time': behavioral_data.get('avg_response_time', 30),
            'typical_accuracy': behavioral_data.get('accuracy_rate', 0.7),
            'speech_pace': behavioral_data.get('speech_pace', 150),
            'engagement_patterns': behavioral_data.get('engagement_patterns', [])
        })

    def adjust_thresholds_for_student(self, student_id, base_thresholds):
        """Adjust intervention thresholds based on student's baseline"""
        if student_id not in self.student_baselines:
            return base_thresholds

        baseline = self.student_baselines[student_id]
        adjusted = base_thresholds.copy()

        # Students with typically lower accuracy need adjusted thresholds
        if baseline['typical_accuracy'] < 0.6:
            adjusted['accuracy_decline'] *= 1.5

        # Students with typically slower responses need adjusted thresholds
        if baseline['avg_response_time'] > 60:
            adjusted['response_time_threshold'] *= 1.3

        return adjusted
```

**Deliverables**:
- Working intervention decision engine
- Prompt injection system to ADAM
- Adaptive threshold management
- Intervention tracking and measurement

---

### **Step 6: Testing & Evaluation Phase B**
**Objective**: Validate emotional analysis and intervention systems

**Unit Tests**:
```python
# tests/test_emotional_system.py
class TestEmotionalSkillSystem:
    def test_skill_initialization(self):
        skill_system = EmotionalSkillSystem()
        assert len(skill_system.skills) == 23
        assert 'high_engagement' in skill_system.skills
        assert 'deep_confusion' in skill_system.skills

    def test_emotional_analysis(self):
        skill_system = EmotionalSkillSystem()
        mock_adam_response = json.dumps({
            'primary_emotion': 'frustrated',
            'confidence': 0.8,
            'observed_behaviors': ['sighing', 'tense_posture']
        })
        mock_performance = {
            'accuracy_decline': 0.3,
            'consecutive_errors': 2
        }

        analysis = skill_system.analyze_emotional_state(mock_adam_response, mock_performance)
        assert analysis['primary_skill'].name == 'Building Frustration'
        assert analysis['confidence'] == 0.8

class TestInterventionEngine:
    @pytest.mark.asyncio
    async def test_intervention_scoring(self):
        engine = InterventionEngine(mock_gemini_client, mock_skill_system)

        high_urgency_analysis = {
            'primary_skill': MockSkill('Deep Confusion'),
            'confidence': 0.9,
            'supporting_evidence': ['performance_decline_supports_confusion']
        }
        high_urgency_performance = {
            'consecutive_errors': 4,
            'accuracy_decline': 0.4
        }

        score = engine._calculate_intervention_score(high_urgency_analysis, high_urgency_performance)
        assert score >= 0.8  # Should trigger immediate intervention

    def test_prompt_generation(self):
        engine = InterventionEngine(mock_gemini_client, mock_skill_system)

        mock_analysis = {
            'primary_skill': MockSkill('Building Frustration', 'Acknowledge difficulty, suggest different approach'),
            'confidence': 0.8
        }
        mock_performance = {'consecutive_errors': 3, 'accuracy_decline': 0.25}

        prompt = engine._generate_intervention_prompt(mock_analysis, mock_performance)
        assert 'frustrated' in prompt.lower()
        assert 'different approach' in prompt.lower()
```

**Integration Tests**:
```python
# tests/test_full_cycle.py
class TestFullAnalysisCycle:
    @pytest.mark.asyncio
    async def test_complete_analysis_cycle(self):
        """Test complete 30-second analysis cycle"""
        # Setup
        performance_tracker = PerformanceTracker()
        skill_system = EmotionalSkillSystem()
        analyzer = EmotionalAnalyzer(mock_gemini_client, skill_system)
        intervention_engine = InterventionEngine(mock_gemini_client, skill_system)

        # Simulate student activity
        for i in range(5):
            performance_tracker.record_question_start(f"q{i}", 0.5)
            performance_tracker.record_answer_submission("answer", i % 2 == 0)  # Alternating correct/incorrect

        # Run analysis cycle
        performance_data = performance_tracker.get_performance_indicators()
        emotional_analysis = await analyzer.request_emotional_analysis(performance_data)
        intervention_triggered = await intervention_engine.evaluate_intervention_need(emotional_analysis, performance_data)

        # Verify
        assert performance_data is not None
        assert emotional_analysis is not None
        assert isinstance(intervention_triggered, bool)
```

**Success Criteria**:
- All emotional skills properly defined and accessible
- ADAM emotional analysis requests work correctly
- Intervention scoring algorithm produces expected results
- Prompt generation creates relevant interventions
- Full analysis cycle completes without errors

---

### **Step 7: Historical Context & Memory System**
**Objective**: Implement vector database and knowledge graph integration

**Tasks**:
1. Set up vector database for behavioral patterns
2. Create knowledge graph for student relationships
3. Implement similarity search for past interventions
4. Build learning system for intervention effectiveness

**Pseudo Code**:
```python
# src/memory/vector_store.py
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import chromadb

class VectorMemorySystem:
    def __init__(self, collection_name="student_behaviors"):
        self.client = chromadb.Client()
        self.collection = self.client.create_collection(collection_name)
        self.embedding_dim = 128

    def store_behavioral_state(self, student_id, emotional_state, performance_data, intervention_result=None):
        """Store behavioral state as vector for future reference"""
        vector = self._encode_behavioral_state(emotional_state, performance_data)

        metadata = {
            'student_id': student_id,
            'timestamp': time.time(),
            'emotional_state': emotional_state['primary_skill'].name,
            'confidence': emotional_state['confidence'],
            'performance_accuracy': performance_data['accuracy_rate'],
            'intervention_success': intervention_result
        }

        document_id = f"{student_id}_{int(time.time())}"
        self.collection.add(
            embeddings=[vector.tolist()],
            documents=[json.dumps(metadata)],
            ids=[document_id]
        )

    def _encode_behavioral_state(self, emotional_state, performance_data):
        """Encode behavioral state into vector representation"""
        # Create feature vector combining emotional and performance data
        emotional_features = self._encode_emotional_state(emotional_state)
        performance_features = self._encode_performance_data(performance_data)

        return np.concatenate([emotional_features, performance_features])

    def _encode_emotional_state(self, emotional_state):
        """Encode emotional state into numerical features"""
        # One-hot encoding for primary emotion (23 dimensions)
        emotion_vector = np.zeros(23)
        emotion_map = {skill_name: i for i, skill_name in enumerate(EMOTIONAL_SKILLS)}

        primary_emotion = emotional_state['primary_skill'].name.lower().replace(' ', '_')
        if primary_emotion in emotion_map:
            emotion_vector[emotion_map[primary_emotion]] = emotional_state['confidence']

        # Additional emotional features
        additional_features = np.array([
            emotional_state['confidence'],
            len(emotional_state.get('supporting_evidence', [])) / 5.0,  # Normalized
            emotional_state.get('emotional_intensity', 0.5)
        ])

        return np.concatenate([emotion_vector, additional_features])

    def _encode_performance_data(self, performance_data):
        """Encode performance data into numerical features"""
        return np.array([
            performance_data['accuracy_rate'],
            min(performance_data['response_time_increase'], 3.0) / 3.0,  # Capped and normalized
            min(performance_data['consecutive_errors'], 5) / 5.0,  # Capped and normalized
            performance_data.get('session_duration_minutes', 0) / 120.0,  # Normalized to 2 hours
            performance_data.get('difficulty_trend', 0)
        ])

    def find_similar_situations(self, current_state, student_id=None, limit=5):
        """Find similar past behavioral situations"""
        current_vector = self._encode_behavioral_state(current_state['emotional'], current_state['performance'])

        # Query vector database
        where_clause = {"student_id": student_id} if student_id else None
        results = self.collection.query(
            query_embeddings=[current_vector.tolist()],
            where=where_clause,
            n_results=limit
        )

        return self._parse_similar_situations(results)

    def _parse_similar_situations(self, results):
        """Parse vector database results into actionable insights"""
        situations = []
        for i, document in enumerate(results['documents'][0]):
            metadata = json.loads(document)
            situations.append({
                'similarity_score': 1 - results['distances'][0][i],  # Convert distance to similarity
                'emotional_state': metadata['emotional_state'],
                'performance_context': {
                    'accuracy': metadata['performance_accuracy'],
                },
                'intervention_success': metadata.get('intervention_success'),
                'timestamp': metadata['timestamp']
            })

        return situations

# src/memory/knowledge_graph.py
import networkx as nx

class StudentKnowledgeGraph:
    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.student_profiles = {}

    def add_student_profile(self, student_id, age, interests, learning_style):
        """Add student node with profile information"""
        self.graph.add_node(student_id,
                           node_type='student',
                           age=age,
                           interests=interests,
                           learning_style=learning_style)

        self.student_profiles[student_id] = {
            'age': age,
            'interests': interests,
            'learning_style': learning_style,
            'behavioral_patterns': {},
            'successful_interventions': []
        }

    def record_intervention_outcome(self, student_id, emotional_state, intervention_type, success):
        """Record intervention outcome for learning"""
        intervention_node = f"intervention_{int(time.time())}"

        self.graph.add_node(intervention_node,
                           node_type='intervention',
                           type=intervention_type,
                           success=success,
                           timestamp=time.time())

        self.graph.add_edge(student_id, intervention_node,
                           relationship='received_intervention',
                           emotional_context=emotional_state)

        # Update student profile
        if success:
            self.student_profiles[student_id]['successful_interventions'].append({
                'type': intervention_type,
                'emotional_context': emotional_state,
                'timestamp': time.time()
            })

    def get_effective_interventions(self, student_id, current_emotional_state):
        """Get historically effective interventions for similar situations"""
        if student_id not in self.student_profiles:
            return []

        successful_interventions = self.student_profiles[student_id]['successful_interventions']

        # Find interventions used in similar emotional contexts
        relevant_interventions = []
        for intervention in successful_interventions:
            if self._emotional_states_similar(intervention['emotional_context'], current_emotional_state):
                relevant_interventions.append(intervention)

        return sorted(relevant_interventions, key=lambda x: x['timestamp'], reverse=True)

    def _emotional_states_similar(self, past_state, current_state, threshold=0.7):
        """Determine if two emotional states are similar"""
        # Simple similarity based on primary emotion category
        past_category = past_state.split('_')[0] if '_' in past_state else past_state
        current_category = current_state.split('_')[0] if '_' in current_state else current_state

        return past_category == current_category

    def update_behavioral_pattern(self, student_id, pattern_type, frequency):
        """Update student's behavioral patterns"""
        if student_id in self.student_profiles:
            self.student_profiles[student_id]['behavioral_patterns'][pattern_type] = frequency

# src/memory/contextual_memory.py
class ContextualMemorySystem:
    def __init__(self, vector_store, knowledge_graph):
        self.vector_store = vector_store
        self.knowledge_graph = knowledge_graph
        self.session_context = {}

    def get_historical_context(self, student_id, current_emotional_state, current_performance):
        """Get comprehensive historical context for intervention decisions"""
        # Get similar situations from vector database
        similar_situations = self.vector_store.find_similar_situations({
            'emotional': current_emotional_state,
            'performance': current_performance
        }, student_id)

        # Get effective interventions from knowledge graph
        effective_interventions = self.knowledge_graph.get_effective_interventions(
            student_id,
            current_emotional_state['primary_skill'].name
        )

        # Get student profile
        student_profile = self.knowledge_graph.student_profiles.get(student_id, {})

        return {
            'similar_situations': similar_situations,
            'effective_interventions': effective_interventions,
            'student_profile': student_profile,
            'personalization_factors': self._extract_personalization_factors(student_profile)
        }

    def _extract_personalization_factors(self, student_profile):
        """Extract factors for personalizing interventions"""
        return {
            'preferred_learning_style': student_profile.get('learning_style', 'visual'),
            'interests': student_profile.get('interests', []),
            'age_appropriate_language': student_profile.get('age', 12) < 16,
            'typical_response_patterns': student_profile.get('behavioral_patterns', {})
        }
```

**Deliverables**:
- Vector database for behavioral pattern storage
- Knowledge graph for student relationships
- Historical context retrieval system
- Personalization based on past interactions

---

### **Step 8: Memory Integration System**
**Objective**: Integrate conversation intelligence, vector database, and knowledge graph into unified memory system

**Tasks**:
1. Create unified memory manager
2. Implement multi-tier memory architecture (short/medium/long-term)
3. Build memory-enhanced analysis pipeline
4. Create conversation-aware context system

**Pseudo Code**:
```python
# src/memory/unified_memory.py
from typing import Dict, List, Any, Optional
import time
import asyncio

class UnifiedMemorySystem:
    def __init__(self, vector_store, knowledge_graph, conversation_transcriber, nlp_processor):
        self.vector_store = vector_store
        self.knowledge_graph = knowledge_graph
        self.conversation_transcriber = conversation_transcriber
        self.nlp_processor = nlp_processor
        self.context_tracker = ConversationContextTracker()

        # Memory tiers
        self.short_term_memory = ShortTermMemory()
        self.medium_term_memory = MediumTermMemory()
        self.long_term_memory = LongTermMemory()

        # Integration layer
        self.memory_integrator = MemoryIntegrator(self)

    async def process_conversation_update(self, student_id: str, utterance: Dict[str, Any]):
        """Process new conversation utterance through all memory systems"""

        # 1. NLP Analysis
        nlp_analysis = await self.nlp_processor.analyze_utterance(utterance)

        # 2. Update conversation context
        self.context_tracker.update_context(nlp_analysis)

        # 3. Update short-term memory
        self.short_term_memory.add_utterance(utterance, nlp_analysis)

        # 4. Check for conversation segments to store
        if self.short_term_memory.should_create_segment():
            segment = self.short_term_memory.create_conversation_segment()
            await self._store_conversation_segment(student_id, segment)

        # 5. Update knowledge graph with learning interactions
        if nlp_analysis['educational_markers']['understanding_claim']:
            await self._record_learning_interaction(student_id, nlp_analysis)

        return nlp_analysis

    async def _store_conversation_segment(self, student_id: str, segment: Dict[str, Any]):
        """Store conversation segment in vector database"""

        # Get current emotional and performance context
        emotional_context = self.short_term_memory.get_emotional_context()
        performance_context = self.short_term_memory.get_performance_context()

        # Store in vector database
        self.vector_store.store_conversation_segment(
            student_id, segment, emotional_context, performance_context
        )

        # Update medium-term memory
        self.medium_term_memory.add_conversation_segment(segment)

    async def _record_learning_interaction(self, student_id: str, nlp_analysis: Dict[str, Any]):
        """Record learning interaction in knowledge graph"""

        topic = nlp_analysis['topic']['label']
        confidence = nlp_analysis['topic']['score']

        interaction_data = {
            'accuracy': confidence,
            'timestamp': nlp_analysis['timestamp'],
            'interaction_type': 'conversation',
            'educational_markers': nlp_analysis['educational_markers']
        }

        self.knowledge_graph.record_learning_interaction(student_id, topic, interaction_data)

    async def get_enhanced_context(self, student_id: str, current_emotional_state: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive context from all memory systems"""

        # Short-term context
        short_term_context = self.short_term_memory.get_current_context()

        # Medium-term patterns
        medium_term_patterns = self.medium_term_memory.get_recent_patterns()

        # Long-term profile
        long_term_profile = self.long_term_memory.get_student_profile(student_id)

        # Vector similarity search
        current_conversation = self.short_term_memory.get_recent_conversation()
        if current_conversation:
            similar_conversations = self.vector_store.find_similar_conversations(
                current_conversation, student_id, limit=5
            )
        else:
            similar_conversations = []

        # Knowledge graph insights
        learning_path = self.knowledge_graph.get_student_learning_path(student_id)
        effective_interventions = self.knowledge_graph.get_effective_interventions(
            student_id, current_emotional_state.get('primary_skill', {}).get('name', 'neutral')
        )

        # Integrate all contexts
        enhanced_context = self.memory_integrator.integrate_contexts({
            'short_term': short_term_context,
            'medium_term': medium_term_patterns,
            'long_term': long_term_profile,
            'similar_conversations': similar_conversations,
            'learning_path': learning_path,
            'effective_interventions': effective_interventions
        })

        return enhanced_context

class ShortTermMemory:
    """Manages current session context and recent interactions"""

    def __init__(self, max_utterances=50):
        self.recent_utterances = deque(maxlen=max_utterances)
        self.current_emotional_state = None
        self.current_performance_metrics = {}
        self.active_topics = {}
        self.conversation_segments = []

    def add_utterance(self, utterance: Dict[str, Any], nlp_analysis: Dict[str, Any]):
        """Add utterance with analysis to short-term memory"""

        enhanced_utterance = {
            **utterance,
            'nlp_analysis': nlp_analysis,
            'timestamp': time.time()
        }

        self.recent_utterances.append(enhanced_utterance)

        # Update current emotional state
        emotion = nlp_analysis['emotion']['label']
        confidence = nlp_analysis['emotion']['score']

        if confidence > 0.7:  # High confidence emotions update current state
            self.current_emotional_state = {
                'emotion': emotion,
                'confidence': confidence,
                'timestamp': time.time()
            }

        # Update active topics
        topic = nlp_analysis['topic']['label']
        if topic not in self.active_topics:
            self.active_topics[topic] = {
                'first_mention': time.time(),
                'mention_count': 0,
                'total_confidence': 0
            }

        self.active_topics[topic]['mention_count'] += 1
        self.active_topics[topic]['total_confidence'] += nlp_analysis['topic']['score']
        self.active_topics[topic]['last_mention'] = time.time()

    def should_create_segment(self) -> bool:
        """Determine if we should create a conversation segment"""

        # Create segment every 10 utterances or on topic change
        if len(self.recent_utterances) >= 10:
            return True

        # Check for major topic shift
        if len(self.active_topics) > 1:
            topic_confidences = [
                t['total_confidence'] / t['mention_count']
                for t in self.active_topics.values()
            ]
            if max(topic_confidences) - min(topic_confidences) > 0.5:
                return True

        return False

    def create_conversation_segment(self) -> Dict[str, Any]:
        """Create conversation segment from recent utterances"""

        segment = {
            'utterances': list(self.recent_utterances),
            'timestamp': time.time(),
            'dominant_emotion': self.current_emotional_state,
            'topics': list(self.active_topics.keys()),
            'duration': self._calculate_segment_duration()
        }

        # Clear for next segment
        self.recent_utterances.clear()
        self.active_topics.clear()

        self.conversation_segments.append(segment)

        return segment

    def _calculate_segment_duration(self) -> float:
        """Calculate duration of current segment"""

        if len(self.recent_utterances) < 2:
            return 0

        start_time = self.recent_utterances[0]['timestamp']
        end_time = self.recent_utterances[-1]['timestamp']

        return end_time - start_time

    def get_current_context(self) -> Dict[str, Any]:
        """Get current short-term context"""

        return {
            'recent_utterances_count': len(self.recent_utterances),
            'current_emotional_state': self.current_emotional_state,
            'active_topics': self.active_topics,
            'conversation_coherence': self._calculate_coherence(),
            'engagement_level': self._calculate_engagement_level()
        }

    def _calculate_coherence(self) -> float:
        """Calculate conversation coherence score"""

        if len(self.recent_utterances) < 3:
            return 1.0

        # Simple coherence based on topic consistency
        topics = [u['nlp_analysis']['topic']['label'] for u in self.recent_utterances[-5:]]
        unique_topics = len(set(topics))

        return max(0, 1.0 - (unique_topics / 5))

    def _calculate_engagement_level(self) -> float:
        """Calculate current engagement level"""

        if not self.recent_utterances:
            return 0.5

        # Based on recent educational markers
        recent_markers = []
        for utterance in self.recent_utterances[-3:]:
            markers = utterance['nlp_analysis']['educational_markers']
            engagement_score = 0

            if markers['engagement_markers']:
                engagement_score += 1
            if markers['understanding_claim']:
                engagement_score += 0.5
            if markers['disengagement_markers']:
                engagement_score -= 1

            recent_markers.append(engagement_score)

        if recent_markers:
            return max(0, min(1, np.mean(recent_markers) + 0.5))
        return 0.5

class MediumTermMemory:
    """Manages patterns and trends over recent sessions"""

    def __init__(self, session_window_days=7):
        self.session_window_days = session_window_days
        self.recent_sessions = deque(maxlen=20)  # Last 20 sessions
        self.behavioral_patterns = {}
        self.learning_trends = {}

    def add_conversation_segment(self, segment: Dict[str, Any]):
        """Add conversation segment and update patterns"""

        # Store segment
        self.recent_sessions.append(segment)

        # Update behavioral patterns
        self._update_behavioral_patterns(segment)

        # Update learning trends
        self._update_learning_trends(segment)

    def _update_behavioral_patterns(self, segment: Dict[str, Any]):
        """Update detected behavioral patterns"""

        dominant_emotion = segment.get('dominant_emotion', {}).get('emotion', 'neutral')

        if dominant_emotion not in self.behavioral_patterns:
            self.behavioral_patterns[dominant_emotion] = {
                'frequency': 0,
                'avg_duration': 0,
                'associated_topics': [],
                'intervention_effectiveness': {}
            }

        pattern = self.behavioral_patterns[dominant_emotion]
        pattern['frequency'] += 1

        # Update average duration
        current_duration = segment.get('duration', 0)
        pattern['avg_duration'] = (
            (pattern['avg_duration'] * (pattern['frequency'] - 1) + current_duration) / pattern['frequency']
        )

        # Update associated topics
        segment_topics = segment.get('topics', [])
        pattern['associated_topics'].extend(segment_topics)

    def _update_learning_trends(self, segment: Dict[str, Any]):
        """Update learning progression trends"""

        topics = segment.get('topics', [])

        for topic in topics:
            if topic not in self.learning_trends:
                self.learning_trends[topic] = {
                    'appearances': 0,
                    'understanding_progression': [],
                    'emotional_associations': []
                }

            trend = self.learning_trends[topic]
            trend['appearances'] += 1

            # Track understanding markers
            understanding_markers = []
            for utterance in segment['utterances']:
                if 'nlp_analysis' in utterance:
                    markers = utterance['nlp_analysis']['educational_markers']
                    if markers['understanding_claim']:
                        understanding_markers.append(1)
                    elif markers['confusion_expression']:
                        understanding_markers.append(-1)

            if understanding_markers:
                avg_understanding = np.mean(understanding_markers)
                trend['understanding_progression'].append(avg_understanding)

            # Track emotional associations
            dominant_emotion = segment.get('dominant_emotion', {}).get('emotion')
            if dominant_emotion:
                trend['emotional_associations'].append(dominant_emotion)

    def get_recent_patterns(self) -> Dict[str, Any]:
        """Get recent behavioral and learning patterns"""

        return {
            'behavioral_patterns': self.behavioral_patterns,
            'learning_trends': self.learning_trends,
            'pattern_stability': self._calculate_pattern_stability(),
            'learning_velocity': self._calculate_learning_velocity()
        }

    def _calculate_pattern_stability(self) -> float:
        """Calculate how stable behavioral patterns are"""

        if len(self.recent_sessions) < 5:
            return 0.5

        # Simple stability measure based on emotional consistency
        recent_emotions = []
        for session in list(self.recent_sessions)[-5:]:
            emotion = session.get('dominant_emotion', {}).get('emotion', 'neutral')
            recent_emotions.append(emotion)

        unique_emotions = len(set(recent_emotions))
        stability = max(0, 1.0 - (unique_emotions / 5))

        return stability

    def _calculate_learning_velocity(self) -> float:
        """Calculate rate of learning progression"""

        if not self.learning_trends:
            return 0.5

        # Average understanding progression across topics
        velocities = []

        for topic, trend in self.learning_trends.items():
            progression = trend['understanding_progression']

            if len(progression) >= 2:
                # Simple velocity: change in understanding over time
                velocity = progression[-1] - progression[0]
                velocities.append(velocity)

        if velocities:
            return max(0, min(1, np.mean(velocities) + 0.5))
        return 0.5

class LongTermMemory:
    """Manages persistent student profiles and historical data"""

    def __init__(self, vector_store, knowledge_graph):
        self.vector_store = vector_store
        self.knowledge_graph = knowledge_graph
        self.student_profiles = {}

    def get_student_profile(self, student_id: str) -> Dict[str, Any]:
        """Get comprehensive student profile"""

        if student_id not in self.student_profiles:
            self._build_student_profile(student_id)

        return self.student_profiles[student_id]

    def _build_student_profile(self, student_id: str):
        """Build student profile from historical data"""

        # Get conversation history
        conversation_history = self.vector_store.get_student_conversation_history(student_id)

        # Get learning path
        learning_path = self.knowledge_graph.get_student_learning_path(student_id)

        # Analyze patterns
        behavioral_patterns = self._analyze_historical_behaviors(conversation_history)
        learning_preferences = self._analyze_learning_preferences(learning_path)
        emotional_patterns = self._analyze_emotional_patterns(conversation_history)

        self.student_profiles[student_id] = {
            'conversation_history_length': len(conversation_history),
            'learning_path_progress': len(learning_path),
            'behavioral_patterns': behavioral_patterns,
            'learning_preferences': learning_preferences,
            'emotional_patterns': emotional_patterns,
            'overall_learning_rate': self._calculate_overall_learning_rate(learning_path),
            'preferred_intervention_types': self._get_preferred_interventions(student_id)
        }

    def _analyze_historical_behaviors(self, conversation_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze historical behavioral patterns"""

        if not conversation_history:
            return {}

        # Extract patterns from metadata
        all_emotions = [conv['metadata']['dominant_emotion'] for conv in conversation_history]
        all_topics = []

        for conv in conversation_history:
            topics = conv['metadata']['topics'].split(',') if conv['metadata']['topics'] else []
            all_topics.extend(topics)

        return {
            'most_common_emotions': self._get_frequency_distribution(all_emotions),
            'most_discussed_topics': self._get_frequency_distribution(all_topics),
            'average_conversation_length': np.mean([conv['metadata']['conversation_length'] for conv in conversation_history]),
            'historical_accuracy': np.mean([conv['metadata']['performance_accuracy'] for conv in conversation_history])
        }

    def _get_frequency_distribution(self, items: List[str]) -> Dict[str, float]:
        """Get frequency distribution of items"""

        if not items:
            return {}

        item_counts = {}
        for item in items:
            if item:  # Skip empty strings
                item_counts[item] = item_counts.get(item, 0) + 1

        total = len(items)
        return {item: count / total for item, count in item_counts.items()}

    def _analyze_learning_preferences(self, learning_path: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze learning preferences from historical data"""

        if not learning_path:
            return {}

        # Learning rate analysis
        learning_rates = []
        concept_types = []

        for item in learning_path:
            if item['interaction_count'] > 0:
                rate = item['mastery_level'] / item['interaction_count']
                learning_rates.append(rate)
                concept_types.append(item['concept_type'])

        return {
            'average_learning_rate': np.mean(learning_rates) if learning_rates else 0.5,
            'preferred_concept_types': self._get_frequency_distribution(concept_types),
            'mastery_distribution': [item['mastery_level'] for item in learning_path],
            'learning_consistency': np.std(learning_rates) if learning_rates else 0
        }

    def _calculate_overall_learning_rate(self, learning_path: List[Dict[str, Any]]) -> float:
        """Calculate student's overall learning rate"""

        if not learning_path:
            return 0.5

        total_interactions = sum(item['interaction_count'] for item in learning_path)
        total_mastery = sum(item['mastery_level'] for item in learning_path)

        if total_interactions > 0:
            return total_mastery / total_interactions
        return 0.5

    def _get_preferred_interventions(self, student_id: str) -> List[Dict[str, Any]]:
        """Get historically effective intervention types"""

        # This would query the knowledge graph for successful interventions
        all_emotions = ['confusion', 'frustration', 'boredom', 'anxiety']
        preferred = []

        for emotion in all_emotions:
            effective_interventions = self.knowledge_graph.get_effective_interventions(student_id, emotion)
            if effective_interventions:
                preferred.extend(effective_interventions)

        return preferred

class MemoryIntegrator:
    """Integrates insights from all memory tiers"""

    def __init__(self, unified_memory):
        self.unified_memory = unified_memory

    def integrate_contexts(self, contexts: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate contexts from all memory systems"""

        integrated = {
            'current_state': self._integrate_current_state(contexts),
            'historical_insights': self._integrate_historical_insights(contexts),
            'predictions': self._generate_predictions(contexts),
            'recommendations': self._generate_recommendations(contexts)
        }

        return integrated

    def _integrate_current_state(self, contexts: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate current state information"""

        short_term = contexts['short_term']
        similar_conversations = contexts['similar_conversations']

        # Enhance current emotional state with historical context
        current_emotion = short_term.get('current_emotional_state', {})

        if similar_conversations:
            # Check if similar situations led to specific outcomes
            similar_outcomes = [conv['intervention_triggered'] for conv in similar_conversations]
            intervention_likelihood = np.mean(similar_outcomes)
        else:
            intervention_likelihood = 0.5

        return {
            'current_emotional_state': current_emotion,
            'engagement_level': short_term.get('engagement_level', 0.5),
            'conversation_coherence': short_term.get('conversation_coherence', 1.0),
            'intervention_likelihood': intervention_likelihood,
            'context_richness': len(similar_conversations)
        }

    def _integrate_historical_insights(self, contexts: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate historical insights"""

        medium_term = contexts['medium_term']
        long_term = contexts['long_term']
        learning_path = contexts['learning_path']

        return {
            'behavioral_stability': medium_term.get('pattern_stability', 0.5),
            'learning_velocity': medium_term.get('learning_velocity', 0.5),
            'overall_progress': len(learning_path),
            'learning_consistency': long_term.get('learning_preferences', {}).get('learning_consistency', 0),
            'historical_accuracy': long_term.get('behavioral_patterns', {}).get('historical_accuracy', 0.5)
        }

    def _generate_predictions(self, contexts: Dict[str, Any]) -> Dict[str, Any]:
        """Generate predictions based on integrated context"""

        # Simple prediction model - can be enhanced with ML
        current_state = self._integrate_current_state(contexts)
        historical = self._integrate_historical_insights(contexts)

        # Predict likely emotional trajectory
        engagement_trend = 'stable'
        if current_state['engagement_level'] > 0.7:
            engagement_trend = 'increasing'
        elif current_state['engagement_level'] < 0.3:
            engagement_trend = 'decreasing'

        # Predict intervention need
        intervention_urgency = 'low'
        if (current_state['intervention_likelihood'] > 0.7 or
            current_state['engagement_level'] < 0.3):
            intervention_urgency = 'high'
        elif current_state['intervention_likelihood'] > 0.5:
            intervention_urgency = 'medium'

        return {
            'engagement_trend': engagement_trend,
            'intervention_urgency': intervention_urgency,
            'predicted_emotional_state': self._predict_next_emotion(contexts),
            'learning_trajectory': self._predict_learning_trajectory(contexts)
        }

    def _predict_next_emotion(self, contexts: Dict[str, Any]) -> str:
        """Predict likely next emotional state"""

        current_emotion = contexts['short_term'].get('current_emotional_state', {}).get('emotion', 'neutral')
        similar_conversations = contexts['similar_conversations']

        if similar_conversations:
            # Look at emotional transitions in similar conversations
            # For now, return most common emotion from similar situations
            emotions = [conv['emotional_context']['emotion'] for conv in similar_conversations]
            if emotions:
                return max(set(emotions), key=emotions.count)

        return current_emotion

    def _predict_learning_trajectory(self, contexts: Dict[str, Any]) -> str:
        """Predict learning trajectory"""

        learning_velocity = contexts['medium_term'].get('learning_velocity', 0.5)

        if learning_velocity > 0.7:
            return 'accelerating'
        elif learning_velocity < 0.3:
            return 'struggling'
        else:
            return 'steady'

    def _generate_recommendations(self, contexts: Dict[str, Any]) -> Dict[str, Any]:
        """Generate recommendations based on integrated analysis"""

        predictions = self._generate_predictions(contexts)
        effective_interventions = contexts['effective_interventions']

        recommendations = {
            'immediate_actions': [],
            'monitoring_priorities': [],
            'long_term_strategies': []
        }

        # Immediate actions based on urgency
        if predictions['intervention_urgency'] == 'high':
            if effective_interventions:
                best_intervention = max(effective_interventions, key=lambda x: x['success_rate'])
                recommendations['immediate_actions'].append(f"Apply {best_intervention['intervention_type']} intervention")
            else:
                recommendations['immediate_actions'].append("Generic emotional support intervention needed")

        # Monitoring priorities
        if predictions['engagement_trend'] == 'decreasing':
            recommendations['monitoring_priorities'].append("Monitor for disengagement markers")

        if contexts['short_term'].get('conversation_coherence', 1.0) < 0.5:
            recommendations['monitoring_priorities'].append("Track conversation topic coherence")

        # Long-term strategies
        learning_path = contexts['learning_path']
        if learning_path and len(learning_path) > 5:
            avg_mastery = np.mean([item['mastery_level'] for item in learning_path])
            if avg_mastery < 0.6:
                recommendations['long_term_strategies'].append("Focus on strengthening foundational concepts")

        return recommendations
```

**Deliverables**:
- Unified memory management system
- Multi-tier memory architecture
- Context integration across all systems
- Memory-enhanced analysis pipeline

---

### **Step 9: Enhanced Emotional State Analysis**
**Objective**: Integrate conversation intelligence with emotional analysis

**Tasks**:
1. Enhance emotional analysis with conversation context
2. Integrate NLP insights with performance data
3. Build conversation-aware emotional skills
4. Create memory-informed emotional assessment

---

### **Step 10: Main Teaching Assistant Controller**
**Objective**: Integrate all components into main control loop with full memory and conversation systems

**Tasks**:
1. Create enhanced TA controller with all memory systems
2. Implement conversation-aware 30-second analysis cycle
3. Add memory-enhanced intervention system
4. Build comprehensive context integration

---

### **Step 11: Testing & Evaluation Phase B**
**Objective**: Validate enhanced system with memory and conversation intelligence

---

### **Step 12: Production Deployment & Monitoring**
**Objective**: Deploy complete system with monitoring and continuous improvement

**Success Criteria for Production**:
- **Functional**: All 23 emotional skills + conversation intelligence working correctly
- **Performance**: <5 second analysis cycles, <1% error rate, conversation processing <100ms
- **Memory**: Vector similarity search <200ms, knowledge graph queries <100ms
- **Reliability**: >99% uptime, graceful error recovery
- **Scalability**: Support 100+ concurrent sessions with full memory systems
- **Accuracy**: >85% emotional state detection accuracy, >80% conversation context accuracy
2. Implement 30-second analysis cycle
3. Add error handling and recovery
4. Build monitoring and dashboard capabilities

**Pseudo Code**:
```python
# src/main.py
class TeachingAssistant:
    def __init__(self, config):
        self.config = config
        self.logger = Logger(config.log_level)

        # Initialize components
        self.gemini_client = GeminiClient(config.gemini_api_key)
        self.performance_tracker = PerformanceTracker()
        self.skill_system = EmotionalSkillSystem()
        self.analyzer = EmotionalAnalyzer(self.gemini_client, self.skill_system)
        self.intervention_engine = InterventionEngine(self.gemini_client, self.skill_system)

        # Memory systems
        self.vector_store = VectorMemorySystem()
        self.knowledge_graph = StudentKnowledgeGraph()
        self.contextual_memory = ContextualMemorySystem(self.vector_store, self.knowledge_graph)

        # State tracking
        self.current_student_id = None
        self.session_active = False
        self.analysis_task = None
        self.last_analysis_time = 0

    async def start_session(self, student_id, student_profile):
        """Start a new tutoring session"""
        self.logger.info(f"Starting session for student {student_id}")

        try:
            # Initialize student in knowledge graph
            self.knowledge_graph.add_student_profile(
                student_id,
                student_profile['age'],
                student_profile['interests'],
                student_profile['learning_style']
            )

            # Initialize Gemini session
            await self.gemini_client.initialize_session()

            # Start tracking
            self.current_student_id = student_id
            self.session_active = True
            self.performance_tracker = PerformanceTracker()  # Reset for new session

            # Start periodic analysis
            self.analysis_task = asyncio.create_task(self._periodic_analysis_loop())

            self.logger.info(f"Session started successfully for {student_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start session: {e}")
            return False

    async def _periodic_analysis_loop(self):
        """Main 30-second analysis loop"""
        while self.session_active:
            try:
                await asyncio.sleep(self.config.analysis_interval)
                await self._run_analysis_cycle()

            except asyncio.CancelledError:
                self.logger.info("Analysis loop cancelled")
                break
            except Exception as e:
                self.logger.error(f"Analysis cycle failed: {e}")
                # Continue loop despite errors
                await asyncio.sleep(5)  # Brief pause before retry

    async def _run_analysis_cycle(self):
        """Execute single analysis cycle"""
        cycle_start = time.time()
        self.logger.debug("Starting analysis cycle")

        try:
            # 1. Get current performance metrics
            performance_data = self.performance_tracker.get_performance_indicators()

            # 2. Get historical context
            historical_context = self.contextual_memory.get_historical_context(
                self.current_student_id,
                self.analyzer.get_last_emotional_state(),
                performance_data
            ) if hasattr(self.analyzer, 'get_last_emotional_state') else None

            # 3. Request emotional analysis from ADAM
            emotional_analysis = await self.analyzer.request_emotional_analysis(performance_data)

            if not emotional_analysis:
                self.logger.warning("No emotional analysis received")
                return

            # 4. Enhanced analysis with historical context
            if historical_context:
                emotional_analysis = self._enhance_with_historical_context(
                    emotional_analysis,
                    historical_context
                )

            # 5. Determine intervention need
            intervention_triggered = await self.intervention_engine.evaluate_intervention_need(
                emotional_analysis,
                performance_data
            )

            # 6. Store results in memory systems
            self.vector_store.store_behavioral_state(
                self.current_student_id,
                emotional_analysis,
                performance_data
            )

            # 7. Update adaptive thresholds
            self._update_adaptive_systems(emotional_analysis, performance_data, intervention_triggered)

            # Log cycle completion
            cycle_duration = time.time() - cycle_start
            self.logger.debug(f"Analysis cycle completed in {cycle_duration:.2f}s")

        except Exception as e:
            self.logger.error(f"Analysis cycle error: {e}")
            raise

    def _enhance_with_historical_context(self, emotional_analysis, historical_context):
        """Enhance current analysis with historical insights"""
        # Adjust confidence based on similar past situations
        similar_situations = historical_context['similar_situations']
        if similar_situations:
            avg_past_confidence = np.mean([s['similarity_score'] for s in similar_situations])
            emotional_analysis['confidence'] = (emotional_analysis['confidence'] + avg_past_confidence) / 2

        # Add personalization factors
        emotional_analysis['personalization'] = historical_context['personalization_factors']

        # Include successful intervention history
        emotional_analysis['historical_interventions'] = historical_context['effective_interventions']

        return emotional_analysis

    def _update_adaptive_systems(self, emotional_analysis, performance_data, intervention_triggered):
        """Update adaptive learning systems"""
        # Update student behavioral patterns
        pattern_type = f"{emotional_analysis['primary_skill'].category}_response"
        self.knowledge_graph.update_behavioral_pattern(
            self.current_student_id,
            pattern_type,
            emotional_analysis['confidence']
        )

        # Track intervention if one was triggered
        if intervention_triggered:
            # Note: Success will be measured later based on student response
            pass

    # Event handlers for student actions
    def on_question_start(self, question_id, difficulty_level):
        """Handle question start event"""
        if self.session_active:
            self.performance_tracker.record_question_start(question_id, difficulty_level)

    def on_answer_submission(self, answer, is_correct, attempts=1):
        """Handle answer submission event"""
        if self.session_active:
            self.performance_tracker.record_answer_submission(answer, is_correct, attempts)

    def on_intervention_feedback(self, intervention_id, success_metrics):
        """Handle feedback on intervention effectiveness"""
        self.intervention_engine.track_intervention_success(intervention_id, success_metrics)

        # Update knowledge graph with intervention outcome
        last_analysis = self.analyzer.analysis_history[-1] if self.analyzer.analysis_history else None
        if last_analysis:
            self.knowledge_graph.record_intervention_outcome(
                self.current_student_id,
                last_analysis['primary_skill'].name,
                intervention_id,
                success_metrics.get('success', False)
            )

    async def end_session(self):
        """End current tutoring session"""
        self.logger.info(f"Ending session for student {self.current_student_id}")

        self.session_active = False

        if self.analysis_task:
            self.analysis_task.cancel()
            try:
                await self.analysis_task
            except asyncio.CancelledError:
                pass

        # Final data storage and cleanup
        await self._save_session_summary()

        self.current_student_id = None

    async def _save_session_summary(self):
        """Save session summary for future reference"""
        session_summary = {
            'student_id': self.current_student_id,
            'session_duration': time.time() - self.performance_tracker.session_start_time,
            'questions_attempted': len(self.performance_tracker.questions_history),
            'overall_accuracy': sum(q['is_correct'] for q in self.performance_tracker.questions_history) / len(self.performance_tracker.questions_history) if self.performance_tracker.questions_history else 0,
            'interventions_triggered': len(self.intervention_engine.intervention_history),
            'emotional_states_detected': [a['primary_skill'].name for a in self.analyzer.analysis_history],
            'timestamp': time.time()
        }

        # Store in knowledge graph and vector database
        self.vector_store.store_behavioral_state(
            self.current_student_id,
            {'session_summary': session_summary},
            {}
        )

# Example usage script
async def main():
    config = Config()
    ta = TeachingAssistant(config)

    # Start session
    student_profile = {
        'age': 14,
        'interests': ['science', 'video_games'],
        'learning_style': 'visual'
    }

    await ta.start_session('student_123', student_profile)

    # Simulate student activity
    ta.on_question_start('q1', 0.5)
    await asyncio.sleep(35)  # Let analysis cycle run
    ta.on_answer_submission('answer1', True)

    # Let it run for a few cycles
    await asyncio.sleep(120)

    # End session
    await ta.end_session()

if __name__ == "__main__":
    asyncio.run(main())
```

**Deliverables**:
- Complete Teaching Assistant controller
- 30-second analysis cycle implementation
- Error handling and recovery mechanisms
- Event-driven student interaction handling

---

### **Step 9: Testing & Evaluation Phase C**
**Objective**: Full system integration testing and performance validation

**Integration Tests**:
```python
# tests/test_full_system.py
class TestFullSystemIntegration:
    @pytest.mark.asyncio
    async def test_complete_session_flow(self):
        """Test complete tutoring session from start to finish"""
        config = Config()
        ta = TeachingAssistant(config)

        # Mock Gemini client for testing
        ta.gemini_client = MockGeminiClient()

        student_profile = {
            'age': 15,
            'interests': ['math', 'music'],
            'learning_style': 'auditory'
        }

        # Start session
        success = await ta.start_session('test_student_1', student_profile)
        assert success == True
        assert ta.session_active == True
        assert ta.current_student_id == 'test_student_1'

        # Simulate realistic student behavior
        test_questions = [
            ('q1', 0.3, 'correct_answer', True, 1),
            ('q2', 0.4, 'wrong_answer', False, 2),
            ('q3', 0.4, 'wrong_answer', False, 1),
            ('q4', 0.5, 'wrong_answer', False, 1),  # Should trigger confusion intervention
            ('q5', 0.6, 'correct_answer', True, 1),
        ]

        interventions_triggered = []

        for i, (qid, difficulty, answer, correct, attempts) in enumerate(test_questions):
            ta.on_question_start(qid, difficulty)

            # Wait for analysis cycle (simulate time passage)
            if i > 0:  # Skip first question
                await asyncio.sleep(1)  # Shortened for testing

                # Check if intervention was triggered
                if ta.intervention_engine.intervention_history:
                    interventions_triggered.append(ta.intervention_engine.intervention_history[-1])

            ta.on_answer_submission(answer, correct, attempts)

        # Verify system behavior
        assert len(ta.performance_tracker.questions_history) == 5
        assert ta.performance_tracker.get_recent_metrics()['consecutive_errors'] >= 2

        # Should have triggered at least one intervention for consecutive errors
        assert len(interventions_triggered) > 0

        # End session
        await ta.end_session()
        assert ta.session_active == False

    @pytest.mark.asyncio
    async def test_emotional_state_detection_accuracy(self):
        """Test accuracy of emotional state detection"""
        ta = TeachingAssistant(Config())
        ta.gemini_client = MockGeminiClient()

        # Test scenarios with known emotional states
        test_scenarios = [
            {
                'performance': {'accuracy_rate': 0.2, 'consecutive_errors': 4, 'response_time_increase': 2.5},
                'expected_emotion_category': 'confused',
                'mock_gemini_response': {'primary_emotion': 'confused', 'confidence': 0.8}
            },
            {
                'performance': {'accuracy_rate': 0.95, 'consecutive_errors': 0, 'response_time_increase': 0.5},
                'expected_emotion_category': 'engaged',
                'mock_gemini_response': {'primary_emotion': 'engaged', 'confidence': 0.9}
            },
            {
                'performance': {'accuracy_rate': 0.4, 'consecutive_errors': 3, 'response_time_increase': 1.8},
                'expected_emotion_category': 'frustrated',
                'mock_gemini_response': {'primary_emotion': 'frustrated', 'confidence': 0.7}
            }
        ]

        await ta.start_session('test_student_2', {'age': 16, 'interests': [], 'learning_style': 'visual'})

        correct_detections = 0

        for scenario in test_scenarios:
            ta.gemini_client.set_mock_response(json.dumps(scenario['mock_gemini_response']))

            analysis = await ta.analyzer.request_emotional_analysis(scenario['performance'])

            if analysis and scenario['expected_emotion_category'] in analysis['primary_skill'].category:
                correct_detections += 1

        accuracy = correct_detections / len(test_scenarios)
        assert accuracy >= 0.8  # 80% accuracy threshold

        await ta.end_session()

    def test_memory_system_learning(self):
        """Test that memory systems learn from interactions"""
        vector_store = VectorMemorySystem()
        knowledge_graph = StudentKnowledgeGraph()

        # Add student profile
        knowledge_graph.add_student_profile('test_student_3', 14, ['science'], 'visual')

        # Simulate successful intervention
        emotional_state = {'primary_skill': MockSkill('Deep Confusion'), 'confidence': 0.8}
        performance_data = {'accuracy_rate': 0.3, 'consecutive_errors': 3}

        vector_store.store_behavioral_state('test_student_3', emotional_state, performance_data, True)
        knowledge_graph.record_intervention_outcome('test_student_3', 'Deep Confusion', 'explanation_intervention', True)

        # Test retrieval
        similar_situations = vector_store.find_similar_situations({
            'emotional': emotional_state,
            'performance': performance_data
        }, 'test_student_3')

        effective_interventions = knowledge_graph.get_effective_interventions('test_student_3', 'Deep Confusion')

        assert len(similar_situations) > 0
        assert len(effective_interventions) > 0
        assert effective_interventions[0]['type'] == 'explanation_intervention'

class TestPerformanceMetrics:
    def test_system_response_time(self):
        """Test that analysis cycles complete within acceptable time"""
        # This would be run with actual timing measurements
        pass

    def test_memory_usage(self):
        """Test memory usage remains within acceptable bounds"""
        # Monitor memory usage during extended sessions
        pass

    def test_intervention_effectiveness(self):
        """Test that interventions actually improve student outcomes"""
        # This would require A/B testing with real students
        pass

# Performance and Load Tests
class TestSystemPerformance:
    @pytest.mark.asyncio
    async def test_concurrent_sessions(self):
        """Test system handling multiple concurrent student sessions"""
        tas = []

        for i in range(5):  # Simulate 5 concurrent students
            ta = TeachingAssistant(Config())
            ta.gemini_client = MockGeminiClient()
            tas.append(ta)

            await ta.start_session(f'student_{i}', {
                'age': 14 + i,
                'interests': ['math'],
                'learning_style': 'visual'
            })

        # Let all sessions run for simulated time
        await asyncio.sleep(2)

        # Verify all sessions are active
        for ta in tas:
            assert ta.session_active == True

        # End all sessions
        for ta in tas:
            await ta.end_session()

    def test_memory_scalability(self):
        """Test vector database performance with large datasets"""
        vector_store = VectorMemorySystem()

        # Add many behavioral states
        for i in range(1000):
            emotional_state = {'primary_skill': MockSkill('High Engagement'), 'confidence': 0.8}
            performance_data = {'accuracy_rate': 0.8, 'consecutive_errors': 0}
            vector_store.store_behavioral_state(f'student_{i%10}', emotional_state, performance_data)

        # Test query performance
        start_time = time.time()
        similar_situations = vector_store.find_similar_situations({
            'emotional': emotional_state,
            'performance': performance_data
        }, 'student_1', limit=10)
        query_time = time.time() - start_time

        assert query_time < 1.0  # Should complete within 1 second
        assert len(similar_situations) > 0
```

**Success Criteria**:
- Complete session flow works end-to-end
- Emotional state detection achieves >80% accuracy
- Analysis cycles complete within 5 seconds
- Memory systems successfully learn and retrieve patterns
- System handles multiple concurrent sessions
- All performance metrics within acceptable bounds

---

### **Step 10: Production Deployment & Monitoring**
**Objective**: Deploy system with monitoring and continuous improvement

**Tasks**:
1. Add comprehensive logging and metrics
2. Create health check endpoints
3. Implement graceful error handling
4. Build monitoring dashboard
5. Add configuration for production environment

**Pseudo Code**:
```python
# src/monitoring/metrics.py
class SystemMetrics:
    def __init__(self):
        self.metrics = {
            'sessions_started': 0,
            'sessions_completed': 0,
            'analysis_cycles_completed': 0,
            'interventions_triggered': 0,
            'errors_encountered': 0,
            'avg_analysis_cycle_time': 0.0,
            'emotional_detection_accuracy': 0.0
        }
        self.start_time = time.time()

    def record_session_start(self):
        self.metrics['sessions_started'] += 1

    def record_session_completion(self):
        self.metrics['sessions_completed'] += 1

    def record_analysis_cycle(self, duration):
        self.metrics['analysis_cycles_completed'] += 1
        # Update rolling average
        total_cycles = self.metrics['analysis_cycles_completed']
        current_avg = self.metrics['avg_analysis_cycle_time']
        self.metrics['avg_analysis_cycle_time'] = ((current_avg * (total_cycles - 1)) + duration) / total_cycles

    def record_intervention(self):
        self.metrics['interventions_triggered'] += 1

    def record_error(self):
        self.metrics['errors_encountered'] += 1

    def get_health_status(self):
        uptime = time.time() - self.start_time
        error_rate = self.metrics['errors_encountered'] / max(1, self.metrics['analysis_cycles_completed'])

        return {
            'status': 'healthy' if error_rate < 0.05 else 'degraded',
            'uptime_seconds': uptime,
            'error_rate': error_rate,
            'metrics': self.metrics
        }

# src/monitoring/dashboard.py
from flask import Flask, jsonify, render_template

class MonitoringDashboard:
    def __init__(self, teaching_assistant):
        self.app = Flask(__name__)
        self.ta = teaching_assistant
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/health')
        def health_check():
            return jsonify(self.ta.metrics.get_health_status())

        @self.app.route('/metrics')
        def get_metrics():
            return jsonify(self.ta.metrics.metrics)

        @self.app.route('/dashboard')
        def dashboard():
            return render_template('dashboard.html', metrics=self.ta.metrics.metrics)

        @self.app.route('/students/<student_id>/session')
        def get_student_session(student_id):
            # Return current session info for student
            return jsonify({
                'student_id': student_id,
                'session_active': self.ta.current_student_id == student_id,
                'recent_performance': self.ta.performance_tracker.get_recent_metrics() if self.ta.session_active else None
            })

    def run(self, host='0.0.0.0', port=8080):
        self.app.run(host=host, port=port)

# src/core/production_config.py
class ProductionConfig(Config):
    def __init__(self):
        super().__init__()
        self.environment = 'production'
        self.log_level = 'WARNING'
        self.max_concurrent_sessions = 100
        self.analysis_interval = 30
        self.health_check_interval = 60
        self.error_recovery_enabled = True
        self.performance_monitoring = True

        # Database configurations
        self.vector_db_host = os.getenv('VECTOR_DB_HOST', 'localhost')
        self.vector_db_port = int(os.getenv('VECTOR_DB_PORT', 6333))

        # API configurations
        self.gemini_api_timeout = 10.0
        self.max_retries = 3

        # Security
        self.api_key_rotation_days = 30
        self.encrypt_stored_data = True

# Enhanced main.py with production features
class ProductionTeachingAssistant(TeachingAssistant):
    def __init__(self, config):
        super().__init__(config)
        self.metrics = SystemMetrics()
        self.health_checker = HealthChecker(self)
        self.error_recovery = ErrorRecoverySystem(self)
        self.monitoring_dashboard = MonitoringDashboard(self)

        # Rate limiting for API calls
        self.api_rate_limiter = RateLimiter(calls_per_minute=120)

        # Graceful shutdown handling
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)

    async def start_session(self, student_id, student_profile):
        """Enhanced start_session with monitoring"""
        self.metrics.record_session_start()

        try:
            result = await super().start_session(student_id, student_profile)
            if result:
                self.logger.info(f"Session started successfully", extra={
                    'student_id': student_id,
                    'session_id': self.generate_session_id()
                })
            return result
        except Exception as e:
            self.metrics.record_error()
            self.logger.error(f"Failed to start session", extra={
                'student_id': student_id,
                'error': str(e)
            })
            raise

    async def _run_analysis_cycle(self):
        """Enhanced analysis cycle with monitoring and error recovery"""
        cycle_start = time.time()

        try:
            await super()._run_analysis_cycle()

            cycle_duration = time.time() - cycle_start
            self.metrics.record_analysis_cycle(cycle_duration)

            if cycle_duration > 10.0:  # Alert if cycle takes too long
                self.logger.warning(f"Slow analysis cycle: {cycle_duration:.2f}s")

        except Exception as e:
            self.metrics.record_error()
            self.logger.error(f"Analysis cycle failed: {e}")

            if self.config.error_recovery_enabled:
                await self.error_recovery.handle_analysis_failure(e)
            else:
                raise

    def _handle_shutdown(self, signum, frame):
        """Graceful shutdown handler"""
        self.logger.info(f"Received shutdown signal {signum}")
        asyncio.create_task(self._graceful_shutdown())

    async def _graceful_shutdown(self):
        """Perform graceful shutdown"""
        self.logger.info("Starting graceful shutdown")

        # Stop accepting new sessions
        self.accepting_new_sessions = False

        # Wait for current analysis cycles to complete
        if self.analysis_task:
            self.analysis_task.cancel()
            try:
                await asyncio.wait_for(self.analysis_task, timeout=30.0)
            except asyncio.TimeoutError:
                self.logger.warning("Analysis task did not complete within timeout")

        # Save current state
        await self._save_session_summary()

        self.logger.info("Graceful shutdown completed")

# src/core/error_recovery.py
class ErrorRecoverySystem:
    def __init__(self, teaching_assistant):
        self.ta = teaching_assistant
        self.failure_count = {}
        self.max_failures = 3
        self.recovery_strategies = {
            'gemini_api_error': self._recover_gemini_connection,
            'analysis_timeout': self._recover_analysis_timeout,
            'memory_error': self._recover_memory_error
        }

    async def handle_analysis_failure(self, error):
        """Handle analysis cycle failures with recovery strategies"""
        error_type = self._classify_error(error)

        if error_type in self.failure_count:
            self.failure_count[error_type] += 1
        else:
            self.failure_count[error_type] = 1

        if self.failure_count[error_type] <= self.max_failures:
            recovery_strategy = self.recovery_strategies.get(error_type)
            if recovery_strategy:
                await recovery_strategy(error)
                return True

        # Too many failures, escalate
        await self._escalate_error(error_type, error)
        return False

    def _classify_error(self, error):
        """Classify error type for appropriate recovery strategy"""
        if 'timeout' in str(error).lower():
            return 'analysis_timeout'
        elif 'gemini' in str(error).lower() or 'api' in str(error).lower():
            return 'gemini_api_error'
        elif 'memory' in str(error).lower():
            return 'memory_error'
        else:
            return 'unknown_error'

    async def _recover_gemini_connection(self, error):
        """Recover from Gemini API connection issues"""
        self.ta.logger.info("Attempting Gemini connection recovery")

        # Wait briefly and retry
        await asyncio.sleep(5)

        try:
            await self.ta.gemini_client.initialize_session()
            self.ta.logger.info("Gemini connection recovered")
            return True
        except Exception as e:
            self.ta.logger.error(f"Gemini recovery failed: {e}")
            return False

    async def _recover_analysis_timeout(self, error):
        """Recover from analysis timeout"""
        self.ta.logger.info("Handling analysis timeout")

        # Skip this analysis cycle and continue
        return True

    async def _recover_memory_error(self, error):
        """Recover from memory system errors"""
        self.ta.logger.info("Handling memory system error")

        # Clear some cached data and continue
        if hasattr(self.ta.vector_store, 'clear_cache'):
            self.ta.vector_store.clear_cache()

        return True

    async def _escalate_error(self, error_type, error):
        """Escalate persistent errors"""
        self.ta.logger.critical(f"Escalating persistent error: {error_type} - {error}")

        # Could send alerts, create tickets, etc.
        # For now, just log and continue with degraded functionality

# Deployment script
def deploy_production():
    """Deploy Teaching Assistant in production mode"""
    config = ProductionConfig()
    ta = ProductionTeachingAssistant(config)

    # Start monitoring dashboard
    dashboard_thread = threading.Thread(
        target=ta.monitoring_dashboard.run,
        args=(config.dashboard_host, config.dashboard_port),
        daemon=True
    )
    dashboard_thread.start()

    # Start health checker
    health_thread = threading.Thread(
        target=ta.health_checker.start_monitoring,
        daemon=True
    )
    health_thread.start()

    return ta

if __name__ == "__main__":
    ta = deploy_production()
    print("Teaching Assistant deployed in production mode")
    print(f"Monitoring dashboard available at http://localhost:8080/dashboard")

    # Keep main thread alive
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("Shutting down...")
```

**Deliverables**:
- Production-ready Teaching Assistant with monitoring
- Health check endpoints and monitoring dashboard
- Error recovery and graceful shutdown
- Comprehensive logging and metrics
- Deployment configuration

---

## **FINAL TESTING & EVALUATION PHASE**

### **Comprehensive System Tests**
1. **End-to-End Functionality**
   - Complete tutoring sessions with real scenarios
   - Emotional state detection accuracy validation
   - Intervention effectiveness measurement

2. **Performance Benchmarks**
   - 30-second analysis cycle timing
   - Memory usage under load
   - Concurrent session handling

3. **Reliability Tests**
   - 24-hour continuous operation
   - Error recovery effectiveness
   - Graceful degradation under failures

4. **Security and Privacy**
   - Data encryption validation
   - API key security
   - Student data protection

### **Success Criteria for Production**
- **Functional**: All 23 emotional skills working correctly
- **Performance**: <5 second analysis cycles, <1% error rate
- **Reliability**: >99% uptime, graceful error recovery
- **Scalability**: Support 100+ concurrent sessions
- **Accuracy**: >85% emotional state detection accuracy

### **Documentation Deliverables**
- API documentation for integration
- Operator manual for monitoring and maintenance
- Student data privacy compliance documentation
- Deployment and scaling guides

---

This comprehensive plan provides a step-by-step roadmap for building the hybrid Teaching Assistant system, with testing phases to ensure quality and reliability at each stage.