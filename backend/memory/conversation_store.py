"""
Conversation Memory System

Persistent storage of tutoring conversations with rich metadata.
Stores complete transcripts, extracts key moments, enables search.
"""

import sqlite3
import logging
from enum import Enum
from typing import Optional, List, Dict
from dataclasses import dataclass, field
from datetime import datetime
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MessageRole(Enum):
    """Roles for conversation messages"""
    STUDENT = "student"
    TUTOR = "tutor"
    SYSTEM = "system"


class InsightType(Enum):
    """Types of conversation insights"""
    BREAKTHROUGH = "breakthrough"
    STRUGGLE = "struggle"
    QUESTION = "question"
    MISCONCEPTION = "misconception"
    STRATEGY = "strategy"


@dataclass
class Message:
    """A single message in a conversation"""
    message_id: str
    conversation_id: str
    role: MessageRole
    content: str
    timestamp: float
    metadata: Dict = field(default_factory=dict)


@dataclass
class ConversationInsight:
    """An insight extracted from conversation"""
    insight_id: str
    conversation_id: str
    insight_type: InsightType
    content: str
    topic: str
    timestamp: float
    metadata: Dict = field(default_factory=dict)


@dataclass
class Conversation:
    """A tutoring conversation/session"""
    conversation_id: str
    student_id: str
    session_id: str
    start_time: float
    end_time: Optional[float] = None
    topic: Optional[str] = None
    summary: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


class ConversationStore:
    """
    Conversation Memory System

    Stores complete tutoring conversations with:
    - Full message transcripts
    - Extracted insights (breakthroughs, struggles, etc.)
    - Session summaries
    - Search and retrieval capabilities
    """

    def __init__(self, db_path: str = "./conversations.db"):
        """
        Initialize conversation store

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_database()
        logger.info(f"Conversation store initialized: {db_path}")

    def _init_database(self):
        """Initialize database schema"""
        cursor = self.conn.cursor()

        # Conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id TEXT PRIMARY KEY,
                student_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                start_time REAL NOT NULL,
                end_time REAL,
                topic TEXT,
                summary TEXT,
                metadata TEXT
            )
        ''')

        # Messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                message_id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp REAL NOT NULL,
                metadata TEXT,
                FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
            )
        ''')

        # Insights table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS insights (
                insight_id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                insight_type TEXT NOT NULL,
                content TEXT NOT NULL,
                topic TEXT NOT NULL,
                timestamp REAL NOT NULL,
                metadata TEXT,
                FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
            )
        ''')

        # Create indices for common queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_student ON conversations(student_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_topic ON conversations(topic)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_conv_messages ON messages(conversation_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_conv_insights ON insights(conversation_id)')

        self.conn.commit()

    def create_conversation(
        self,
        student_id: str,
        session_id: str,
        topic: Optional[str] = None
    ) -> Conversation:
        """
        Create a new conversation

        Args:
            student_id: Student identifier
            session_id: Session identifier
            topic: Optional topic/subject

        Returns:
            Created Conversation object
        """
        conversation_id = str(uuid.uuid4())
        start_time = datetime.now().timestamp()

        conversation = Conversation(
            conversation_id=conversation_id,
            student_id=student_id,
            session_id=session_id,
            start_time=start_time,
            topic=topic
        )

        cursor = self.conn.cursor()

        cursor.execute('''
            INSERT INTO conversations
            (conversation_id, student_id, session_id, start_time, topic)
            VALUES (?, ?, ?, ?, ?)
        ''', (conversation_id, student_id, session_id, start_time, topic))

        self.conn.commit()

        logger.info(f"Created conversation: {conversation_id} for student {student_id}")
        return conversation

    def add_message(
        self,
        conversation_id: str,
        role: MessageRole,
        content: str,
        metadata: Optional[Dict] = None
    ) -> Message:
        """
        Add a message to conversation

        Args:
            conversation_id: Conversation to add message to
            role: Message role (student/tutor/system)
            content: Message text
            metadata: Optional metadata

        Returns:
            Created Message object
        """
        if not content or len(content.strip()) == 0:
            raise ValueError("Message content cannot be empty")

        # Verify conversation exists
        if not self.get_conversation(conversation_id):
            raise ValueError(f"Conversation {conversation_id} does not exist")

        message_id = str(uuid.uuid4())
        timestamp = datetime.now().timestamp()

        message = Message(
            message_id=message_id,
            conversation_id=conversation_id,
            role=role,
            content=content,
            timestamp=timestamp,
            metadata=metadata or {}
        )

        # Use self.conn
        cursor = self.conn.cursor()

        cursor.execute('''
            INSERT INTO messages
            (message_id, conversation_id, role, content, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (message_id, conversation_id, role.value, content, timestamp, str(metadata or {})))

        self.conn.commit()
        

        logger.debug(f"Added message to conversation {conversation_id}")
        return message

    def add_insight(
        self,
        conversation_id: str,
        insight_type: InsightType,
        content: str,
        topic: str,
        metadata: Optional[Dict] = None
    ) -> ConversationInsight:
        """
        Add an insight to conversation

        Args:
            conversation_id: Conversation identifier
            insight_type: Type of insight
            content: Insight description
            topic: Related topic
            metadata: Optional metadata

        Returns:
            Created ConversationInsight object
        """
        insight_id = str(uuid.uuid4())
        timestamp = datetime.now().timestamp()

        insight = ConversationInsight(
            insight_id=insight_id,
            conversation_id=conversation_id,
            insight_type=insight_type,
            content=content,
            topic=topic,
            timestamp=timestamp,
            metadata=metadata or {}
        )

        # Use self.conn
        cursor = self.conn.cursor()

        cursor.execute('''
            INSERT INTO insights
            (insight_id, conversation_id, insight_type, content, topic, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (insight_id, conversation_id, insight_type.value, content, topic, timestamp, str(metadata or {})))

        self.conn.commit()
        

        logger.info(f"Added {insight_type.value} insight to conversation {conversation_id}")
        return insight

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        Get conversation by ID

        Args:
            conversation_id: Conversation identifier

        Returns:
            Conversation object or None
        """
        # Use self.conn
        cursor = self.conn.cursor()

        cursor.execute('''
            SELECT conversation_id, student_id, session_id, start_time,
                   end_time, topic, summary, metadata
            FROM conversations
            WHERE conversation_id = ?
        ''', (conversation_id,))

        row = cursor.fetchone()
        

        if not row:
            return None

        return Conversation(
            conversation_id=row[0],
            student_id=row[1],
            session_id=row[2],
            start_time=row[3],
            end_time=row[4],
            topic=row[5],
            summary=row[6],
            metadata=eval(row[7]) if row[7] else {}
        )

    def get_conversations_by_student(self, student_id: str) -> List[Conversation]:
        """
        Get all conversations for a student

        Args:
            student_id: Student identifier

        Returns:
            List of Conversation objects
        """
        # Use self.conn
        cursor = self.conn.cursor()

        cursor.execute('''
            SELECT conversation_id, student_id, session_id, start_time,
                   end_time, topic, summary, metadata
            FROM conversations
            WHERE student_id = ?
            ORDER BY start_time DESC
        ''', (student_id,))

        rows = cursor.fetchall()
        

        conversations = []
        for row in rows:
            conversations.append(Conversation(
                conversation_id=row[0],
                student_id=row[1],
                session_id=row[2],
                start_time=row[3],
                end_time=row[4],
                topic=row[5],
                summary=row[6],
                metadata=eval(row[7]) if row[7] else {}
            ))

        return conversations

    def get_messages(self, conversation_id: str) -> List[Message]:
        """
        Get all messages from a conversation

        Args:
            conversation_id: Conversation identifier

        Returns:
            List of Message objects
        """
        # Use self.conn
        cursor = self.conn.cursor()

        cursor.execute('''
            SELECT message_id, conversation_id, role, content, timestamp, metadata
            FROM messages
            WHERE conversation_id = ?
            ORDER BY timestamp ASC
        ''', (conversation_id,))

        rows = cursor.fetchall()
        

        messages = []
        for row in rows:
            messages.append(Message(
                message_id=row[0],
                conversation_id=row[1],
                role=MessageRole(row[2]),
                content=row[3],
                timestamp=row[4],
                metadata=eval(row[5]) if row[5] else {}
            ))

        return messages

    def get_insights(
        self,
        conversation_id: str,
        insight_type: Optional[InsightType] = None
    ) -> List[ConversationInsight]:
        """
        Get insights from a conversation

        Args:
            conversation_id: Conversation identifier
            insight_type: Optional filter by insight type

        Returns:
            List of ConversationInsight objects
        """
        # Use self.conn
        cursor = self.conn.cursor()

        if insight_type:
            cursor.execute('''
                SELECT insight_id, conversation_id, insight_type, content,
                       topic, timestamp, metadata
                FROM insights
                WHERE conversation_id = ? AND insight_type = ?
                ORDER BY timestamp ASC
            ''', (conversation_id, insight_type.value))
        else:
            cursor.execute('''
                SELECT insight_id, conversation_id, insight_type, content,
                       topic, timestamp, metadata
                FROM insights
                WHERE conversation_id = ?
                ORDER BY timestamp ASC
            ''', (conversation_id,))

        rows = cursor.fetchall()
        

        insights = []
        for row in rows:
            insights.append(ConversationInsight(
                insight_id=row[0],
                conversation_id=row[1],
                insight_type=InsightType(row[2]),
                content=row[3],
                topic=row[4],
                timestamp=row[5],
                metadata=eval(row[6]) if row[6] else {}
            ))

        return insights

    def search_conversations(
        self,
        student_id: Optional[str] = None,
        topic: Optional[str] = None,
        start_date: Optional[float] = None,
        end_date: Optional[float] = None
    ) -> List[Conversation]:
        """
        Search conversations with filters

        Args:
            student_id: Filter by student
            topic: Filter by topic
            start_date: Filter by start date (timestamp)
            end_date: Filter by end date (timestamp)

        Returns:
            List of matching Conversation objects
        """
        # Use self.conn
        cursor = self.conn.cursor()

        query = '''
            SELECT conversation_id, student_id, session_id, start_time,
                   end_time, topic, summary, metadata
            FROM conversations
            WHERE 1=1
        '''
        params = []

        if student_id:
            query += ' AND student_id = ?'
            params.append(student_id)

        if topic:
            query += ' AND topic = ?'
            params.append(topic)

        if start_date:
            query += ' AND start_time >= ?'
            params.append(start_date)

        if end_date:
            query += ' AND start_time <= ?'
            params.append(end_date)

        query += ' ORDER BY start_time DESC'

        cursor.execute(query, params)
        rows = cursor.fetchall()
        

        conversations = []
        for row in rows:
            conversations.append(Conversation(
                conversation_id=row[0],
                student_id=row[1],
                session_id=row[2],
                start_time=row[3],
                end_time=row[4],
                topic=row[5],
                summary=row[6],
                metadata=eval(row[7]) if row[7] else {}
            ))

        return conversations

    def generate_summary(self, conversation_id: str) -> str:
        """
        Generate summary for conversation

        Args:
            conversation_id: Conversation identifier

        Returns:
            Summary text
        """
        messages = self.get_messages(conversation_id)
        insights = self.get_insights(conversation_id)

        # Simple summary: count messages and insights
        summary_parts = []
        summary_parts.append(f"{len(messages)} messages exchanged")

        if insights:
            insight_counts = {}
            for insight in insights:
                insight_counts[insight.insight_type.value] = insight_counts.get(insight.insight_type.value, 0) + 1

            for insight_type, count in insight_counts.items():
                summary_parts.append(f"{count} {insight_type}(s)")

        summary = ", ".join(summary_parts)

        # Store summary in conversation
        # Use self.conn
        cursor = self.conn.cursor()

        cursor.execute('''
            UPDATE conversations
            SET summary = ?
            WHERE conversation_id = ?
        ''', (summary, conversation_id))

        self.conn.commit()
        

        logger.info(f"Generated summary for conversation {conversation_id}")
        return summary

    def close_conversation(self, conversation_id: str):
        """
        Close a conversation (set end time)

        Args:
            conversation_id: Conversation identifier
        """
        end_time = datetime.now().timestamp()

        # Use self.conn
        cursor = self.conn.cursor()

        cursor.execute('''
            UPDATE conversations
            SET end_time = ?
            WHERE conversation_id = ?
        ''', (end_time, conversation_id))

        self.conn.commit()
        

        logger.info(f"Closed conversation {conversation_id}")
