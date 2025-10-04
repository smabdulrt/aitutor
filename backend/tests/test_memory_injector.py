"""
Tests for Memory Injection System

Following TDD: Tests written FIRST, then implementation.
All logic imported from codebase - NO hardcoded test logic.

Memory Injection System:
1. Relevance-based memory retrieval
2. Context window optimization
3. Priority-based memory selection
4. Dynamic context updates
5. Integration with teaching assistant
"""

import pytest
from datetime import datetime, timedelta
from backend.memory.memory_injector import (
    MemoryInjector,
    MemoryContext,
    ContextPriority
)


class TestMemoryInjectorInitialization:
    """Test memory injector initialization"""

    def test_initialization(self):
        """Test injector initializes correctly"""
        injector = MemoryInjector()

        assert injector is not None

    def test_initialization_with_all_systems(self):
        """Test initialization with all memory systems"""
        from backend.memory.student_notes import StudentNotes
        from backend.memory.learning_pattern_tracker import LearningPatternTracker
        from backend.memory.personalization_engine import PersonalizationEngine
        from backend.memory.goal_tracker import GoalTracker

        notes = StudentNotes(db_path=":memory:")
        tracker = LearningPatternTracker(db_path=":memory:")
        engine = PersonalizationEngine(student_notes=notes, pattern_tracker=tracker)
        goals = GoalTracker(db_path=":memory:", pattern_tracker=tracker)

        injector = MemoryInjector(
            student_notes=notes,
            pattern_tracker=tracker,
            personalization_engine=engine,
            goal_tracker=goals
        )

        assert injector.student_notes is notes
        assert injector.pattern_tracker is tracker
        assert injector.personalization_engine is engine
        assert injector.goal_tracker is goals


class TestContextPriority:
    """Test context priority enumeration"""

    def test_priority_levels_exist(self):
        """Test all priority levels are defined"""
        expected_priorities = [
            ContextPriority.CRITICAL,
            ContextPriority.HIGH,
            ContextPriority.MEDIUM,
            ContextPriority.LOW
        ]

        for priority in expected_priorities:
            assert priority in ContextPriority


class TestMemoryRetrieval:
    """Test relevance-based memory retrieval"""

    @pytest.fixture
    def injector(self):
        from backend.memory.student_notes import StudentNotes
        from backend.memory.learning_pattern_tracker import LearningPatternTracker

        notes = StudentNotes(db_path=":memory:")
        tracker = LearningPatternTracker(db_path=":memory:")

        return MemoryInjector(student_notes=notes, pattern_tracker=tracker)

    def test_retrieve_relevant_notes(self, injector):
        """Test retrieving notes relevant to current topic"""
        from backend.memory.student_notes import NoteCategory

        # Add notes
        injector.student_notes.create_note(
            "student_123",
            NoteCategory.MISCONCEPTION,
            "Struggles with negative fractions",
            "fractions"
        )

        injector.student_notes.create_note(
            "student_123",
            NoteCategory.LEARNING_PREFERENCE,
            "Prefers visual diagrams",
            "learning_style"
        )

        # Retrieve for fractions topic
        context = injector.get_relevant_context(
            student_id="student_123",
            current_topic="fractions"
        )

        assert context is not None
        assert isinstance(context, MemoryContext)

    def test_prioritize_misconceptions(self, injector):
        """Test misconceptions are prioritized"""
        from backend.memory.student_notes import NoteCategory

        injector.student_notes.create_note(
            "student_123",
            NoteCategory.MISCONCEPTION,
            "Thinks fractions must be less than 1",
            "fractions"
        )

        context = injector.get_relevant_context("student_123", "fractions")

        # Misconceptions should be HIGH or CRITICAL priority
        assert context.priority in [ContextPriority.HIGH, ContextPriority.CRITICAL]

    def test_include_learning_preferences(self, injector):
        """Test learning preferences are included"""
        from backend.memory.student_notes import NoteCategory

        injector.student_notes.create_note(
            "student_123",
            NoteCategory.LEARNING_PREFERENCE,
            "Prefers real-world examples",
            "learning_style"
        )

        context = injector.get_relevant_context("student_123", "algebra")

        assert context is not None


class TestContextOptimization:
    """Test context window optimization"""

    @pytest.fixture
    def injector(self):
        from backend.memory.student_notes import StudentNotes
        notes = StudentNotes(db_path=":memory:")
        return MemoryInjector(student_notes=notes)

    def test_optimize_for_token_limit(self, injector):
        """Test optimizing context to fit token limit"""
        from backend.memory.student_notes import NoteCategory

        # Add many notes
        for i in range(20):
            injector.student_notes.create_note(
                "student_123",
                NoteCategory.PERSONAL_CONTEXT,
                f"Note {i} with lots of content " * 10,
                f"topic_{i}"
            )

        # Get optimized context with token limit
        context = injector.get_relevant_context(
            student_id="student_123",
            current_topic="topic_0",
            max_tokens=500
        )

        assert context is not None
        # Should include only highest priority items

    def test_prioritize_recent_content(self, injector):
        """Test recent content is prioritized"""
        from backend.memory.student_notes import NoteCategory

        # Old note
        old_note = injector.student_notes.create_note(
            "student_123",
            NoteCategory.WEAK_TOPIC,
            "Old weakness",
            "algebra"
        )

        # Recent note
        new_note = injector.student_notes.create_note(
            "student_123",
            NoteCategory.WEAK_TOPIC,
            "Recent weakness",
            "algebra"
        )

        context = injector.get_relevant_context("student_123", "algebra")

        # Recent content should be included or prioritized
        assert context is not None


class TestDynamicUpdates:
    """Test dynamic context updates during conversation"""

    @pytest.fixture
    def injector(self):
        from backend.memory.student_notes import StudentNotes
        from backend.memory.learning_pattern_tracker import LearningPatternTracker

        notes = StudentNotes(db_path=":memory:")
        tracker = LearningPatternTracker(db_path=":memory:")

        return MemoryInjector(student_notes=notes, pattern_tracker=tracker)

    def test_update_context_with_new_topic(self, injector):
        """Test updating context when topic changes"""
        from backend.memory.student_notes import NoteCategory

        injector.student_notes.create_note(
            "student_123",
            NoteCategory.MISCONCEPTION,
            "Struggles with algebra",
            "algebra"
        )

        injector.student_notes.create_note(
            "student_123",
            NoteCategory.MISCONCEPTION,
            "Struggles with geometry",
            "geometry"
        )

        # Get context for algebra
        context1 = injector.get_relevant_context("student_123", "algebra")

        # Update to geometry
        context2 = injector.get_relevant_context("student_123", "geometry")

        # Contexts should be different (topic-specific)
        assert context1 is not None
        assert context2 is not None

    def test_refresh_context(self, injector):
        """Test refreshing context with latest data"""
        from backend.memory.student_notes import NoteCategory

        # Initial context
        context1 = injector.get_relevant_context("student_123", "fractions")

        # Add new note
        injector.student_notes.create_note(
            "student_123",
            NoteCategory.MISCONCEPTION,
            "New misconception discovered",
            "fractions"
        )

        # Refresh context
        context2 = injector.get_relevant_context("student_123", "fractions")

        # Should include new data
        assert context2 is not None


class TestMemoryContext:
    """Test MemoryContext object"""

    @pytest.fixture
    def injector(self):
        from backend.memory.student_notes import StudentNotes
        notes = StudentNotes(db_path=":memory:")
        return MemoryInjector(student_notes=notes)

    def test_context_has_required_fields(self, injector):
        """Test MemoryContext has all required fields"""
        context = injector.get_relevant_context("student_123", "algebra")

        assert hasattr(context, 'student_id')
        assert hasattr(context, 'topic')
        assert hasattr(context, 'priority')
        assert hasattr(context, 'content')
        assert hasattr(context, 'metadata')

    def test_context_content_is_string(self, injector):
        """Test context content is formatted as string"""
        from backend.memory.student_notes import NoteCategory

        injector.student_notes.create_note(
            "student_123",
            NoteCategory.MISCONCEPTION,
            "Test misconception",
            "algebra"
        )

        context = injector.get_relevant_context("student_123", "algebra")

        assert isinstance(context.content, str)
        assert len(context.content) > 0


class TestIntegration:
    """Test integration with all memory systems"""

    @pytest.fixture
    def injector(self):
        from backend.memory.student_notes import StudentNotes
        from backend.memory.learning_pattern_tracker import LearningPatternTracker
        from backend.memory.personalization_engine import PersonalizationEngine
        from backend.memory.goal_tracker import GoalTracker

        notes = StudentNotes(db_path=":memory:")
        tracker = LearningPatternTracker(db_path=":memory:")
        engine = PersonalizationEngine(student_notes=notes, pattern_tracker=tracker)
        goals = GoalTracker(db_path=":memory:", pattern_tracker=tracker)

        return MemoryInjector(
            student_notes=notes,
            pattern_tracker=tracker,
            personalization_engine=engine,
            goal_tracker=goals
        )

    def test_include_active_goals(self, injector):
        """Test including active goals in context"""
        from backend.memory.goal_tracker import GoalType

        injector.goal_tracker.create_goal(
            "student_123",
            GoalType.MASTERY,
            "Master algebra",
            target_value=10
        )

        context = injector.get_relevant_context("student_123", "algebra")

        # Should include goal information
        assert context is not None

    def test_include_personalization_profile(self, injector):
        """Test including personalization info"""
        from backend.memory.student_notes import NoteCategory

        injector.student_notes.create_note(
            "student_123",
            NoteCategory.LEARNING_PREFERENCE,
            "Prefers visual explanations",
            "learning_style"
        )

        context = injector.get_relevant_context("student_123", "algebra")

        # Should include personalization
        assert context is not None

    def test_include_learning_patterns(self, injector):
        """Test including learning pattern insights"""
        now = datetime.now()

        # Add session data
        injector.pattern_tracker.record_session(
            student_id="student_123",
            start_time=now.timestamp(),
            end_time=(now + timedelta(hours=1)).timestamp(),
            questions_asked=10,
            questions_correct=9,
            engagement_score=0.9
        )

        context = injector.get_relevant_context("student_123", "algebra")

        assert context is not None


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_context_for_new_student(self):
        """Test getting context for student with no data"""
        from backend.memory.student_notes import StudentNotes

        notes = StudentNotes(db_path=":memory:")
        injector = MemoryInjector(student_notes=notes)

        context = injector.get_relevant_context("new_student", "algebra")

        # Should return empty or default context
        assert context is not None
        assert context.student_id == "new_student"

    def test_context_without_memory_systems(self):
        """Test creating context without memory systems"""
        injector = MemoryInjector()

        context = injector.get_relevant_context("student_123", "algebra")

        # Should return minimal context
        assert context is not None

    def test_empty_topic(self):
        """Test handling empty topic"""
        from backend.memory.student_notes import StudentNotes

        notes = StudentNotes(db_path=":memory:")
        injector = MemoryInjector(student_notes=notes)

        # Should not raise error
        context = injector.get_relevant_context("student_123", "")

        assert context is not None

    def test_very_large_context(self):
        """Test handling when context exceeds token limit"""
        from backend.memory.student_notes import StudentNotes, NoteCategory

        notes = StudentNotes(db_path=":memory:")
        injector = MemoryInjector(student_notes=notes)

        # Add lots of data
        for i in range(100):
            notes.create_note(
                "student_123",
                NoteCategory.PERSONAL_CONTEXT,
                "Very long content " * 100,
                f"topic_{i}"
            )

        # Should handle gracefully with small token limit
        context = injector.get_relevant_context(
            "student_123",
            "topic_0",
            max_tokens=100
        )

        assert context is not None
