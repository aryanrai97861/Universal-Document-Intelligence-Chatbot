import chromadb
import os
from typing import List, Dict
from sentence_transformers import SentenceTransformer
import numpy as np


class VectorStore:
    """Handles vector storage and semantic search using ChromaDB"""

    def __init__(self, collection_name: str = "documents"):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection_name = collection_name
        self.collection = None

        # Use SentenceTransformers for local embeddings. Model can be configured
        # via the EMBEDDING_MODEL environment variable.
        model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        self.embed_model = SentenceTransformer(model_name)

        self._initialize_collection()

    def _initialize_collection(self):
        """Initialize or get existing collection"""
        try:
            # Try to get existing collection
            self.collection = self.client.get_collection(name=self.collection_name)
        except Exception:
            # Create new collection if it doesn't exist
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )

    def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using sentence-transformers

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        try:
            embeddings = self.embed_model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
            if isinstance(embeddings, np.ndarray):
                return embeddings.tolist()
            return [list(e) for e in embeddings]
        except Exception as e:
            raise Exception(f"Error generating embeddings: {str(e)}")

    def add_documents(self, chunks: List[Dict]):
        """
        Add document chunks to the vector store

        Args:
            chunks: List of document chunks with metadata
        """
        if not chunks:
            return

        try:
            # Prepare data for ChromaDB
            texts = [chunk['content'] for chunk in chunks]
            metadatas = [chunk['metadata'] for chunk in chunks]
            ids = [f"doc_{i}_{chunk['metadata'].get('filename','unknown')}_{chunk['metadata'].get('chunk_index', i)}"
                   for i, chunk in enumerate(chunks)]

            # Generate embeddings
            embeddings = self._get_embeddings(texts)

            # Add to collection
            if self.collection is not None:
                self.collection.add(
                    embeddings=embeddings,  # type: ignore
                    documents=texts,
                    metadatas=metadatas,
                    ids=ids
                )
            else:
                raise Exception("Collection not initialized")

        except Exception as e:
            raise Exception(f"Error adding documents to vector store: {str(e)}")

    def search(self, query: str, k: int = 5) -> List[Dict]:
        """
        Search for relevant documents

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of relevant documents with metadata
        """
        try:
            # Check if collection has any documents
            if self.collection is None:
                return []

            count = self.collection.count()
            if count == 0:
                return []

            # Generate query embedding
            query_embedding = self._get_embeddings([query])[0]

            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=min(k, count)
            )

            # Format results
            documents = []
            if results and results.get('documents') and results['documents'] and len(results['documents']) > 0 and results['documents'][0]:
                documents_list = results['documents'][0]
                metadatas_list = results.get('metadatas', [[]])[0] if results.get('metadatas') else []
                distances_list = results.get('distances', [[]])[0] if results.get('distances') else []
                ids_list = results.get('ids', [[]])[0] if results.get('ids') else []

                for i in range(len(documents_list)):
                    doc = {
                        'content': documents_list[i],
                        'metadata': metadatas_list[i] if i < len(metadatas_list) else {},
                        'distance': distances_list[i] if i < len(distances_list) else 0,
                        'id': ids_list[i] if i < len(ids_list) else f"doc_{i}"
                    }
                    documents.append(doc)

            return documents

        except Exception as e:
            raise Exception(f"Error searching vector store: {str(e)}")

    def clear(self):
        """Clear all documents from the vector store"""
        try:
            # Delete the collection
            self.client.delete_collection(name=self.collection_name)
            # Recreate empty collection
            self._initialize_collection()
        except Exception as e:
            raise Exception(f"Error clearing vector store: {str(e)}")

    def get_stats(self) -> Dict:
        """Get statistics about the vector store"""
        try:
            if self.collection is None:
                return {
                    'total_documents': 0,
                    'collection_name': self.collection_name,
                    'error': 'Collection not initialized'
                }

            count = self.collection.count()
            return {
                'total_documents': count,
                'collection_name': self.collection_name
            }
        except Exception as e:
            return {'error': str(e)}
