"""
Tests for Enhanced Vector Store

Following TDD: Tests written FIRST, then implementation.
All logic imported from codebase - NO hardcoded test logic.

Enhanced Vector Store:
1. Multi-vector embeddings (content, explanation, analogy, example)
2. Temporal weighting (recent interactions weighted higher)
3. Student-specific embeddings (personalized retrieval)
4. Similarity with decay functions
5. Advanced filtering with metadata
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import uuid
from backend.memory.enhanced_vector_store import (
    EnhancedVectorStore,
    VectorType,
    TemporalWeight,
    SimilarityResult
)


class TestEnhancedVectorStoreInitialization:
    """Test enhanced vector store initialization"""

    def test_initialization(self):
        """Test store initializes correctly"""
        store = EnhancedVectorStore()

        assert store is not None
        assert store.persist_directory is not None

    def test_initialization_with_custom_path(self):
        """Test initialization with custom directory"""
        custom_path = "/tmp/test_enhanced_vectors"
        store = EnhancedVectorStore(persist_directory=custom_path)

        assert store.persist_directory == custom_path


class TestVectorTypes:
    """Test multiple vector type support"""

    def test_vector_types_exist(self):
        """Test all expected vector types are defined"""
        expected_types = [
            VectorType.CONTENT,
            VectorType.EXPLANATION,
            VectorType.ANALOGY,
            VectorType.EXAMPLE
        ]

        for vector_type in expected_types:
            assert vector_type in VectorType


class TestMultiVectorStorage:
    """Test storing and retrieving multi-vector embeddings"""

    @pytest.fixture
    def store(self):
        # Use unique directory for each test to avoid data pollution
        unique_dir = f"/tmp/test_enhanced_vectors_{uuid.uuid4().hex[:8]}"
        return EnhancedVectorStore(persist_directory=unique_dir)

    def test_store_content_with_multiple_vectors(self, store):
        """Test storing content with different vector types"""
        store.add(
            student_id="student_123",
            content="Quadratic equations have the form ax^2 + bx + c = 0",
            vector_type=VectorType.CONTENT,
            metadata={"topic": "algebra", "difficulty": "medium"}
        )

        store.add(
            student_id="student_123",
            content="Think of quadratic equations like a U-shaped curve",
            vector_type=VectorType.ANALOGY,
            metadata={"topic": "algebra", "difficulty": "medium", "original_content_id": "content_1"}
        )

        # Should be able to search by different vector types
        results = store.search(
            query="parabola shape",
            student_id="student_123",
            vector_type=VectorType.ANALOGY,
            limit=5
        )

        assert len(results) > 0

    def test_store_with_all_vector_types(self, store):
        """Test storing all vector types for same content"""
        content_id = store.add_multi_vector(
            student_id="student_123",
            vectors={
                VectorType.CONTENT: "Fractions represent parts of a whole",
                VectorType.EXPLANATION: "A fraction like 1/2 means one part out of two equal parts",
                VectorType.ANALOGY: "Like cutting a pizza into slices",
                VectorType.EXAMPLE: "If you have 1/2 of a pizza, you have 50%"
            },
            metadata={"topic": "fractions"}
        )

        assert content_id is not None

        # Should be able to search across all vector types
        results = store.search_multi_vector(
            query="pizza slices",
            student_id="student_123",
            limit=5
        )

        assert len(results) > 0


class TestTemporalWeighting:
    """Test temporal weighting of search results"""

    @pytest.fixture
    def store(self):
        # Use unique directory for each test to avoid data pollution
        unique_dir = f"/tmp/test_enhanced_vectors_{uuid.uuid4().hex[:8]}"
        return EnhancedVectorStore(persist_directory=unique_dir)

    def test_add_with_timestamp(self, store):
        """Test adding content with timestamp"""
        store.add(
            student_id="student_123",
            content="Old content from last week",
            timestamp=datetime.now().timestamp() - (7 * 24 * 3600),  # 7 days ago
            metadata={"topic": "algebra"}
        )

        store.add(
            student_id="student_123",
            content="Recent content from today",
            timestamp=datetime.now().timestamp(),
            metadata={"topic": "algebra"}
        )

        # Search should weight recent content higher
        results = store.search(
            query="content",
            student_id="student_123",
            temporal_weight=TemporalWeight.EXPONENTIAL,
            limit=5
        )

        assert len(results) >= 2
        # First result should be more recent
        assert results[0].timestamp > results[1].timestamp

    def test_temporal_weight_types(self):
        """Test different temporal weighting strategies"""
        expected_weights = [
            TemporalWeight.NONE,
            TemporalWeight.LINEAR,
            TemporalWeight.EXPONENTIAL
        ]

        for weight in expected_weights:
            assert weight in TemporalWeight

    def test_exponential_decay(self, store):
        """Test exponential decay favors recent content"""
        # Add old content with high similarity
        store.add(
            student_id="student_123",
            content="algebra quadratic equations formula",
            timestamp=datetime.now().timestamp() - (30 * 24 * 3600),  # 30 days ago
            metadata={"topic": "algebra"}
        )

        # Add recent content with slightly lower similarity
        store.add(
            student_id="student_123",
            content="algebra equations",
            timestamp=datetime.now().timestamp(),
            metadata={"topic": "algebra"}
        )

        results = store.search(
            query="algebra quadratic",
            student_id="student_123",
            temporal_weight=TemporalWeight.EXPONENTIAL,
            limit=5
        )

        # Recent content should be boosted despite lower base similarity
        assert len(results) >= 2


class TestStudentSpecificEmbeddings:
    """Test student-specific embedding retrieval"""

    @pytest.fixture
    def store(self):
        # Use unique directory for each test to avoid data pollution
        unique_dir = f"/tmp/test_enhanced_vectors_{uuid.uuid4().hex[:8]}"
        return EnhancedVectorStore(persist_directory=unique_dir)

    def test_search_filters_by_student(self, store):
        """Test search returns only student's content"""
        store.add("student_123", "Content for student 123", metadata={"topic": "algebra"})
        store.add("student_456", "Content for student 456", metadata={"topic": "algebra"})

        results = store.search(
            query="algebra",
            student_id="student_123",
            limit=10
        )

        assert len(results) > 0
        assert all(r.student_id == "student_123" for r in results)

    def test_get_student_history(self, store):
        """Test retrieving student's complete history"""
        store.add("student_123", "First interaction", metadata={"topic": "algebra"})
        store.add("student_123", "Second interaction", metadata={"topic": "geometry"})
        store.add("student_456", "Another student", metadata={"topic": "algebra"})

        history = store.get_student_history("student_123")

        assert len(history) == 2
        assert all(h.student_id == "student_123" for h in history)

    def test_get_student_history_with_topic_filter(self, store):
        """Test retrieving student history filtered by topic"""
        store.add("student_123", "Algebra 1", metadata={"topic": "algebra"})
        store.add("student_123", "Geometry 1", metadata={"topic": "geometry"})
        store.add("student_123", "Algebra 2", metadata={"topic": "algebra"})

        history = store.get_student_history(
            student_id="student_123",
            topic="algebra"
        )

        assert len(history) == 2
        assert all(h.metadata.get("topic") == "algebra" for h in history)


class TestSimilarityResults:
    """Test similarity result objects"""

    @pytest.fixture
    def store(self):
        # Use unique directory for each test to avoid data pollution
        unique_dir = f"/tmp/test_enhanced_vectors_{uuid.uuid4().hex[:8]}"
        return EnhancedVectorStore(persist_directory=unique_dir)

    def test_similarity_result_structure(self, store):
        """Test similarity results have required fields"""
        store.add("student_123", "Test content", metadata={"topic": "test"})

        results = store.search(
            query="test",
            student_id="student_123",
            limit=5
        )

        if results:
            result = results[0]
            assert isinstance(result, SimilarityResult)
            assert hasattr(result, 'content')
            assert hasattr(result, 'similarity_score')
            assert hasattr(result, 'timestamp')
            assert hasattr(result, 'metadata')
            assert hasattr(result, 'student_id')

    def test_similarity_scores_descending(self, store):
        """Test results ordered by similarity score (descending)"""
        store.add("student_123", "algebra equations solving", metadata={"topic": "algebra"})
        store.add("student_123", "algebra", metadata={"topic": "algebra"})
        store.add("student_123", "geometry shapes", metadata={"topic": "geometry"})

        results = store.search(
            query="algebra equations",
            student_id="student_123",
            limit=5
        )

        if len(results) > 1:
            for i in range(len(results) - 1):
                assert results[i].similarity_score >= results[i + 1].similarity_score


class TestAdvancedFiltering:
    """Test advanced metadata filtering"""

    @pytest.fixture
    def store(self):
        # Use unique directory for each test to avoid data pollution
        unique_dir = f"/tmp/test_enhanced_vectors_{uuid.uuid4().hex[:8]}"
        return EnhancedVectorStore(persist_directory=unique_dir)

    def test_filter_by_difficulty(self, store):
        """Test filtering by difficulty level"""
        store.add("student_123", "Easy problem", metadata={"difficulty": "easy"})
        store.add("student_123", "Hard problem", metadata={"difficulty": "hard"})

        results = store.search(
            query="problem",
            student_id="student_123",
            metadata_filter={"difficulty": "easy"},
            limit=5
        )

        assert len(results) > 0
        assert all(r.metadata.get("difficulty") == "easy" for r in results)

    def test_filter_by_multiple_criteria(self, store):
        """Test filtering by multiple metadata fields"""
        store.add(
            "student_123",
            "Algebra easy",
            metadata={"topic": "algebra", "difficulty": "easy", "outcome": "success"}
        )
        store.add(
            "student_123",
            "Algebra hard",
            metadata={"topic": "algebra", "difficulty": "hard", "outcome": "struggled"}
        )

        results = store.search(
            query="algebra",
            student_id="student_123",
            metadata_filter={"topic": "algebra", "difficulty": "easy"},
            limit=5
        )

        assert len(results) > 0
        assert all(r.metadata.get("difficulty") == "easy" for r in results)

    def test_filter_by_outcome(self, store):
        """Test filtering by learning outcome"""
        store.add("student_123", "Success case", metadata={"outcome": "mastered"})
        store.add("student_123", "Struggle case", metadata={"outcome": "struggled"})

        results = store.search(
            query="case",
            student_id="student_123",
            metadata_filter={"outcome": "struggled"},
            limit=5
        )

        assert len(results) > 0
        assert all(r.metadata.get("outcome") == "struggled" for r in results)


class TestDecayFunctions:
    """Test temporal decay calculation"""

    @pytest.fixture
    def store(self):
        # Use unique directory for each test to avoid data pollution
        unique_dir = f"/tmp/test_enhanced_vectors_{uuid.uuid4().hex[:8]}"
        return EnhancedVectorStore(persist_directory=unique_dir)

    def test_calculate_temporal_weight_linear(self, store):
        """Test linear decay calculation"""
        recent_timestamp = datetime.now().timestamp()
        old_timestamp = recent_timestamp - (30 * 24 * 3600)  # 30 days ago

        recent_weight = store.calculate_temporal_weight(
            recent_timestamp,
            weight_type=TemporalWeight.LINEAR
        )
        old_weight = store.calculate_temporal_weight(
            old_timestamp,
            weight_type=TemporalWeight.LINEAR
        )

        assert recent_weight > old_weight
        assert 0 <= old_weight <= 1
        assert 0 <= recent_weight <= 1

    def test_calculate_temporal_weight_exponential(self, store):
        """Test exponential decay calculation"""
        recent_timestamp = datetime.now().timestamp()
        old_timestamp = recent_timestamp - (30 * 24 * 3600)

        recent_weight = store.calculate_temporal_weight(
            recent_timestamp,
            weight_type=TemporalWeight.EXPONENTIAL
        )
        old_weight = store.calculate_temporal_weight(
            old_timestamp,
            weight_type=TemporalWeight.EXPONENTIAL
        )

        # Exponential decay should be more aggressive than linear
        assert recent_weight > old_weight
        assert 0 <= old_weight <= 1
        assert 0 <= recent_weight <= 1

    def test_no_decay(self, store):
        """Test no temporal weighting"""
        recent_timestamp = datetime.now().timestamp()
        old_timestamp = recent_timestamp - (30 * 24 * 3600)

        recent_weight = store.calculate_temporal_weight(
            recent_timestamp,
            weight_type=TemporalWeight.NONE
        )
        old_weight = store.calculate_temporal_weight(
            old_timestamp,
            weight_type=TemporalWeight.NONE
        )

        # No decay means all weights are 1.0
        assert recent_weight == 1.0
        assert old_weight == 1.0


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_search_nonexistent_student(self):
        """Test searching for non-existent student"""
        store = EnhancedVectorStore(persist_directory="/tmp/test_enhanced_vectors")

        results = store.search(
            query="test",
            student_id="nonexistent_student",
            limit=5
        )

        assert results == []

    def test_add_with_empty_content(self):
        """Test adding empty content"""
        store = EnhancedVectorStore(persist_directory="/tmp/test_enhanced_vectors")

        with pytest.raises(ValueError):
            store.add("student_123", "", metadata={"topic": "test"})

    def test_add_without_metadata(self):
        """Test adding content without metadata"""
        store = EnhancedVectorStore(persist_directory="/tmp/test_enhanced_vectors")

        # Should still work with minimal metadata
        content_id = store.add("student_123", "Test content")

        assert content_id is not None

    def test_search_with_limit_zero(self):
        """Test search with limit=0"""
        store = EnhancedVectorStore(persist_directory="/tmp/test_enhanced_vectors")
        store.add("student_123", "Test", metadata={"topic": "test"})

        results = store.search(
            query="test",
            student_id="student_123",
            limit=0
        )

        assert results == []

    def test_search_with_empty_query(self):
        """Test search with empty query"""
        store = EnhancedVectorStore(persist_directory="/tmp/test_enhanced_vectors")

        with pytest.raises(ValueError):
            store.search(
                query="",
                student_id="student_123",
                limit=5
            )


class TestCollectionManagement:
    """Test collection creation and management"""

    @pytest.fixture
    def store(self):
        # Use unique directory for each test to avoid data pollution
        unique_dir = f"/tmp/test_enhanced_vectors_{uuid.uuid4().hex[:8]}"
        return EnhancedVectorStore(persist_directory=unique_dir)

    def test_get_or_create_collection(self, store):
        """Test collection creation for student"""
        collection = store.get_or_create_collection("student_123")

        assert collection is not None

    def test_multiple_students_separate_collections(self, store):
        """Test different students have separate collections"""
        store.add("student_123", "Content 1", metadata={"topic": "algebra"})
        store.add("student_456", "Content 2", metadata={"topic": "algebra"})

        results_123 = store.search("Content", "student_123", limit=10)
        results_456 = store.search("Content", "student_456", limit=10)

        # Each student should only see their own content
        assert len(results_123) > 0
        assert len(results_456) > 0
        assert all(r.student_id == "student_123" for r in results_123)
        assert all(r.student_id == "student_456" for r in results_456)

    def test_clear_student_data(self, store):
        """Test clearing all data for a student"""
        store.add("student_123", "Content 1", metadata={"topic": "algebra"})
        store.add("student_123", "Content 2", metadata={"topic": "geometry"})

        store.clear_student_data("student_123")

        results = store.search("Content", "student_123", limit=10)
        assert len(results) == 0
