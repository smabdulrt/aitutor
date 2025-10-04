"""
Tests for Performance Tracking System

Following TDD: Tests written FIRST, then implementation.
All logic imported from codebase - NO hardcoded test logic.

Performance Tracking:
1. Track session metrics (questions, accuracy, time, hints, emotions)
2. Calculate performance statistics
3. Detect trends and patterns
4. Generate suggestions for improvement
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock
from backend.teaching_assistant.performance_tracker import (
    PerformanceTracker,
    SessionMetrics,
    PerformanceTrend,
    DifficultyAdjustment
)


class TestPerformanceTrackerInitialization:
    """Test performance tracker initialization"""

    def test_initialization(self):
        """Test tracker initializes correctly"""
        tracker = PerformanceTracker()

        assert tracker is not None
        assert tracker.session_history == []

    def test_initialization_with_callback(self):
        """Test initialization with suggestion callback"""
        callback = AsyncMock()
        tracker = PerformanceTracker(suggestion_callback=callback)

        assert tracker.suggestion_callback == callback


class TestSessionMetrics:
    """Test session metrics tracking"""

    @pytest.fixture
    def tracker(self):
        return PerformanceTracker()

    def test_track_metrics(self, tracker):
        """Test tracking session metrics"""
        session_data = {
            "session_id": "session_1",
            "student_id": "student_123",
            "questions_answered": 5,
            "questions_correct": 4,
            "total_time": 600,  # seconds
            "hints_used": 2,
            "emotions": ["confident", "confused", "confident"]
        }

        metrics = tracker.track_metrics(session_data)

        assert metrics is not None
        assert isinstance(metrics, SessionMetrics)
        assert metrics.questions_answered == 5
        assert metrics.questions_correct == 4

    def test_metrics_added_to_history(self, tracker):
        """Test metrics are added to session history"""
        session_data = {
            "session_id": "session_1",
            "questions_answered": 3,
            "questions_correct": 2
        }

        tracker.track_metrics(session_data)

        assert len(tracker.session_history) == 1
        assert tracker.session_history[0].questions_answered == 3

    def test_track_multiple_sessions(self, tracker):
        """Test tracking multiple sessions"""
        for i in range(3):
            session_data = {
                "session_id": f"session_{i}",
                "questions_answered": i + 1,
                "questions_correct": i
            }
            tracker.track_metrics(session_data)

        assert len(tracker.session_history) == 3


class TestAccuracyCalculation:
    """Test accuracy calculation"""

    @pytest.fixture
    def tracker(self):
        return PerformanceTracker()

    def test_calculate_accuracy_perfect(self, tracker):
        """Test accuracy calculation with perfect score"""
        session_data = {
            "session_id": "session_1",
            "questions_answered": 5,
            "questions_correct": 5
        }

        metrics = tracker.track_metrics(session_data)
        accuracy = tracker.calculate_accuracy(metrics)

        assert accuracy == 1.0  # 100%

    def test_calculate_accuracy_partial(self, tracker):
        """Test accuracy calculation with partial score"""
        session_data = {
            "session_id": "session_1",
            "questions_answered": 10,
            "questions_correct": 7
        }

        metrics = tracker.track_metrics(session_data)
        accuracy = tracker.calculate_accuracy(metrics)

        assert accuracy == 0.7  # 70%

    def test_calculate_accuracy_zero_questions(self, tracker):
        """Test accuracy with zero questions"""
        session_data = {
            "session_id": "session_1",
            "questions_answered": 0,
            "questions_correct": 0
        }

        metrics = tracker.track_metrics(session_data)
        accuracy = tracker.calculate_accuracy(metrics)

        assert accuracy == 0.0  # Handle gracefully


class TestTrendDetection:
    """Test trend detection over multiple sessions"""

    @pytest.fixture
    def tracker(self):
        return PerformanceTracker()

    def test_detect_improving_trend(self, tracker):
        """Test detecting improving performance trend"""
        # Add sessions with increasing accuracy
        sessions = [
            {"session_id": "s1", "questions_answered": 5, "questions_correct": 2},  # 40%
            {"session_id": "s2", "questions_answered": 5, "questions_correct": 3},  # 60%
            {"session_id": "s3", "questions_answered": 5, "questions_correct": 4},  # 80%
        ]

        for session in sessions:
            tracker.track_metrics(session)

        trend = tracker.detect_trends()

        assert trend == PerformanceTrend.IMPROVING

    def test_detect_declining_trend(self, tracker):
        """Test detecting declining performance trend"""
        sessions = [
            {"session_id": "s1", "questions_answered": 5, "questions_correct": 4},  # 80%
            {"session_id": "s2", "questions_answered": 5, "questions_correct": 3},  # 60%
            {"session_id": "s3", "questions_answered": 5, "questions_correct": 2},  # 40%
        ]

        for session in sessions:
            tracker.track_metrics(session)

        trend = tracker.detect_trends()

        assert trend == PerformanceTrend.DECLINING

    def test_detect_stable_trend(self, tracker):
        """Test detecting stable performance trend"""
        sessions = [
            {"session_id": "s1", "questions_answered": 5, "questions_correct": 3},
            {"session_id": "s2", "questions_answered": 5, "questions_correct": 3},
            {"session_id": "s3", "questions_answered": 5, "questions_correct": 3},
        ]

        for session in sessions:
            tracker.track_metrics(session)

        trend = tracker.detect_trends()

        assert trend == PerformanceTrend.STABLE

    def test_detect_trends_insufficient_data(self, tracker):
        """Test trend detection with insufficient data"""
        session = {"session_id": "s1", "questions_answered": 5, "questions_correct": 3}
        tracker.track_metrics(session)

        trend = tracker.detect_trends()

        # Should return stable or unknown with < 3 sessions
        assert trend in [PerformanceTrend.STABLE, PerformanceTrend.INSUFFICIENT_DATA]


class TestDifficultyAdjustment:
    """Test difficulty adjustment suggestions"""

    @pytest.fixture
    def tracker(self):
        return PerformanceTracker()

    def test_suggest_increase_difficulty_high_accuracy(self, tracker):
        """Test suggesting difficulty increase for high accuracy (>90%)"""
        session_data = {
            "session_id": "session_1",
            "questions_answered": 10,
            "questions_correct": 9  # 90%+
        }

        metrics = tracker.track_metrics(session_data)
        adjustment = tracker.suggest_difficulty_adjustment(metrics)

        assert adjustment == DifficultyAdjustment.INCREASE

    def test_suggest_decrease_difficulty_low_accuracy(self, tracker):
        """Test suggesting difficulty decrease for low accuracy (<50%)"""
        session_data = {
            "session_id": "session_1",
            "questions_answered": 10,
            "questions_correct": 4  # 40%
        }

        metrics = tracker.track_metrics(session_data)
        adjustment = tracker.suggest_difficulty_adjustment(metrics)

        assert adjustment == DifficultyAdjustment.DECREASE

    def test_suggest_maintain_difficulty_moderate_accuracy(self, tracker):
        """Test suggesting maintain difficulty for moderate accuracy (50-90%)"""
        session_data = {
            "session_id": "session_1",
            "questions_answered": 10,
            "questions_correct": 7  # 70%
        }

        metrics = tracker.track_metrics(session_data)
        adjustment = tracker.suggest_difficulty_adjustment(metrics)

        assert adjustment == DifficultyAdjustment.MAINTAIN


class TestPerformanceSuggestions:
    """Test generating performance improvement suggestions"""

    @pytest.fixture
    def tracker(self):
        callback = AsyncMock()
        return PerformanceTracker(suggestion_callback=callback)

    @pytest.mark.asyncio
    async def test_generate_suggestions_high_accuracy(self, tracker):
        """Test generating suggestions for high accuracy"""
        session_data = {
            "session_id": "session_1",
            "questions_answered": 10,
            "questions_correct": 9
        }

        metrics = tracker.track_metrics(session_data)
        suggestions = await tracker.generate_suggestions(metrics)

        assert suggestions is not None
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

    @pytest.mark.asyncio
    async def test_generate_suggestions_low_accuracy(self, tracker):
        """Test generating suggestions for low accuracy"""
        session_data = {
            "session_id": "session_1",
            "questions_answered": 10,
            "questions_correct": 3
        }

        metrics = tracker.track_metrics(session_data)
        suggestions = await tracker.generate_suggestions(metrics)

        assert suggestions is not None
        assert len(suggestions) > 0
        # Should suggest reviewing fundamentals
        assert any("review" in s.lower() or "fundamental" in s.lower() for s in suggestions)

    @pytest.mark.asyncio
    async def test_suggestions_sent_to_callback(self, tracker):
        """Test suggestions are sent via callback"""
        session_data = {
            "session_id": "session_1",
            "questions_answered": 10,
            "questions_correct": 5
        }

        metrics = tracker.track_metrics(session_data)
        await tracker.generate_suggestions(metrics)

        # Verify callback was called
        tracker.suggestion_callback.assert_called_once()


class TestTimePerQuestion:
    """Test time per question tracking"""

    @pytest.fixture
    def tracker(self):
        return PerformanceTracker()

    def test_calculate_time_per_question(self, tracker):
        """Test calculating average time per question"""
        session_data = {
            "session_id": "session_1",
            "questions_answered": 5,
            "questions_correct": 4,
            "total_time": 300  # 5 minutes = 300 seconds
        }

        metrics = tracker.track_metrics(session_data)
        time_per_q = tracker.calculate_time_per_question(metrics)

        assert time_per_q == 60  # 60 seconds per question

    def test_time_per_question_zero_questions(self, tracker):
        """Test time calculation with zero questions"""
        session_data = {
            "session_id": "session_1",
            "questions_answered": 0,
            "total_time": 100
        }

        metrics = tracker.track_metrics(session_data)
        time_per_q = tracker.calculate_time_per_question(metrics)

        assert time_per_q == 0  # Handle gracefully


class TestEmotionalTrends:
    """Test emotional state tracking"""

    @pytest.fixture
    def tracker(self):
        return PerformanceTracker()

    def test_track_emotions(self, tracker):
        """Test tracking emotional states during session"""
        session_data = {
            "session_id": "session_1",
            "questions_answered": 5,
            "questions_correct": 4,
            "emotions": ["confident", "confused", "confident", "confident"]
        }

        metrics = tracker.track_metrics(session_data)

        assert metrics.emotions == ["confident", "confused", "confident", "confident"]

    def test_analyze_emotional_trend(self, tracker):
        """Test analyzing emotional trends"""
        session_data = {
            "session_id": "session_1",
            "questions_answered": 5,
            "questions_correct": 4,
            "emotions": ["frustrated", "frustrated", "confused", "confident", "confident"]
        }

        metrics = tracker.track_metrics(session_data)
        emotional_trend = tracker.analyze_emotional_trend(metrics)

        # Should detect improvement (frustrated → confident)
        assert emotional_trend == "improving"


class TestSessionMetricsDataClass:
    """Test SessionMetrics data structure"""

    def test_create_session_metrics(self):
        """Test creating session metrics"""
        metrics = SessionMetrics(
            session_id="session_1",
            student_id="student_123",
            questions_answered=10,
            questions_correct=8,
            total_time=600,
            hints_used=3,
            emotions=["confident"],
            timestamp=datetime.now().timestamp()
        )

        assert metrics.session_id == "session_1"
        assert metrics.questions_answered == 10
        assert metrics.questions_correct == 8

    def test_metrics_default_values(self):
        """Test metrics with default values"""
        metrics = SessionMetrics(
            session_id="session_1",
            questions_answered=5,
            questions_correct=3
        )

        assert metrics.student_id is None
        assert metrics.hints_used == 0
        assert metrics.emotions == []


class TestPerformanceDashboard:
    """Test performance dashboard data generation"""

    @pytest.fixture
    def tracker(self):
        tracker = PerformanceTracker()
        # Add multiple sessions
        for i in range(5):
            tracker.track_metrics({
                "session_id": f"session_{i}",
                "questions_answered": 10,
                "questions_correct": 7 + i  # Improving over time
            })
        return tracker

    def test_get_dashboard_data(self, tracker):
        """Test generating dashboard data"""
        dashboard = tracker.get_dashboard_data()

        assert dashboard is not None
        assert "total_sessions" in dashboard
        assert dashboard["total_sessions"] == 5

    def test_dashboard_includes_trends(self, tracker):
        """Test dashboard includes performance trends"""
        dashboard = tracker.get_dashboard_data()

        assert "trend" in dashboard
        assert dashboard["trend"] == PerformanceTrend.IMPROVING

    def test_dashboard_includes_averages(self, tracker):
        """Test dashboard includes average metrics"""
        dashboard = tracker.get_dashboard_data()

        assert "average_accuracy" in dashboard
        assert dashboard["average_accuracy"] > 0


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_track_metrics_missing_fields(self):
        """Test tracking metrics with missing fields"""
        tracker = PerformanceTracker()

        session_data = {
            "session_id": "session_1"
            # Missing most fields
        }

        # Should handle gracefully with defaults
        metrics = tracker.track_metrics(session_data)

        assert metrics is not None
        assert metrics.questions_answered == 0

    def test_history_size_limit(self):
        """Test history doesn't grow unbounded"""
        tracker = PerformanceTracker(history_limit=10)

        # Add 20 sessions
        for i in range(20):
            tracker.track_metrics({
                "session_id": f"session_{i}",
                "questions_answered": 5,
                "questions_correct": 3
            })

        # Should limit to 10
        assert len(tracker.session_history) <= 10

    @pytest.mark.asyncio
    async def test_generate_suggestions_without_callback(self):
        """Test generating suggestions without callback"""
        tracker = PerformanceTracker()  # No callback

        session_data = {
            "session_id": "session_1",
            "questions_answered": 10,
            "questions_correct": 5
        }

        metrics = tracker.track_metrics(session_data)

        # Should still generate suggestions, just not send them
        suggestions = await tracker.generate_suggestions(metrics)

        assert suggestions is not None
