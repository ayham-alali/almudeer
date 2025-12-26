"""
Al-Mudeer - Knowledge Base Service (RAG)
Manages vector storage (ChromaDB) and document retrieval.
"""

import os
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional, Any
from services.llm_provider import GeminiProvider, LLMConfig
import logging

logger = logging.getLogger(__name__)

class KnowledgeBase:
    _instance = None
    
    def __init__(self, persist_path: str = "./data/chroma_db"):
        self.persist_path = persist_path
        self.client = chromadb.PersistentClient(path=persist_path)
        
        # Use a single collection for simplicity
        self.collection = self.client.get_or_create_collection(
            name="almudeer_knowledge",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Initialize Gemini Provider for embeddings
        self.llm_provider = GeminiProvider(LLMConfig())
        
    @classmethod
    def get_instance(cls) -> "KnowledgeBase":
        if cls._instance is None:
            # Ensure data directory exists
            os.makedirs("./data", exist_ok=True)
            cls._instance = cls()
        return cls._instance

    async def add_document(self, text: str, metadata: Dict[str, Any] = None) -> bool:
        """
        Embed and store a document in the vector DB.
        """
        if not text:
            return False
            
        try:
            # 1. Generate ID
            import hashlib
            doc_id = hashlib.md5(text.encode()).hexdigest()
            
            # 2. Generate Embedding
            embedding = await self.llm_provider.embed_text(text)
            
            if not embedding:
                logger.error("Failed to generate embedding for document")
                return False
                
            # 3. Store in Chroma
            self.collection.upsert(
                ids=[doc_id],
                documents=[text],
                embeddings=[embedding],
                metadatas=[metadata or {}]
            )
            
            logger.info(f"Added document to KB: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding document to KB: {e}")
            return False

    async def search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        Search the KB for relevant documents.
        """
        if not query:
            return []
            
        try:
            # 1. Embed query
            embedding = await self.llm_provider.embed_text(query)
            
            if not embedding:
                return []
                
            # 2. Query Chroma
            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=k
            )
            
            # 3. Format results
            documents = results['documents'][0]
            metadatas = results['metadatas'][0]
            distances = results['distances'][0]
            
            formatted_results = []
            for i in range(len(documents)):
                # Filter by distance if needed (lower is better for cosine distance in Chroma?)
                # Actually Chroma default is l2, but we set cosine. Cosine distance = 1 - similarity.
                # So lower is better. Threshold e.g. 0.4
                if distances[i] < 0.5: 
                    formatted_results.append({
                        "text": documents[i],
                        "metadata": metadatas[i],
                        "score": distances[i]
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching KB: {e}")
            return []

    async def list_documents(self, limit: int = 100) -> List[Dict[str, Any]]:
        """List all documents in the KB"""
        try:
            # ChromaDB get() without ids returns all match
            data = self.collection.get(limit=limit, include=["metadatas", "documents"])
            
            formatted = []
            if data and data['ids']:
                for i in range(len(data['ids'])):
                    formatted.append({
                        "id": data['ids'][i],
                        "text": data['documents'][i],
                        "metadata": data['metadatas'][i] or {}
                    })
            return formatted
        except Exception as e:
            logger.error(f"Error listing KB docs: {e}")
            return []

# Singleton accessor
def get_knowledge_base() -> KnowledgeBase:
    return KnowledgeBase.get_instance()
