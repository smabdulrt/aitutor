"""
Emotional Intelligence Layer

Detects student emotions and informs Adam to enhance his teaching awareness.
The TA provides emotional context to Adam, who makes all teaching decisions.
"""

import logging
from enum import Enum
from typing import Optional, Callable, List
from dataclasses import dataclass
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmotionState(Enum):
    """Possible student emotional states"""
    NEUTRAL = "neutral"
    FRUSTRATED = "frustrated"
    CONFUSED = "confused"
    CONFIDENT = "confident"
    DISENGAGED = "disengaged"
    UNCERTAIN = "uncertain"


@dataclass
class EmotionDetectionResult:
    """Result of emotion detection"""
    emotion: EmotionState
    confidence: float
    timestamp: float
    source: str  # "transcript", "camera", "both"
    context: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().timestamp()


class EmotionalIntelligence:
    """
    Emotional Intelligence Layer

    Responsibilities:
    1. Detect student emotions from camera frames and transcript
    2. Inform Adam with emotional context
    3. Provide suggestions (not commands) to enhance Adam's awareness

    Note: The TA is Adam's intelligent assistant, not his supervisor.
    Adam makes all teaching decisions. TA provides situational awareness.
    """

    def __init__(
        self,
        prompt_injection_callback: Optional[Callable] = None,
        history_limit: int = 100
    ):
        """
        Initialize Emotional Intelligence

        Args:
            prompt_injection_callback: Async function to inject context to Adam/Gemini
            history_limit: Maximum emotion history to retain
        """
        self.prompt_injection_callback = prompt_injection_callback
        self.history_limit = history_limit

        self.current_emotion = EmotionState.NEUTRAL
        self.emotion_history: List[EmotionDetectionResult] = []

        logger.info("Emotional Intelligence initialized")

    async def detect_emotion(
        self,
        camera_frame=None,
        transcript: Optional[str] = None
    ) -> EmotionDetectionResult:
        """
        Detect student emotion from camera and/or transcript

        Args:
            camera_frame: Optional camera frame for facial expression analysis
            transcript: Optional text transcript for sentiment analysis

        Returns:
            EmotionDetectionResult with detected emotion and confidence
        """
        # If no input, return neutral
        if not camera_frame and not transcript:
            result = EmotionDetectionResult(
                emotion=EmotionState.NEUTRAL,
                confidence=1.0,
                source="none",
                timestamp=datetime.now().timestamp()
            )
            self._add_to_history(result)
            return result

        # Determine source
        if camera_frame and transcript:
            source = "both"
        elif camera_frame:
            source = "camera"
        else:
            source = "transcript"

        # Detect emotion from transcript (simple keyword-based for now)
        # In production, this would use sentiment analysis models
        emotion, confidence = self._analyze_transcript(transcript or "")

        result = EmotionDetectionResult(
            emotion=emotion,
            confidence=confidence,
            source=source,
            timestamp=datetime.now().timestamp(),
            context=transcript
        )

        # Update current emotion and history
        self.current_emotion = emotion
        self._add_to_history(result)

        logger.info(f"Emotion detected: {emotion.value} (confidence: {confidence:.2f})")
        return result

    def _analyze_transcript(self, transcript: str) -> tuple[EmotionState, float]:
        """
        Analyze transcript for emotion (simple keyword-based)

        In production, this would use:
        - Sentiment analysis models
        - Tone detection
        - Pattern recognition

        Args:
            transcript: Text to analyze

        Returns:
            (EmotionState, confidence_score)
        """
        if not transcript or len(transcript.strip()) == 0:
            return (EmotionState.NEUTRAL, 1.0)

        transcript_lower = transcript.lower()

        # Frustrated indicators
        frustrated_keywords = [
            "impossible", "never", "can't do", "too hard", "give up",
            "don't understand this at all", "so hard", "this is hard"
        ]
        if any(keyword in transcript_lower for keyword in frustrated_keywords):
            return (EmotionState.FRUSTRATED, 0.8)

        # Confused indicators
        confused_keywords = [
            "confused", "don't understand", "not sure", "confusing",
            "can you explain", "what does", "i'm lost"
        ]
        if any(keyword in transcript_lower for keyword in confused_keywords):
            return (EmotionState.CONFUSED, 0.7)

        # Uncertain indicators
        uncertain_keywords = [
            "maybe", "i think", "probably", "perhaps", "not certain"
        ]
        if any(keyword in transcript_lower for keyword in uncertain_keywords):
            return (EmotionState.UNCERTAIN, 0.6)

        # Confident indicators
        confident_keywords = [
            "got it", "i get it", "makes sense", "i understand",
            "perfect sense", "i see", "oh!", "aha"
        ]
        if any(keyword in transcript_lower for keyword in confident_keywords):
            return (EmotionState.CONFIDENT, 0.8)

        # Disengaged indicators (very short responses)
        if len(transcript.strip()) <= 3:
            return (EmotionState.DISENGAGED, 0.5)

        # Default to neutral
        return (EmotionState.NEUTRAL, 0.6)

    def _add_to_history(self, result: EmotionDetectionResult):
        """Add emotion result to history with size limit"""
        self.emotion_history.append(result)

        # Maintain history limit
        if len(self.emotion_history) > self.history_limit:
            self.emotion_history = self.emotion_history[-self.history_limit:]

    async def inform_adam_of_emotion(
        self,
        emotion_result: EmotionDetectionResult,
        additional_context: Optional[str] = None
    ) -> bool:
        """
        Inform Adam about detected student emotion to enhance his teaching awareness

        Args:
            emotion_result: Detected emotion result
            additional_context: Optional additional context

        Returns:
            True if context was injected, False otherwise
        """
        if not self.prompt_injection_callback:
            logger.warning("No prompt injection callback set")
            return False

        # Build context message for Adam
        emotion_name = emotion_result.emotion.value
        confidence_pct = int(emotion_result.confidence * 100)

        context_parts = [
            f"[Student Emotional State] {emotion_name.title()} (confidence: {confidence_pct}%)"
        ]

        if emotion_result.context:
            context_parts.append(f"Student said: \"{emotion_result.context}\"")

        # Add teaching suggestions based on emotion
        suggestions = self._get_teaching_suggestions(emotion_result.emotion)
        if suggestions:
            context_parts.append(f"Teaching considerations: {suggestions}")

        if additional_context:
            context_parts.append(f"Additional context: {additional_context}")

        # Format as informational context (not a command)
        context_message = "\n".join(context_parts)

        # Inject context to Adam
        await self.prompt_injection_callback(context_message)
        logger.info(f"Informed Adam of {emotion_name} emotion")
        return True

    def _get_teaching_suggestions(self, emotion: EmotionState) -> str:
        """
        Get teaching suggestions based on emotion (informational, not commands)

        Args:
            emotion: Detected emotion

        Returns:
            Teaching suggestions as a string
        """
        suggestions = {
            EmotionState.FRUSTRATED: (
                "Student may benefit from breaking problem into smaller steps "
                "or encouragement to reduce frustration"
            ),
            EmotionState.CONFUSED: (
                "Student may need clarification or a different explanation approach"
            ),
            EmotionState.CONFIDENT: (
                "Student is confident - may be ready for more challenging material"
            ),
            EmotionState.DISENGAGED: (
                "Student appears disengaged - consider re-engaging with questions "
                "or changing topic approach"
            ),
            EmotionState.UNCERTAIN: (
                "Student is uncertain - gentle guidance or confirmation may help"
            ),
            EmotionState.NEUTRAL: ""
        }

        return suggestions.get(emotion, "")

    async def process_emotion(
        self,
        camera_frame=None,
        transcript: Optional[str] = None,
        auto_inform: bool = True
    ) -> EmotionDetectionResult:
        """
        Convenience method: detect emotion and optionally inform Adam

        This is the main workflow for emotional intelligence:
        1. Detect emotion from input
        2. If significant emotion detected and auto_inform=True, inform Adam
        3. Adam uses this context to adapt his teaching (he makes the decisions)

        Args:
            camera_frame: Optional camera frame
            transcript: Optional transcript
            auto_inform: Whether to automatically inform Adam of non-neutral emotions

        Returns:
            Emotion detection result
        """
        # Step 1: Detect emotion
        emotion_result = await self.detect_emotion(
            camera_frame=camera_frame,
            transcript=transcript
        )

        # Step 2: If significant emotion detected and auto-inform enabled, inform Adam
        if auto_inform and emotion_result.emotion != EmotionState.NEUTRAL:
            await self.inform_adam_of_emotion(emotion_result)

        return emotion_result
