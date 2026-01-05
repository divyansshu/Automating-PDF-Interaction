"""
rag_pipeline.py
---------------
Implements the Retrieval-Augmented Generation (RAG) pipeline.
Uses LangChain and HuggingFace to answer user queries based on PDF context.
"""

import os
import sys
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Import our local vector store helper
from backend.app.vector_store import load_index, load_metadata, search_index, _FAISS_AVAILABLE

# Load environment variables
load_dotenv()

class RAGPipeline:
    def __init__(self, 
                 index_path: str = "faiss_index.idx", 
                 meta_path: str = "meta_store.pkl",
                 model_repo_id: str = "meta-llama/Llama-3.1-8B-Instruct"):
        """
        Initialize the RAG pipeline.
        """
        self.index_path = index_path
        self.meta_path = meta_path
        self.repo_id = model_repo_id
        
        # Load Vector Store
        try:
            self.metadata = load_metadata(meta_path)
            if _FAISS_AVAILABLE:
                self.index = load_index(index_path)
            else:
                self.index = None # Fallback to in-memory search
        except FileNotFoundError:
            print(" Vector store not found. Please upload a PDF first.")
            self.index = None
            self.metadata = []

        # Initialize Inference Client (API)
        hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
        if not hf_token:
            print(" HUGGINGFACEHUB_API_TOKEN not found in .env. LLM might fail.")
        
        try:
            print(f"Loading Inference Client for: {self.repo_id}")
            from huggingface_hub import InferenceClient
            self.client = InferenceClient(
                model=self.repo_id,
                token=hf_token
            )
            print(" Inference Client initialized.")
        except Exception as e:
            print(f" Failed to initialize Client: {e}")
            self.client = None

    def reload_index(self):
        """Reloads the index and metadata (useful after a new upload)."""
        try:
            self.metadata = load_metadata(self.meta_path)
            if _FAISS_AVAILABLE:
                self.index = load_index(self.index_path)
            else:
                self.index = None
            print(" RAG Pipeline: Index reloaded.")
        except Exception as e:
            print(f" Could not reload index: {e}")

    def retrieve_context(self, query: str, top_k: int = 3) -> List[str]:
        """
        Retrieves relevant text chunks for the query.
        """
        if not self.metadata:
            return []
            
        from backend.app.embeddings_generator import EmbeddingGenerator
        if not hasattr(self, 'embedder'):
             self.embedder = EmbeddingGenerator()

        query_embedding = self.embedder.model.encode(query, convert_to_numpy=True)
        
        results = search_index(query_embedding, self.index, self.metadata, top_k=top_k)
        
        # Extract text from results
        context_chunks = [res[0]['text'] for res in results]
        return context_chunks

    def answer_query(self, query: str) -> str:
        """
        End-to-end RAG: Retrieve context -> Generate Answer using Chat Completion.
        """
        if not self.client:
            return "Error: Client not initialized. Check API token."

        # 1. Retrieve
        context_chunks = self.retrieve_context(query)
        if not context_chunks:
            return "I couldn't find any relevant information in the uploaded PDF."
        
        context_str = "\n\n".join(context_chunks)
        
        # 2. Generate using Chat Completion API
        # This avoids the "text-generation" task restriction
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant. Answer the question based on the context provided below."
            },
            {
                "role": "user",
                "content": f"Context:\n{context_str}\n\nQuestion:\n{query}"
            }
        ]
        
        try:
            response = self.client.chat_completion(
                messages=messages,
                max_tokens=512,
                temperature=0.5
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error generating answer: {e}"

if __name__ == "__main__":
    # Test run
    rag = RAGPipeline()
    print(rag.answer_query("What is this document about?"))
