"""
Tests for Student Notes & Annotations

Following TDD: Tests written FIRST, then implementation.
All logic imported from codebase - NO hardcoded test logic.

Student Notes:
1. Auto-extract notes from conversations (LLM-powered)
2. Categorize notes (preferences, misconceptions, strong/weak topics, personal context, goals)
3. Store and retrieve notes
4. Search notes by category, topic, or query
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
from backend.memory.student_notes import (
    StudentNotes,
    Note,
    NoteCategory,
    NoteExtractor
)


class TestStudentNotesInitialization:
    """Test student notes system initialization"""

    def test_initialization(self):
        """Test notes system initializes correctly"""
        notes = StudentNotes()

        assert notes is not None
        assert notes.db_path is not None

    def test_initialization_with_custom_path(self):
        """Test initialization with custom database path"""
        custom_path = "/tmp/test_notes.db"
        notes = StudentNotes(db_path=custom_path)

        assert notes.db_path == custom_path


class TestNoteCreation:
    """Test creating and storing notes"""

    @pytest.fixture
    def notes(self):
        return StudentNotes(db_path=":memory:")

    def test_create_note(self, notes):
        """Test creating a note"""
        note = notes.create_note(
            student_id="student_123",
            category=NoteCategory.LEARNING_PREFERENCE,
            content="Prefers visual explanations with diagrams",
            topic="learning_style"
        )

        assert note is not None
        assert isinstance(note, Note)
        assert note.student_id == "student_123"
        assert note.category == NoteCategory.LEARNING_PREFERENCE
        assert "visual" in note.content

    def test_note_has_timestamp(self, notes):
        """Test note gets timestamp"""
        note = notes.create_note(
            student_id="student_456",
            category=NoteCategory.STRONG_TOPIC,
            content="Excels at geometry",
            topic="geometry"
        )

        assert note.timestamp is not None
        assert isinstance(note.timestamp, float)

    def test_note_with_source_conversation(self, notes):
        """Test note can reference source conversation"""
        note = notes.create_note(
            student_id="student_789",
            category=NoteCategory.MISCONCEPTION,
            content="Thinks fractions must be less than 1",
            topic="fractions",
            source_conversation_id="conv_123"
        )

        assert note.source_conversation_id == "conv_123"


class TestNoteCategories:
    """Test note categorization"""

    def test_note_categories_exist(self):
        """Test all expected note categories are defined"""
        expected_categories = [
            NoteCategory.LEARNING_PREFERENCE,
            NoteCategory.MISCONCEPTION,
            NoteCategory.STRONG_TOPIC,
            NoteCategory.WEAK_TOPIC,
            NoteCategory.PERSONAL_CONTEXT,
            NoteCategory.SESSION_GOAL
        ]

        for category in expected_categories:
            assert category in NoteCategory


class TestNoteRetrieval:
    """Test retrieving notes"""

    @pytest.fixture
    def notes(self):
        system = StudentNotes(db_path=":memory:")

        # Add sample notes
        system.create_note(
            "student_123",
            NoteCategory.LEARNING_PREFERENCE,
            "Likes basketball analogies",
            "preferences"
        )
        system.create_note(
            "student_123",
            NoteCategory.WEAK_TOPIC,
            "Struggles with negative numbers",
            "negatives"
        )
        system.create_note(
            "student_456",
            NoteCategory.STRONG_TOPIC,
            "Great at mental math",
            "arithmetic"
        )

        return system

    def test_get_notes_by_student(self, notes):
        """Test retrieving all notes for a student"""
        student_notes = notes.get_notes_by_student("student_123")

        assert len(student_notes) == 2
        assert all(n.student_id == "student_123" for n in student_notes)

    def test_get_notes_by_category(self, notes):
        """Test filtering notes by category"""
        weak_topics = notes.get_notes_by_category(
            "student_123",
            NoteCategory.WEAK_TOPIC
        )

        assert len(weak_topics) == 1
        assert weak_topics[0].category == NoteCategory.WEAK_TOPIC

    def test_get_notes_by_topic(self, notes):
        """Test filtering notes by topic"""
        notes_about_negatives = notes.get_notes_by_topic(
            "student_123",
            "negatives"
        )

        assert len(notes_about_negatives) == 1
        assert "negative" in notes_about_negatives[0].content.lower()

    def test_get_recent_notes(self, notes):
        """Test retrieving recent notes"""
        recent = notes.get_recent_notes("student_123", limit=1)

        assert len(recent) == 1
        # Should return most recently created note


class TestNoteExtraction:
    """Test extracting notes from conversations"""

    @pytest.fixture
    def extractor(self):
        return NoteExtractor()

    @pytest.mark.asyncio
    async def test_extract_notes_from_conversation(self, extractor):
        """Test extracting notes from conversation transcript"""
        conversation_transcript = [
            {"role": "student", "content": "I like when you use basketball examples"},
            {"role": "tutor", "content": "Great! I'll keep using sports analogies"},
            {"role": "student", "content": "I'm confused about negative fractions"}
        ]

        notes = await extractor.extract_notes(
            student_id="student_123",
            conversation_id="conv_abc",
            transcript=conversation_transcript
        )

        assert notes is not None
        assert isinstance(notes, list)
        assert len(notes) > 0
        assert all(isinstance(n, Note) for n in notes)

    @pytest.mark.asyncio
    async def test_extract_learning_preference(self, extractor):
        """Test extracting learning preference notes"""
        transcript = [
            {"role": "student", "content": "Can you draw a diagram? That helps me understand better"}
        ]

        notes = await extractor.extract_notes(
            student_id="student_123",
            conversation_id="conv_abc",
            transcript=transcript
        )

        # Should detect visual learning preference
        pref_notes = [n for n in notes if n.category == NoteCategory.LEARNING_PREFERENCE]
        assert len(pref_notes) > 0

    @pytest.mark.asyncio
    async def test_extract_misconception(self, extractor):
        """Test extracting misconception notes"""
        transcript = [
            {"role": "student", "content": "So fractions are always smaller than 1, right?"},
            {"role": "tutor", "content": "Not always! Improper fractions can be greater than 1"}
        ]

        notes = await extractor.extract_notes(
            student_id="student_123",
            conversation_id="conv_abc",
            transcript=transcript
        )

        # Should detect misconception
        misconceptions = [n for n in notes if n.category == NoteCategory.MISCONCEPTION]
        assert len(misconceptions) > 0

    @pytest.mark.asyncio
    async def test_extract_with_mock_llm(self, extractor):
        """Test extraction with mocked LLM response"""
        transcript = [
            {"role": "student", "content": "I prefer real-world examples"}
        ]

        # Mock LLM to return specific notes
        with patch.object(extractor, '_call_llm', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = [
                {
                    "category": "LEARNING_PREFERENCE",
                    "content": "Prefers real-world examples over abstract concepts",
                    "topic": "learning_style"
                }
            ]

            notes = await extractor.extract_notes(
                student_id="student_123",
                conversation_id="conv_abc",
                transcript=transcript
            )

            mock_llm.assert_called_once()
            assert len(notes) == 1
            assert notes[0].category == NoteCategory.LEARNING_PREFERENCE


class TestNoteStorage:
    """Test note storage and persistence"""

    @pytest.fixture
    def notes(self):
        return StudentNotes(db_path=":memory:")

    def test_store_multiple_notes(self, notes):
        """Test storing multiple notes"""
        note1 = notes.create_note(
            "student_123",
            NoteCategory.LEARNING_PREFERENCE,
            "Note 1",
            "topic1"
        )
        note2 = notes.create_note(
            "student_123",
            NoteCategory.WEAK_TOPIC,
            "Note 2",
            "topic2"
        )

        all_notes = notes.get_notes_by_student("student_123")
        assert len(all_notes) == 2

    def test_update_note(self, notes):
        """Test updating an existing note"""
        note = notes.create_note(
            "student_123",
            NoteCategory.SESSION_GOAL,
            "Goal: Master algebra",
            "algebra"
        )

        updated_note = notes.update_note(
            note.note_id,
            content="Goal: Master algebra by next month"
        )

        assert updated_note.content == "Goal: Master algebra by next month"
        assert updated_note.note_id == note.note_id

    def test_delete_note(self, notes):
        """Test deleting a note"""
        note = notes.create_note(
            "student_123",
            NoteCategory.MISCONCEPTION,
            "Temporary note",
            "temp"
        )

        notes.delete_note(note.note_id)

        all_notes = notes.get_notes_by_student("student_123")
        assert len(all_notes) == 0


class TestNoteSearch:
    """Test searching notes"""

    @pytest.fixture
    def notes(self):
        system = StudentNotes(db_path=":memory:")

        # Add diverse notes
        system.create_note(
            "student_123",
            NoteCategory.LEARNING_PREFERENCE,
            "Prefers visual diagrams and charts",
            "learning_style"
        )
        system.create_note(
            "student_123",
            NoteCategory.WEAK_TOPIC,
            "Struggles with word problems involving fractions",
            "fractions"
        )
        system.create_note(
            "student_123",
            NoteCategory.PERSONAL_CONTEXT,
            "Learning math for SAT preparation",
            "context"
        )

        return system

    def test_search_notes_by_keyword(self, notes):
        """Test searching notes by keyword"""
        results = notes.search_notes("student_123", query="fractions")

        assert len(results) > 0
        assert any("fractions" in n.content.lower() for n in results)

    def test_search_notes_by_multiple_keywords(self, notes):
        """Test searching with multiple keywords"""
        results = notes.search_notes("student_123", query="visual diagrams")

        assert len(results) > 0

    def test_search_returns_relevance_score(self, notes):
        """Test search results include relevance scoring"""
        results = notes.search_notes("student_123", query="fractions", include_score=True)

        assert len(results) > 0
        # Results should be tuples of (note, score) when include_score=True
        if results:
            assert hasattr(results[0], '__iter__') or hasattr(results[0], 'relevance_score')


class TestNoteAggregation:
    """Test aggregating notes for context"""

    @pytest.fixture
    def notes(self):
        system = StudentNotes(db_path=":memory:")

        system.create_note(
            "student_123",
            NoteCategory.LEARNING_PREFERENCE,
            "Likes sports analogies",
            "preferences"
        )
        system.create_note(
            "student_123",
            NoteCategory.WEAK_TOPIC,
            "Struggles with fractions",
            "fractions"
        )
        system.create_note(
            "student_123",
            NoteCategory.SESSION_GOAL,
            "Goal: 80% accuracy on algebra",
            "algebra"
        )

        return system

    def test_get_summary_for_student(self, notes):
        """Test generating summary of student notes"""
        summary = notes.get_student_summary("student_123")

        assert summary is not None
        assert isinstance(summary, dict)
        assert "learning_preferences" in summary
        assert "weak_topics" in summary
        assert "goals" in summary

    def test_summary_groups_by_category(self, notes):
        """Test summary groups notes by category"""
        summary = notes.get_student_summary("student_123")

        assert len(summary["learning_preferences"]) > 0
        assert len(summary["weak_topics"]) > 0
        assert len(summary["goals"]) > 0

    def test_get_context_for_topic(self, notes):
        """Test getting relevant notes for a specific topic"""
        context = notes.get_context_for_topic("student_123", "fractions")

        assert context is not None
        assert len(context) > 0
        # Should return notes relevant to fractions


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_get_notes_for_nonexistent_student(self):
        """Test retrieving notes for non-existent student"""
        notes = StudentNotes(db_path=":memory:")

        result = notes.get_notes_by_student("nonexistent_student")

        assert result == []

    def test_create_note_with_empty_content(self):
        """Test creating note with empty content"""
        notes = StudentNotes(db_path=":memory:")

        with pytest.raises(ValueError):
            notes.create_note(
                "student_123",
                NoteCategory.LEARNING_PREFERENCE,
                "",  # Empty content
                "topic"
            )

    def test_update_nonexistent_note(self):
        """Test updating non-existent note"""
        notes = StudentNotes(db_path=":memory:")

        with pytest.raises(ValueError):
            notes.update_note("nonexistent_id", content="New content")

    def test_delete_nonexistent_note(self):
        """Test deleting non-existent note"""
        notes = StudentNotes(db_path=":memory:")

        # Should not raise error, just return False or None
        result = notes.delete_note("nonexistent_id")
        assert result is False or result is None

    @pytest.mark.asyncio
    async def test_extract_notes_from_empty_transcript(self):
        """Test extracting notes from empty transcript"""
        extractor = NoteExtractor()

        notes = await extractor.extract_notes(
            student_id="student_123",
            conversation_id="conv_abc",
            transcript=[]
        )

        # Should return empty list or handle gracefully
        assert notes == []

    def test_note_history_limit(self):
        """Test that old notes can be archived/limited"""
        notes = StudentNotes(db_path=":memory:", note_limit=10)

        # Add 15 notes
        for i in range(15):
            notes.create_note(
                "student_123",
                NoteCategory.LEARNING_PREFERENCE,
                f"Note {i}",
                f"topic_{i}"
            )

        active_notes = notes.get_notes_by_student("student_123")

        # Should limit active notes (or have all archived)
        assert len(active_notes) <= 10 or notes.has_archived_notes("student_123")
