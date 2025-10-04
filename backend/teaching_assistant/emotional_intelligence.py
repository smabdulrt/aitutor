"""
Emotional Intelligence Layer

Detects student emotions and consults Adam for response strategies.
The TA detects emotions but defers to Adam for how to respond.
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
    2. Consult Adam (Gemini) for response strategy
    3. Execute Adam's recommended strategy

    Note: The TA detects emotions but does NOT decide how to respond.
    All response strategies come from Adam.
    """

    def __init__(
        self,
        adam_callback: Optional[Callable] = None,
        prompt_injection_callback: Optional[Callable] = None,
        history_limit: int = 100
    ):
        """
        Initialize Emotional Intelligence

        Args:
            adam_callback: Async function to consult Adam for strategies
            prompt_injection_callback: Async function to inject prompts to Gemini
            history_limit: Maximum emotion history to retain
        """
        self.adam_callback = adam_callback
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
            "confused", "don't understand", "not sure", "wait",
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

    async def ask_adam_strategy(
        self,
        emotion_state: EmotionState,
        context: Optional[str] = None
    ) -> Optional[str]:
        """
        Ask Adam (Gemini) for strategy to handle detected emotion

        Args:
            emotion_state: Detected emotion
            context: Optional context (transcript, situation)

        Returns:
            Adam's recommended strategy, or None if no callback set
        """
        if not self.adam_callback:
            logger.warning("No Adam callback set for strategy consultation")
            return None

        # Construct query to Adam
        emotion_name = emotion_state.value
        query_parts = [
            f"The student appears to be {emotion_name}."
        ]

        if context:
            query_parts.append(f"Context: \"{context}\"")

        query_parts.append(
            "As an expert teacher, how would you handle this situation? "
            "Please provide a brief strategy for responding to this emotional state."
        )

        query = " ".join(query_parts)

        # Consult Adam
        logger.info(f"Consulting Adam for {emotion_name} strategy")
        strategy = await self.adam_callback(query)

        logger.info(f"Adam's strategy: {strategy[:50]}...")
        return strategy

    async def execute_strategy(self, adam_response: str):
        """
        Execute Adam's recommended strategy

        Args:
            adam_response: Strategy from Adam
        """
        if not self.prompt_injection_callback:
            logger.warning("No prompt injection callback set")
            return

        # Format Adam's strategy as a system prompt
        # This instructs Adam to incorporate the strategy into his next response
        strategy_prompt = (
            f"[Teaching Strategy] {adam_response}\n\n"
            f"Please incorporate this strategy naturally into your next interaction "
            f"with the student."
        )

        # Inject the strategy
        await self.prompt_injection_callback(strategy_prompt)
        logger.info("Strategy executed (prompt injected)")

    async def process_emotion(
        self,
        camera_frame=None,
        transcript: Optional[str] = None
    ) -> Optional[EmotionDetectionResult]:
        """
        Convenience method: detect emotion, consult Adam, execute strategy

        This is the main workflow for emotional intelligence:
        1. Detect emotion
        2. If significant emotion (not neutral), ask Adam
        3. Execute Adam's strategy

        Args:
            camera_frame: Optional camera frame
            transcript: Optional transcript

        Returns:
            Emotion detection result
        """
        # Step 1: Detect emotion
        emotion_result = await self.detect_emotion(
            camera_frame=camera_frame,
            transcript=transcript
        )

        # Step 2: If significant emotion detected, consult Adam
        if emotion_result.emotion != EmotionState.NEUTRAL:
            strategy = await self.ask_adam_strategy(
                emotion_result.emotion,
                context=emotion_result.context
            )

            # Step 3: Execute strategy
            if strategy:
                await self.execute_strategy(strategy)

        return emotion_result
