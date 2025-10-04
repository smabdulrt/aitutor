"""
Goal & Progress Tracking System

This module tracks student goals, milestones, and achievements:
1. SMART goal CRUD operations
2. Milestone detection from learning patterns
3. Progress calculation toward goals
4. Goal recommendations based on velocity
5. Achievement tracking and celebrations
"""

import sqlite3
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime
import logging
import uuid
from backend.memory.learning_pattern_tracker import LearningPatternTracker

logger = logging.getLogger(__name__)


class GoalType(str, Enum):
    """Types of goals"""
    MASTERY = "mastery"
    ACCURACY = "accuracy"
    VELOCITY = "velocity"
    CONSISTENCY = "consistency"


class GoalStatus(str, Enum):
    """Goal status"""
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    ABANDONED = "abandoned"


@dataclass
class Goal:
    """Student goal"""
    goal_id: str
    student_id: str
    goal_type: GoalType
    title: str
    description: Optional[str]
    target_value: float
    current_value: float
    status: GoalStatus
    created_at: float
    deadline: Optional[float]
    completed_at: Optional[float]


@dataclass
class Milestone:
    """Goal milestone"""
    milestone_id: str
    goal_id: str
    milestone_type: str  # "25%", "50%", "75%", "100%", or custom
    description: str
    achieved_at: float


@dataclass
class Achievement:
    """Student achievement"""
    achievement_id: str
    student_id: str
    achievement_type: str
    title: str
    description: str
    awarded_at: float


class GoalTracker:
    """
    Track student goals, milestones, and achievements
    """

    def __init__(
        self,
        db_path: str = "./goals.db",
        pattern_tracker: Optional[LearningPatternTracker] = None
    ):
        """
        Initialize goal tracker

        Args:
            db_path: Path to SQLite database
            pattern_tracker: Optional LearningPatternTracker instance
        """
        self.db_path = db_path
        self.pattern_tracker = pattern_tracker
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_database()

        logger.info(f"Goal tracker initialized at {db_path}")

    def _init_database(self):
        """Initialize database schema"""
        cursor = self.conn.cursor()

        # Goals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS goals (
                goal_id TEXT PRIMARY KEY,
                student_id TEXT NOT NULL,
                goal_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                target_value REAL NOT NULL,
                current_value REAL DEFAULT 0,
                status TEXT DEFAULT 'active',
                created_at REAL NOT NULL,
                deadline REAL,
                completed_at REAL
            )
        ''')

        # Milestones table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS milestones (
                milestone_id TEXT PRIMARY KEY,
                goal_id TEXT NOT NULL,
                milestone_type TEXT NOT NULL,
                description TEXT,
                achieved_at REAL NOT NULL,
                FOREIGN KEY (goal_id) REFERENCES goals(goal_id)
            )
        ''')

        # Achievements table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS achievements (
                achievement_id TEXT PRIMARY KEY,
                student_id TEXT NOT NULL,
                achievement_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                awarded_at REAL NOT NULL
            )
        ''')

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_goals_student ON goals(student_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_milestones_goal ON milestones(goal_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_achievements_student ON achievements(student_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_achievements_type ON achievements(student_id, achievement_type)')

        self.conn.commit()
        logger.debug("Database schema initialized")

    def create_goal(
        self,
        student_id: str,
        goal_type: GoalType,
        title: str,
        target_value: float,
        description: Optional[str] = None,
        deadline: Optional[float] = None
    ) -> Goal:
        """
        Create a new goal

        Args:
            student_id: Student identifier
            goal_type: Type of goal
            title: Goal title
            target_value: Target value to achieve
            description: Optional description
            deadline: Optional deadline timestamp

        Returns:
            Goal object

        Raises:
            ValueError: If target_value is invalid
        """
        if target_value <= 0:
            raise ValueError("Target value must be positive")

        goal_id = str(uuid.uuid4())
        created_at = datetime.now().timestamp()

        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO goals (
                goal_id, student_id, goal_type, title, description,
                target_value, current_value, status, created_at, deadline
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            goal_id, student_id, goal_type.value, title, description,
            target_value, 0, GoalStatus.ACTIVE.value, created_at, deadline
        ))

        self.conn.commit()

        logger.info(f"Created goal {goal_id} for student {student_id}")

        return Goal(
            goal_id=goal_id,
            student_id=student_id,
            goal_type=goal_type,
            title=title,
            description=description,
            target_value=target_value,
            current_value=0,
            status=GoalStatus.ACTIVE,
            created_at=created_at,
            deadline=deadline,
            completed_at=None
        )

    def get_goal(self, goal_id: str) -> Optional[Goal]:
        """
        Get goal by ID

        Args:
            goal_id: Goal identifier

        Returns:
            Goal object or None
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM goals WHERE goal_id = ?', (goal_id,))
        row = cursor.fetchone()

        if not row:
            return None

        return Goal(
            goal_id=row[0],
            student_id=row[1],
            goal_type=GoalType(row[2]),
            title=row[3],
            description=row[4],
            target_value=row[5],
            current_value=row[6],
            status=GoalStatus(row[7]),
            created_at=row[8],
            deadline=row[9],
            completed_at=row[10]
        )

    def get_student_goals(
        self,
        student_id: str,
        status: Optional[GoalStatus] = None
    ) -> List[Goal]:
        """
        Get all goals for a student

        Args:
            student_id: Student identifier
            status: Optional status filter

        Returns:
            List of Goal objects
        """
        cursor = self.conn.cursor()

        if status:
            cursor.execute('''
                SELECT * FROM goals
                WHERE student_id = ? AND status = ?
                ORDER BY created_at DESC
            ''', (student_id, status.value))
        else:
            cursor.execute('''
                SELECT * FROM goals
                WHERE student_id = ?
                ORDER BY created_at DESC
            ''', (student_id,))

        rows = cursor.fetchall()
        goals = []

        for row in rows:
            goals.append(Goal(
                goal_id=row[0],
                student_id=row[1],
                goal_type=GoalType(row[2]),
                title=row[3],
                description=row[4],
                target_value=row[5],
                current_value=row[6],
                status=GoalStatus(row[7]),
                created_at=row[8],
                deadline=row[9],
                completed_at=row[10]
            ))

        return goals

    def update_goal_status(self, goal_id: str, status: GoalStatus) -> Goal:
        """
        Update goal status

        Args:
            goal_id: Goal identifier
            status: New status

        Returns:
            Updated Goal object

        Raises:
            ValueError: If goal not found
        """
        goal = self.get_goal(goal_id)
        if not goal:
            raise ValueError(f"Goal {goal_id} not found")

        cursor = self.conn.cursor()

        completed_at = datetime.now().timestamp() if status == GoalStatus.COMPLETED else None

        cursor.execute('''
            UPDATE goals
            SET status = ?, completed_at = ?
            WHERE goal_id = ?
        ''', (status.value, completed_at, goal_id))

        self.conn.commit()

        logger.info(f"Updated goal {goal_id} status to {status.value}")

        return self.get_goal(goal_id)

    def update_goal_progress(self, goal_id: str, current_value: float):
        """
        Update goal progress

        Args:
            goal_id: Goal identifier
            current_value: New current value
        """
        goal = self.get_goal(goal_id)
        if not goal:
            raise ValueError(f"Goal {goal_id} not found")

        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE goals
            SET current_value = ?
            WHERE goal_id = ?
        ''', (current_value, goal_id))

        self.conn.commit()

        # Check for milestone achievement
        self._check_milestones(goal_id, current_value, goal.target_value)

        # Auto-complete if target reached
        if current_value >= goal.target_value:
            self.update_goal_status(goal_id, GoalStatus.COMPLETED)
            logger.info(f"Goal {goal_id} auto-completed (target reached)")

    def _check_milestones(self, goal_id: str, current_value: float, target_value: float):
        """Check and create milestones for progress"""
        if target_value == 0:
            return

        progress_pct = min(100, (current_value / target_value) * 100)

        # Milestone thresholds
        thresholds = [25, 50, 75, 100]

        for threshold in thresholds:
            if progress_pct >= threshold:
                # Check if milestone already exists
                cursor = self.conn.cursor()
                cursor.execute('''
                    SELECT milestone_id FROM milestones
                    WHERE goal_id = ? AND milestone_type = ?
                ''', (goal_id, f"{threshold}%"))

                if not cursor.fetchone():
                    # Create milestone
                    self.create_milestone(
                        goal_id=goal_id,
                        milestone_type=f"{threshold}%",
                        description=f"Reached {threshold}% progress",
                        achieved_at=datetime.now().timestamp()
                    )

    def create_milestone(
        self,
        goal_id: str,
        milestone_type: str,
        description: str,
        achieved_at: float
    ) -> Milestone:
        """
        Create a milestone

        Args:
            goal_id: Goal identifier
            milestone_type: Type of milestone
            description: Description
            achieved_at: Achievement timestamp

        Returns:
            Milestone object
        """
        milestone_id = str(uuid.uuid4())

        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO milestones (
                milestone_id, goal_id, milestone_type, description, achieved_at
            ) VALUES (?, ?, ?, ?, ?)
        ''', (milestone_id, goal_id, milestone_type, description, achieved_at))

        self.conn.commit()

        logger.debug(f"Created milestone {milestone_id} for goal {goal_id}")

        return Milestone(
            milestone_id=milestone_id,
            goal_id=goal_id,
            milestone_type=milestone_type,
            description=description,
            achieved_at=achieved_at
        )

    def get_goal_milestones(self, goal_id: str) -> List[Milestone]:
        """
        Get all milestones for a goal

        Args:
            goal_id: Goal identifier

        Returns:
            List of Milestone objects
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM milestones
            WHERE goal_id = ?
            ORDER BY achieved_at ASC
        ''', (goal_id,))

        rows = cursor.fetchall()
        milestones = []

        for row in rows:
            milestones.append(Milestone(
                milestone_id=row[0],
                goal_id=row[1],
                milestone_type=row[2],
                description=row[3],
                achieved_at=row[4]
            ))

        return milestones

    def calculate_progress(self, goal_id: str, include_time: bool = False) -> Dict:
        """
        Calculate progress toward goal

        Args:
            goal_id: Goal identifier
            include_time: Whether to include time-based progress

        Returns:
            Dict with progress information
        """
        goal = self.get_goal(goal_id)
        if not goal:
            return {}

        # Value-based progress
        percentage = min(100, int((goal.current_value / goal.target_value) * 100))

        progress = {
            "percentage": percentage,
            "current": goal.current_value,
            "target": goal.target_value,
            "remaining": max(0, goal.target_value - goal.current_value)
        }

        # Time-based progress
        if include_time and goal.deadline:
            now = datetime.now().timestamp()
            total_time = goal.deadline - goal.created_at
            elapsed_time = now - goal.created_at

            if total_time > 0:
                time_progress = min(100, int((elapsed_time / total_time) * 100))
                progress["time_progress"] = time_progress

        return progress

    def recommend_goals(self, student_id: str) -> List[Dict]:
        """
        Recommend goals based on learning patterns

        Args:
            student_id: Student identifier

        Returns:
            List of goal recommendation dicts
        """
        if not self.pattern_tracker:
            return []

        recommendations = []

        # Check velocity
        velocity = self.pattern_tracker.calculate_learning_velocity(student_id)
        if velocity and velocity.concepts_per_session > 0:
            recommendations.append({
                "type": "velocity",
                "title": f"Learn {int(velocity.concepts_per_session * 7)} concepts per week",
                "target_value": velocity.concepts_per_session * 7,
                "goal_type": GoalType.VELOCITY
            })

        # Check accuracy
        try:
            cursor = self.pattern_tracker.conn.cursor()
            cursor.execute('''
                SELECT AVG(CAST(questions_correct AS REAL) / NULLIF(questions_asked, 0))
                FROM sessions
                WHERE student_id = ? AND questions_asked > 0
                LIMIT 10
            ''', (student_id,))

            row = cursor.fetchone()
            if row and row[0]:
                avg_accuracy = row[0]
                if avg_accuracy < 0.8:
                    target = max(0.8, avg_accuracy + 0.1)
                    recommendations.append({
                        "type": "accuracy",
                        "title": f"Achieve {int(target * 100)}% accuracy",
                        "target_value": target,
                        "goal_type": GoalType.ACCURACY
                    })
        except Exception as e:
            logger.warning(f"Error checking accuracy: {e}")

        # Check consistency
        consistency = self.pattern_tracker.calculate_consistency_score(student_id, days=7)
        if consistency is not None and consistency < 0.7:
            recommendations.append({
                "type": "consistency",
                "title": "Practice 5 days per week",
                "target_value": 5,
                "goal_type": GoalType.CONSISTENCY
            })

        return recommendations

    def award_achievement(
        self,
        student_id: str,
        achievement_type: str,
        title: str,
        description: str
    ) -> Optional[Achievement]:
        """
        Award achievement to student

        Args:
            student_id: Student identifier
            achievement_type: Type of achievement
            title: Achievement title
            description: Achievement description

        Returns:
            Achievement object or None if already awarded
        """
        # Check if already awarded
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT achievement_id FROM achievements
            WHERE student_id = ? AND achievement_type = ?
        ''', (student_id, achievement_type))

        if cursor.fetchone():
            logger.debug(f"Achievement {achievement_type} already awarded to {student_id}")
            return None

        achievement_id = str(uuid.uuid4())
        awarded_at = datetime.now().timestamp()

        cursor.execute('''
            INSERT INTO achievements (
                achievement_id, student_id, achievement_type, title, description, awarded_at
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (achievement_id, student_id, achievement_type, title, description, awarded_at))

        self.conn.commit()

        logger.info(f"Awarded achievement {achievement_type} to student {student_id}")

        return Achievement(
            achievement_id=achievement_id,
            student_id=student_id,
            achievement_type=achievement_type,
            title=title,
            description=description,
            awarded_at=awarded_at
        )

    def get_student_achievements(self, student_id: str) -> List[Achievement]:
        """
        Get all achievements for a student

        Args:
            student_id: Student identifier

        Returns:
            List of Achievement objects
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM achievements
            WHERE student_id = ?
            ORDER BY awarded_at DESC
        ''', (student_id,))

        rows = cursor.fetchall()
        achievements = []

        for row in rows:
            achievements.append(Achievement(
                achievement_id=row[0],
                student_id=row[1],
                achievement_type=row[2],
                title=row[3],
                description=row[4],
                awarded_at=row[5]
            ))

        return achievements
