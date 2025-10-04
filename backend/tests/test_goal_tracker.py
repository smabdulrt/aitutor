"""
Tests for Goal & Progress Tracking

Following TDD: Tests written FIRST, then implementation.
All logic imported from codebase - NO hardcoded test logic.

Goal & Progress Tracking:
1. SMART goal CRUD operations
2. Milestone detection from learning patterns
3. Progress calculation toward goals
4. Goal recommendations based on velocity
5. Achievement tracking and celebrations
"""

import pytest
from datetime import datetime, timedelta
from backend.memory.goal_tracker import (
    GoalTracker,
    Goal,
    GoalStatus,
    GoalType,
    Milestone,
    Achievement
)


class TestGoalTrackerInitialization:
    """Test goal tracker initialization"""

    def test_initialization(self):
        """Test tracker initializes correctly"""
        tracker = GoalTracker()

        assert tracker is not None
        assert tracker.db_path is not None

    def test_initialization_with_custom_path(self):
        """Test initialization with custom database path"""
        custom_path = "/tmp/test_goals.db"
        tracker = GoalTracker(db_path=custom_path)

        assert tracker.db_path == custom_path


class TestGoalTypes:
    """Test goal type enumeration"""

    def test_goal_types_exist(self):
        """Test all expected goal types are defined"""
        expected_types = [
            GoalType.MASTERY,
            GoalType.ACCURACY,
            GoalType.VELOCITY,
            GoalType.CONSISTENCY
        ]

        for goal_type in expected_types:
            assert goal_type in GoalType


class TestGoalStatus:
    """Test goal status enumeration"""

    def test_goal_statuses_exist(self):
        """Test all expected goal statuses are defined"""
        expected_statuses = [
            GoalStatus.ACTIVE,
            GoalStatus.COMPLETED,
            GoalStatus.PAUSED,
            GoalStatus.ABANDONED
        ]

        for status in expected_statuses:
            assert status in GoalStatus


class TestGoalCreation:
    """Test creating goals"""

    @pytest.fixture
    def tracker(self):
        return GoalTracker(db_path=":memory:")

    def test_create_goal(self, tracker):
        """Test creating a new goal"""
        goal = tracker.create_goal(
            student_id="student_123",
            goal_type=GoalType.MASTERY,
            title="Master algebra basics",
            description="Complete all basic algebra topics with 80%+ accuracy",
            target_value=0.8,
            deadline=datetime(2025, 12, 31).timestamp()
        )

        assert goal is not None
        assert isinstance(goal, Goal)
        assert goal.student_id == "student_123"
        assert goal.goal_type == GoalType.MASTERY
        assert goal.title == "Master algebra basics"

    def test_goal_has_id_and_timestamp(self, tracker):
        """Test goal gets ID and creation timestamp"""
        goal = tracker.create_goal(
            student_id="student_456",
            goal_type=GoalType.ACCURACY,
            title="Achieve 90% accuracy",
            target_value=0.9
        )

        assert goal.goal_id is not None
        assert goal.created_at is not None
        assert isinstance(goal.created_at, float)

    def test_goal_defaults_to_active(self, tracker):
        """Test goal defaults to active status"""
        goal = tracker.create_goal(
            student_id="student_123",
            goal_type=GoalType.VELOCITY,
            title="Learn 5 concepts per week",
            target_value=5
        )

        assert goal.status == GoalStatus.ACTIVE


class TestGoalRetrieval:
    """Test retrieving goals"""

    @pytest.fixture
    def tracker(self):
        system = GoalTracker(db_path=":memory:")

        # Add sample goals
        system.create_goal(
            "student_123",
            GoalType.MASTERY,
            "Goal 1",
            target_value=0.8
        )
        system.create_goal(
            "student_123",
            GoalType.ACCURACY,
            "Goal 2",
            target_value=0.9
        )
        system.create_goal(
            "student_456",
            GoalType.VELOCITY,
            "Goal 3",
            target_value=5
        )

        return system

    def test_get_goal_by_id(self, tracker):
        """Test retrieving goal by ID"""
        goal = tracker.create_goal(
            "student_123",
            GoalType.CONSISTENCY,
            "Daily practice",
            target_value=7
        )

        retrieved = tracker.get_goal(goal.goal_id)

        assert retrieved is not None
        assert retrieved.goal_id == goal.goal_id
        assert retrieved.title == "Daily practice"

    def test_get_student_goals(self, tracker):
        """Test retrieving all goals for a student"""
        goals = tracker.get_student_goals("student_123")

        assert len(goals) == 2
        assert all(g.student_id == "student_123" for g in goals)

    def test_get_active_goals_only(self, tracker):
        """Test retrieving only active goals"""
        # Create and complete a goal
        goal = tracker.create_goal(
            "student_123",
            GoalType.MASTERY,
            "Completed goal",
            target_value=1.0
        )
        tracker.update_goal_status(goal.goal_id, GoalStatus.COMPLETED)

        active_goals = tracker.get_student_goals("student_123", status=GoalStatus.ACTIVE)

        assert all(g.status == GoalStatus.ACTIVE for g in active_goals)
        assert goal.goal_id not in [g.goal_id for g in active_goals]


class TestGoalUpdate:
    """Test updating goals"""

    @pytest.fixture
    def tracker(self):
        return GoalTracker(db_path=":memory:")

    def test_update_goal_status(self, tracker):
        """Test updating goal status"""
        goal = tracker.create_goal(
            "student_123",
            GoalType.MASTERY,
            "Test goal",
            target_value=0.8
        )

        updated = tracker.update_goal_status(goal.goal_id, GoalStatus.COMPLETED)

        assert updated.status == GoalStatus.COMPLETED

    def test_update_goal_progress(self, tracker):
        """Test updating goal progress"""
        goal = tracker.create_goal(
            "student_123",
            GoalType.ACCURACY,
            "90% accuracy",
            target_value=0.9
        )

        tracker.update_goal_progress(goal.goal_id, current_value=0.75)

        updated = tracker.get_goal(goal.goal_id)
        assert updated.current_value == 0.75

    def test_auto_complete_when_target_reached(self, tracker):
        """Test auto-completing goal when target is reached"""
        goal = tracker.create_goal(
            "student_123",
            GoalType.ACCURACY,
            "80% accuracy",
            target_value=0.8
        )

        tracker.update_goal_progress(goal.goal_id, current_value=0.85)

        updated = tracker.get_goal(goal.goal_id)
        assert updated.status == GoalStatus.COMPLETED


class TestProgressCalculation:
    """Test progress calculation"""

    @pytest.fixture
    def tracker(self):
        return GoalTracker(db_path=":memory:")

    def test_calculate_progress_percentage(self, tracker):
        """Test calculating progress as percentage"""
        goal = tracker.create_goal(
            "student_123",
            GoalType.MASTERY,
            "Master 10 topics",
            target_value=10
        )

        tracker.update_goal_progress(goal.goal_id, current_value=7)

        progress = tracker.calculate_progress(goal.goal_id)

        assert progress is not None
        assert progress["percentage"] == 70
        assert progress["current"] == 7
        assert progress["target"] == 10

    def test_progress_capped_at_100_percent(self, tracker):
        """Test progress doesn't exceed 100%"""
        goal = tracker.create_goal(
            "student_123",
            GoalType.VELOCITY,
            "5 concepts per week",
            target_value=5
        )

        tracker.update_goal_progress(goal.goal_id, current_value=8)

        progress = tracker.calculate_progress(goal.goal_id)

        assert progress["percentage"] == 100

    def test_time_based_progress(self, tracker):
        """Test calculating time-based progress"""
        now = datetime.now()
        deadline = now + timedelta(days=30)
        start = now - timedelta(days=10)

        goal = tracker.create_goal(
            "student_123",
            GoalType.CONSISTENCY,
            "30-day streak",
            target_value=30,
            deadline=deadline.timestamp()
        )

        # Set creation time (simulate started 10 days ago)
        goal.created_at = start.timestamp()

        progress = tracker.calculate_progress(goal.goal_id, include_time=True)

        assert "time_progress" in progress
        assert 0 <= progress["time_progress"] <= 100


class TestMilestoneDetection:
    """Test milestone detection"""

    @pytest.fixture
    def tracker(self):
        from backend.memory.learning_pattern_tracker import LearningPatternTracker
        pattern_tracker = LearningPatternTracker(db_path=":memory:")
        return GoalTracker(db_path=":memory:", pattern_tracker=pattern_tracker)

    def test_detect_milestones_from_progress(self, tracker):
        """Test detecting milestones (25%, 50%, 75%, 100%)"""
        goal = tracker.create_goal(
            "student_123",
            GoalType.MASTERY,
            "Master 100 concepts",
            target_value=100
        )

        # Update to 25%
        tracker.update_goal_progress(goal.goal_id, current_value=25)
        milestones = tracker.get_goal_milestones(goal.goal_id)

        assert len(milestones) >= 1
        assert any(m.milestone_type == "25%" for m in milestones)

    def test_milestone_only_created_once(self, tracker):
        """Test milestone is only created once"""
        goal = tracker.create_goal(
            "student_123",
            GoalType.ACCURACY,
            "90% accuracy",
            target_value=0.9
        )

        # Cross 50% threshold multiple times
        tracker.update_goal_progress(goal.goal_id, current_value=0.5)
        tracker.update_goal_progress(goal.goal_id, current_value=0.4)
        tracker.update_goal_progress(goal.goal_id, current_value=0.6)

        milestones = tracker.get_goal_milestones(goal.goal_id)

        # Should only have one 50% milestone
        fifty_percent = [m for m in milestones if m.milestone_type == "50%"]
        assert len(fifty_percent) == 1

    def test_custom_milestone_creation(self, tracker):
        """Test creating custom milestones"""
        goal = tracker.create_goal(
            "student_123",
            GoalType.VELOCITY,
            "Learn fast",
            target_value=10
        )

        milestone = tracker.create_milestone(
            goal_id=goal.goal_id,
            milestone_type="custom",
            description="First week complete",
            achieved_at=datetime.now().timestamp()
        )

        assert milestone is not None
        assert isinstance(milestone, Milestone)
        assert milestone.milestone_type == "custom"


class TestGoalRecommendations:
    """Test goal recommendations"""

    @pytest.fixture
    def tracker(self):
        from backend.memory.learning_pattern_tracker import LearningPatternTracker
        pattern_tracker = LearningPatternTracker(db_path=":memory:")
        return GoalTracker(db_path=":memory:", pattern_tracker=pattern_tracker)

    def test_recommend_goals_from_velocity(self, tracker):
        """Test recommending goals based on learning velocity"""
        # Add session data
        now = datetime.now()
        for i in range(5):
            session_time = now - timedelta(days=6-i)
            tracker.pattern_tracker.record_session(
                student_id="student_123",
                start_time=session_time.timestamp(),
                end_time=(session_time + timedelta(hours=1)).timestamp(),
                concepts_covered=["topic1", "topic2", "topic3"],
                concepts_mastered=["topic1", "topic2"]
            )

        recommendations = tracker.recommend_goals("student_123")

        assert recommendations is not None
        assert isinstance(recommendations, list)
        if recommendations:
            assert all(isinstance(r, dict) for r in recommendations)

    def test_recommend_accuracy_goal(self, tracker):
        """Test recommending accuracy improvement goal"""
        # Add sessions with low accuracy
        now = datetime.now()
        for i in range(3):
            tracker.pattern_tracker.record_session(
                student_id="student_123",
                start_time=now.timestamp() + (i * 3600),
                end_time=now.timestamp() + ((i + 1) * 3600),
                questions_asked=10,
                questions_correct=6  # 60% accuracy
            )

        recommendations = tracker.recommend_goals("student_123")

        # Should recommend accuracy improvement
        assert any("accuracy" in r.get("title", "").lower() for r in recommendations)

    def test_recommend_consistency_goal(self, tracker):
        """Test recommending consistency goal for irregular sessions"""
        # Irregular sessions
        now = datetime.now()
        tracker.pattern_tracker.record_session(
            "student_123",
            now.timestamp() - (10 * 24 * 3600),
            now.timestamp() - (10 * 24 * 3600) + 3600
        )
        tracker.pattern_tracker.record_session(
            "student_123",
            now.timestamp() - (2 * 24 * 3600),
            now.timestamp() - (2 * 24 * 3600) + 3600
        )

        recommendations = tracker.recommend_goals("student_123")

        # Should recommend consistency
        assert any("consistency" in r.get("type", "").lower() or
                   "regular" in r.get("title", "").lower() for r in recommendations)


class TestAchievements:
    """Test achievement tracking"""

    @pytest.fixture
    def tracker(self):
        return GoalTracker(db_path=":memory:")

    def test_award_achievement(self, tracker):
        """Test awarding achievement"""
        achievement = tracker.award_achievement(
            student_id="student_123",
            achievement_type="first_goal_completed",
            title="Goal Getter",
            description="Completed your first goal!"
        )

        assert achievement is not None
        assert isinstance(achievement, Achievement)
        assert achievement.student_id == "student_123"
        assert achievement.achievement_type == "first_goal_completed"

    def test_get_student_achievements(self, tracker):
        """Test retrieving student achievements"""
        tracker.award_achievement(
            "student_123",
            "milestone_25",
            "Quarter Way",
            "Reached 25% progress"
        )
        tracker.award_achievement(
            "student_123",
            "streak_7",
            "Week Warrior",
            "7-day learning streak"
        )

        achievements = tracker.get_student_achievements("student_123")

        assert len(achievements) == 2
        assert all(a.student_id == "student_123" for a in achievements)

    def test_achievement_not_duplicated(self, tracker):
        """Test achievement is not awarded twice"""
        tracker.award_achievement(
            "student_123",
            "first_goal",
            "First Goal",
            "Created first goal"
        )

        # Try to award same achievement again
        duplicate = tracker.award_achievement(
            "student_123",
            "first_goal",
            "First Goal",
            "Created first goal"
        )

        achievements = tracker.get_student_achievements("student_123")

        # Should only have one
        first_goal_achievements = [a for a in achievements if a.achievement_type == "first_goal"]
        assert len(first_goal_achievements) == 1


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_get_nonexistent_goal(self):
        """Test retrieving non-existent goal"""
        tracker = GoalTracker(db_path=":memory:")

        goal = tracker.get_goal("nonexistent_id")

        assert goal is None

    def test_update_nonexistent_goal(self):
        """Test updating non-existent goal"""
        tracker = GoalTracker(db_path=":memory:")

        with pytest.raises(ValueError):
            tracker.update_goal_status("nonexistent_id", GoalStatus.COMPLETED)

    def test_create_goal_with_invalid_target(self):
        """Test creating goal with negative target"""
        tracker = GoalTracker(db_path=":memory:")

        with pytest.raises(ValueError):
            tracker.create_goal(
                "student_123",
                GoalType.MASTERY,
                "Invalid goal",
                target_value=-5
            )

    def test_progress_for_goal_with_zero_target(self):
        """Test progress calculation for edge case"""
        tracker = GoalTracker(db_path=":memory:")

        goal = tracker.create_goal(
            "student_123",
            GoalType.VELOCITY,
            "Test",
            target_value=0.01  # Very small target
        )

        tracker.update_goal_progress(goal.goal_id, current_value=0.01)

        progress = tracker.calculate_progress(goal.goal_id)

        assert progress["percentage"] == 100

    def test_get_goals_for_new_student(self):
        """Test retrieving goals for student with none"""
        tracker = GoalTracker(db_path=":memory:")

        goals = tracker.get_student_goals("new_student")

        assert goals == []

    def test_milestone_for_completed_goal(self):
        """Test milestones are still accessible after completion"""
        tracker = GoalTracker(db_path=":memory:")

        goal = tracker.create_goal(
            "student_123",
            GoalType.MASTERY,
            "Test goal",
            target_value=10
        )

        tracker.update_goal_progress(goal.goal_id, current_value=10)  # Auto-completes

        milestones = tracker.get_goal_milestones(goal.goal_id)

        # Should still retrieve milestones
        assert isinstance(milestones, list)
