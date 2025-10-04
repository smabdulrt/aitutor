"""
Tests for Teaching Assistant Core

Following TDD: Tests written FIRST, then implementation.
All logic imported from codebase - NO hardcoded test logic.
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from backend.teaching_assistant.ta_core import (
    TeachingAssistant,
    SessionState,
    ActivityMonitor
)


class TestTeachingAssistantInitialization:
    """Test TA initialization and basic setup"""

    def test_initialization(self):
        """Test TA initializes with correct defaults"""
        ta = TeachingAssistant()

        assert ta is not None
        assert ta.session_state == SessionState.IDLE
        assert ta.inactivity_threshold == 60  # 60 seconds default
        assert ta.is_monitoring is False


class TestSessionGreeting:
    """Test session greeting functionality"""

    @pytest.fixture
    def ta(self):
        return TeachingAssistant()

    @pytest.mark.asyncio
    async def test_greet_on_startup_generates_prompt(self, ta):
        """Test greeting generation on session startup"""
        student_name = "Alex"

        greeting_prompt = await ta.greet_on_startup(student_name)

        assert greeting_prompt is not None
        assert isinstance(greeting_prompt, str)
        assert len(greeting_prompt) > 0
        assert "Alex" in greeting_prompt or "student" in greeting_prompt.lower()

    @pytest.mark.asyncio
    async def test_greet_on_startup_updates_session_state(self, ta):
        """Test session state changes to ACTIVE after greeting"""
        student_name = "Jordan"

        await ta.greet_on_startup(student_name)

        assert ta.session_state == SessionState.ACTIVE

    @pytest.mark.asyncio
    async def test_greet_on_startup_with_callback(self, ta):
        """Test greeting calls injection callback"""
        callback = AsyncMock()
        ta.set_prompt_injection_callback(callback)

        greeting_prompt = await ta.greet_on_startup("Sam")

        callback.assert_called_once()
        assert callback.call_args[0][0] == greeting_prompt


class TestSessionClosure:
    """Test session closure functionality"""

    @pytest.fixture
    def ta(self):
        ta = TeachingAssistant()
        ta.session_state = SessionState.ACTIVE
        return ta

    @pytest.mark.asyncio
    async def test_greet_on_close_generates_summary(self, ta):
        """Test closure generates summary prompt"""
        session_summary = {
            "questions_answered": 5,
            "accuracy": 0.8,
            "topics_covered": ["fractions", "decimals"]
        }

        closure_prompt = await ta.greet_on_close(session_summary)

        assert closure_prompt is not None
        assert isinstance(closure_prompt, str)
        assert len(closure_prompt) > 0

    @pytest.mark.asyncio
    async def test_greet_on_close_updates_session_state(self, ta):
        """Test session state changes to CLOSED"""
        session_summary = {"questions_answered": 3}

        await ta.greet_on_close(session_summary)

        assert ta.session_state == SessionState.CLOSED

    @pytest.mark.asyncio
    async def test_greet_on_close_stops_monitoring(self, ta):
        """Test monitoring stops on session close"""
        ta.is_monitoring = True
        session_summary = {"questions_answered": 2}

        await ta.greet_on_close(session_summary)

        assert ta.is_monitoring is False


class TestActivityMonitoring:
    """Test inactivity detection and nudging"""

    @pytest.fixture
    def ta(self):
        ta = TeachingAssistant(inactivity_threshold=2)  # 2 seconds for testing
        ta.session_state = SessionState.ACTIVE
        return ta

    @pytest.mark.asyncio
    async def test_monitor_activity_starts(self, ta):
        """Test activity monitor starts correctly"""
        monitor_task = asyncio.create_task(ta.monitor_activity())
        await asyncio.sleep(0.1)  # Let it start

        assert ta.is_monitoring is True

        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass

    @pytest.mark.asyncio
    async def test_inactivity_triggers_nudge(self, ta):
        """Test nudge sent after inactivity threshold"""
        nudge_callback = AsyncMock()
        ta.set_prompt_injection_callback(nudge_callback)

        # Start monitoring
        monitor_task = asyncio.create_task(ta.monitor_activity())

        # Wait for inactivity threshold + buffer
        await asyncio.sleep(2.5)

        # Verify nudge was sent
        assert nudge_callback.called
        nudge_prompt = nudge_callback.call_args[0][0]
        assert isinstance(nudge_prompt, str)
        assert len(nudge_prompt) > 0

        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass

    @pytest.mark.asyncio
    async def test_activity_reset_prevents_nudge(self, ta):
        """Test activity reset prevents premature nudging"""
        nudge_callback = AsyncMock()
        ta.set_prompt_injection_callback(nudge_callback)

        monitor_task = asyncio.create_task(ta.monitor_activity())

        # Reset activity before threshold
        await asyncio.sleep(1)
        ta.reset_activity()

        # Wait a bit more (total < 2 * threshold)
        await asyncio.sleep(1)

        # Should not have nudged yet
        assert nudge_callback.call_count == 0

        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass

    @pytest.mark.asyncio
    async def test_monitor_stops_when_session_closed(self, ta):
        """Test monitor stops when session closes"""
        monitor_task = asyncio.create_task(ta.monitor_activity())
        await asyncio.sleep(0.1)

        # Close session
        ta.session_state = SessionState.CLOSED

        # Wait a bit for monitor to detect closure
        await asyncio.sleep(0.5)

        assert monitor_task.done() or ta.is_monitoring is False

        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass


class TestPromptInjection:
    """Test prompt injection to Gemini"""

    @pytest.fixture
    def ta(self):
        return TeachingAssistant()

    @pytest.mark.asyncio
    async def test_inject_prompt_with_callback(self, ta):
        """Test prompt injection calls callback"""
        callback = AsyncMock()
        ta.set_prompt_injection_callback(callback)

        test_prompt = "Test prompt for Gemini"
        await ta.inject_prompt(test_prompt)

        callback.assert_called_once_with(test_prompt)

    @pytest.mark.asyncio
    async def test_inject_prompt_without_callback(self, ta):
        """Test inject_prompt handles missing callback gracefully"""
        # Should not raise error
        await ta.inject_prompt("Test prompt")

    def test_set_callback(self, ta):
        """Test setting callback function"""
        callback = AsyncMock()
        ta.set_prompt_injection_callback(callback)

        assert ta.prompt_injection_callback == callback


class TestEdgeCases:
    """Test edge cases and error handling"""

    @pytest.mark.asyncio
    async def test_greet_empty_student_name(self):
        """Test greeting with empty student name"""
        ta = TeachingAssistant()

        greeting = await ta.greet_on_startup("")

        # Should still generate greeting (generic)
        assert greeting is not None
        assert len(greeting) > 0

    @pytest.mark.asyncio
    async def test_close_with_empty_summary(self):
        """Test closure with empty session summary"""
        ta = TeachingAssistant()
        ta.session_state = SessionState.ACTIVE

        closure = await ta.greet_on_close({})

        # Should still generate closure
        assert closure is not None
        assert len(closure) > 0

    @pytest.mark.asyncio
    async def test_multiple_greeting_calls(self):
        """Test multiple greeting calls (idempotency)"""
        ta = TeachingAssistant()

        greeting1 = await ta.greet_on_startup("Alex")
        greeting2 = await ta.greet_on_startup("Alex")

        # Should generate greetings both times
        assert greeting1 is not None
        assert greeting2 is not None
        assert ta.session_state == SessionState.ACTIVE
