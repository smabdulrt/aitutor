"""
Tests for Emotional Intelligence Layer (Refactored)

Emotional Intelligence Layer:
1. Detects student emotions from camera frame and transcript
2. Informs Adam (Gemini) with emotional context and teaching suggestions
3. Adam makes all teaching decisions based on this awareness
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.teaching_assistant.emotional_intelligence import (
    EmotionalIntelligence,
    EmotionState,
    EmotionDetectionResult
)


class TestEmotionalIntelligenceInitialization:
    """Test emotional intelligence initialization"""

    def test_initialization(self):
        """Test EI initializes correctly"""
        ei = EmotionalIntelligence()
        assert ei is not None
        assert ei.current_emotion == EmotionState.NEUTRAL
        assert ei.emotion_history == []
        assert ei.prompt_injection_callback is None

    def test_initialization_with_callback(self):
        """Test initialization with prompt injection callback"""
        callback = AsyncMock()
        ei = EmotionalIntelligence(prompt_injection_callback=callback)
        assert ei.prompt_injection_callback == callback


class TestEmotionDetection:
    """Test emotion detection from camera and transcript"""

    @pytest.fixture
    def ei(self):
        return EmotionalIntelligence()

    @pytest.mark.asyncio
    async def test_detect_emotion_from_transcript_frustrated(self, ei):
        transcript = "This is so hard! I don't understand this at all!"
        result = await ei.detect_emotion(transcript=transcript)
        assert result.emotion == EmotionState.FRUSTRATED
        assert result.confidence > 0

    @pytest.mark.asyncio
    async def test_detect_emotion_confident(self, ei):
        transcript = "I got it! This makes perfect sense now!"
        result = await ei.detect_emotion(transcript=transcript)
        assert result.emotion == EmotionState.CONFIDENT

    @pytest.mark.asyncio
    async def test_detect_emotion_confused(self, ei):
        transcript = "Wait, I'm not sure I understand... can you explain that again?"
        result = await ei.detect_emotion(transcript=transcript)
        assert result.emotion == EmotionState.CONFUSED

    @pytest.mark.asyncio
    async def test_detect_emotion_disengaged(self, ei):
        transcript = "ok"
        result = await ei.detect_emotion(transcript=transcript)
        assert result.emotion == EmotionState.DISENGAGED

    @pytest.mark.asyncio
    async def test_emotion_detection_updates_history(self, ei):
        transcript = "This is confusing"
        await ei.detect_emotion(transcript=transcript)
        assert len(ei.emotion_history) == 1
        assert ei.emotion_history[0].emotion == EmotionState.CONFUSED


class TestAdamInforming:
    """Test informing Adam about student's emotional state"""

    @pytest.fixture
    def ei(self):
        callback = AsyncMock()
        return EmotionalIntelligence(prompt_injection_callback=callback)

    @pytest.mark.asyncio
    async def test_inform_adam_frustrated(self, ei):
        """Test informing Adam when student is frustrated"""
        emotion_result = EmotionDetectionResult(
            emotion=EmotionState.FRUSTRATED,
            confidence=0.8,
            source="transcript",
            context="I can't do this.",
            timestamp=12345.678
        )
        result = await ei.inform_adam_of_emotion(emotion_result)
        assert result is True
        ei.prompt_injection_callback.assert_called_once()
        call_args = ei.prompt_injection_callback.call_args[0][0]
        assert "frustrated" in call_args.lower()
        assert "student may benefit" in call_args.lower()

    @pytest.mark.asyncio
    async def test_inform_adam_without_callback(self):
        """Test informing Adam without a callback returns False"""
        ei = EmotionalIntelligence()  # No callback
        emotion_result = EmotionDetectionResult(emotion=EmotionState.CONFUSED, confidence=0.7, source="none", timestamp=12345.678)
        result = await ei.inform_adam_of_emotion(emotion_result)
        assert result is False


class TestEmotionalWorkflow:
    """Test complete emotional intelligence workflow"""

    @pytest.fixture
    def ei(self):
        prompt_injection = AsyncMock()
        return EmotionalIntelligence(prompt_injection_callback=prompt_injection)

    @pytest.mark.asyncio
    async def test_full_workflow_frustrated_student(self, ei):
        """Test full workflow: detect -> inform Adam"""
        transcript = "This is impossible! I'll never get this!"
        await ei.process_emotion(transcript=transcript, auto_inform=True)

        assert len(ei.emotion_history) == 1
        assert ei.emotion_history[0].emotion == EmotionState.FRUSTRATED

        ei.prompt_injection_callback.assert_called_once()
        call_args = ei.prompt_injection_callback.call_args[0][0]
        assert "Frustrated" in call_args
        assert "Teaching considerations" in call_args

    @pytest.mark.asyncio
    async def test_workflow_does_not_inform_on_neutral(self, ei):
        """Test that workflow does not inform Adam on neutral emotion"""
        transcript = "This is a neutral statement."
        await ei.process_emotion(transcript=transcript, auto_inform=True)

        assert ei.emotion_history[0].emotion == EmotionState.NEUTRAL
        ei.prompt_injection_callback.assert_not_called()


class TestEdgeCases:
    """Test edge cases and error handling"""

    @pytest.fixture
    def ei(self):
        return EmotionalIntelligence(history_limit=50)

    @pytest.mark.asyncio
    async def test_detect_emotion_empty_transcript(self, ei):
        result = await ei.detect_emotion(transcript="")
        assert result.emotion == EmotionState.NEUTRAL

    @pytest.mark.asyncio
    async def test_detect_emotion_no_input(self, ei):
        result = await ei.detect_emotion()
        assert result.emotion == EmotionState.NEUTRAL

    @pytest.mark.asyncio
    async def test_emotion_history_limit(self, ei):
        """Test emotion history doesn't grow unbounded"""
        for i in range(100):
            await ei.detect_emotion(transcript=f"Test {i}")
        assert len(ei.emotion_history) == 50

    @pytest.mark.asyncio
    async def test_rapid_emotion_changes(self):
        """Test handling rapid emotion changes"""
        ei = EmotionalIntelligence(prompt_injection_callback=AsyncMock())
        await ei.detect_emotion(transcript="This is hard!")
        await ei.detect_emotion(transcript="Oh wait, I get it!")
        await ei.detect_emotion(transcript="Actually no, I'm confused")
        assert len(ei.emotion_history) == 3
        assert ei.emotion_history[0].emotion == EmotionState.FRUSTRATED
        assert ei.emotion_history[1].emotion == EmotionState.CONFIDENT
        assert ei.emotion_history[2].emotion == EmotionState.CONFUSED
