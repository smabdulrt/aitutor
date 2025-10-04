"""
Learning Pattern Tracker for Cross-Session Analytics

This module tracks and analyzes learning patterns across multiple sessions:
1. Time-of-day performance patterns
2. Session length and focus patterns
3. Learning velocity (concepts per session)
4. Error patterns and recovery time
5. Cross-session retention and spacing
"""

import sqlite3
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import logging
import json
import uuid
import statistics

logger = logging.getLogger(__name__)


@dataclass
class TimeOfDayPattern:
    """Time-of-day performance pattern"""
    best_time_range: Optional[Tuple[int, int]]  # (start_hour, end_hour)
    worst_time_range: Optional[Tuple[int, int]]
    hourly_performance: Dict[int, float]  # hour -> avg performance
    sample_size: int


@dataclass
class SessionPattern:
    """Session length and focus pattern"""
    optimal_duration_minutes: Optional[int]
    focus_degradation_point: Optional[int]  # Minutes into session
    average_session_length: float
    performance_by_duration: Dict[str, float]  # duration_range -> performance


@dataclass
class LearningVelocity:
    """Learning velocity metrics"""
    concepts_per_session: float
    mastery_rate: float  # Fraction of concepts mastered
    trend: str  # "accelerating", "stable", "decelerating"
    weekly_velocity: List[float]


@dataclass
class ErrorPattern:
    """Error pattern analysis"""
    most_common_errors: List[Dict]  # [{concept, count, type}]
    average_recovery_time: Optional[float]  # Seconds
    error_clusters: List[str]  # Concepts with repeated errors


@dataclass
class PatternInsight:
    """Actionable insight from patterns"""
    insight_type: str
    message: str
    priority: int  # 1-5, higher is more important
    data: Dict


class LearningPatternTracker:
    """
    Track and analyze learning patterns across sessions
    """

    def __init__(self, db_path: str = "./learning_patterns.db"):
        """
        Initialize learning pattern tracker

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_database()

        logger.info(f"Learning pattern tracker initialized at {db_path}")

    def _init_database(self):
        """Initialize database schema"""
        cursor = self.conn.cursor()

        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                student_id TEXT NOT NULL,
                start_time REAL NOT NULL,
                end_time REAL NOT NULL,
                concepts_covered TEXT,
                concepts_mastered TEXT,
                questions_asked INTEGER DEFAULT 0,
                questions_correct INTEGER DEFAULT 0,
                engagement_score REAL,
                retention_quiz_score REAL,
                metadata TEXT
            )
        ''')

        # Errors table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS errors (
                error_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                student_id TEXT NOT NULL,
                concept TEXT NOT NULL,
                error_type TEXT,
                timestamp REAL NOT NULL,
                recovered_at REAL,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        ''')

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_student ON sessions(student_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_errors_student ON errors(student_id)')

        self.conn.commit()
        logger.debug("Database schema initialized")

    def record_session(
        self,
        student_id: str,
        start_time: float,
        end_time: float,
        concepts_covered: Optional[List[str]] = None,
        concepts_mastered: Optional[List[str]] = None,
        questions_asked: int = 0,
        questions_correct: int = 0,
        engagement_score: Optional[float] = None,
        retention_quiz_score: Optional[float] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Record a learning session

        Args:
            student_id: Student identifier
            start_time: Session start timestamp
            end_time: Session end timestamp
            concepts_covered: List of concepts covered
            concepts_mastered: List of concepts mastered
            questions_asked: Number of questions asked
            questions_correct: Number of correct answers
            engagement_score: Engagement score (0-1)
            retention_quiz_score: Retention quiz score (0-1)
            metadata: Additional metadata

        Returns:
            Session ID

        Raises:
            ValueError: If session times invalid or scores out of range
        """
        if end_time <= start_time:
            raise ValueError("Session end time must be after start time")

        if engagement_score is not None and (engagement_score < 0 or engagement_score > 1):
            raise ValueError("Engagement score must be between 0 and 1")

        session_id = str(uuid.uuid4())

        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO sessions (
                session_id, student_id, start_time, end_time,
                concepts_covered, concepts_mastered, questions_asked,
                questions_correct, engagement_score, retention_quiz_score, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            student_id,
            start_time,
            end_time,
            json.dumps(concepts_covered) if concepts_covered else None,
            json.dumps(concepts_mastered) if concepts_mastered else None,
            questions_asked,
            questions_correct,
            engagement_score,
            retention_quiz_score,
            json.dumps(metadata) if metadata else None
        ))

        self.conn.commit()
        logger.debug(f"Recorded session {session_id} for student {student_id}")
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict]:
        """
        Get session data

        Args:
            session_id: Session identifier

        Returns:
            Session data dict or None
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM sessions WHERE session_id = ?', (session_id,))
        row = cursor.fetchone()

        if not row:
            return None

        return {
            "session_id": row[0],
            "student_id": row[1],
            "start_time": row[2],
            "end_time": row[3],
            "concepts_covered": json.loads(row[4]) if row[4] else [],
            "concepts_mastered": json.loads(row[5]) if row[5] else [],
            "questions_asked": row[6],
            "questions_correct": row[7],
            "engagement_score": row[8],
            "retention_quiz_score": row[9],
            "metadata": json.loads(row[10]) if row[10] else {}
        }

    def record_error(
        self,
        session_id: str,
        student_id: str,
        concept: str,
        error_type: str,
        timestamp: float,
        recovered_at: Optional[float] = None
    ) -> str:
        """
        Record an error during a session

        Args:
            session_id: Session identifier
            student_id: Student identifier
            concept: Concept with error
            error_type: Type of error
            timestamp: Error timestamp
            recovered_at: Optional recovery timestamp

        Returns:
            Error ID
        """
        error_id = str(uuid.uuid4())

        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO errors (
                error_id, session_id, student_id, concept,
                error_type, timestamp, recovered_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (error_id, session_id, student_id, concept, error_type, timestamp, recovered_at))

        self.conn.commit()
        logger.debug(f"Recorded error {error_id} in session {session_id}")
        return error_id

    def get_session_errors(self, session_id: str) -> List[Dict]:
        """
        Get all errors for a session

        Args:
            session_id: Session identifier

        Returns:
            List of error dicts
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM errors WHERE session_id = ?', (session_id,))
        rows = cursor.fetchall()

        errors = []
        for row in rows:
            errors.append({
                "error_id": row[0],
                "session_id": row[1],
                "student_id": row[2],
                "concept": row[3],
                "error_type": row[4],
                "timestamp": row[5],
                "recovered_at": row[6]
            })

        return errors

    def analyze_time_of_day_patterns(self, student_id: str) -> Optional[TimeOfDayPattern]:
        """
        Analyze performance by time of day

        Args:
            student_id: Student identifier

        Returns:
            TimeOfDayPattern or None if insufficient data
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT start_time, questions_asked, questions_correct, engagement_score
            FROM sessions
            WHERE student_id = ? AND questions_asked > 0
        ''', (student_id,))

        rows = cursor.fetchall()

        if len(rows) < 1:
            return TimeOfDayPattern(
                best_time_range=None,
                worst_time_range=None,
                hourly_performance={},
                sample_size=len(rows)
            )

        # Group by hour
        hourly_data = {}
        for row in rows:
            start_time, asked, correct, engagement = row
            hour = datetime.fromtimestamp(start_time).hour

            if hour not in hourly_data:
                hourly_data[hour] = []

            # Calculate performance score
            accuracy = correct / asked if asked > 0 else 0
            engagement_val = engagement if engagement else 0.5
            performance = (accuracy + engagement_val) / 2

            hourly_data[hour].append(performance)

        # Calculate average performance per hour
        hourly_performance = {}
        for hour, scores in hourly_data.items():
            hourly_performance[hour] = statistics.mean(scores)

        # Find best and worst time ranges
        if hourly_performance:
            sorted_hours = sorted(hourly_performance.items(), key=lambda x: x[1], reverse=True)
            best_hour = sorted_hours[0][0]
            worst_hour = sorted_hours[-1][0]

            # Create 2-hour ranges
            best_range = (max(0, best_hour - 1), min(23, best_hour + 1))
            worst_range = (max(0, worst_hour - 1), min(23, worst_hour + 1))
        else:
            best_range = None
            worst_range = None

        return TimeOfDayPattern(
            best_time_range=best_range,
            worst_time_range=worst_range,
            hourly_performance=hourly_performance,
            sample_size=len(rows)
        )

    def analyze_session_length_patterns(self, student_id: str) -> Optional[SessionPattern]:
        """
        Analyze optimal session length

        Args:
            student_id: Student identifier

        Returns:
            SessionPattern or None
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT start_time, end_time, questions_asked, questions_correct, engagement_score
            FROM sessions
            WHERE student_id = ?
        ''', (student_id,))

        rows = cursor.fetchall()

        if len(rows) < 1:
            return SessionPattern(
                optimal_duration_minutes=None,
                focus_degradation_point=None,
                average_session_length=0,
                performance_by_duration={}
            )

        # Analyze by duration
        duration_buckets = {"0-30": [], "30-60": [], "60-90": [], "90+": []}
        durations = []

        for row in rows:
            start, end, asked, correct, engagement = row
            duration_min = (end - start) / 60
            durations.append(duration_min)

            # Calculate performance
            accuracy = correct / asked if asked > 0 else 0
            engagement_val = engagement if engagement else 0.5
            performance = (accuracy + engagement_val) / 2

            # Bucket by duration
            if duration_min <= 30:
                duration_buckets["0-30"].append(performance)
            elif duration_min <= 60:
                duration_buckets["30-60"].append(performance)
            elif duration_min <= 90:
                duration_buckets["60-90"].append(performance)
            else:
                duration_buckets["90+"].append(performance)

        # Calculate average performance by duration
        performance_by_duration = {}
        for bucket, scores in duration_buckets.items():
            if scores:
                performance_by_duration[bucket] = statistics.mean(scores)

        # Find optimal duration
        if performance_by_duration:
            best_bucket = max(performance_by_duration.items(), key=lambda x: x[1])[0]
            if best_bucket == "0-30":
                optimal_duration = 25
            elif best_bucket == "30-60":
                optimal_duration = 45
            elif best_bucket == "60-90":
                optimal_duration = 75
            else:
                optimal_duration = 60  # Default
        else:
            optimal_duration = None

        # Detect focus degradation (when performance drops in longer sessions)
        focus_point = None
        if "60-90" in performance_by_duration and "90+" in performance_by_duration:
            if performance_by_duration["90+"] < performance_by_duration["60-90"] * 0.8:
                focus_point = 75  # Degrades after 75 min
        elif "90+" in performance_by_duration and performance_by_duration["90+"] < 0.6:
            # Single long session with low performance
            focus_point = 60  # Likely degraded around 60 min

        return SessionPattern(
            optimal_duration_minutes=optimal_duration,
            focus_degradation_point=focus_point,
            average_session_length=statistics.mean(durations) if durations else 0,
            performance_by_duration=performance_by_duration
        )

    def calculate_learning_velocity(self, student_id: str) -> Optional[LearningVelocity]:
        """
        Calculate learning velocity

        Args:
            student_id: Student identifier

        Returns:
            LearningVelocity or None
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT concepts_covered, concepts_mastered, start_time
            FROM sessions
            WHERE student_id = ? AND concepts_covered IS NOT NULL
            ORDER BY start_time ASC
        ''', (student_id,))

        rows = cursor.fetchall()

        if len(rows) < 2:
            return LearningVelocity(
                concepts_per_session=0,
                mastery_rate=0,
                trend="stable",
                weekly_velocity=[]
            )

        total_concepts = 0
        total_mastered = 0
        weekly_concepts = []
        current_week_concepts = 0
        current_week_start = None

        for row in rows:
            covered = json.loads(row[0]) if row[0] else []
            mastered = json.loads(row[1]) if row[1] else []
            timestamp = row[2]

            total_concepts += len(covered)
            total_mastered += len(mastered)

            # Track weekly velocity
            session_date = datetime.fromtimestamp(timestamp)
            if current_week_start is None:
                current_week_start = session_date

            days_diff = (session_date - current_week_start).days
            if days_diff >= 7:
                weekly_concepts.append(current_week_concepts)
                current_week_concepts = len(covered)
                current_week_start = session_date
            else:
                current_week_concepts += len(covered)

        if current_week_concepts > 0:
            weekly_concepts.append(current_week_concepts)

        # Calculate metrics
        concepts_per_session = total_concepts / len(rows) if rows else 0
        mastery_rate = total_mastered / total_concepts if total_concepts > 0 else 0

        # Detect trend
        if len(weekly_concepts) >= 2:
            first_half_avg = statistics.mean(weekly_concepts[:len(weekly_concepts)//2])
            second_half_avg = statistics.mean(weekly_concepts[len(weekly_concepts)//2:])

            if second_half_avg > first_half_avg * 1.2:
                trend = "accelerating"
            elif second_half_avg < first_half_avg * 0.8:
                trend = "decelerating"
            else:
                trend = "stable"
        else:
            trend = "stable"

        return LearningVelocity(
            concepts_per_session=concepts_per_session,
            mastery_rate=mastery_rate,
            trend=trend,
            weekly_velocity=weekly_concepts
        )

    def analyze_error_patterns(self, student_id: str) -> Optional[ErrorPattern]:
        """
        Analyze error patterns

        Args:
            student_id: Student identifier

        Returns:
            ErrorPattern or None
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT concept, error_type, timestamp, recovered_at
            FROM errors
            WHERE student_id = ?
        ''', (student_id,))

        rows = cursor.fetchall()

        if not rows:
            return ErrorPattern(
                most_common_errors=[],
                average_recovery_time=None,
                error_clusters=[]
            )

        # Count errors by concept and type
        error_counts = {}
        recovery_times = []

        for row in rows:
            concept, error_type, timestamp, recovered_at = row

            key = f"{concept}:{error_type}"
            error_counts[key] = error_counts.get(key, 0) + 1

            if recovered_at:
                recovery_times.append(recovered_at - timestamp)

        # Most common errors
        most_common = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        most_common_errors = []
        for key, count in most_common:
            concept, error_type = key.split(":", 1)
            most_common_errors.append({
                "concept": concept,
                "type": error_type,
                "count": count
            })

        # Average recovery time
        avg_recovery = statistics.mean(recovery_times) if recovery_times else None

        # Error clusters (concepts with 3+ errors)
        concept_counts = {}
        for row in rows:
            concept = row[0]
            concept_counts[concept] = concept_counts.get(concept, 0) + 1

        error_clusters = [c for c, count in concept_counts.items() if count >= 3]

        return ErrorPattern(
            most_common_errors=most_common_errors,
            average_recovery_time=avg_recovery,
            error_clusters=error_clusters
        )

    def analyze_concept_retention(self, student_id: str, concept: str) -> Optional[float]:
        """
        Analyze retention of a concept across sessions

        Args:
            student_id: Student identifier
            concept: Concept to analyze

        Returns:
            Retention score (0-1) or None
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT retention_quiz_score
            FROM sessions
            WHERE student_id = ? AND concepts_covered LIKE ?
            AND retention_quiz_score IS NOT NULL
            ORDER BY start_time DESC
            LIMIT 1
        ''', (student_id, f'%"{concept}"%'))

        row = cursor.fetchone()
        return row[0] if row else None

    def analyze_session_spacing(self, student_id: str) -> Optional[Dict]:
        """
        Analyze optimal spacing between sessions

        Args:
            student_id: Student identifier

        Returns:
            Dict with spacing analysis or None
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT start_time, engagement_score
            FROM sessions
            WHERE student_id = ?
            ORDER BY start_time ASC
        ''', (student_id,))

        rows = cursor.fetchall()

        if len(rows) < 3:
            return None

        gaps_and_performance = []
        for i in range(1, len(rows)):
            prev_time = rows[i-1][0]
            curr_time = rows[i][0]
            curr_engagement = rows[i][1]

            gap_days = (curr_time - prev_time) / (24 * 3600)

            if curr_engagement is not None:
                gaps_and_performance.append((gap_days, curr_engagement))

        if not gaps_and_performance:
            return None

        # Find optimal gap
        gap_buckets = {"0-1": [], "1-3": [], "3-7": [], "7+": []}
        for gap, perf in gaps_and_performance:
            if gap <= 1:
                gap_buckets["0-1"].append(perf)
            elif gap <= 3:
                gap_buckets["1-3"].append(perf)
            elif gap <= 7:
                gap_buckets["3-7"].append(perf)
            else:
                gap_buckets["7+"].append(perf)

        # Find best bucket
        best_gap = None
        best_perf = 0
        for bucket, scores in gap_buckets.items():
            if scores:
                avg = statistics.mean(scores)
                if avg > best_perf:
                    best_perf = avg
                    best_gap = bucket

        # Convert to days
        gap_map = {"0-1": 0.5, "1-3": 2, "3-7": 5, "7+": 7}
        optimal_gap_days = gap_map.get(best_gap, 2)

        return {
            "optimal_gap_days": optimal_gap_days,
            "gap_performance": {k: statistics.mean(v) if v else 0 for k, v in gap_buckets.items()}
        }

    def calculate_consistency_score(self, student_id: str, days: int = 7) -> Optional[float]:
        """
        Calculate consistency of learning sessions

        Args:
            student_id: Student identifier
            days: Number of days to analyze

        Returns:
            Consistency score (0-1) or None
        """
        cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)

        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT start_time
            FROM sessions
            WHERE student_id = ? AND start_time >= ?
            ORDER BY start_time ASC
        ''', (student_id, cutoff_time))

        rows = cursor.fetchall()

        if not rows:
            return 0.0

        # Count sessions per day
        session_days = set()
        for row in rows:
            day = datetime.fromtimestamp(row[0]).date()
            session_days.add(day)

        # Consistency = (days with sessions) / total days
        consistency = len(session_days) / days
        return min(1.0, consistency)

    def generate_insights(self, student_id: str) -> List[PatternInsight]:
        """
        Generate actionable insights from patterns

        Args:
            student_id: Student identifier

        Returns:
            List of PatternInsight objects
        """
        insights = []

        # Time of day insights
        time_patterns = self.analyze_time_of_day_patterns(student_id)
        if time_patterns and time_patterns.best_time_range:
            insights.append(PatternInsight(
                insight_type="time_of_day",
                message=f"Best performance between {time_patterns.best_time_range[0]}:00-{time_patterns.best_time_range[1]}:00",
                priority=4,
                data={"best_time": time_patterns.best_time_range}
            ))

        # Session length insights
        session_patterns = self.analyze_session_length_patterns(student_id)
        if session_patterns and session_patterns.optimal_duration_minutes:
            insights.append(PatternInsight(
                insight_type="session_length",
                message=f"Optimal session length: {session_patterns.optimal_duration_minutes} minutes",
                priority=3,
                data={"optimal_duration": session_patterns.optimal_duration_minutes}
            ))

        # Engagement insights
        if session_patterns and session_patterns.average_session_length > 0:
            latest_engagement = self._get_latest_engagement(student_id)
            if latest_engagement and latest_engagement < 0.5:
                insights.append(PatternInsight(
                    insight_type="engagement",
                    message="Recent engagement is low - consider shorter sessions or breaks",
                    priority=5,
                    data={"engagement": latest_engagement}
                ))

        # Learning velocity insights
        velocity = self.calculate_learning_velocity(student_id)
        if velocity and velocity.trend == "accelerating":
            insights.append(PatternInsight(
                insight_type="velocity",
                message="Learning velocity is accelerating - great progress!",
                priority=2,
                data={"trend": velocity.trend}
            ))

        # Sort by priority (descending)
        insights.sort(key=lambda x: x.priority, reverse=True)

        return insights

    def _get_latest_engagement(self, student_id: str) -> Optional[float]:
        """Get most recent engagement score"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT engagement_score
            FROM sessions
            WHERE student_id = ? AND engagement_score IS NOT NULL
            ORDER BY start_time DESC
            LIMIT 1
        ''', (student_id,))

        row = cursor.fetchone()
        return row[0] if row else None
