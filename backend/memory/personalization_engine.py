"""
Personalization Engine for Adaptive Learning

This module uses accumulated memory data to personalize the tutoring experience:
1. Explanation style adaptation (visual/verbal/kinesthetic)
2. Difficulty calibration using performance history
3. Example selection based on student interests
4. Pacing adjustment from session patterns
5. Learning path optimization
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import logging
from backend.memory.student_notes import StudentNotes, NoteCategory
from backend.memory.learning_pattern_tracker import LearningPatternTracker
from backend.memory.enhanced_vector_store import EnhancedVectorStore, VectorType

logger = logging.getLogger(__name__)


class ExplanationStyle(str, Enum):
    """Types of explanation styles"""
    VISUAL = "visual"
    VERBAL = "verbal"
    KINESTHETIC = "kinesthetic"
    MIXED = "mixed"


class DifficultyLevel(str, Enum):
    """Difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class PersonalizationProfile:
    """Complete personalization profile for a student"""
    student_id: str
    preferred_explanation_style: ExplanationStyle
    current_difficulty_level: DifficultyLevel
    interests: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    optimal_session_duration: Optional[int] = None
    best_time_range: Optional[Tuple[int, int]] = None


@dataclass
class LearningRecommendation:
    """Personalized learning recommendation"""
    recommendation_type: str
    message: str
    priority: int  # 1-5, higher is more important
    data: Dict


class PersonalizationEngine:
    """
    Engine for personalizing the learning experience based on accumulated memory
    """

    def __init__(
        self,
        student_notes: Optional[StudentNotes] = None,
        pattern_tracker: Optional[LearningPatternTracker] = None,
        vector_store: Optional[EnhancedVectorStore] = None
    ):
        """
        Initialize personalization engine

        Args:
            student_notes: StudentNotes instance
            pattern_tracker: LearningPatternTracker instance
            vector_store: EnhancedVectorStore instance
        """
        self.student_notes = student_notes
        self.pattern_tracker = pattern_tracker
        self.vector_store = vector_store

        logger.info("Personalization engine initialized")

    def get_personalization_profile(self, student_id: str) -> PersonalizationProfile:
        """
        Get complete personalization profile for student

        Args:
            student_id: Student identifier

        Returns:
            PersonalizationProfile
        """
        # Detect explanation style
        explanation_style = self._detect_explanation_style(student_id)

        # Calibrate difficulty
        difficulty_level = self._calibrate_difficulty(student_id)

        # Extract interests, strengths, weaknesses
        interests = self._extract_interests(student_id)
        strengths = self._extract_strengths(student_id)
        weaknesses = self._extract_weaknesses(student_id)

        # Get optimal pacing
        pacing = self.recommend_pacing(student_id)
        optimal_duration = pacing.get("session_duration") if pacing else None
        best_time = pacing.get("best_time_range") if pacing else None

        profile = PersonalizationProfile(
            student_id=student_id,
            preferred_explanation_style=explanation_style,
            current_difficulty_level=difficulty_level,
            interests=interests,
            strengths=strengths,
            weaknesses=weaknesses,
            optimal_session_duration=optimal_duration,
            best_time_range=best_time
        )

        logger.debug(f"Generated profile for {student_id}: {explanation_style}, {difficulty_level}")
        return profile

    def _detect_explanation_style(self, student_id: str) -> ExplanationStyle:
        """
        Detect preferred explanation style from notes

        Args:
            student_id: Student identifier

        Returns:
            ExplanationStyle
        """
        if not self.student_notes:
            return ExplanationStyle.MIXED

        # Get learning preference notes
        notes = self.student_notes.get_notes_by_category(
            student_id,
            NoteCategory.LEARNING_PREFERENCE
        )

        if not notes:
            return ExplanationStyle.MIXED

        # Analyze content for style keywords
        visual_keywords = ["visual", "diagram", "chart", "picture", "graph", "drawing", "image"]
        verbal_keywords = ["verbal", "discussion", "explanation", "talking", "speaking", "reading"]
        kinesthetic_keywords = ["hands-on", "practice", "doing", "interactive", "physical"]

        visual_count = 0
        verbal_count = 0
        kinesthetic_count = 0

        for note in notes:
            content_lower = note.content.lower()
            visual_count += sum(1 for kw in visual_keywords if kw in content_lower)
            verbal_count += sum(1 for kw in verbal_keywords if kw in content_lower)
            kinesthetic_count += sum(1 for kw in kinesthetic_keywords if kw in content_lower)

        # Determine dominant style
        max_count = max(visual_count, verbal_count, kinesthetic_count)

        if max_count == 0:
            return ExplanationStyle.MIXED

        if visual_count == max_count:
            return ExplanationStyle.VISUAL
        elif verbal_count == max_count:
            return ExplanationStyle.VERBAL
        elif kinesthetic_count == max_count:
            return ExplanationStyle.KINESTHETIC
        else:
            return ExplanationStyle.MIXED

    def _calibrate_difficulty(self, student_id: str) -> DifficultyLevel:
        """
        Calibrate difficulty level from performance history

        Args:
            student_id: Student identifier

        Returns:
            DifficultyLevel
        """
        if not self.pattern_tracker:
            return DifficultyLevel.BEGINNER

        # Get recent sessions
        try:
            cursor = self.pattern_tracker.conn.cursor()
            cursor.execute('''
                SELECT questions_asked, questions_correct, engagement_score
                FROM sessions
                WHERE student_id = ? AND questions_asked > 0
                ORDER BY start_time DESC
                LIMIT 10
            ''', (student_id,))

            rows = cursor.fetchall()

            if not rows:
                return DifficultyLevel.BEGINNER

            # Calculate average performance
            total_accuracy = 0
            total_engagement = 0
            count = 0

            for row in rows:
                asked, correct, engagement = row
                accuracy = correct / asked if asked > 0 else 0
                engagement_val = engagement if engagement else 0.5

                total_accuracy += accuracy
                total_engagement += engagement_val
                count += 1

            avg_accuracy = total_accuracy / count if count > 0 else 0
            avg_engagement = total_engagement / count if count > 0 else 0

            # Combined performance score
            performance = (avg_accuracy + avg_engagement) / 2

            # Calibrate difficulty
            if performance >= 0.85:
                return DifficultyLevel.EXPERT
            elif performance >= 0.70:
                return DifficultyLevel.ADVANCED
            elif performance >= 0.50:
                return DifficultyLevel.INTERMEDIATE
            else:
                return DifficultyLevel.BEGINNER

        except Exception as e:
            logger.warning(f"Error calibrating difficulty: {e}")
            return DifficultyLevel.BEGINNER

    def recommend_difficulty_adjustment(self, student_id: str) -> str:
        """
        Recommend difficulty adjustment

        Args:
            student_id: Student identifier

        Returns:
            "increase", "maintain", or "decrease"
        """
        if not self.pattern_tracker:
            return "maintain"

        try:
            cursor = self.pattern_tracker.conn.cursor()
            cursor.execute('''
                SELECT questions_asked, questions_correct, engagement_score
                FROM sessions
                WHERE student_id = ? AND questions_asked > 0
                ORDER BY start_time DESC
                LIMIT 5
            ''', (student_id,))

            rows = cursor.fetchall()

            if len(rows) < 3:
                return "maintain"

            # Calculate recent performance
            performances = []
            for row in rows:
                asked, correct, engagement = row
                accuracy = correct / asked if asked > 0 else 0
                engagement_val = engagement if engagement else 0.5
                performance = (accuracy + engagement_val) / 2
                performances.append(performance)

            avg_performance = sum(performances) / len(performances)

            # Recommend based on performance
            if avg_performance >= 0.85:
                return "increase"
            elif avg_performance < 0.50:
                return "decrease"
            else:
                return "maintain"

        except Exception as e:
            logger.warning(f"Error recommending difficulty: {e}")
            return "maintain"

    def _extract_interests(self, student_id: str) -> List[str]:
        """Extract student interests from notes"""
        if not self.student_notes:
            return []

        notes = self.student_notes.get_notes_by_category(
            student_id,
            NoteCategory.PERSONAL_CONTEXT
        )

        interests = []
        for note in notes:
            if "interest" in note.content.lower() or "like" in note.content.lower() or "love" in note.content.lower():
                # Extract keywords (simplified)
                words = note.content.lower().split()
                for i, word in enumerate(words):
                    if word in ["basketball", "sports", "music", "art", "science", "games", "reading"]:
                        if word not in interests:
                            interests.append(word)

        return interests

    def _extract_strengths(self, student_id: str) -> List[str]:
        """Extract student strengths from notes"""
        if not self.student_notes:
            return []

        notes = self.student_notes.get_notes_by_category(
            student_id,
            NoteCategory.STRONG_TOPIC
        )

        return [note.topic for note in notes if note.topic]

    def _extract_weaknesses(self, student_id: str) -> List[str]:
        """Extract student weaknesses from notes"""
        if not self.student_notes:
            return []

        notes = self.student_notes.get_notes_by_category(
            student_id,
            NoteCategory.WEAK_TOPIC
        )

        return [note.topic for note in notes if note.topic]

    def select_examples(
        self,
        student_id: str,
        topic: str,
        count: int = 3
    ) -> List[str]:
        """
        Select examples based on student interests

        Args:
            student_id: Student identifier
            topic: Topic to find examples for
            count: Number of examples to return

        Returns:
            List of example strings
        """
        if not self.vector_store:
            return []

        # Get student interests
        interests = self._extract_interests(student_id)

        # Search for examples matching interests and topic
        examples = []

        try:
            # Try interest-based search first
            for interest in interests[:2]:  # Top 2 interests
                results = self.vector_store.search(
                    query=f"{topic} {interest}",
                    student_id=student_id,
                    vector_type=VectorType.EXAMPLE,
                    limit=count
                )

                for result in results:
                    if result.content not in examples:
                        examples.append(result.content)

                if len(examples) >= count:
                    break

            # Fill remaining with topic-based examples
            if len(examples) < count:
                results = self.vector_store.search(
                    query=topic,
                    student_id=student_id,
                    vector_type=VectorType.EXAMPLE,
                    limit=count - len(examples)
                )

                for result in results:
                    if result.content not in examples:
                        examples.append(result.content)

        except Exception as e:
            logger.warning(f"Error selecting examples: {e}")

        return examples[:count]

    def recommend_pacing(self, student_id: str) -> Dict:
        """
        Recommend pacing adjustments

        Args:
            student_id: Student identifier

        Returns:
            Dict with pacing recommendations
        """
        if not self.pattern_tracker:
            return {}

        pacing = {}

        # Optimal session duration
        try:
            session_patterns = self.pattern_tracker.analyze_session_length_patterns(student_id)
            if session_patterns and session_patterns.optimal_duration_minutes:
                pacing["session_duration"] = session_patterns.optimal_duration_minutes

                # Break frequency based on focus degradation
                if session_patterns.focus_degradation_point:
                    pacing["break_frequency"] = session_patterns.focus_degradation_point
                else:
                    pacing["break_frequency"] = session_patterns.optimal_duration_minutes // 2
        except Exception as e:
            logger.warning(f"Error analyzing session patterns: {e}")

        # Best time of day
        try:
            time_patterns = self.pattern_tracker.analyze_time_of_day_patterns(student_id)
            if time_patterns and time_patterns.best_time_range:
                pacing["best_time_range"] = time_patterns.best_time_range
        except Exception as e:
            logger.warning(f"Error analyzing time patterns: {e}")

        return pacing

    def identify_knowledge_gaps(self, student_id: str) -> List[Dict]:
        """
        Identify knowledge gaps from misconceptions and weak topics

        Args:
            student_id: Student identifier

        Returns:
            List of knowledge gap dicts
        """
        if not self.student_notes:
            return []

        gaps = []

        # Get misconceptions
        misconceptions = self.student_notes.get_notes_by_category(
            student_id,
            NoteCategory.MISCONCEPTION
        )

        for note in misconceptions:
            gaps.append({
                "type": "misconception",
                "topic": note.topic,
                "description": note.content,
                "priority": "high"
            })

        # Get weak topics
        weak_topics = self.student_notes.get_notes_by_category(
            student_id,
            NoteCategory.WEAK_TOPIC
        )

        for note in weak_topics:
            gaps.append({
                "type": "weak_topic",
                "topic": note.topic,
                "description": note.content,
                "priority": "medium"
            })

        return gaps

    def recommend_next_topics(self, student_id: str, count: int = 3) -> List[str]:
        """
        Recommend next topics to study

        Args:
            student_id: Student identifier
            count: Number of topics to recommend

        Returns:
            List of topic strings
        """
        recommendations = []

        # Prioritize knowledge gaps
        gaps = self.identify_knowledge_gaps(student_id)

        # Add high-priority gaps first
        for gap in gaps:
            if gap["priority"] == "high" and gap["topic"] not in recommendations:
                recommendations.append(gap["topic"])
                if len(recommendations) >= count:
                    return recommendations

        # Add medium-priority gaps
        for gap in gaps:
            if gap["priority"] == "medium" and gap["topic"] not in recommendations:
                recommendations.append(gap["topic"])
                if len(recommendations) >= count:
                    return recommendations

        # If we still need more, suggest progression topics
        # (simplified - in production would use knowledge graph)
        if self.pattern_tracker:
            try:
                cursor = self.pattern_tracker.conn.cursor()
                cursor.execute('''
                    SELECT DISTINCT concepts_covered
                    FROM sessions
                    WHERE student_id = ? AND concepts_covered IS NOT NULL
                    ORDER BY start_time DESC
                    LIMIT 5
                ''', (student_id,))

                rows = cursor.fetchall()
                # This is simplified - just return empty for now
            except Exception as e:
                logger.warning(f"Error getting session concepts: {e}")

        return recommendations

    def personalize_topic_sequence(
        self,
        student_id: str,
        available_topics: List[str]
    ) -> List[str]:
        """
        Personalize topic learning sequence

        Args:
            student_id: Student identifier
            available_topics: List of available topics

        Returns:
            Ordered list of topics
        """
        if not self.student_notes:
            return available_topics

        # Get strengths and weaknesses
        strengths = self._extract_strengths(student_id)
        weaknesses = self._extract_weaknesses(student_id)

        # Prioritize: weaknesses > neutral > strengths
        weak_topics = [t for t in available_topics if t in weaknesses]
        neutral_topics = [t for t in available_topics if t not in strengths and t not in weaknesses]
        strong_topics = [t for t in available_topics if t in strengths]

        # Combine in priority order
        sequence = weak_topics + neutral_topics + strong_topics

        logger.debug(f"Personalized sequence for {student_id}: {sequence}")
        return sequence

    def generate_recommendations(self, student_id: str) -> List[LearningRecommendation]:
        """
        Generate personalized learning recommendations

        Args:
            student_id: Student identifier

        Returns:
            List of LearningRecommendation objects
        """
        recommendations = []

        # Difficulty recommendations
        difficulty_rec = self.recommend_difficulty_adjustment(student_id)
        if difficulty_rec == "increase":
            recommendations.append(LearningRecommendation(
                recommendation_type="difficulty",
                message="You're doing great! Ready for more challenging problems.",
                priority=3,
                data={"adjustment": "increase"}
            ))
        elif difficulty_rec == "decrease":
            recommendations.append(LearningRecommendation(
                recommendation_type="difficulty",
                message="Let's focus on building confidence with easier problems.",
                priority=5,
                data={"adjustment": "decrease"}
            ))

        # Pacing recommendations
        pacing = self.recommend_pacing(student_id)
        if pacing.get("session_duration"):
            recommendations.append(LearningRecommendation(
                recommendation_type="pacing",
                message=f"Optimal session length: {pacing['session_duration']} minutes",
                priority=2,
                data=pacing
            ))

        # Knowledge gap recommendations
        gaps = self.identify_knowledge_gaps(student_id)
        if gaps:
            high_priority_gaps = [g for g in gaps if g["priority"] == "high"]
            if high_priority_gaps:
                recommendations.append(LearningRecommendation(
                    recommendation_type="knowledge_gap",
                    message=f"Let's address misconception in {high_priority_gaps[0]['topic']}",
                    priority=4,
                    data={"gaps": high_priority_gaps[:3]}
                ))

        # Sort by priority (descending)
        recommendations.sort(key=lambda x: x.priority, reverse=True)

        logger.debug(f"Generated {len(recommendations)} recommendations for {student_id}")
        return recommendations
