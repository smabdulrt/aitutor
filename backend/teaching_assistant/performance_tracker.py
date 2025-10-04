"""
Performance Tracking System

Tracks session metrics, detects trends, and generates improvement suggestions.
"""

import logging
from enum import Enum
from typing import Optional, Callable, List, Dict
from dataclasses import dataclass, field
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PerformanceTrend(Enum):
    """Performance trend over time"""
    IMPROVING = "improving"
    DECLINING = "declining"
    STABLE = "stable"
    INSUFFICIENT_DATA = "insufficient_data"


class DifficultyAdjustment(Enum):
    """Suggested difficulty adjustments"""
    INCREASE = "increase"
    DECREASE = "decrease"
    MAINTAIN = "maintain"


@dataclass
class SessionMetrics:
    """Metrics for a single tutoring session"""
    session_id: str
    questions_answered: int
    questions_correct: int
    student_id: Optional[str] = None
    total_time: float = 0  # seconds
    hints_used: int = 0
    emotions: List[str] = field(default_factory=list)
    timestamp: Optional[float] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().timestamp()


class PerformanceTracker:
    """
    Performance Tracking System

    Tracks and analyzes student performance metrics:
    - Questions answered and accuracy
    - Time per question
    - Hints needed
    - Emotional state trends
    - Skill mastery progression
    """

    def __init__(
        self,
        suggestion_callback: Optional[Callable] = None,
        history_limit: int = 100
    ):
        """
        Initialize Performance Tracker

        Args:
            suggestion_callback: Async function to send suggestions to Adam
            history_limit: Maximum number of sessions to retain in history
        """
        self.suggestion_callback = suggestion_callback
        self.history_limit = history_limit
        self.session_history: List[SessionMetrics] = []

        logger.info("Performance Tracker initialized")

    def track_metrics(self, session_data: Dict) -> SessionMetrics:
        """
        Track metrics for a session

        Args:
            session_data: Dictionary containing session metrics

        Returns:
            SessionMetrics object
        """
        # Extract metrics from session data
        metrics = SessionMetrics(
            session_id=session_data.get("session_id", f"session_{datetime.now().timestamp()}"),
            student_id=session_data.get("student_id"),
            questions_answered=session_data.get("questions_answered", 0),
            questions_correct=session_data.get("questions_correct", 0),
            total_time=session_data.get("total_time", 0),
            hints_used=session_data.get("hints_used", 0),
            emotions=session_data.get("emotions", []),
            timestamp=session_data.get("timestamp")
        )

        # Add to history
        self.session_history.append(metrics)

        # Maintain history limit
        if len(self.session_history) > self.history_limit:
            self.session_history = self.session_history[-self.history_limit:]

        logger.info(f"Tracked metrics for session: {metrics.session_id}")
        return metrics

    def calculate_accuracy(self, metrics: SessionMetrics) -> float:
        """
        Calculate accuracy for a session

        Args:
            metrics: Session metrics

        Returns:
            Accuracy as float (0.0 to 1.0)
        """
        if metrics.questions_answered == 0:
            return 0.0

        accuracy = metrics.questions_correct / metrics.questions_answered
        return accuracy

    def calculate_time_per_question(self, metrics: SessionMetrics) -> float:
        """
        Calculate average time per question

        Args:
            metrics: Session metrics

        Returns:
            Average time per question in seconds
        """
        if metrics.questions_answered == 0:
            return 0.0

        time_per_q = metrics.total_time / metrics.questions_answered
        return time_per_q

    def detect_trends(self, n_sessions: int = 3) -> PerformanceTrend:
        """
        Detect performance trend over recent sessions

        Args:
            n_sessions: Number of recent sessions to analyze

        Returns:
            PerformanceTrend enum
        """
        if len(self.session_history) < n_sessions:
            return PerformanceTrend.INSUFFICIENT_DATA

        # Get recent sessions
        recent_sessions = self.session_history[-n_sessions:]

        # Calculate accuracy for each session
        accuracies = [self.calculate_accuracy(session) for session in recent_sessions]

        # Detect trend
        if all(accuracies[i] < accuracies[i + 1] for i in range(len(accuracies) - 1)):
            return PerformanceTrend.IMPROVING
        elif all(accuracies[i] > accuracies[i + 1] for i in range(len(accuracies) - 1)):
            return PerformanceTrend.DECLINING
        else:
            return PerformanceTrend.STABLE

    def suggest_difficulty_adjustment(self, metrics: SessionMetrics) -> DifficultyAdjustment:
        """
        Suggest difficulty adjustment based on performance

        Args:
            metrics: Session metrics

        Returns:
            DifficultyAdjustment enum
        """
        accuracy = self.calculate_accuracy(metrics)

        # High accuracy (>=90%) → increase difficulty
        if accuracy >= 0.9:
            return DifficultyAdjustment.INCREASE

        # Low accuracy (<50%) → decrease difficulty
        elif accuracy < 0.5:
            return DifficultyAdjustment.DECREASE

        # Moderate accuracy (50-90%) → maintain
        else:
            return DifficultyAdjustment.MAINTAIN

    async def generate_suggestions(self, metrics: SessionMetrics) -> List[str]:
        """
        Generate performance improvement suggestions

        Args:
            metrics: Session metrics

        Returns:
            List of suggestion strings
        """
        suggestions = []
        accuracy = self.calculate_accuracy(metrics)
        difficulty_adjustment = self.suggest_difficulty_adjustment(metrics)

        # Accuracy-based suggestions
        if accuracy > 0.9:
            suggestions.append(
                "Excellent work! You're mastering this material. "
                "Consider moving to more challenging problems."
            )
        elif accuracy < 0.5:
            suggestions.append(
                "Let's review the fundamentals of this topic. "
                "Breaking down the concepts into smaller steps might help."
            )
        else:
            suggestions.append(
                "Good progress! Keep practicing to solidify your understanding."
            )

        # Hints-based suggestions
        if metrics.hints_used > metrics.questions_answered * 0.5:
            suggestions.append(
                "You're using hints frequently. Try working through problems step-by-step "
                "before asking for help to build confidence."
            )

        # Time-based suggestions
        time_per_q = self.calculate_time_per_question(metrics)
        if time_per_q > 0:
            if time_per_q > 180:  # More than 3 minutes per question
                suggestions.append(
                    "Take your time, but if you're stuck for more than a few minutes, "
                    "try breaking the problem into smaller parts."
                )
            elif time_per_q < 30:  # Less than 30 seconds per question
                suggestions.append(
                    "You're working quickly! Make sure you're taking time to understand "
                    "the concepts, not just getting answers."
                )

        # Difficulty adjustment suggestion
        if difficulty_adjustment == DifficultyAdjustment.INCREASE:
            suggestions.append(
                "You're ready for more challenging material. "
                "Let's explore advanced concepts in this area."
            )
        elif difficulty_adjustment == DifficultyAdjustment.DECREASE:
            suggestions.append(
                "Let's adjust the difficulty to match your current level. "
                "Building a strong foundation is important."
            )

        # Send suggestions via callback if available
        if self.suggestion_callback:
            suggestions_text = "\n".join([f"- {s}" for s in suggestions])
            await self.suggestion_callback(suggestions_text)
            logger.info("Suggestions sent to callback")

        logger.info(f"Generated {len(suggestions)} suggestions")
        return suggestions

    def analyze_emotional_trend(self, metrics: SessionMetrics) -> str:
        """
        Analyze emotional trend during session

        Args:
            metrics: Session metrics

        Returns:
            Emotional trend description
        """
        if not metrics.emotions or len(metrics.emotions) == 0:
            return "neutral"

        # Simple analysis: compare beginning vs end
        first_half = metrics.emotions[:len(metrics.emotions) // 2]
        second_half = metrics.emotions[len(metrics.emotions) // 2:]

        # Count positive emotions (confident) vs negative (frustrated, confused)
        positive_emotions = {"confident"}
        negative_emotions = {"frustrated", "confused"}

        first_positive = sum(1 for e in first_half if e in positive_emotions)
        second_positive = sum(1 for e in second_half if e in positive_emotions)

        if second_positive > first_positive:
            return "improving"
        elif second_positive < first_positive:
            return "declining"
        else:
            return "stable"

    def get_dashboard_data(self) -> Dict:
        """
        Get performance dashboard data

        Returns:
            Dictionary with dashboard metrics
        """
        if len(self.session_history) == 0:
            return {
                "total_sessions": 0,
                "average_accuracy": 0.0,
                "trend": PerformanceTrend.INSUFFICIENT_DATA
            }

        # Calculate aggregated metrics
        total_sessions = len(self.session_history)

        # Average accuracy across all sessions
        accuracies = [self.calculate_accuracy(session) for session in self.session_history]
        average_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0.0

        # Overall trend
        trend = self.detect_trends()

        # Total questions
        total_questions = sum(s.questions_answered for s in self.session_history)
        total_correct = sum(s.questions_correct for s in self.session_history)

        # Average time per question
        total_time = sum(s.total_time for s in self.session_history)
        avg_time_per_q = total_time / total_questions if total_questions > 0 else 0

        dashboard = {
            "total_sessions": total_sessions,
            "total_questions": total_questions,
            "total_correct": total_correct,
            "average_accuracy": average_accuracy,
            "trend": trend,
            "average_time_per_question": avg_time_per_q
        }

        logger.info(f"Dashboard data: {total_sessions} sessions, {average_accuracy:.0%} avg accuracy")
        return dashboard
