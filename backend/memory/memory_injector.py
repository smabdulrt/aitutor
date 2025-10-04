"""
Memory Injection System

This module integrates all memory systems to provide smart context injection:
1. Relevance-based memory retrieval
2. Context window optimization
3. Priority-based memory selection
4. Dynamic context updates
5. Integration with teaching assistant
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import logging
from backend.memory.student_notes import StudentNotes, NoteCategory
from backend.memory.learning_pattern_tracker import LearningPatternTracker
from backend.memory.personalization_engine import PersonalizationEngine
from backend.memory.goal_tracker import GoalTracker, GoalStatus

logger = logging.getLogger(__name__)


class ContextPriority(str, Enum):
    """Priority levels for context"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class MemoryContext:
    """Assembled memory context for injection"""
    student_id: str
    topic: str
    priority: ContextPriority
    content: str
    metadata: Dict = field(default_factory=dict)


class MemoryInjector:
    """
    Inject relevant memory context into conversations
    """

    def __init__(
        self,
        student_notes: Optional[StudentNotes] = None,
        pattern_tracker: Optional[LearningPatternTracker] = None,
        personalization_engine: Optional[PersonalizationEngine] = None,
        goal_tracker: Optional[GoalTracker] = None
    ):
        """
        Initialize memory injector

        Args:
            student_notes: StudentNotes instance
            pattern_tracker: LearningPatternTracker instance
            personalization_engine: PersonalizationEngine instance
            goal_tracker: GoalTracker instance
        """
        self.student_notes = student_notes
        self.pattern_tracker = pattern_tracker
        self.personalization_engine = personalization_engine
        self.goal_tracker = goal_tracker

        logger.info("Memory injector initialized")

    def get_relevant_context(
        self,
        student_id: str,
        current_topic: str,
        max_tokens: Optional[int] = None
    ) -> MemoryContext:
        """
        Get relevant memory context for current topic

        Args:
            student_id: Student identifier
            current_topic: Current topic being discussed
            max_tokens: Optional maximum token limit

        Returns:
            MemoryContext object
        """
        # Collect context from all systems
        context_items = []

        # 1. Get misconceptions (CRITICAL priority)
        if self.student_notes:
            misconceptions = self._get_misconceptions(student_id, current_topic)
            for misc in misconceptions:
                context_items.append({
                    "priority": ContextPriority.CRITICAL,
                    "type": "misconception",
                    "content": misc["content"],
                    "weight": 100
                })

        # 2. Get weak topics (HIGH priority)
        if self.student_notes:
            weak_topics = self._get_weak_topics(student_id, current_topic)
            for weak in weak_topics:
                context_items.append({
                    "priority": ContextPriority.HIGH,
                    "type": "weak_topic",
                    "content": weak["content"],
                    "weight": 80
                })

        # 3. Get learning preferences (HIGH priority)
        if self.student_notes:
            preferences = self._get_learning_preferences(student_id)
            for pref in preferences:
                context_items.append({
                    "priority": ContextPriority.HIGH,
                    "type": "preference",
                    "content": pref["content"],
                    "weight": 75
                })

        # 4. Get active goals (MEDIUM priority)
        if self.goal_tracker:
            goals = self._get_active_goals(student_id, current_topic)
            for goal in goals:
                context_items.append({
                    "priority": ContextPriority.MEDIUM,
                    "type": "goal",
                    "content": goal["content"],
                    "weight": 60
                })

        # 5. Get personalization profile (MEDIUM priority)
        if self.personalization_engine:
            profile = self._get_profile_summary(student_id)
            if profile:
                context_items.append({
                    "priority": ContextPriority.MEDIUM,
                    "type": "profile",
                    "content": profile["content"],
                    "weight": 50
                })

        # 6. Get learning patterns (LOW priority)
        if self.pattern_tracker:
            patterns = self._get_pattern_insights(student_id)
            for pattern in patterns:
                context_items.append({
                    "priority": ContextPriority.LOW,
                    "type": "pattern",
                    "content": pattern["content"],
                    "weight": 30
                })

        # Optimize for token limit
        if max_tokens:
            context_items = self._optimize_for_tokens(context_items, max_tokens)

        # Assemble final context
        priority, content = self._assemble_context(context_items)

        metadata = {
            "items_included": len(context_items),
            "topic": current_topic
        }

        return MemoryContext(
            student_id=student_id,
            topic=current_topic,
            priority=priority,
            content=content,
            metadata=metadata
        )

    def _get_misconceptions(self, student_id: str, topic: str) -> List[Dict]:
        """Get misconceptions related to topic"""
        misconceptions = []

        try:
            # Get topic-specific misconceptions
            notes = self.student_notes.get_notes_by_category(
                student_id,
                NoteCategory.MISCONCEPTION
            )

            for note in notes:
                if topic and topic.lower() in note.content.lower() or note.topic == topic:
                    misconceptions.append({
                        "content": f"⚠️ Misconception: {note.content}",
                        "topic": note.topic
                    })
        except Exception as e:
            logger.warning(f"Error getting misconceptions: {e}")

        return misconceptions

    def _get_weak_topics(self, student_id: str, topic: str) -> List[Dict]:
        """Get weak topics"""
        weak_topics = []

        try:
            notes = self.student_notes.get_notes_by_category(
                student_id,
                NoteCategory.WEAK_TOPIC
            )

            for note in notes:
                if topic and note.topic == topic:
                    weak_topics.append({
                        "content": f"📍 Weak area: {note.content}",
                        "topic": note.topic
                    })
        except Exception as e:
            logger.warning(f"Error getting weak topics: {e}")

        return weak_topics

    def _get_learning_preferences(self, student_id: str) -> List[Dict]:
        """Get learning preferences"""
        preferences = []

        try:
            notes = self.student_notes.get_notes_by_category(
                student_id,
                NoteCategory.LEARNING_PREFERENCE
            )

            for note in notes[:3]:  # Top 3 preferences
                preferences.append({
                    "content": f"✨ Preference: {note.content}",
                    "topic": note.topic
                })
        except Exception as e:
            logger.warning(f"Error getting preferences: {e}")

        return preferences

    def _get_active_goals(self, student_id: str, topic: str) -> List[Dict]:
        """Get active goals"""
        goals = []

        try:
            active_goals = self.goal_tracker.get_student_goals(
                student_id,
                status=GoalStatus.ACTIVE
            )

            for goal in active_goals[:2]:  # Top 2 active goals
                progress = self.goal_tracker.calculate_progress(goal.goal_id)
                goals.append({
                    "content": f"🎯 Goal: {goal.title} ({progress['percentage']}% complete)",
                    "goal_id": goal.goal_id
                })
        except Exception as e:
            logger.warning(f"Error getting goals: {e}")

        return goals

    def _get_profile_summary(self, student_id: str) -> Optional[Dict]:
        """Get personalization profile summary"""
        try:
            profile = self.personalization_engine.get_personalization_profile(student_id)

            content = f"👤 Learning style: {profile.preferred_explanation_style.value}, " \
                     f"Current level: {profile.current_difficulty_level.value}"

            if profile.interests:
                content += f", Interests: {', '.join(profile.interests[:2])}"

            return {"content": content}
        except Exception as e:
            logger.warning(f"Error getting profile: {e}")
            return None

    def _get_pattern_insights(self, student_id: str) -> List[Dict]:
        """Get learning pattern insights"""
        patterns = []

        try:
            insights = self.pattern_tracker.generate_insights(student_id)

            for insight in insights[:2]:  # Top 2 insights
                patterns.append({
                    "content": f"💡 Insight: {insight.message}",
                    "priority": insight.priority
                })
        except Exception as e:
            logger.warning(f"Error getting patterns: {e}")

        return patterns

    def _optimize_for_tokens(
        self,
        items: List[Dict],
        max_tokens: int
    ) -> List[Dict]:
        """
        Optimize context items to fit within token limit

        Args:
            items: List of context items
            max_tokens: Maximum token limit

        Returns:
            Optimized list of items
        """
        # Sort by weight (descending)
        sorted_items = sorted(items, key=lambda x: x["weight"], reverse=True)

        # Simple token estimation (rough: 1 token ≈ 4 characters)
        optimized = []
        token_count = 0

        for item in sorted_items:
            estimated_tokens = len(item["content"]) // 4

            if token_count + estimated_tokens <= max_tokens:
                optimized.append(item)
                token_count += estimated_tokens
            else:
                break

        logger.debug(f"Optimized {len(items)} items to {len(optimized)} within {max_tokens} tokens")
        return optimized

    def _assemble_context(self, items: List[Dict]) -> tuple:
        """
        Assemble context items into final content string

        Args:
            items: List of context items

        Returns:
            Tuple of (priority, content_string)
        """
        if not items:
            return ContextPriority.LOW, "No prior context available for this student."

        # Determine overall priority (highest priority item)
        priorities = [item.get("priority", ContextPriority.LOW) for item in items]

        priority_order = [ContextPriority.CRITICAL, ContextPriority.HIGH, ContextPriority.MEDIUM, ContextPriority.LOW]
        overall_priority = ContextPriority.LOW

        for p in priority_order:
            if p in priorities:
                overall_priority = p
                break

        # Assemble content
        content_parts = [item["content"] for item in items]
        content = "\n".join(content_parts)

        return overall_priority, content
