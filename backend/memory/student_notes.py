"""
Student Notes & Annotations

Auto-extract and store personalized notes from tutoring conversations.
Categories: Learning Preferences, Misconceptions, Strong/Weak Topics, Personal Context, Goals
"""

import sqlite3
import logging
from enum import Enum
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NoteCategory(Enum):
    """Categories of student notes"""
    LEARNING_PREFERENCE = "learning_preference"
    MISCONCEPTION = "misconception"
    STRONG_TOPIC = "strong_topic"
    WEAK_TOPIC = "weak_topic"
    PERSONAL_CONTEXT = "personal_context"
    SESSION_GOAL = "session_goal"


@dataclass
class Note:
    """A student note/annotation"""
    note_id: str
    student_id: str
    category: NoteCategory
    content: str
    topic: str
    timestamp: float
    source_conversation_id: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    is_archived: bool = False


class StudentNotes:
    """
    Student Notes & Annotations System

    Stores personalized notes extracted from conversations:
    - Learning preferences (visual learner, likes examples, etc.)
    - Misconceptions (common errors, misunderstandings)
    - Strong topics (excels at geometry, quick with mental math)
    - Weak topics (struggles with word problems, needs help with negatives)
    - Personal context (learning for SAT, plays basketball)
    - Session goals (master algebra, improve accuracy to 80%)
    """

    def __init__(self, db_path: str = "./student_notes.db", note_limit: Optional[int] = None):
        """
        Initialize student notes system

        Args:
            db_path: Path to SQLite database file
            note_limit: Optional limit on active notes per student
        """
        self.db_path = db_path
        self.note_limit = note_limit
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_database()
        logger.info(f"Student notes system initialized: {db_path}")

    def _init_database(self):
        """Initialize database schema"""
        cursor = self.conn.cursor()

        # Notes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                note_id TEXT PRIMARY KEY,
                student_id TEXT NOT NULL,
                category TEXT NOT NULL,
                content TEXT NOT NULL,
                topic TEXT NOT NULL,
                timestamp REAL NOT NULL,
                source_conversation_id TEXT,
                metadata TEXT,
                is_archived INTEGER DEFAULT 0
            )
        ''')

        # Create indices for common queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_student_notes ON notes(student_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON notes(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_topic ON notes(topic)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_archived ON notes(is_archived)')

        # Full-text search index
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts USING fts5(
                note_id, content, topic, tokenize='porter'
            )
        ''')

        self.conn.commit()

    def create_note(
        self,
        student_id: str,
        category: NoteCategory,
        content: str,
        topic: str,
        source_conversation_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Note:
        """
        Create a new note

        Args:
            student_id: Student identifier
            category: Note category
            content: Note text
            topic: Related topic
            source_conversation_id: Optional source conversation
            metadata: Optional metadata

        Returns:
            Created Note object
        """
        if not content or len(content.strip()) == 0:
            raise ValueError("Note content cannot be empty")

        note_id = str(uuid.uuid4())
        timestamp = datetime.now().timestamp()

        note = Note(
            note_id=note_id,
            student_id=student_id,
            category=category,
            content=content,
            topic=topic,
            timestamp=timestamp,
            source_conversation_id=source_conversation_id,
            metadata=metadata or {}
        )

        cursor = self.conn.cursor()

        # Insert into main table
        cursor.execute('''
            INSERT INTO notes
            (note_id, student_id, category, content, topic, timestamp,
             source_conversation_id, metadata, is_archived)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (note_id, student_id, category.value, content, topic, timestamp,
              source_conversation_id, json.dumps(metadata or {}), 0))

        # Insert into FTS table
        cursor.execute('''
            INSERT INTO notes_fts (note_id, content, topic)
            VALUES (?, ?, ?)
        ''', (note_id, content, topic))

        self.conn.commit()

        # Check note limit
        if self.note_limit:
            self._enforce_note_limit(student_id)

        logger.info(f"Created note for student {student_id}: {category.value}")
        return note

    def get_notes_by_student(self, student_id: str, include_archived: bool = False) -> List[Note]:
        """
        Get all notes for a student

        Args:
            student_id: Student identifier
            include_archived: Include archived notes

        Returns:
            List of Note objects
        """
        cursor = self.conn.cursor()

        if include_archived:
            cursor.execute('''
                SELECT note_id, student_id, category, content, topic, timestamp,
                       source_conversation_id, metadata, is_archived
                FROM notes
                WHERE student_id = ?
                ORDER BY timestamp DESC
            ''', (student_id,))
        else:
            cursor.execute('''
                SELECT note_id, student_id, category, content, topic, timestamp,
                       source_conversation_id, metadata, is_archived
                FROM notes
                WHERE student_id = ? AND is_archived = 0
                ORDER BY timestamp DESC
            ''', (student_id,))

        rows = cursor.fetchall()

        notes = []
        for row in rows:
            notes.append(Note(
                note_id=row[0],
                student_id=row[1],
                category=NoteCategory(row[2]),
                content=row[3],
                topic=row[4],
                timestamp=row[5],
                source_conversation_id=row[6],
                metadata=json.loads(row[7]) if row[7] else {},
                is_archived=bool(row[8])
            ))

        return notes

    def get_notes_by_category(
        self,
        student_id: str,
        category: NoteCategory
    ) -> List[Note]:
        """
        Get notes filtered by category

        Args:
            student_id: Student identifier
            category: Note category

        Returns:
            List of Note objects
        """
        cursor = self.conn.cursor()

        cursor.execute('''
            SELECT note_id, student_id, category, content, topic, timestamp,
                   source_conversation_id, metadata, is_archived
            FROM notes
            WHERE student_id = ? AND category = ? AND is_archived = 0
            ORDER BY timestamp DESC
        ''', (student_id, category.value))

        rows = cursor.fetchall()

        notes = []
        for row in rows:
            notes.append(Note(
                note_id=row[0],
                student_id=row[1],
                category=NoteCategory(row[2]),
                content=row[3],
                topic=row[4],
                timestamp=row[5],
                source_conversation_id=row[6],
                metadata=json.loads(row[7]) if row[7] else {},
                is_archived=bool(row[8])
            ))

        return notes

    def get_notes_by_topic(self, student_id: str, topic: str) -> List[Note]:
        """
        Get notes filtered by topic

        Args:
            student_id: Student identifier
            topic: Topic string

        Returns:
            List of Note objects
        """
        cursor = self.conn.cursor()

        cursor.execute('''
            SELECT note_id, student_id, category, content, topic, timestamp,
                   source_conversation_id, metadata, is_archived
            FROM notes
            WHERE student_id = ? AND topic = ? AND is_archived = 0
            ORDER BY timestamp DESC
        ''', (student_id, topic))

        rows = cursor.fetchall()

        notes = []
        for row in rows:
            notes.append(Note(
                note_id=row[0],
                student_id=row[1],
                category=NoteCategory(row[2]),
                content=row[3],
                topic=row[4],
                timestamp=row[5],
                source_conversation_id=row[6],
                metadata=json.loads(row[7]) if row[7] else {},
                is_archived=bool(row[8])
            ))

        return notes

    def get_recent_notes(self, student_id: str, limit: int = 10) -> List[Note]:
        """
        Get recent notes for a student

        Args:
            student_id: Student identifier
            limit: Maximum number of notes

        Returns:
            List of Note objects
        """
        cursor = self.conn.cursor()

        cursor.execute('''
            SELECT note_id, student_id, category, content, topic, timestamp,
                   source_conversation_id, metadata, is_archived
            FROM notes
            WHERE student_id = ? AND is_archived = 0
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (student_id, limit))

        rows = cursor.fetchall()

        notes = []
        for row in rows:
            notes.append(Note(
                note_id=row[0],
                student_id=row[1],
                category=NoteCategory(row[2]),
                content=row[3],
                topic=row[4],
                timestamp=row[5],
                source_conversation_id=row[6],
                metadata=json.loads(row[7]) if row[7] else {},
                is_archived=bool(row[8])
            ))

        return notes

    def search_notes(
        self,
        student_id: str,
        query: str,
        include_score: bool = False
    ) -> List:
        """
        Search notes using full-text search

        Args:
            student_id: Student identifier
            query: Search query
            include_score: Include relevance scores

        Returns:
            List of Note objects (or tuples with scores)
        """
        cursor = self.conn.cursor()

        # Use FTS for search
        cursor.execute('''
            SELECT n.note_id, n.student_id, n.category, n.content, n.topic,
                   n.timestamp, n.source_conversation_id, n.metadata, n.is_archived
            FROM notes n
            INNER JOIN notes_fts fts ON n.note_id = fts.note_id
            WHERE fts.notes_fts MATCH ? AND n.student_id = ? AND n.is_archived = 0
            ORDER BY rank
        ''', (query, student_id))

        rows = cursor.fetchall()

        notes = []
        for row in rows:
            note = Note(
                note_id=row[0],
                student_id=row[1],
                category=NoteCategory(row[2]),
                content=row[3],
                topic=row[4],
                timestamp=row[5],
                source_conversation_id=row[6],
                metadata=json.loads(row[7]) if row[7] else {},
                is_archived=bool(row[8])
            )

            if include_score:
                # Add relevance score attribute
                note.relevance_score = 1.0  # Simplified scoring
                notes.append(note)
            else:
                notes.append(note)

        return notes

    def update_note(self, note_id: str, content: str) -> Note:
        """
        Update a note's content

        Args:
            note_id: Note identifier
            content: New content

        Returns:
            Updated Note object
        """
        cursor = self.conn.cursor()

        # Check if note exists
        cursor.execute('SELECT * FROM notes WHERE note_id = ?', (note_id,))
        row = cursor.fetchone()

        if not row:
            raise ValueError(f"Note {note_id} does not exist")

        # Update note
        cursor.execute('''
            UPDATE notes
            SET content = ?
            WHERE note_id = ?
        ''', (content, note_id))

        # Update FTS
        cursor.execute('''
            UPDATE notes_fts
            SET content = ?
            WHERE note_id = ?
        ''', (content, note_id))

        self.conn.commit()

        # Return updated note
        cursor.execute('''
            SELECT note_id, student_id, category, content, topic, timestamp,
                   source_conversation_id, metadata, is_archived
            FROM notes
            WHERE note_id = ?
        ''', (note_id,))

        row = cursor.fetchone()

        return Note(
            note_id=row[0],
            student_id=row[1],
            category=NoteCategory(row[2]),
            content=row[3],
            topic=row[4],
            timestamp=row[5],
            source_conversation_id=row[6],
            metadata=json.loads(row[7]) if row[7] else {},
            is_archived=bool(row[8])
        )

    def delete_note(self, note_id: str) -> bool:
        """
        Delete a note

        Args:
            note_id: Note identifier

        Returns:
            True if deleted, False if not found
        """
        cursor = self.conn.cursor()

        cursor.execute('DELETE FROM notes WHERE note_id = ?', (note_id,))
        cursor.execute('DELETE FROM notes_fts WHERE note_id = ?', (note_id,))

        self.conn.commit()

        return cursor.rowcount > 0

    def get_student_summary(self, student_id: str) -> Dict:
        """
        Get summary of student notes grouped by category

        Args:
            student_id: Student identifier

        Returns:
            Dictionary with notes grouped by category
        """
        all_notes = self.get_notes_by_student(student_id)

        summary = {
            "learning_preferences": [],
            "misconceptions": [],
            "strong_topics": [],
            "weak_topics": [],
            "personal_context": [],
            "goals": []
        }

        for note in all_notes:
            if note.category == NoteCategory.LEARNING_PREFERENCE:
                summary["learning_preferences"].append(note)
            elif note.category == NoteCategory.MISCONCEPTION:
                summary["misconceptions"].append(note)
            elif note.category == NoteCategory.STRONG_TOPIC:
                summary["strong_topics"].append(note)
            elif note.category == NoteCategory.WEAK_TOPIC:
                summary["weak_topics"].append(note)
            elif note.category == NoteCategory.PERSONAL_CONTEXT:
                summary["personal_context"].append(note)
            elif note.category == NoteCategory.SESSION_GOAL:
                summary["goals"].append(note)

        return summary

    def get_context_for_topic(self, student_id: str, topic: str) -> List[Note]:
        """
        Get relevant notes for a specific topic

        Args:
            student_id: Student identifier
            topic: Topic string

        Returns:
            List of relevant notes
        """
        # Get notes directly related to topic
        topic_notes = self.get_notes_by_topic(student_id, topic)

        # Also search for topic in content
        search_notes = self.search_notes(student_id, topic)

        # Combine and deduplicate
        seen_ids = set()
        combined = []

        for note in topic_notes + search_notes:
            if note.note_id not in seen_ids:
                seen_ids.add(note.note_id)
                combined.append(note)

        return combined

    def has_archived_notes(self, student_id: str) -> bool:
        """
        Check if student has archived notes

        Args:
            student_id: Student identifier

        Returns:
            True if student has archived notes
        """
        cursor = self.conn.cursor()

        cursor.execute('''
            SELECT COUNT(*) FROM notes
            WHERE student_id = ? AND is_archived = 1
        ''', (student_id,))

        count = cursor.fetchone()[0]
        return count > 0

    def _enforce_note_limit(self, student_id: str):
        """
        Enforce note limit by archiving oldest notes

        Args:
            student_id: Student identifier
        """
        if not self.note_limit:
            return

        cursor = self.conn.cursor()

        # Count active notes
        cursor.execute('''
            SELECT COUNT(*) FROM notes
            WHERE student_id = ? AND is_archived = 0
        ''', (student_id,))

        count = cursor.fetchone()[0]

        if count > self.note_limit:
            # Archive oldest notes
            excess = count - self.note_limit

            cursor.execute('''
                UPDATE notes
                SET is_archived = 1
                WHERE note_id IN (
                    SELECT note_id FROM notes
                    WHERE student_id = ? AND is_archived = 0
                    ORDER BY timestamp ASC
                    LIMIT ?
                )
            ''', (student_id, excess))

            self.conn.commit()
            logger.info(f"Archived {excess} old notes for student {student_id}")


class NoteExtractor:
    """
    Extract notes from conversation transcripts using LLM
    """

    def __init__(self, llm_provider: Optional[str] = None):
        """
        Initialize note extractor

        Args:
            llm_provider: Optional LLM provider (gpt-4, claude, etc.)
        """
        self.llm_provider = llm_provider or "mock"
        logger.info(f"Note extractor initialized with provider: {self.llm_provider}")

    async def extract_notes(
        self,
        student_id: str,
        conversation_id: str,
        transcript: List[Dict]
    ) -> List[Note]:
        """
        Extract notes from conversation transcript

        Args:
            student_id: Student identifier
            conversation_id: Conversation identifier
            transcript: List of message dicts with 'role' and 'content'

        Returns:
            List of extracted Note objects
        """
        if not transcript:
            return []

        # Call LLM to extract notes
        extracted = await self._call_llm(transcript)

        # Convert to Note objects
        notes = []
        for item in extracted:
            try:
                note = Note(
                    note_id=str(uuid.uuid4()),
                    student_id=student_id,
                    category=NoteCategory[item["category"]],
                    content=item["content"],
                    topic=item["topic"],
                    timestamp=datetime.now().timestamp(),
                    source_conversation_id=conversation_id
                )
                notes.append(note)
            except (KeyError, ValueError) as e:
                logger.warning(f"Skipping invalid extracted note: {e}")
                continue

        logger.info(f"Extracted {len(notes)} notes from conversation {conversation_id}")
        return notes

    async def _call_llm(self, transcript: List[Dict]) -> List[Dict]:
        """
        Call LLM to extract notes from transcript

        Args:
            transcript: Conversation transcript

        Returns:
            List of extracted note dicts
        """
        # Mock implementation for testing
        # In production, this would call GPT-4 or Claude
        extracted_notes = []

        for message in transcript:
            content = message.get("content", "").lower()
            role = message.get("role", "")

            # Simple keyword-based extraction for testing
            if "prefer" in content or "like" in content or "diagram" in content or "example" in content:
                extracted_notes.append({
                    "category": "LEARNING_PREFERENCE",
                    "content": f"Student mentioned: {message['content'][:50]}...",
                    "topic": "learning_style"
                })

            # Detect misconceptions from student questions/statements
            if role == "student":
                if ("confused" in content or
                    "don't understand" in content or
                    ("right?" in content and ("always" in content or "never" in content)) or
                    ("thinks" in content.lower() and message.get("role") == "tutor")):
                    extracted_notes.append({
                        "category": "MISCONCEPTION",
                        "content": f"Confusion point: {message['content'][:50]}...",
                        "topic": "understanding"
                    })

        return extracted_notes
