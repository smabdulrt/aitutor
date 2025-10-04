"""
Tests for Conversation Memory System

Following TDD: Tests written FIRST, then implementation.
All logic imported from codebase - NO hardcoded test logic.

Conversation Store:
1. Store complete conversation transcripts
2. Extract key moments (breakthroughs, struggles, questions)
3. Search conversations by topic, date, outcome
4. Generate session summaries
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock
from backend.memory.conversation_store import (
    ConversationStore,
    Conversation,
    Message,
    MessageRole,
    ConversationInsight,
    InsightType
)


class TestConversationStoreInitialization:
    """Test conversation store initialization"""

    def test_initialization(self):
        """Test store initializes correctly"""
        store = ConversationStore()

        assert store is not None
        assert store.db_path is not None

    def test_initialization_with_custom_path(self):
        """Test initialization with custom database path"""
        custom_path = "/tmp/test_conversations.db"
        store = ConversationStore(db_path=custom_path)

        assert store.db_path == custom_path


class TestConversationCreation:
    """Test creating and storing conversations"""

    @pytest.fixture
    def store(self):
        return ConversationStore(db_path=":memory:")

    def test_create_conversation(self, store):
        """Test creating a new conversation"""
        conv = store.create_conversation(
            student_id="student_123",
            session_id="session_abc"
        )

        assert conv is not None
        assert isinstance(conv, Conversation)
        assert conv.student_id == "student_123"
        assert conv.session_id == "session_abc"
        assert conv.conversation_id is not None

    def test_conversation_has_timestamp(self, store):
        """Test conversation gets timestamp"""
        conv = store.create_conversation(
            student_id="student_456",
            session_id="session_xyz"
        )

        assert conv.start_time is not None
        assert isinstance(conv.start_time, float)


class TestMessageStorage:
    """Test storing messages in conversations"""

    @pytest.fixture
    def store(self):
        return ConversationStore(db_path=":memory:")

    @pytest.fixture
    def conversation(self, store):
        return store.create_conversation(
            student_id="student_123",
            session_id="session_abc"
        )

    def test_add_message(self, store, conversation):
        """Test adding a message to conversation"""
        message = store.add_message(
            conversation_id=conversation.conversation_id,
            role=MessageRole.STUDENT,
            content="What is 2+2?"
        )

        assert message is not None
        assert isinstance(message, Message)
        assert message.role == MessageRole.STUDENT
        assert message.content == "What is 2+2?"

    def test_add_tutor_message(self, store, conversation):
        """Test adding tutor response"""
        message = store.add_message(
            conversation_id=conversation.conversation_id,
            role=MessageRole.TUTOR,
            content="What do you think? Let's work through it."
        )

        assert message.role == MessageRole.TUTOR
        assert "work through it" in message.content

    def test_message_has_timestamp(self, store, conversation):
        """Test messages get timestamps"""
        message = store.add_message(
            conversation_id=conversation.conversation_id,
            role=MessageRole.STUDENT,
            content="Test message"
        )

        assert message.timestamp is not None


class TestConversationRetrieval:
    """Test retrieving conversations"""

    @pytest.fixture
    def store(self):
        return ConversationStore(db_path=":memory:")

    def test_get_conversation_by_id(self, store):
        """Test retrieving conversation by ID"""
        conv = store.create_conversation(
            student_id="student_123",
            session_id="session_abc"
        )

        retrieved = store.get_conversation(conv.conversation_id)

        assert retrieved is not None
        assert retrieved.conversation_id == conv.conversation_id
        assert retrieved.student_id == "student_123"

    def test_get_conversations_by_student(self, store):
        """Test retrieving all conversations for a student"""
        store.create_conversation(student_id="student_123", session_id="s1")
        store.create_conversation(student_id="student_123", session_id="s2")
        store.create_conversation(student_id="student_456", session_id="s3")

        conversations = store.get_conversations_by_student("student_123")

        assert len(conversations) == 2
        assert all(c.student_id == "student_123" for c in conversations)

    def test_get_conversation_messages(self, store):
        """Test retrieving messages from conversation"""
        conv = store.create_conversation(
            student_id="student_123",
            session_id="session_abc"
        )

        store.add_message(conv.conversation_id, MessageRole.STUDENT, "Question 1")
        store.add_message(conv.conversation_id, MessageRole.TUTOR, "Answer 1")
        store.add_message(conv.conversation_id, MessageRole.STUDENT, "Question 2")

        messages = store.get_messages(conv.conversation_id)

        assert len(messages) == 3
        assert messages[0].role == MessageRole.STUDENT
        assert messages[1].role == MessageRole.TUTOR


class TestConversationInsights:
    """Test extracting and storing conversation insights"""

    @pytest.fixture
    def store(self):
        return ConversationStore(db_path=":memory:")

    @pytest.fixture
    def conversation(self, store):
        return store.create_conversation(
            student_id="student_123",
            session_id="session_abc"
        )

    def test_add_insight(self, store, conversation):
        """Test adding insight to conversation"""
        insight = store.add_insight(
            conversation_id=conversation.conversation_id,
            insight_type=InsightType.BREAKTHROUGH,
            content="Student understood quadratic formula!",
            topic="algebra"
        )

        assert insight is not None
        assert isinstance(insight, ConversationInsight)
        assert insight.insight_type == InsightType.BREAKTHROUGH
        assert insight.topic == "algebra"

    def test_add_struggle_insight(self, store, conversation):
        """Test adding struggle insight"""
        insight = store.add_insight(
            conversation_id=conversation.conversation_id,
            insight_type=InsightType.STRUGGLE,
            content="Confused about negative exponents",
            topic="exponents"
        )

        assert insight.insight_type == InsightType.STRUGGLE

    def test_get_insights_by_conversation(self, store, conversation):
        """Test retrieving insights for a conversation"""
        store.add_insight(
            conversation.conversation_id,
            InsightType.BREAKTHROUGH,
            "Moment 1",
            "topic1"
        )
        store.add_insight(
            conversation.conversation_id,
            InsightType.QUESTION,
            "Moment 2",
            "topic2"
        )

        insights = store.get_insights(conversation.conversation_id)

        assert len(insights) == 2

    def test_get_insights_by_type(self, store, conversation):
        """Test filtering insights by type"""
        store.add_insight(
            conversation.conversation_id,
            InsightType.BREAKTHROUGH,
            "Breakthrough",
            "algebra"
        )
        store.add_insight(
            conversation.conversation_id,
            InsightType.STRUGGLE,
            "Struggle",
            "geometry"
        )

        breakthroughs = store.get_insights(
            conversation.conversation_id,
            insight_type=InsightType.BREAKTHROUGH
        )

        assert len(breakthroughs) == 1
        assert breakthroughs[0].insight_type == InsightType.BREAKTHROUGH


class TestConversationSearch:
    """Test searching conversations"""

    @pytest.fixture
    def store(self):
        return ConversationStore(db_path=":memory:")

    def test_search_by_topic(self, store):
        """Test searching conversations by topic"""
        conv1 = store.create_conversation("student_123", "s1", topic="algebra")
        conv2 = store.create_conversation("student_123", "s2", topic="geometry")
        conv3 = store.create_conversation("student_456", "s3", topic="algebra")

        results = store.search_conversations(topic="algebra")

        assert len(results) == 2
        assert all(c.topic == "algebra" for c in results)

    def test_search_by_student_and_topic(self, store):
        """Test searching with multiple filters"""
        store.create_conversation("student_123", "s1", topic="algebra")
        store.create_conversation("student_123", "s2", topic="geometry")
        store.create_conversation("student_456", "s3", topic="algebra")

        results = store.search_conversations(
            student_id="student_123",
            topic="algebra"
        )

        assert len(results) == 1
        assert results[0].student_id == "student_123"
        assert results[0].topic == "algebra"

    def test_search_by_date_range(self, store):
        """Test searching conversations by date range"""
        conv = store.create_conversation("student_123", "s1")

        # Search should find recent conversation
        results = store.search_conversations(
            student_id="student_123",
            start_date=datetime.now().timestamp() - 3600  # Last hour
        )

        assert len(results) == 1


class TestConversationSummary:
    """Test generating conversation summaries"""

    @pytest.fixture
    def store(self):
        return ConversationStore(db_path=":memory:")

    def test_generate_summary(self, store):
        """Test generating summary for conversation"""
        conv = store.create_conversation("student_123", "s1")

        store.add_message(conv.conversation_id, MessageRole.STUDENT, "What is 2+2?")
        store.add_message(conv.conversation_id, MessageRole.TUTOR, "What do you think?")
        store.add_message(conv.conversation_id, MessageRole.STUDENT, "Is it 4?")

        summary = store.generate_summary(conv.conversation_id)

        assert summary is not None
        assert isinstance(summary, str)
        assert len(summary) > 0

    def test_summary_stored_in_conversation(self, store):
        """Test summary is stored with conversation"""
        conv = store.create_conversation("student_123", "s1")

        store.add_message(conv.conversation_id, MessageRole.STUDENT, "Question")
        summary = store.generate_summary(conv.conversation_id)

        retrieved = store.get_conversation(conv.conversation_id)
        assert retrieved.summary == summary


class TestMessageRoleEnum:
    """Test message role enumeration"""

    def test_message_roles_exist(self):
        """Test all expected message roles are defined"""
        expected_roles = [
            MessageRole.STUDENT,
            MessageRole.TUTOR,
            MessageRole.SYSTEM
        ]

        for role in expected_roles:
            assert role in MessageRole


class TestInsightTypeEnum:
    """Test insight type enumeration"""

    def test_insight_types_exist(self):
        """Test all expected insight types are defined"""
        expected_types = [
            InsightType.BREAKTHROUGH,
            InsightType.STRUGGLE,
            InsightType.QUESTION,
            InsightType.MISCONCEPTION,
            InsightType.STRATEGY
        ]

        for insight_type in expected_types:
            assert insight_type in InsightType


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_get_nonexistent_conversation(self):
        """Test retrieving non-existent conversation"""
        store = ConversationStore(db_path=":memory:")

        result = store.get_conversation("nonexistent_id")

        assert result is None

    def test_add_message_to_nonexistent_conversation(self):
        """Test adding message to non-existent conversation"""
        store = ConversationStore(db_path=":memory:")

        with pytest.raises(ValueError):
            store.add_message("nonexistent_id", MessageRole.STUDENT, "Test")

    def test_empty_message_content(self):
        """Test handling empty message content"""
        store = ConversationStore(db_path=":memory:")
        conv = store.create_conversation("student_123", "s1")

        with pytest.raises(ValueError):
            store.add_message(conv.conversation_id, MessageRole.STUDENT, "")

    def test_close_conversation(self):
        """Test closing a conversation"""
        store = ConversationStore(db_path=":memory:")
        conv = store.create_conversation("student_123", "s1")

        store.close_conversation(conv.conversation_id)

        retrieved = store.get_conversation(conv.conversation_id)
        assert retrieved.end_time is not None
        assert retrieved.end_time > retrieved.start_time
