"""
Knowledge Graph using NetworkX

Represents skills, prerequisites, and learning paths as a graph structure.
"""

import networkx as nx
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional, Set
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SkillEdgeType(Enum):
    """Types of edges in the knowledge graph"""
    PREREQUISITE = "prerequisite"
    SIMILARITY = "similarity"
    LEARNING_PATH = "learning_path"


@dataclass
class SkillNode:
    """Represents a skill node in the graph"""
    skill_id: str
    name: str
    grade_level: Optional[int] = None
    difficulty: Optional[float] = None
    description: Optional[str] = None


class KnowledgeGraph:
    """Graph-based representation of skills and learning paths"""

    def __init__(self):
        """Initialize knowledge graph"""
        self.graph = nx.DiGraph()  # Directed graph for prerequisites
        self.similarity_graph = nx.Graph()  # Undirected graph for similarities
        logger.info("Knowledge graph initialized")

    def add_skill_node(
        self,
        skill_id: str,
        name: str,
        grade_level: Optional[int] = None,
        difficulty: Optional[float] = None,
        description: Optional[str] = None
    ) -> None:
        """
        Add a skill node to the graph

        Args:
            skill_id: Unique identifier for the skill
            name: Human-readable name
            grade_level: Grade level (K=0, 1-12)
            difficulty: Difficulty score (0-1)
            description: Optional description
        """
        self.graph.add_node(
            skill_id,
            name=name,
            grade_level=grade_level,
            difficulty=difficulty,
            description=description
        )
        logger.info(f"Added skill node: {skill_id} - {name}")

    def has_skill(self, skill_id: str) -> bool:
        """Check if skill exists in graph"""
        return skill_id in self.graph.nodes

    def get_skill(self, skill_id: str) -> Optional[Dict]:
        """Get skill node data"""
        if skill_id in self.graph.nodes:
            return dict(self.graph.nodes[skill_id])
        return None

    def add_prerequisite_edge(self, from_skill: str, to_skill: str, weight: float = 1.0) -> None:
        """
        Add prerequisite relationship

        Args:
            from_skill: Prerequisite skill
            to_skill: Skill that requires the prerequisite
            weight: Importance of prerequisite (0-1)
        """
        self.graph.add_edge(
            from_skill,
            to_skill,
            edge_type=SkillEdgeType.PREREQUISITE.value,
            weight=weight
        )
        logger.info(f"Added prerequisite: {from_skill} -> {to_skill}")

    def add_similarity_edge(self, skill1: str, skill2: str, weight: float = 0.5) -> None:
        """
        Add similarity relationship between skills

        Args:
            skill1: First skill
            skill2: Second skill
            weight: Similarity score (0-1)
        """
        self.similarity_graph.add_edge(
            skill1,
            skill2,
            edge_type=SkillEdgeType.SIMILARITY.value,
            weight=weight
        )

    def get_prerequisites(self, skill_id: str) -> List[str]:
        """
        Get all prerequisites for a skill

        Args:
            skill_id: Skill to get prerequisites for

        Returns:
            List of prerequisite skill IDs
        """
        if skill_id not in self.graph:
            return []

        # Get all predecessors (skills that point to this skill)
        return list(self.graph.predecessors(skill_id))

    def find_prerequisite_gaps(
        self,
        current_skill: str,
        student_skills: Dict[str, float],
        threshold: float = 0.5
    ) -> List[Dict]:
        """
        Find prerequisite gaps for a student

        Args:
            current_skill: Skill student is working on
            student_skills: Dict mapping skill_id to mastery level (0-1)
            threshold: Minimum mastery level to consider "learned"

        Returns:
            List of prerequisite gaps with skill info
        """
        gaps = []

        # Get all prerequisites recursively
        prerequisites = self.get_prerequisites(current_skill)

        for prereq_skill in prerequisites:
            mastery = student_skills.get(prereq_skill, 0.0)

            if mastery < threshold:
                skill_data = self.get_skill(prereq_skill)
                gaps.append({
                    "skill_id": prereq_skill,
                    "name": skill_data.get("name", "Unknown") if skill_data else "Unknown",
                    "current_mastery": mastery,
                    "required_mastery": threshold,
                    "gap": threshold - mastery
                })

        # Sort by gap size (largest gaps first)
        gaps.sort(key=lambda x: x["gap"], reverse=True)

        logger.info(f"Found {len(gaps)} prerequisite gaps for {current_skill}")
        return gaps

    def get_learning_path(self, start_skill: str, end_skill: str) -> Optional[List[str]]:
        """
        Find learning path from start to end skill

        Args:
            start_skill: Starting skill
            end_skill: Goal skill

        Returns:
            List of skill IDs representing the path, or None if no path exists
        """
        try:
            path = nx.shortest_path(self.graph, start_skill, end_skill)
            return path
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

    def add_student_progress(
        self,
        student_id: str,
        skill_id: str,
        mastery_level: float,
        practice_count: int = 0
    ) -> None:
        """
        Track student progress on a skill

        Args:
            student_id: Student identifier
            skill_id: Skill identifier
            mastery_level: Current mastery (0-1)
            practice_count: Number of times practiced
        """
        # Store as node attribute
        if skill_id in self.graph.nodes:
            if "student_progress" not in self.graph.nodes[skill_id]:
                self.graph.nodes[skill_id]["student_progress"] = {}

            self.graph.nodes[skill_id]["student_progress"][student_id] = {
                "mastery_level": mastery_level,
                "practice_count": practice_count
            }

    def get_student_progress(self, student_id: str, skill_id: str) -> Optional[Dict]:
        """Get student's progress on a skill"""
        if skill_id in self.graph.nodes:
            progress = self.graph.nodes[skill_id].get("student_progress", {})
            return progress.get(student_id)
        return None

    def get_similar_skills(self, skill_id: str, threshold: float = 0.5) -> List[str]:
        """
        Get skills similar to the given skill

        Args:
            skill_id: Skill to find similar skills for
            threshold: Minimum similarity score

        Returns:
            List of similar skill IDs
        """
        if skill_id not in self.similarity_graph:
            return []

        similar = []
        for neighbor in self.similarity_graph.neighbors(skill_id):
            edge_data = self.similarity_graph[skill_id][neighbor]
            weight = edge_data.get("weight", 0.0)

            if weight >= threshold:
                similar.append(neighbor)

        return similar

    def get_stats(self) -> Dict:
        """Get statistics about the knowledge graph"""
        return {
            "total_skills": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "total_prerequisites": sum(
                1 for _, _, data in self.graph.edges(data=True)
                if data.get("edge_type") == SkillEdgeType.PREREQUISITE.value
            ),
            "total_similarities": self.similarity_graph.number_of_edges()
        }

    def integrate_with_dash_system(self, dash_system) -> None:
        """
        Integrate with existing DashSystem

        Args:
            dash_system: DashSystem instance
        """
        logger.info("Integrating knowledge graph with DashSystem...")

        # Import skills from DashSystem
        for skill_id, skill in dash_system.skills.items():
            self.add_skill_node(
                skill_id=skill_id,
                name=skill.name,
                grade_level=skill.grade_level.value if hasattr(skill.grade_level, 'value') else None,
                difficulty=skill.difficulty
            )

            # Add prerequisites
            for prereq_id in skill.prerequisites:
                if prereq_id in dash_system.skills:
                    self.add_prerequisite_edge(prereq_id, skill_id)

        logger.info(f"Integrated {len(dash_system.skills)} skills from DashSystem")
