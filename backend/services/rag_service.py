# backend/services/rag_service.py
import json
import os
from typing import List, Dict
import chromadb
from chromadb.utils import embedding_functions
from ..config import config

class RAGService:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./backend/chroma_db")
        
        # Use a simple default embedding function if no specific one is configured
        # In a production env with OpenAI, you'd use OpenAIEmbeddingFunction
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        
        self.collection = self.client.get_or_create_collection(
            name="travel_knowledge",
            embedding_function=self.embedding_fn
        )

    def ingest_data(self, file_path: str = "backend/data/travel_knowledge.json"):
        """
        Ingests data from a JSON file into the vector database.
        """
        try:
            if not os.path.exists(file_path):
                print(f"Data file not found: {file_path}")
                return False

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            ids = []
            documents = []
            metadatas = []

            for item in data:
                ids.append(item["id"])
                documents.append(item["content"])
                metadatas.append({
                    "category": item["category"],
                    "tags": ",".join(item["tags"])
                })

            if ids:
                self.collection.upsert(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas
                )
                print(f"Successfully ingested {len(ids)} items into RAG.")
                return True
            return False

        except Exception as e:
            print(f"Error ingesting data: {e}")
            return False

    def query(self, query_text: str, n_results: int = 3) -> List[str]:
        """
        Retrieves relevant documents based on the query.
        """
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            
            # results['documents'] is a list of lists (one list per query)
            if results and results['documents']:
                return results['documents'][0]
            return []

        except Exception as e:
            print(f"Error querying RAG: {e}")
            return []

# Singleton instance
rag_service = RAGService()
