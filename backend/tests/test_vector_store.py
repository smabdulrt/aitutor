"""
Test suite for Vector Store (ChromaDB)

CRITICAL: Tests ONLY import from codebase and verify behavior.
NO logic hardcoded - we test the actual implementation.
"""

import pytest
from backend.memory.vector_store import VectorStore, InteractionDocument


class TestVectorStore:
    """Test VectorStore - imports from backend, no hardcoding"""

    @pytest.fixture
    def vector_store(self, tmp_path):
        """Create VectorStore instance for testing"""
        return VectorStore(persist_directory=str(tmp_path / "chroma_test"))

    def test_initialization(self, vector_store):
        """Test vector store initializes correctly"""
        assert vector_store is not None
        assert vector_store.collection is not None

    def test_store_interaction(self, vector_store):
        """Test storing an interaction"""
        doc_id = vector_store.store(
            text="Student struggled with 2x+4=10",
            metadata={
                "session_id": "test_session_1",
                "student_id": "student_1",
                "topic": "linear_equations",
                "outcome": "struggled"
            }
        )

        assert doc_id is not None
        assert isinstance(doc_id, str)

    def test_similarity_search(self, vector_store):
        """Test similarity search retrieval"""
        # Store some test interactions
        vector_store.store(
            "Student mastered fractions",
            {"topic": "fractions", "outcome": "mastered"}
        )
        vector_store.store(
            "Student struggled with fractions",
            {"topic": "fractions", "outcome": "struggled"}
        )
        vector_store.store(
            "Student learned multiplication",
            {"topic": "multiplication", "outcome": "mastered"}
        )

        # Search for fraction-related content
        results = vector_store.similarity_search(
            query="fractions difficulty",
            k=2
        )

        assert len(results) <= 2
        assert any("fraction" in r["text"].lower() for r in results)

    def test_filter_by_metadata(self, vector_store):
        """Test filtering by metadata"""
        vector_store.store(
            "Struggled with algebra",
            {"student_id": "s1", "outcome": "struggled"}
        )
        vector_store.store(
            "Mastered algebra",
            {"student_id": "s1", "outcome": "mastered"}
        )
        vector_store.store(
            "Struggled with geometry",
            {"student_id": "s2", "outcome": "struggled"}
        )

        # Filter by student and outcome (using $and operator for ChromaDB)
        results = vector_store.similarity_search(
            query="algebra",
            filter_metadata={"$and": [{"student_id": "s1"}, {"outcome": "struggled"}]},
            k=5
        )

        assert len(results) >= 1
        assert all(r["metadata"]["student_id"] == "s1" for r in results)

    def test_get_by_session(self, vector_store):
        """Test retrieving all interactions from a session"""
        session_id = "session_123"

        vector_store.store("Question 1", {"session_id": session_id})
        vector_store.store("Question 2", {"session_id": session_id})
        vector_store.store("Question 3", {"session_id": "other_session"})

        results = vector_store.get_by_session(session_id)

        assert len(results) >= 2
        assert all(r["metadata"]["session_id"] == session_id for r in results)

    def test_get_stats(self, vector_store):
        """Test getting collection statistics"""
        vector_store.store("Test 1", {"type": "test"})
        vector_store.store("Test 2", {"type": "test"})

        stats = vector_store.get_stats()

        assert stats["total_documents"] >= 2
        assert "collection_name" in stats


class TestInteractionDocument:
    """Test InteractionDocument data class"""

    def test_document_creation(self):
        """Test creating InteractionDocument"""
        from backend.memory.vector_store import InteractionDocument

        doc = InteractionDocument(
            text="Test interaction",
            metadata={"key": "value"},
            doc_id="test_123"
        )

        assert doc.text == "Test interaction"
        assert doc.metadata["key"] == "value"
        assert doc.doc_id == "test_123"

    def test_document_to_dict(self):
        """Test converting document to dict"""
        from backend.memory.vector_store import InteractionDocument

        doc = InteractionDocument(
            text="Sample text",
            metadata={"session": "s1"}
        )

        doc_dict = doc.to_dict()

        assert doc_dict["text"] == "Sample text"
        assert doc_dict["metadata"]["session"] == "s1"
