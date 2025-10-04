"""
Test suite for Knowledge Graph (NetworkX)

CRITICAL: Tests ONLY import from codebase and verify behavior.
NO logic hardcoded - we test the actual implementation.
"""

import pytest
from backend.memory.knowledge_graph import KnowledgeGraph, SkillNode, SkillEdgeType


class TestKnowledgeGraph:
    """Test KnowledgeGraph - imports from backend, no hardcoding"""

    @pytest.fixture
    def graph(self):
        """Create KnowledgeGraph instance for testing"""
        return KnowledgeGraph()

    def test_initialization(self, graph):
        """Test knowledge graph initializes correctly"""
        assert graph is not None
        assert graph.graph is not None

    def test_add_skill_node(self, graph):
        """Test adding a skill node"""
        graph.add_skill_node(
            skill_id="addition",
            name="Basic Addition",
            grade_level=1,
            difficulty=0.3
        )

        assert graph.has_skill("addition")
        node_data = graph.get_skill("addition")
        assert node_data["name"] == "Basic Addition"
        assert node_data["grade_level"] == 1

    def test_add_prerequisite_edge(self, graph):
        """Test adding prerequisite relationships"""
        graph.add_skill_node("counting", name="Counting", grade_level=0)
        graph.add_skill_node("addition", name="Addition", grade_level=1)

        graph.add_prerequisite_edge("counting", "addition")

        prerequisites = graph.get_prerequisites("addition")
        assert "counting" in prerequisites

    def test_find_prerequisite_gaps(self, graph):
        """Test finding missing prerequisites for a student"""
        # Build skill tree
        graph.add_skill_node("counting", name="Counting")
        graph.add_skill_node("addition", name="Addition")
        graph.add_skill_node("subtraction", name="Subtraction")
        graph.add_skill_node("multiplication", name="Multiplication")

        graph.add_prerequisite_edge("counting", "addition")
        graph.add_prerequisite_edge("counting", "subtraction")
        graph.add_prerequisite_edge("addition", "multiplication")
        graph.add_prerequisite_edge("subtraction", "multiplication")

        # Student has weak counting skill
        student_skills = {
            "counting": 0.4,  # Weak
            "addition": 0.7,
            "subtraction": 0.6
        }

        gaps = graph.find_prerequisite_gaps(
            current_skill="multiplication",
            student_skills=student_skills,
            threshold=0.5
        )

        # Should identify counting as a gap
        assert any(gap["skill_id"] == "counting" for gap in gaps)

    def test_get_learning_path(self, graph):
        """Test finding learning path between skills"""
        graph.add_skill_node("a", name="A")
        graph.add_skill_node("b", name="B")
        graph.add_skill_node("c", name="C")

        graph.add_prerequisite_edge("a", "b")
        graph.add_prerequisite_edge("b", "c")

        path = graph.get_learning_path("a", "c")

        assert path is not None
        assert path[0] == "a"
        assert path[-1] == "c"

    def test_add_student_progress(self, graph):
        """Test tracking student progress on a skill"""
        graph.add_skill_node("fractions", name="Fractions")

        graph.add_student_progress(
            student_id="student_1",
            skill_id="fractions",
            mastery_level=0.75,
            practice_count=10
        )

        progress = graph.get_student_progress("student_1", "fractions")

        assert progress["mastery_level"] == 0.75
        assert progress["practice_count"] == 10

    def test_get_similar_skills(self, graph):
        """Test finding similar skills"""
        graph.add_skill_node("add_fractions", name="Add Fractions", difficulty=0.6)
        graph.add_skill_node("subtract_fractions", name="Subtract Fractions", difficulty=0.6)
        graph.add_skill_node("multiply_integers", name="Multiply Integers", difficulty=0.4)

        graph.add_similarity_edge("add_fractions", "subtract_fractions", weight=0.9)

        similar = graph.get_similar_skills("add_fractions", threshold=0.8)

        assert "subtract_fractions" in similar

    def test_get_stats(self, graph):
        """Test getting graph statistics"""
        graph.add_skill_node("skill1", name="Skill 1")
        graph.add_skill_node("skill2", name="Skill 2")
        graph.add_prerequisite_edge("skill1", "skill2")

        stats = graph.get_stats()

        assert stats["total_skills"] >= 2
        assert stats["total_edges"] >= 1


class TestSkillNode:
    """Test SkillNode data class"""

    def test_node_creation(self):
        """Test creating SkillNode"""
        from backend.memory.knowledge_graph import SkillNode

        node = SkillNode(
            skill_id="test_skill",
            name="Test Skill",
            grade_level=5,
            difficulty=0.7
        )

        assert node.skill_id == "test_skill"
        assert node.name == "Test Skill"
        assert node.grade_level == 5
        assert node.difficulty == 0.7


class TestSkillEdgeType:
    """Test SkillEdgeType enum"""

    def test_edge_types(self):
        """Test edge type enum values"""
        from backend.memory.knowledge_graph import SkillEdgeType

        assert SkillEdgeType.PREREQUISITE.value == "prerequisite"
        assert SkillEdgeType.SIMILARITY.value == "similarity"
        assert SkillEdgeType.LEARNING_PATH.value == "learning_path"
