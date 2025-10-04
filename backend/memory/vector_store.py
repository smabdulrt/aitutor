"""
Vector Store using ChromaDB

Stores and retrieves tutoring interactions using semantic similarity.
"""

import chromadb
from chromadb.config import Settings
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
import uuid
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class InteractionDocument:
    """Represents a stored interaction document"""
    text: str
    metadata: Dict = field(default_factory=dict)
    doc_id: Optional[str] = None
    timestamp: Optional[float] = None

    def __post_init__(self):
        if self.doc_id is None:
            self.doc_id = str(uuid.uuid4())
        if self.timestamp is None:
            self.timestamp = datetime.now().timestamp()

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "text": self.text,
            "metadata": self.metadata,
            "doc_id": self.doc_id,
            "timestamp": self.timestamp
        }


class VectorStore:
    """ChromaDB-based vector store for tutoring interactions"""

    def __init__(self, persist_directory: str = "./chroma_db", collection_name: str = "tutoring_interactions"):
        """
        Initialize vector store

        Args:
            persist_directory: Directory to persist ChromaDB data
            collection_name: Name of the collection
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name

        # Initialize ChromaDB client with PersistentClient for testing compatibility
        self.client = chromadb.PersistentClient(
            path=persist_directory
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "AI Tutor teaching interactions"}
        )

        logger.info(f"Vector store initialized: {collection_name} at {persist_directory}")

    def store(self, text: str, metadata: Optional[Dict] = None) -> str:
        """
        Store an interaction in the vector database

        Args:
            text: Text content of the interaction
            metadata: Optional metadata (session_id, student_id, topic, etc.)

        Returns:
            Document ID
        """
        doc = InteractionDocument(text=text, metadata=metadata or {})

        # Add to ChromaDB
        self.collection.add(
            documents=[doc.text],
            metadatas=[doc.metadata],
            ids=[doc.doc_id]
        )

        logger.info(f"Stored interaction: {doc.doc_id} - {text[:50]}...")
        return doc.doc_id

    def similarity_search(
        self,
        query: str,
        k: int = 3,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search for similar interactions

        Args:
            query: Query text
            k: Number of results to return
            filter_metadata: Optional metadata filters

        Returns:
            List of matching documents with metadata
        """
        where_clause = filter_metadata if filter_metadata else None

        results = self.collection.query(
            query_texts=[query],
            n_results=k,
            where=where_clause
        )

        # Format results
        formatted_results = []
        if results and results['documents'] and len(results['documents']) > 0:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    "text": doc,
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "doc_id": results['ids'][0][i] if results['ids'] else None,
                    "distance": results['distances'][0][i] if results.get('distances') else None
                })

        logger.info(f"Similarity search for '{query[:30]}...' returned {len(formatted_results)} results")
        return formatted_results

    def get_by_session(self, session_id: str) -> List[Dict]:
        """
        Get all interactions from a specific session

        Args:
            session_id: Session identifier

        Returns:
            List of interactions from that session
        """
        results = self.collection.get(
            where={"session_id": session_id}
        )

        formatted_results = []
        if results and results['documents']:
            for i, doc in enumerate(results['documents']):
                formatted_results.append({
                    "text": doc,
                    "metadata": results['metadatas'][i] if results['metadatas'] else {},
                    "doc_id": results['ids'][i] if results['ids'] else None
                })

        return formatted_results

    def get_stats(self) -> Dict:
        """Get statistics about the vector store"""
        count = self.collection.count()

        return {
            "total_documents": count,
            "collection_name": self.collection_name,
            "persist_directory": self.persist_directory
        }

    def clear(self):
        """Clear all data from collection (use with caution!)"""
        # Delete and recreate collection
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.get_or_create_collection(name=self.collection_name)
        logger.warning(f"Cleared collection: {self.collection_name}")
