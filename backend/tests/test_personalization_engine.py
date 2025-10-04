"""
Tests for Personalization Engine

Following TDD: Tests written FIRST, then implementation.
All logic imported from codebase - NO hardcoded test logic.

Personalization Engine:
1. Explanation style adaptation (visual/verbal/kinesthetic)
2. Difficulty calibration using performance history
3. Example selection based on student interests
4. Pacing adjustment from session patterns
5. Learning path optimization
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from backend.memory.personalization_engine import (
    PersonalizationEngine,
    ExplanationStyle,
    DifficultyLevel,
    PersonalizationProfile,
    LearningRecommendation
)
from backend.memory.student_notes import NoteCategory


class TestPersonalizationEngineInitialization:
    """Test personalization engine initialization"""

    def test_initialization(self):
        """Test engine initializes correctly"""
        engine = PersonalizationEngine()

        assert engine is not None

    def test_initialization_with_dependencies(self):
        """Test initialization with memory system dependencies"""
        from backend.memory.student_notes import StudentNotes
        from backend.memory.learning_pattern_tracker import LearningPatternTracker
        from backend.memory.enhanced_vector_store import EnhancedVectorStore

        notes = StudentNotes(db_path=":memory:")
        tracker = LearningPatternTracker(db_path=":memory:")
        vector_store = EnhancedVectorStore(persist_directory="/tmp/test_vectors")

        engine = PersonalizationEngine(
            student_notes=notes,
            pattern_tracker=tracker,
            vector_store=vector_store
        )

        assert engine.student_notes is notes
        assert engine.pattern_tracker is tracker
        assert engine.vector_store is vector_store


class TestExplanationStyleAdaptation:
    """Test explanation style adaptation"""

    @pytest.fixture
    def engine(self):
        from backend.memory.student_notes import StudentNotes
        notes = StudentNotes(db_path=":memory:")
        return PersonalizationEngine(student_notes=notes)

    def test_explanation_styles_exist(self):
        """Test all expected explanation styles are defined"""
        expected_styles = [
            ExplanationStyle.VISUAL,
            ExplanationStyle.VERBAL,
            ExplanationStyle.KINESTHETIC,
            ExplanationStyle.MIXED
        ]

        for style in expected_styles:
            assert style in ExplanationStyle

    def test_detect_preferred_style_from_notes(self, engine):
        """Test detecting preferred explanation style from notes"""
        # Add notes indicating visual preference
        engine.student_notes.create_note(
            student_id="student_123",
            category=NoteCategory.LEARNING_PREFERENCE,
            content="Prefers diagrams and visual representations",
            topic="learning_style"
        )

        profile = engine.get_personalization_profile("student_123")

        assert profile is not None
        assert profile.preferred_explanation_style == ExplanationStyle.VISUAL

    def test_detect_verbal_preference(self, engine):
        """Test detecting verbal learning preference"""
        engine.student_notes.create_note(
            student_id="student_123",
            category=NoteCategory.LEARNING_PREFERENCE,
            content="Learns best through discussion and verbal explanations",
            topic="learning_style"
        )

        profile = engine.get_personalization_profile("student_123")

        assert profile.preferred_explanation_style == ExplanationStyle.VERBAL

    def test_default_to_mixed_style(self, engine):
        """Test defaults to mixed style when no clear preference"""
        # No learning preference notes
        profile = engine.get_personalization_profile("student_456")

        assert profile.preferred_explanation_style == ExplanationStyle.MIXED


class TestDifficultyCalibration:
    """Test difficulty calibration"""

    @pytest.fixture
    def engine(self):
        from backend.memory.learning_pattern_tracker import LearningPatternTracker
        tracker = LearningPatternTracker(db_path=":memory:")
        return PersonalizationEngine(pattern_tracker=tracker)

    def test_difficulty_levels_exist(self):
        """Test all expected difficulty levels are defined"""
        expected_levels = [
            DifficultyLevel.BEGINNER,
            DifficultyLevel.INTERMEDIATE,
            DifficultyLevel.ADVANCED,
            DifficultyLevel.EXPERT
        ]

        for level in expected_levels:
            assert level in DifficultyLevel

    def test_calibrate_from_performance_history(self, engine):
        """Test calibrating difficulty from performance"""
        # Record high-performing sessions
        for i in range(5):
            engine.pattern_tracker.record_session(
                student_id="student_123",
                start_time=datetime.now().timestamp() + (i * 3600),
                end_time=datetime.now().timestamp() + ((i + 1) * 3600),
                questions_asked=10,
                questions_correct=9,  # 90% accuracy
                engagement_score=0.9
            )

        profile = engine.get_personalization_profile("student_123")

        assert profile.current_difficulty_level in [
            DifficultyLevel.INTERMEDIATE,
            DifficultyLevel.ADVANCED,
            DifficultyLevel.EXPERT
        ]

    def test_calibrate_from_low_performance(self, engine):
        """Test calibrating to easier difficulty for struggling student"""
        # Record struggling sessions
        for i in range(5):
            engine.pattern_tracker.record_session(
                student_id="student_456",
                start_time=datetime.now().timestamp() + (i * 3600),
                end_time=datetime.now().timestamp() + ((i + 1) * 3600),
                questions_asked=10,
                questions_correct=4,  # 40% accuracy
                engagement_score=0.5
            )

        profile = engine.get_personalization_profile("student_456")

        assert profile.current_difficulty_level == DifficultyLevel.BEGINNER

    def test_difficulty_progression_recommendation(self, engine):
        """Test recommending difficulty progression"""
        # Student performing well
        for i in range(3):
            engine.pattern_tracker.record_session(
                student_id="student_123",
                start_time=datetime.now().timestamp() + (i * 3600),
                end_time=datetime.now().timestamp() + ((i + 1) * 3600),
                questions_asked=10,
                questions_correct=9,
                engagement_score=0.9
            )

        recommendation = engine.recommend_difficulty_adjustment("student_123")

        assert recommendation is not None
        assert recommendation in ["increase", "maintain", "decrease"]


class TestExampleSelection:
    """Test example selection based on student interests"""

    @pytest.fixture
    def engine(self):
        from backend.memory.student_notes import StudentNotes
        from backend.memory.enhanced_vector_store import EnhancedVectorStore
        import uuid

        notes = StudentNotes(db_path=":memory:")
        vector_store = EnhancedVectorStore(persist_directory=f"/tmp/test_vectors_{uuid.uuid4().hex[:8]}")

        return PersonalizationEngine(
            student_notes=notes,
            vector_store=vector_store
        )

    def test_select_examples_based_on_interests(self, engine):
        """Test selecting examples matching student interests"""
        # Add interest note
        engine.student_notes.create_note(
            student_id="student_123",
            category=NoteCategory.PERSONAL_CONTEXT,
            content="Loves basketball and sports",
            topic="interests"
        )

        # Add example to vector store
        engine.vector_store.add(
            student_id="student_123",
            content="Think of fractions like basketball free throws - if you make 3 out of 4, that's 3/4 or 75%",
            metadata={"topic": "fractions", "interest": "basketball"}
        )

        examples = engine.select_examples(
            student_id="student_123",
            topic="fractions",
            count=3
        )

        assert examples is not None
        assert isinstance(examples, list)
        if examples:
            assert "basketball" in examples[0].lower() or "sports" in examples[0].lower()

    def test_fallback_to_generic_examples(self, engine):
        """Test falling back to generic examples when no interests match"""
        examples = engine.select_examples(
            student_id="student_789",
            topic="algebra",
            count=3
        )

        # Should return empty list or generic examples
        assert isinstance(examples, list)


class TestPacingAdjustment:
    """Test pacing adjustment from session patterns"""

    @pytest.fixture
    def engine(self):
        from backend.memory.learning_pattern_tracker import LearningPatternTracker
        tracker = LearningPatternTracker(db_path=":memory:")
        return PersonalizationEngine(pattern_tracker=tracker)

    def test_recommend_session_duration(self, engine):
        """Test recommending optimal session duration"""
        # Record sessions with various durations
        now = datetime.now()

        # 30-min sessions with good performance
        for i in range(3):
            session_time = now - timedelta(days=6-i)
            engine.pattern_tracker.record_session(
                student_id="student_123",
                start_time=session_time.timestamp(),
                end_time=(session_time + timedelta(minutes=30)).timestamp(),
                questions_asked=10,
                questions_correct=9,
                engagement_score=0.9
            )

        pacing = engine.recommend_pacing("student_123")

        assert pacing is not None
        assert "session_duration" in pacing
        assert pacing["session_duration"] > 0
        assert pacing["session_duration"] <= 120

    def test_recommend_break_frequency(self, engine):
        """Test recommending break frequency"""
        # Long session with declining performance
        now = datetime.now()
        engine.pattern_tracker.record_session(
            student_id="student_123",
            start_time=now.timestamp(),
            end_time=(now + timedelta(minutes=90)).timestamp(),
            questions_asked=30,
            questions_correct=15,
            engagement_score=0.4
        )

        pacing = engine.recommend_pacing("student_123")

        assert "break_frequency" in pacing
        assert pacing["break_frequency"] is not None

    def test_recommend_best_time_of_day(self, engine):
        """Test recommending best learning time"""
        # Morning sessions with high performance
        for i in range(5):
            morning_time = datetime(2025, 1, i+1, 9, 0)
            engine.pattern_tracker.record_session(
                student_id="student_123",
                start_time=morning_time.timestamp(),
                end_time=(morning_time + timedelta(hours=1)).timestamp(),
                questions_asked=10,
                questions_correct=9,
                engagement_score=0.9
            )

        pacing = engine.recommend_pacing("student_123")

        assert "best_time_range" in pacing
        if pacing["best_time_range"]:
            assert isinstance(pacing["best_time_range"], tuple)
            assert len(pacing["best_time_range"]) == 2


class TestLearningPathOptimization:
    """Test learning path optimization"""

    @pytest.fixture
    def engine(self):
        from backend.memory.student_notes import StudentNotes
        from backend.memory.learning_pattern_tracker import LearningPatternTracker

        notes = StudentNotes(db_path=":memory:")
        tracker = LearningPatternTracker(db_path=":memory:")

        return PersonalizationEngine(
            student_notes=notes,
            pattern_tracker=tracker
        )

    def test_identify_knowledge_gaps(self, engine):
        """Test identifying knowledge gaps from misconceptions"""
        engine.student_notes.create_note(
            student_id="student_123",
            category=NoteCategory.MISCONCEPTION,
            content="Thinks negative times negative equals negative",
            topic="multiplication"
        )

        engine.student_notes.create_note(
            student_id="student_123",
            category=NoteCategory.WEAK_TOPIC,
            content="Struggles with fraction division",
            topic="fractions"
        )

        gaps = engine.identify_knowledge_gaps("student_123")

        assert gaps is not None
        assert isinstance(gaps, list)
        assert len(gaps) > 0

    def test_recommend_next_topics(self, engine):
        """Test recommending next topics to study"""
        # Record mastery of basic topics
        now = datetime.now()
        engine.pattern_tracker.record_session(
            student_id="student_123",
            start_time=now.timestamp(),
            end_time=(now + timedelta(hours=1)).timestamp(),
            concepts_covered=["addition", "subtraction"],
            concepts_mastered=["addition", "subtraction"]
        )

        recommendations = engine.recommend_next_topics("student_123", count=3)

        assert recommendations is not None
        assert isinstance(recommendations, list)
        assert len(recommendations) <= 3

    def test_personalize_topic_sequence(self, engine):
        """Test personalizing topic learning sequence"""
        # Add strong/weak topics
        engine.student_notes.create_note(
            student_id="student_123",
            category=NoteCategory.STRONG_TOPIC,
            content="Excels at geometry",
            topic="geometry"
        )

        engine.student_notes.create_note(
            student_id="student_123",
            category=NoteCategory.WEAK_TOPIC,
            content="Struggles with algebra",
            topic="algebra"
        )

        sequence = engine.personalize_topic_sequence(
            student_id="student_123",
            available_topics=["algebra", "geometry", "calculus", "statistics"]
        )

        assert sequence is not None
        assert isinstance(sequence, list)
        # Weak topics should be prioritized
        if "algebra" in sequence:
            assert sequence.index("algebra") < len(sequence) / 2


class TestPersonalizationProfile:
    """Test personalization profile generation"""

    @pytest.fixture
    def engine(self):
        from backend.memory.student_notes import StudentNotes
        from backend.memory.learning_pattern_tracker import LearningPatternTracker

        notes = StudentNotes(db_path=":memory:")
        tracker = LearningPatternTracker(db_path=":memory:")

        return PersonalizationEngine(
            student_notes=notes,
            pattern_tracker=tracker
        )

    def test_generate_complete_profile(self, engine):
        """Test generating complete personalization profile"""
        # Add various data
        engine.student_notes.create_note(
            student_id="student_123",
            category=NoteCategory.LEARNING_PREFERENCE,
            content="Prefers visual explanations",
            topic="learning_style"
        )

        now = datetime.now()
        engine.pattern_tracker.record_session(
            student_id="student_123",
            start_time=now.timestamp(),
            end_time=(now + timedelta(hours=1)).timestamp(),
            questions_asked=10,
            questions_correct=8,
            engagement_score=0.8
        )

        profile = engine.get_personalization_profile("student_123")

        assert isinstance(profile, PersonalizationProfile)
        assert profile.student_id == "student_123"
        assert profile.preferred_explanation_style is not None
        assert profile.current_difficulty_level is not None

    def test_profile_includes_all_fields(self, engine):
        """Test profile contains all expected fields"""
        profile = engine.get_personalization_profile("student_123")

        assert hasattr(profile, 'student_id')
        assert hasattr(profile, 'preferred_explanation_style')
        assert hasattr(profile, 'current_difficulty_level')
        assert hasattr(profile, 'interests')
        assert hasattr(profile, 'strengths')
        assert hasattr(profile, 'weaknesses')


class TestLearningRecommendations:
    """Test learning recommendation generation"""

    @pytest.fixture
    def engine(self):
        from backend.memory.student_notes import StudentNotes
        from backend.memory.learning_pattern_tracker import LearningPatternTracker

        notes = StudentNotes(db_path=":memory:")
        tracker = LearningPatternTracker(db_path=":memory:")

        return PersonalizationEngine(
            student_notes=notes,
            pattern_tracker=tracker
        )

    def test_generate_recommendations(self, engine):
        """Test generating personalized recommendations"""
        # Add data
        now = datetime.now()
        engine.pattern_tracker.record_session(
            student_id="student_123",
            start_time=now.timestamp(),
            end_time=(now + timedelta(hours=1)).timestamp(),
            questions_asked=10,
            questions_correct=9,
            engagement_score=0.9
        )

        recommendations = engine.generate_recommendations("student_123")

        assert recommendations is not None
        assert isinstance(recommendations, list)
        if recommendations:
            assert all(isinstance(r, LearningRecommendation) for r in recommendations)

    def test_recommendation_has_required_fields(self, engine):
        """Test recommendations have required fields"""
        now = datetime.now()
        engine.pattern_tracker.record_session(
            student_id="student_123",
            start_time=now.timestamp(),
            end_time=(now + timedelta(hours=1)).timestamp()
        )

        recommendations = engine.generate_recommendations("student_123")

        if recommendations:
            rec = recommendations[0]
            assert hasattr(rec, 'recommendation_type')
            assert hasattr(rec, 'message')
            assert hasattr(rec, 'priority')
            assert hasattr(rec, 'data')


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_profile_for_new_student(self):
        """Test generating profile for student with no data"""
        from backend.memory.student_notes import StudentNotes
        from backend.memory.learning_pattern_tracker import LearningPatternTracker

        notes = StudentNotes(db_path=":memory:")
        tracker = LearningPatternTracker(db_path=":memory:")
        engine = PersonalizationEngine(student_notes=notes, pattern_tracker=tracker)

        profile = engine.get_personalization_profile("new_student")

        assert profile is not None
        assert profile.student_id == "new_student"
        # Should have defaults
        assert profile.preferred_explanation_style == ExplanationStyle.MIXED
        assert profile.current_difficulty_level == DifficultyLevel.BEGINNER

    def test_recommendations_with_minimal_data(self):
        """Test recommendations with minimal student data"""
        from backend.memory.learning_pattern_tracker import LearningPatternTracker

        tracker = LearningPatternTracker(db_path=":memory:")
        engine = PersonalizationEngine(pattern_tracker=tracker)

        # Single session
        now = datetime.now()
        engine.pattern_tracker.record_session(
            student_id="student_123",
            start_time=now.timestamp(),
            end_time=(now + timedelta(hours=1)).timestamp()
        )

        recommendations = engine.generate_recommendations("student_123")

        # Should still return recommendations (possibly empty)
        assert isinstance(recommendations, list)

    def test_select_examples_with_no_vector_store(self):
        """Test example selection without vector store"""
        engine = PersonalizationEngine()

        examples = engine.select_examples(
            student_id="student_123",
            topic="algebra",
            count=3
        )

        # Should return empty list
        assert examples == []

    def test_invalid_topic_in_recommendation(self):
        """Test handling invalid topic"""
        from backend.memory.student_notes import StudentNotes

        notes = StudentNotes(db_path=":memory:")
        engine = PersonalizationEngine(student_notes=notes)

        # Should not raise error
        recommendations = engine.recommend_next_topics("student_123", count=3)
        assert isinstance(recommendations, list)
