"""
Tests for Historical Context Provider

Following TDD: Tests written FIRST, then implementation.
All logic imported from codebase - NO hardcoded test logic.

Historical Context Provider:
1. Query Vector DB for past similar struggles
2. Query Knowledge Graph for prerequisite gaps
3. Inject context to Adam BEFORE his response
"""

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from backend.teaching_assistant.context_provider import (
    ContextProvider,
    ContextResult,
    ContextType
)
from backend.memory.vector_store import VectorStore
from backend.memory.knowledge_graph import KnowledgeGraph


class TestContextProviderInitialization:
    """Test context provider initialization"""

    def test_initialization_with_stores(self):
        """Test initialization with vector store and knowledge graph"""
        vector_store = Mock(spec=VectorStore)
        knowledge_graph = Mock(spec=KnowledgeGraph)

        cp = ContextProvider(
            vector_store=vector_store,
            knowledge_graph=knowledge_graph
        )

        assert cp is not None
        assert cp.vector_store == vector_store
        assert cp.knowledge_graph == knowledge_graph

    def test_initialization_without_stores(self):
        """Test initialization without stores (graceful handling)"""
        cp = ContextProvider()

        assert cp is not None


class TestPastStruggles:
    """Test retrieving past struggles from Vector DB"""

    @pytest.fixture
    def cp(self):
        vector_store = Mock(spec=VectorStore)
        vector_store.similarity_search = Mock(return_value=[
            {
                "text": "Student struggled with fraction division",
                "metadata": {"topic": "fractions", "outcome": "struggled"},
                "distance": 0.15
            },
            {
                "text": "Confusion about converting fractions to decimals",
                "metadata": {"topic": "fractions", "outcome": "confused"},
                "distance": 0.22
            }
        ])

        knowledge_graph = Mock(spec=KnowledgeGraph)
        return ContextProvider(vector_store=vector_store, knowledge_graph=knowledge_graph)

    @pytest.mark.asyncio
    async def test_get_past_struggles_returns_results(self, cp):
        """Test getting past struggles for a topic"""
        topic = "fractions"
        student_id = "student_123"

        results = await cp.get_past_struggles(topic, student_id)

        assert results is not None
        assert len(results) > 0
        assert isinstance(results[0], ContextResult)

    @pytest.mark.asyncio
    async def test_get_past_struggles_calls_vector_store(self, cp):
        """Test that past struggles queries vector store correctly"""
        topic = "algebra"
        student_id = "student_456"

        await cp.get_past_struggles(topic, student_id)

        cp.vector_store.similarity_search.assert_called_once()
        call_kwargs = cp.vector_store.similarity_search.call_args.kwargs

        # Should search for topic in query
        query = call_kwargs.get('query', '')
        assert topic in query.lower()

    @pytest.mark.asyncio
    async def test_get_past_struggles_filters_by_student(self, cp):
        """Test filtering past struggles by student_id"""
        topic = "geometry"
        student_id = "student_789"

        await cp.get_past_struggles(topic, student_id)

        call_args = cp.vector_store.similarity_search.call_args
        filter_metadata = call_args[1].get('filter_metadata', {})

        # Should filter by student_id
        assert filter_metadata.get('student_id') == student_id

    @pytest.mark.asyncio
    async def test_get_past_struggles_without_vector_store(self):
        """Test handling when no vector store available"""
        cp = ContextProvider()  # No vector store

        results = await cp.get_past_struggles("topic", "student")

        # Should return empty list gracefully
        assert results == []


class TestPrerequisiteGaps:
    """Test identifying prerequisite gaps from Knowledge Graph"""

    @pytest.fixture
    def cp(self):
        vector_store = Mock(spec=VectorStore)

        knowledge_graph = Mock(spec=KnowledgeGraph)
        knowledge_graph.find_prerequisite_gaps = Mock(return_value=[
            {
                "skill_id": "fractions_basics",
                "current_mastery": 0.3,
                "gap": 0.2
            },
            {
                "skill_id": "division",
                "current_mastery": 0.4,
                "gap": 0.1
            }
        ])

        return ContextProvider(vector_store=vector_store, knowledge_graph=knowledge_graph)

    @pytest.mark.asyncio
    async def test_get_prerequisite_gaps_returns_results(self, cp):
        """Test getting prerequisite gaps for a skill"""
        current_skill = "fractions_division"
        student_id = "student_123"
        student_skills = {
            "fractions_basics": 0.3,
            "division": 0.4
        }

        gaps = await cp.get_prerequisite_gaps(current_skill, student_id, student_skills)

        assert gaps is not None
        assert len(gaps) > 0
        assert isinstance(gaps[0], ContextResult)

    @pytest.mark.asyncio
    async def test_get_prerequisite_gaps_calls_knowledge_graph(self, cp):
        """Test that prerequisite gaps queries knowledge graph"""
        current_skill = "algebra_equations"
        student_skills = {"variables": 0.5}

        await cp.get_prerequisite_gaps(current_skill, "student_id", student_skills)

        cp.knowledge_graph.find_prerequisite_gaps.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_prerequisite_gaps_without_knowledge_graph(self):
        """Test handling when no knowledge graph available"""
        cp = ContextProvider()  # No knowledge graph

        gaps = await cp.get_prerequisite_gaps("skill", "student", {})

        # Should return empty list gracefully
        assert gaps == []


class TestContextInjection:
    """Test injecting context to Adam"""

    @pytest.fixture
    def cp(self):
        vector_store = Mock(spec=VectorStore)
        vector_store.similarity_search = Mock(return_value=[
            {
                "text": "Student struggled with this concept before",
                "metadata": {"outcome": "struggled"}
            }
        ])

        knowledge_graph = Mock(spec=KnowledgeGraph)
        knowledge_graph.find_prerequisite_gaps = Mock(return_value=[
            {
                "skill_id": "prerequisite_skill",
                "gap": 0.3
            }
        ])

        prompt_callback = AsyncMock()

        return ContextProvider(
            vector_store=vector_store,
            knowledge_graph=knowledge_graph,
            prompt_injection_callback=prompt_callback
        )

    @pytest.mark.asyncio
    async def test_inject_context_to_adam(self, cp):
        """Test injecting context as prompt to Adam"""
        context = [
            ContextResult(
                context_type=ContextType.PAST_STRUGGLE,
                content="Student struggled with fractions last session",
                relevance_score=0.9
            )
        ]

        await cp.inject_context_to_adam(context)

        # Verify prompt injection was called
        cp.prompt_injection_callback.assert_called_once()
        injected_prompt = cp.prompt_injection_callback.call_args[0][0]

        assert isinstance(injected_prompt, str)
        assert "fractions" in injected_prompt.lower()

    @pytest.mark.asyncio
    async def test_inject_context_multiple_items(self, cp):
        """Test injecting multiple context items"""
        context = [
            ContextResult(
                context_type=ContextType.PAST_STRUGGLE,
                content="Struggled with concept A",
                relevance_score=0.8
            ),
            ContextResult(
                context_type=ContextType.PREREQUISITE_GAP,
                content="Missing skill B",
                relevance_score=0.7
            )
        ]

        await cp.inject_context_to_adam(context)

        cp.prompt_injection_callback.assert_called_once()
        injected_prompt = cp.prompt_injection_callback.call_args[0][0]

        # Should include both context items
        assert "Struggled with concept A" in injected_prompt
        assert "Missing skill B" in injected_prompt

    @pytest.mark.asyncio
    async def test_inject_context_without_callback(self):
        """Test inject_context without callback (graceful handling)"""
        cp = ContextProvider()  # No callback

        context = [
            ContextResult(
                context_type=ContextType.PAST_STRUGGLE,
                content="Some context",
                relevance_score=0.5
            )
        ]

        # Should not raise error
        await cp.inject_context_to_adam(context)


class TestCompleteContextWorkflow:
    """Test complete context retrieval and injection workflow"""

    @pytest.fixture
    def cp(self):
        vector_store = Mock(spec=VectorStore)
        vector_store.similarity_search = Mock(return_value=[
            {
                "text": "Previous struggle with topic",
                "metadata": {"topic": "test_topic"},
                "distance": 0.1
            }
        ])

        knowledge_graph = Mock(spec=KnowledgeGraph)
        knowledge_graph.find_prerequisite_gaps = Mock(return_value=[
            {"skill_id": "prereq_skill", "gap": 0.2}
        ])

        prompt_callback = AsyncMock()

        return ContextProvider(
            vector_store=vector_store,
            knowledge_graph=knowledge_graph,
            prompt_injection_callback=prompt_callback
        )

    @pytest.mark.asyncio
    async def test_full_context_workflow(self, cp):
        """Test complete workflow: retrieve struggles, gaps, and inject"""
        topic = "fractions"
        current_skill = "fractions_division"
        student_id = "student_123"
        student_skills = {"fractions_basics": 0.4}

        # Step 1: Get past struggles
        struggles = await cp.get_past_struggles(topic, student_id)
        assert len(struggles) > 0

        # Step 2: Get prerequisite gaps
        gaps = await cp.get_prerequisite_gaps(current_skill, student_id, student_skills)
        assert len(gaps) > 0

        # Step 3: Combine and inject
        all_context = struggles + gaps
        await cp.inject_context_to_adam(all_context)

        # Verify injection happened
        cp.prompt_injection_callback.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_workflow_helper_method(self, cp):
        """Test convenience method that handles full workflow"""
        topic = "algebra"
        current_skill = "equations"
        student_id = "student_456"
        student_skills = {"variables": 0.5}

        # Should retrieve and inject automatically
        await cp.provide_context(
            topic=topic,
            current_skill=current_skill,
            student_id=student_id,
            student_skills=student_skills
        )

        # Verify both stores were queried
        cp.vector_store.similarity_search.assert_called()
        cp.knowledge_graph.find_prerequisite_gaps.assert_called()

        # Verify context was injected
        cp.prompt_injection_callback.assert_called()


class TestContextResult:
    """Test ContextResult data structure"""

    def test_context_result_creation(self):
        """Test creating a context result"""
        result = ContextResult(
            context_type=ContextType.PAST_STRUGGLE,
            content="Student struggled with this",
            relevance_score=0.8
        )

        assert result.context_type == ContextType.PAST_STRUGGLE
        assert result.content == "Student struggled with this"
        assert result.relevance_score == 0.8

    def test_context_types_exist(self):
        """Test all expected context types are defined"""
        expected_types = [
            ContextType.PAST_STRUGGLE,
            ContextType.PREREQUISITE_GAP,
            ContextType.PAST_SUCCESS
        ]

        for context_type in expected_types:
            assert context_type in ContextType


class TestEdgeCases:
    """Test edge cases and error handling"""

    @pytest.mark.asyncio
    async def test_empty_past_struggles(self):
        """Test handling when no past struggles found"""
        vector_store = Mock(spec=VectorStore)
        vector_store.similarity_search = Mock(return_value=[])

        cp = ContextProvider(vector_store=vector_store)

        results = await cp.get_past_struggles("topic", "student")

        assert results == []

    @pytest.mark.asyncio
    async def test_empty_prerequisite_gaps(self):
        """Test handling when no prerequisite gaps"""
        knowledge_graph = Mock(spec=KnowledgeGraph)
        knowledge_graph.find_prerequisite_gaps = Mock(return_value=[])

        cp = ContextProvider(knowledge_graph=knowledge_graph)

        gaps = await cp.get_prerequisite_gaps("skill", "student", {})

        assert gaps == []

    @pytest.mark.asyncio
    async def test_inject_empty_context(self):
        """Test injecting empty context list"""
        prompt_callback = AsyncMock()
        cp = ContextProvider(prompt_injection_callback=prompt_callback)

        await cp.inject_context_to_adam([])

        # Should not call injection for empty context
        prompt_callback.assert_not_called()

    @pytest.mark.asyncio
    async def test_context_with_missing_student_skills(self):
        """Test handling when student_skills is empty"""
        knowledge_graph = Mock(spec=KnowledgeGraph)
        knowledge_graph.find_prerequisite_gaps = Mock(return_value=[])

        cp = ContextProvider(knowledge_graph=knowledge_graph)

        # Should handle empty skills dict gracefully
        gaps = await cp.get_prerequisite_gaps("skill", "student", {})

        assert gaps == []
