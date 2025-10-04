"""
Tests for Emotional Intelligence Layer

Following TDD: Tests written FIRST, then implementation.
All logic imported from codebase - NO hardcoded test logic.

Emotional Intelligence Layer:
1. Detects student emotions from camera frame and transcript
2. Asks Adam (Gemini) for strategy when emotion detected
3. Executes Adam's recommended strategy (no additional TA intelligence)
"""

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock, patch
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

    def test_initialization_with_callback(self):
        """Test initialization with Adam consultation callback"""
        callback = AsyncMock()
        ei = EmotionalIntelligence(adam_callback=callback)

        assert ei.adam_callback == callback


class TestEmotionDetection:
    """Test emotion detection from camera and transcript"""

    @pytest.fixture
    def ei(self):
        return EmotionalIntelligence()

    @pytest.mark.asyncio
    async def test_detect_emotion_from_transcript(self, ei):
        """Test emotion detection from text transcript"""
        # Frustrated transcript
        transcript = "This is so hard! I don't understand this at all!"

        result = await ei.detect_emotion(transcript=transcript)

        assert result is not None
        assert isinstance(result, EmotionDetectionResult)
        assert result.emotion in [EmotionState.FRUSTRATED, EmotionState.CONFUSED]
        assert result.confidence > 0

    @pytest.mark.asyncio
    async def test_detect_emotion_confident(self, ei):
        """Test detecting confident emotion"""
        transcript = "I got it! This makes perfect sense now!"

        result = await ei.detect_emotion(transcript=transcript)

        assert result.emotion == EmotionState.CONFIDENT
        assert result.confidence > 0.5

    @pytest.mark.asyncio
    async def test_detect_emotion_confused(self, ei):
        """Test detecting confused emotion"""
        transcript = "Wait, I'm not sure I understand... can you explain that again?"

        result = await ei.detect_emotion(transcript=transcript)

        assert result.emotion in [EmotionState.CONFUSED, EmotionState.UNCERTAIN]

    @pytest.mark.asyncio
    async def test_detect_emotion_disengaged(self, ei):
        """Test detecting disengaged emotion"""
        # Minimal/short responses indicate disengagement
        transcript = "ok"

        result = await ei.detect_emotion(transcript=transcript)

        # Short responses should indicate low engagement
        assert result is not None

    @pytest.mark.asyncio
    async def test_detect_emotion_with_camera_frame(self, ei):
        """Test emotion detection with camera frame"""
        # Mock camera frame (in real implementation, would use facial recognition)
        mock_frame = MagicMock()  # Simulated camera frame
        transcript = "I think I understand"

        result = await ei.detect_emotion(camera_frame=mock_frame, transcript=transcript)

        assert result is not None
        assert isinstance(result, EmotionDetectionResult)

    @pytest.mark.asyncio
    async def test_emotion_detection_updates_history(self, ei):
        """Test emotion detection adds to history"""
        transcript = "This is confusing"

        await ei.detect_emotion(transcript=transcript)

        assert len(ei.emotion_history) > 0
        assert ei.emotion_history[-1].emotion in EmotionState


class TestAdamConsultation:
    """Test asking Adam for emotional response strategy"""

    @pytest.fixture
    def ei(self):
        callback = AsyncMock(return_value="Use encouragement and break down the concept into smaller steps")
        return EmotionalIntelligence(adam_callback=callback)

    @pytest.mark.asyncio
    async def test_ask_adam_strategy_frustrated(self, ei):
        """Test asking Adam for strategy when student is frustrated"""
        emotion_state = EmotionState.FRUSTRATED
        context = "Student struggling with fractions for 10 minutes"

        strategy = await ei.ask_adam_strategy(emotion_state, context)

        assert strategy is not None
        assert isinstance(strategy, str)
        assert len(strategy) > 0
        ei.adam_callback.assert_called_once()

    @pytest.mark.asyncio
    async def test_ask_adam_strategy_confused(self, ei):
        """Test asking Adam for strategy when student is confused"""
        emotion_state = EmotionState.CONFUSED

        strategy = await ei.ask_adam_strategy(emotion_state)

        assert strategy is not None
        ei.adam_callback.assert_called_once()

    @pytest.mark.asyncio
    async def test_ask_adam_includes_emotion_context(self, ei):
        """Test Adam consultation includes emotion in query"""
        emotion_state = EmotionState.FRUSTRATED

        await ei.ask_adam_strategy(emotion_state)

        # Verify the query to Adam mentions the emotion
        call_args = ei.adam_callback.call_args[0][0]
        assert "frustrated" in call_args.lower() or "frustration" in call_args.lower()

    @pytest.mark.asyncio
    async def test_ask_adam_without_callback(self):
        """Test asking Adam without callback returns None"""
        ei = EmotionalIntelligence()  # No callback

        strategy = await ei.ask_adam_strategy(EmotionState.FRUSTRATED)

        assert strategy is None


class TestStrategyExecution:
    """Test executing Adam's recommended strategy"""

    @pytest.fixture
    def ei(self):
        adam_callback = AsyncMock(return_value="Provide positive encouragement")
        prompt_injection = AsyncMock()
        ei = EmotionalIntelligence(
            adam_callback=adam_callback,
            prompt_injection_callback=prompt_injection
        )
        return ei

    @pytest.mark.asyncio
    async def test_execute_strategy(self, ei):
        """Test executing a strategy from Adam"""
        adam_response = "Use encouraging language and simplify the explanation"

        await ei.execute_strategy(adam_response)

        # Verify prompt injection was called with Adam's strategy
        ei.prompt_injection_callback.assert_called_once()
        injected_prompt = ei.prompt_injection_callback.call_args[0][0]
        assert isinstance(injected_prompt, str)
        assert len(injected_prompt) > 0

    @pytest.mark.asyncio
    async def test_execute_strategy_without_callback(self):
        """Test execute_strategy without injection callback"""
        ei = EmotionalIntelligence(adam_callback=AsyncMock())

        # Should not raise error
        await ei.execute_strategy("Some strategy")


class TestEmotionalWorkflow:
    """Test complete emotional intelligence workflow"""

    @pytest.fixture
    def ei(self):
        adam_callback = AsyncMock(return_value="Provide encouragement and break problem into steps")
        prompt_injection = AsyncMock()
        return EmotionalIntelligence(
            adam_callback=adam_callback,
            prompt_injection_callback=prompt_injection
        )

    @pytest.mark.asyncio
    async def test_full_workflow_frustrated_student(self, ei):
        """Test full workflow: detect → ask Adam → execute"""
        transcript = "This is impossible! I'll never get this!"

        # Step 1: Detect emotion
        emotion_result = await ei.detect_emotion(transcript=transcript)
        assert emotion_result.emotion == EmotionState.FRUSTRATED

        # Step 2: Ask Adam for strategy
        strategy = await ei.ask_adam_strategy(emotion_result.emotion, transcript)
        assert strategy is not None

        # Step 3: Execute strategy
        await ei.execute_strategy(strategy)

        # Verify complete flow
        ei.adam_callback.assert_called_once()
        ei.prompt_injection_callback.assert_called_once()

    @pytest.mark.asyncio
    async def test_workflow_helper_method(self, ei):
        """Test convenience method that handles full workflow"""
        transcript = "I don't understand this at all"

        # Should detect, consult Adam, and execute automatically
        await ei.process_emotion(transcript=transcript)

        # Verify workflow executed
        assert len(ei.emotion_history) > 0
        # Should have consulted Adam if significant emotion detected
        if ei.emotion_history[-1].emotion != EmotionState.NEUTRAL:
            assert ei.adam_callback.called


class TestEmotionStateEnum:
    """Test emotion state enumeration"""

    def test_emotion_states_exist(self):
        """Test all expected emotion states are defined"""
        expected_states = [
            EmotionState.NEUTRAL,
            EmotionState.FRUSTRATED,
            EmotionState.CONFUSED,
            EmotionState.CONFIDENT,
            EmotionState.DISENGAGED,
            EmotionState.UNCERTAIN
        ]

        for state in expected_states:
            assert state in EmotionState


class TestEdgeCases:
    """Test edge cases and error handling"""

    @pytest.mark.asyncio
    async def test_detect_emotion_empty_transcript(self):
        """Test emotion detection with empty transcript"""
        ei = EmotionalIntelligence()

        result = await ei.detect_emotion(transcript="")

        # Should return neutral or handle gracefully
        assert result is not None
        assert result.emotion == EmotionState.NEUTRAL

    @pytest.mark.asyncio
    async def test_detect_emotion_no_input(self):
        """Test emotion detection with no input"""
        ei = EmotionalIntelligence()

        result = await ei.detect_emotion()

        # Should return neutral when no input
        assert result.emotion == EmotionState.NEUTRAL

    @pytest.mark.asyncio
    async def test_emotion_history_limit(self):
        """Test emotion history doesn't grow unbounded"""
        ei = EmotionalIntelligence()

        # Add many emotions
        for i in range(150):
            await ei.detect_emotion(transcript=f"Test {i}")

        # History should be limited (e.g., last 100)
        assert len(ei.emotion_history) <= 100

    @pytest.mark.asyncio
    async def test_rapid_emotion_changes(self):
        """Test handling rapid emotion changes"""
        ei = EmotionalIntelligence(
            adam_callback=AsyncMock(return_value="strategy"),
            prompt_injection_callback=AsyncMock()
        )

        # Rapid changes
        await ei.detect_emotion(transcript="This is hard!")
        await ei.detect_emotion(transcript="Oh wait, I get it!")
        await ei.detect_emotion(transcript="Actually no, I'm confused")

        # Should track all changes
        assert len(ei.emotion_history) == 3
