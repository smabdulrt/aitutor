"""
Enhanced Vector Store for Multi-Vector Embeddings and Temporal Weighting

This module extends the basic VectorStore with:
1. Multi-vector embeddings (content, explanation, analogy, example)
2. Temporal weighting for recent interactions
3. Student-specific collections
4. Advanced similarity search with decay functions
"""

import chromadb
from chromadb.config import Settings
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional, Union
from datetime import datetime
import logging
import math
import uuid

logger = logging.getLogger(__name__)


class VectorType(str, Enum):
    """Types of vector embeddings"""
    CONTENT = "content"
    EXPLANATION = "explanation"
    ANALOGY = "analogy"
    EXAMPLE = "example"


class TemporalWeight(str, Enum):
    """Temporal weighting strategies"""
    NONE = "none"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"


@dataclass
class SimilarityResult:
    """Result from similarity search"""
    content: str
    similarity_score: float
    timestamp: float
    metadata: Dict
    student_id: str
    vector_type: Optional[VectorType] = None


class EnhancedVectorStore:
    """
    Enhanced vector store with multi-vector embeddings and temporal weighting
    """

    def __init__(
        self,
        persist_directory: str = "./enhanced_chroma_db",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize enhanced vector store

        Args:
            persist_directory: Directory for persistent storage
            embedding_model: Sentence transformer model name
        """
        self.persist_directory = persist_directory
        self.embedding_model = embedding_model
        self.client = chromadb.PersistentClient(path=persist_directory)

        logger.info(f"Enhanced vector store initialized at {persist_directory}")

    def get_or_create_collection(self, student_id: str, vector_type: VectorType = VectorType.CONTENT):
        """
        Get or create collection for student and vector type

        Args:
            student_id: Student identifier
            vector_type: Type of vector embedding

        Returns:
            ChromaDB collection
        """
        collection_name = f"{student_id}_{vector_type.value}"

        try:
            collection = self.client.get_collection(name=collection_name)
            logger.debug(f"Retrieved existing collection: {collection_name}")
        except:
            collection = self.client.create_collection(
                name=collection_name,
                metadata={"student_id": student_id, "vector_type": vector_type.value}
            )
            logger.info(f"Created new collection: {collection_name}")

        return collection

    def add(
        self,
        student_id: str,
        content: str,
        vector_type: VectorType = VectorType.CONTENT,
        metadata: Optional[Dict] = None,
        timestamp: Optional[float] = None
    ) -> str:
        """
        Add content to vector store

        Args:
            student_id: Student identifier
            content: Content text to embed
            vector_type: Type of vector embedding
            metadata: Optional metadata
            timestamp: Optional timestamp (defaults to now)

        Returns:
            Content ID

        Raises:
            ValueError: If content is empty
        """
        if not content or not content.strip():
            raise ValueError("Content cannot be empty")

        content_id = str(uuid.uuid4())
        timestamp = timestamp or datetime.now().timestamp()

        # Prepare metadata
        meta = metadata.copy() if metadata else {}
        meta.update({
            "student_id": student_id,
            "vector_type": vector_type.value,
            "timestamp": timestamp
        })

        # Get collection
        collection = self.get_or_create_collection(student_id, vector_type)

        # Add to collection
        collection.add(
            documents=[content],
            metadatas=[meta],
            ids=[content_id]
        )

        logger.debug(f"Added content {content_id} for student {student_id} (type: {vector_type.value})")
        return content_id

    def add_multi_vector(
        self,
        student_id: str,
        vectors: Dict[VectorType, str],
        metadata: Optional[Dict] = None,
        timestamp: Optional[float] = None
    ) -> str:
        """
        Add content with multiple vector types

        Args:
            student_id: Student identifier
            vectors: Dict mapping VectorType to content text
            metadata: Optional metadata
            timestamp: Optional timestamp

        Returns:
            Base content ID
        """
        base_id = str(uuid.uuid4())
        timestamp = timestamp or datetime.now().timestamp()

        # Add base metadata
        meta = metadata.copy() if metadata else {}
        meta["base_id"] = base_id

        # Add each vector type
        for vector_type, content in vectors.items():
            self.add(
                student_id=student_id,
                content=content,
                vector_type=vector_type,
                metadata=meta,
                timestamp=timestamp
            )

        logger.info(f"Added multi-vector content {base_id} with {len(vectors)} vector types")
        return base_id

    def search(
        self,
        query: str,
        student_id: str,
        vector_type: VectorType = VectorType.CONTENT,
        limit: int = 5,
        metadata_filter: Optional[Dict] = None,
        temporal_weight: TemporalWeight = TemporalWeight.NONE
    ) -> List[SimilarityResult]:
        """
        Search for similar content

        Args:
            query: Query text
            student_id: Student identifier
            vector_type: Type of vector to search
            limit: Maximum results to return
            metadata_filter: Optional metadata filters
            temporal_weight: Temporal weighting strategy

        Returns:
            List of similarity results

        Raises:
            ValueError: If query is empty or limit is invalid
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        if limit == 0:
            return []

        # Get collection
        collection = self.get_or_create_collection(student_id, vector_type)

        # Build where clause
        where_conditions = [{"student_id": student_id}]

        if metadata_filter:
            # Add each filter condition
            for key, value in metadata_filter.items():
                where_conditions.append({key: value})

        # Build final where clause
        if len(where_conditions) == 1:
            where = where_conditions[0]
        else:
            where = {"$and": where_conditions}

        # Query collection
        try:
            results = collection.query(
                query_texts=[query],
                n_results=limit,
                where=where
            )
        except Exception as e:
            logger.warning(f"Query failed: {e}, returning empty results")
            return []

        # Convert to SimilarityResult objects
        similarity_results = []

        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i]
                distance = results['distances'][0][i] if 'distances' in results and results['distances'] else 0.0

                # Convert distance to similarity (ChromaDB uses L2 distance)
                similarity = 1.0 / (1.0 + distance)

                # Apply temporal weighting
                timestamp = metadata.get('timestamp', datetime.now().timestamp())
                temporal_multiplier = self.calculate_temporal_weight(timestamp, temporal_weight)
                weighted_similarity = similarity * temporal_multiplier

                result = SimilarityResult(
                    content=doc,
                    similarity_score=weighted_similarity,
                    timestamp=timestamp,
                    metadata=metadata,
                    student_id=student_id,
                    vector_type=vector_type
                )
                similarity_results.append(result)

        # Sort by weighted similarity (descending)
        similarity_results.sort(key=lambda x: x.similarity_score, reverse=True)

        logger.debug(f"Found {len(similarity_results)} results for query (student: {student_id})")
        return similarity_results

    def search_multi_vector(
        self,
        query: str,
        student_id: str,
        limit: int = 5,
        metadata_filter: Optional[Dict] = None,
        temporal_weight: TemporalWeight = TemporalWeight.NONE
    ) -> List[SimilarityResult]:
        """
        Search across all vector types

        Args:
            query: Query text
            student_id: Student identifier
            limit: Maximum results to return
            metadata_filter: Optional metadata filters
            temporal_weight: Temporal weighting strategy

        Returns:
            Combined and sorted results from all vector types
        """
        all_results = []

        # Search each vector type
        for vector_type in VectorType:
            results = self.search(
                query=query,
                student_id=student_id,
                vector_type=vector_type,
                limit=limit,
                metadata_filter=metadata_filter,
                temporal_weight=temporal_weight
            )
            all_results.extend(results)

        # Sort by similarity and return top results
        all_results.sort(key=lambda x: x.similarity_score, reverse=True)
        return all_results[:limit]

    def get_student_history(
        self,
        student_id: str,
        topic: Optional[str] = None,
        vector_type: VectorType = VectorType.CONTENT
    ) -> List[SimilarityResult]:
        """
        Get student's complete history

        Args:
            student_id: Student identifier
            topic: Optional topic filter
            vector_type: Type of vectors to retrieve

        Returns:
            List of all content for student
        """
        collection = self.get_or_create_collection(student_id, vector_type)

        # Build where clause
        if topic:
            where = {"$and": [{"student_id": student_id}, {"topic": topic}]}
        else:
            where = {"student_id": student_id}

        try:
            # Get all documents
            results = collection.get(where=where)

            history = []
            if results['documents']:
                for i, doc in enumerate(results['documents']):
                    metadata = results['metadatas'][i]
                    result = SimilarityResult(
                        content=doc,
                        similarity_score=1.0,  # No similarity score for history
                        timestamp=metadata.get('timestamp', 0.0),
                        metadata=metadata,
                        student_id=student_id,
                        vector_type=vector_type
                    )
                    history.append(result)

            # Sort by timestamp (most recent first)
            history.sort(key=lambda x: x.timestamp, reverse=True)

            logger.debug(f"Retrieved {len(history)} history items for student {student_id}")
            return history

        except Exception as e:
            logger.warning(f"Failed to retrieve history: {e}")
            return []

    def calculate_temporal_weight(
        self,
        timestamp: float,
        weight_type: TemporalWeight,
        half_life_days: float = 30.0
    ) -> float:
        """
        Calculate temporal weight for a timestamp

        Args:
            timestamp: Unix timestamp
            weight_type: Weighting strategy
            half_life_days: Half-life for exponential decay (days)

        Returns:
            Weight multiplier between 0 and 1
        """
        if weight_type == TemporalWeight.NONE:
            return 1.0

        # Calculate age in days
        now = datetime.now().timestamp()
        age_seconds = now - timestamp
        age_days = age_seconds / (24 * 3600)

        if age_days < 0:
            age_days = 0

        if weight_type == TemporalWeight.LINEAR:
            # Linear decay over 90 days
            max_age = 90.0
            weight = max(0.0, 1.0 - (age_days / max_age))
            return weight

        elif weight_type == TemporalWeight.EXPONENTIAL:
            # Exponential decay with half-life
            decay_constant = math.log(2) / half_life_days
            weight = math.exp(-decay_constant * age_days)
            return weight

        return 1.0

    def clear_student_data(self, student_id: str):
        """
        Clear all data for a student

        Args:
            student_id: Student identifier
        """
        # Delete all collections for this student
        for vector_type in VectorType:
            collection_name = f"{student_id}_{vector_type.value}"
            try:
                self.client.delete_collection(name=collection_name)
                logger.info(f"Deleted collection {collection_name}")
            except Exception as e:
                logger.debug(f"Collection {collection_name} does not exist or cannot be deleted: {e}")

        logger.info(f"Cleared all data for student {student_id}")
