"""
Tests for Learning Pattern Tracker

Following TDD: Tests written FIRST, then implementation.
All logic imported from codebase - NO hardcoded test logic.

Learning Pattern Tracker:
1. Track time-of-day performance patterns
2. Session length and focus patterns
3. Learning velocity (concepts per session)
4. Error patterns and recovery time
5. Cross-session learning analytics
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock
from backend.memory.learning_pattern_tracker import (
    LearningPatternTracker,
    TimeOfDayPattern,
    SessionPattern,
    LearningVelocity,
    ErrorPattern,
    PatternInsight
)


class TestLearningPatternTrackerInitialization:
    """Test learning pattern tracker initialization"""

    def test_initialization(self):
        """Test tracker initializes correctly"""
        tracker = LearningPatternTracker()

        assert tracker is not None
        assert tracker.db_path is not None

    def test_initialization_with_custom_path(self):
        """Test initialization with custom database path"""
        custom_path = "/tmp/test_patterns.db"
        tracker = LearningPatternTracker(db_path=custom_path)

        assert tracker.db_path == custom_path


class TestSessionTracking:
    """Test tracking learning sessions"""

    @pytest.fixture
    def tracker(self):
        return LearningPatternTracker(db_path=":memory:")

    def test_record_session(self, tracker):
        """Test recording a learning session"""
        session_id = tracker.record_session(
            student_id="student_123",
            start_time=datetime(2025, 1, 15, 14, 0).timestamp(),
            end_time=datetime(2025, 1, 15, 15, 0).timestamp(),
            concepts_covered=["algebra", "equations"],
            questions_asked=5,
            questions_correct=4,
            engagement_score=0.8
        )

        assert session_id is not None

    def test_get_session(self, tracker):
        """Test retrieving session data"""
        session_id = tracker.record_session(
            student_id="student_123",
            start_time=datetime.now().timestamp(),
            end_time=datetime.now().timestamp() + 3600,
            concepts_covered=["geometry"]
        )

        session = tracker.get_session(session_id)

        assert session is not None
        assert session["student_id"] == "student_123"
        assert "geometry" in session["concepts_covered"]


class TestTimeOfDayPatterns:
    """Test time-of-day performance analysis"""

    @pytest.fixture
    def tracker(self):
        return LearningPatternTracker(db_path=":memory:")

    def test_analyze_time_of_day_patterns(self, tracker):
        """Test analyzing performance by time of day"""
        # Record morning sessions (better performance)
        for i in range(5):
            tracker.record_session(
                student_id="student_123",
                start_time=datetime(2025, 1, i+1, 9, 0).timestamp(),  # 9 AM
                end_time=datetime(2025, 1, i+1, 10, 0).timestamp(),
                questions_asked=10,
                questions_correct=9,  # 90% accuracy
                engagement_score=0.9
            )

        # Record evening sessions (worse performance)
        for i in range(5):
            tracker.record_session(
                student_id="student_123",
                start_time=datetime(2025, 1, i+1, 20, 0).timestamp(),  # 8 PM
                end_time=datetime(2025, 1, i+1, 21, 0).timestamp(),
                questions_asked=10,
                questions_correct=6,  # 60% accuracy
                engagement_score=0.6
            )

        patterns = tracker.analyze_time_of_day_patterns("student_123")

        assert patterns is not None
        assert isinstance(patterns, TimeOfDayPattern)
        assert patterns.best_time_range is not None
        assert patterns.worst_time_range is not None

    def test_best_time_recommendation(self, tracker):
        """Test recommendation for best learning time"""
        # Add data for morning peak performance
        tracker.record_session(
            student_id="student_123",
            start_time=datetime(2025, 1, 1, 10, 0).timestamp(),
            end_time=datetime(2025, 1, 1, 11, 0).timestamp(),
            questions_asked=10,
            questions_correct=9
        )

        patterns = tracker.analyze_time_of_day_patterns("student_123")

        assert patterns.best_time_range is not None


class TestSessionLengthPatterns:
    """Test session length and focus analysis"""

    @pytest.fixture
    def tracker(self):
        return LearningPatternTracker(db_path=":memory:")

    def test_optimal_session_length(self, tracker):
        """Test finding optimal session length"""
        # Short sessions - good performance
        for i in range(3):
            tracker.record_session(
                student_id="student_123",
                start_time=datetime.now().timestamp(),
                end_time=datetime.now().timestamp() + 1800,  # 30 min
                questions_asked=10,
                questions_correct=9,
                engagement_score=0.9
            )

        # Long sessions - declining performance
        for i in range(3):
            tracker.record_session(
                student_id="student_123",
                start_time=datetime.now().timestamp(),
                end_time=datetime.now().timestamp() + 7200,  # 2 hours
                questions_asked=20,
                questions_correct=12,
                engagement_score=0.5
            )

        patterns = tracker.analyze_session_length_patterns("student_123")

        assert patterns is not None
        assert isinstance(patterns, SessionPattern)
        assert patterns.optimal_duration_minutes is not None
        assert 0 < patterns.optimal_duration_minutes <= 120

    def test_focus_degradation_detection(self, tracker):
        """Test detecting when focus degrades during session"""
        tracker.record_session(
            student_id="student_123",
            start_time=datetime.now().timestamp(),
            end_time=datetime.now().timestamp() + 5400,  # 90 min
            questions_asked=30,
            questions_correct=15,
            engagement_score=0.4  # Low engagement
        )

        patterns = tracker.analyze_session_length_patterns("student_123")

        assert patterns.focus_degradation_point is not None


class TestLearningVelocity:
    """Test learning velocity tracking"""

    @pytest.fixture
    def tracker(self):
        return LearningPatternTracker(db_path=":memory:")

    def test_calculate_learning_velocity(self, tracker):
        """Test calculating concepts mastered per session"""
        tracker.record_session(
            student_id="student_123",
            start_time=datetime(2025, 1, 1, 10, 0).timestamp(),
            end_time=datetime(2025, 1, 1, 11, 0).timestamp(),
            concepts_covered=["algebra", "equations", "variables"],
            concepts_mastered=["algebra", "variables"]
        )

        tracker.record_session(
            student_id="student_123",
            start_time=datetime(2025, 1, 2, 10, 0).timestamp(),
            end_time=datetime(2025, 1, 2, 11, 0).timestamp(),
            concepts_covered=["geometry", "triangles"],
            concepts_mastered=["geometry"]
        )

        velocity = tracker.calculate_learning_velocity("student_123")

        assert velocity is not None
        assert isinstance(velocity, LearningVelocity)
        assert velocity.concepts_per_session > 0
        assert velocity.mastery_rate > 0

    def test_velocity_trend_over_time(self, tracker):
        """Test detecting if learning is accelerating or decelerating"""
        # Week 1 - slower learning
        tracker.record_session(
            student_id="student_123",
            start_time=datetime(2025, 1, 1, 10, 0).timestamp(),
            end_time=datetime(2025, 1, 1, 11, 0).timestamp(),
            concepts_covered=["topic1"],
            concepts_mastered=["topic1"]
        )

        # Week 2 - faster learning
        tracker.record_session(
            student_id="student_123",
            start_time=datetime(2025, 1, 8, 10, 0).timestamp(),
            end_time=datetime(2025, 1, 8, 11, 0).timestamp(),
            concepts_covered=["topic2", "topic3", "topic4"],
            concepts_mastered=["topic2", "topic3", "topic4"]
        )

        velocity = tracker.calculate_learning_velocity("student_123")

        assert velocity.trend is not None
        # Should detect acceleration


class TestErrorPatterns:
    """Test error pattern analysis"""

    @pytest.fixture
    def tracker(self):
        return LearningPatternTracker(db_path=":memory:")

    def test_record_errors(self, tracker):
        """Test recording errors during session"""
        session_id = tracker.record_session(
            student_id="student_123",
            start_time=datetime.now().timestamp(),
            end_time=datetime.now().timestamp() + 3600
        )

        tracker.record_error(
            session_id=session_id,
            student_id="student_123",
            concept="algebra",
            error_type="calculation",
            timestamp=datetime.now().timestamp()
        )

        errors = tracker.get_session_errors(session_id)

        assert len(errors) > 0
        assert errors[0]["concept"] == "algebra"

    def test_analyze_error_patterns(self, tracker):
        """Test analyzing common error patterns"""
        session_id = tracker.record_session(
            student_id="student_123",
            start_time=datetime.now().timestamp(),
            end_time=datetime.now().timestamp() + 3600
        )

        # Record multiple errors in same concept
        for i in range(5):
            tracker.record_error(
                session_id=session_id,
                student_id="student_123",
                concept="fractions",
                error_type="division",
                timestamp=datetime.now().timestamp() + (i * 60)
            )

        patterns = tracker.analyze_error_patterns("student_123")

        assert patterns is not None
        assert isinstance(patterns, ErrorPattern)
        assert patterns.most_common_errors is not None
        assert len(patterns.most_common_errors) > 0

    def test_error_recovery_time(self, tracker):
        """Test calculating time to recover from errors"""
        session_id = tracker.record_session(
            student_id="student_123",
            start_time=datetime.now().timestamp(),
            end_time=datetime.now().timestamp() + 3600
        )

        error_time = datetime.now().timestamp()
        recovery_time = error_time + 300  # 5 minutes later

        tracker.record_error(
            session_id=session_id,
            student_id="student_123",
            concept="algebra",
            error_type="calculation",
            timestamp=error_time,
            recovered_at=recovery_time
        )

        patterns = tracker.analyze_error_patterns("student_123")

        assert patterns.average_recovery_time is not None
        assert patterns.average_recovery_time > 0


class TestCrossSessionAnalytics:
    """Test cross-session learning analytics"""

    @pytest.fixture
    def tracker(self):
        return LearningPatternTracker(db_path=":memory:")

    def test_concept_retention_over_sessions(self, tracker):
        """Test tracking concept retention across sessions"""
        # Session 1 - learn algebra
        tracker.record_session(
            student_id="student_123",
            start_time=datetime(2025, 1, 1, 10, 0).timestamp(),
            end_time=datetime(2025, 1, 1, 11, 0).timestamp(),
            concepts_covered=["algebra"],
            concepts_mastered=["algebra"]
        )

        # Session 2 (7 days later) - revisit algebra
        tracker.record_session(
            student_id="student_123",
            start_time=datetime(2025, 1, 8, 10, 0).timestamp(),
            end_time=datetime(2025, 1, 8, 11, 0).timestamp(),
            concepts_covered=["algebra"],
            retention_quiz_score=0.8  # 80% retention
        )

        retention = tracker.analyze_concept_retention("student_123", "algebra")

        assert retention is not None
        assert 0 <= retention <= 1

    def test_session_spacing_patterns(self, tracker):
        """Test analyzing optimal spacing between sessions"""
        # Record sessions with various gaps
        base_time = datetime(2025, 1, 1, 10, 0).timestamp()

        tracker.record_session(
            student_id="student_123",
            start_time=base_time,
            end_time=base_time + 3600,
            engagement_score=0.9
        )

        # 1 day gap
        tracker.record_session(
            student_id="student_123",
            start_time=base_time + (24 * 3600),
            end_time=base_time + (24 * 3600) + 3600,
            engagement_score=0.85
        )

        # 7 day gap
        tracker.record_session(
            student_id="student_123",
            start_time=base_time + (7 * 24 * 3600),
            end_time=base_time + (7 * 24 * 3600) + 3600,
            engagement_score=0.6
        )

        patterns = tracker.analyze_session_spacing("student_123")

        assert patterns is not None
        assert patterns["optimal_gap_days"] is not None

    def test_learning_consistency_score(self, tracker):
        """Test calculating consistency of learning sessions"""
        # Consistent sessions - use recent dates
        now = datetime.now()
        for i in range(7):
            session_time = now - timedelta(days=6-i)  # Last 7 days
            tracker.record_session(
                student_id="student_123",
                start_time=session_time.timestamp(),
                end_time=(session_time + timedelta(hours=1)).timestamp()
            )

        consistency = tracker.calculate_consistency_score("student_123", days=7)

        assert consistency is not None
        assert 0 <= consistency <= 1
        assert consistency > 0.8  # Should be high for daily sessions


class TestPatternInsights:
    """Test generating insights from patterns"""

    @pytest.fixture
    def tracker(self):
        return LearningPatternTracker(db_path=":memory:")

    def test_generate_insights(self, tracker):
        """Test generating actionable insights"""
        # Add some session data
        tracker.record_session(
            student_id="student_123",
            start_time=datetime(2025, 1, 1, 9, 0).timestamp(),
            end_time=datetime(2025, 1, 1, 10, 0).timestamp(),
            questions_asked=10,
            questions_correct=9,
            engagement_score=0.9
        )

        insights = tracker.generate_insights("student_123")

        assert insights is not None
        assert isinstance(insights, list)
        if insights:
            assert all(isinstance(i, PatternInsight) for i in insights)

    def test_insight_priorities(self, tracker):
        """Test insights are prioritized by importance"""
        tracker.record_session(
            student_id="student_123",
            start_time=datetime.now().timestamp(),
            end_time=datetime.now().timestamp() + 3600,
            engagement_score=0.3  # Low engagement - high priority insight
        )

        insights = tracker.generate_insights("student_123")

        if len(insights) > 1:
            # Insights should be ordered by priority
            assert insights[0].priority >= insights[-1].priority


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_get_patterns_for_nonexistent_student(self):
        """Test analyzing patterns for student with no data"""
        tracker = LearningPatternTracker(db_path=":memory:")

        patterns = tracker.analyze_time_of_day_patterns("nonexistent_student")

        assert patterns is None or patterns.best_time_range is None

    def test_session_with_no_questions(self):
        """Test recording session with no questions asked"""
        tracker = LearningPatternTracker(db_path=":memory:")

        session_id = tracker.record_session(
            student_id="student_123",
            start_time=datetime.now().timestamp(),
            end_time=datetime.now().timestamp() + 3600,
            questions_asked=0,
            questions_correct=0
        )

        assert session_id is not None

    def test_invalid_session_times(self):
        """Test handling invalid session times (end before start)"""
        tracker = LearningPatternTracker(db_path=":memory:")

        with pytest.raises(ValueError):
            tracker.record_session(
                student_id="student_123",
                start_time=datetime.now().timestamp() + 3600,
                end_time=datetime.now().timestamp()  # End before start
            )

    def test_negative_engagement_score(self):
        """Test handling invalid engagement scores"""
        tracker = LearningPatternTracker(db_path=":memory:")

        with pytest.raises(ValueError):
            tracker.record_session(
                student_id="student_123",
                start_time=datetime.now().timestamp(),
                end_time=datetime.now().timestamp() + 3600,
                engagement_score=-0.5  # Invalid
            )

    def test_get_insights_with_minimal_data(self):
        """Test generating insights with insufficient data"""
        tracker = LearningPatternTracker(db_path=":memory:")

        # Only one session
        tracker.record_session(
            student_id="student_123",
            start_time=datetime.now().timestamp(),
            end_time=datetime.now().timestamp() + 3600
        )

        insights = tracker.generate_insights("student_123")

        # Should return empty or minimal insights
        assert insights is not None
        assert isinstance(insights, list)
