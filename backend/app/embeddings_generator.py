"""
embeddings_generator.py
-----------------------
Generates text embeddings for PDF chunks using Sentence-Transformers.
Stores them in a local vector database (Chroma or FAISS).
"""

from typing import List, Dict
from sentence_transformers import SentenceTransformer
import numpy as np
import os
import pickle
import torch
import sys
import os


# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from pdf_processor import prepare_chunks_from_pdf


class EmbeddingGenerator:
    """
    Handles embedding generation and storage using PyTorch backend.
    """

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        print(f" Loading embedding model: {model_name}")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = SentenceTransformer(model_name, device=self.device)
        print(f" Model loaded on: {self.device.upper()}")

    def generate_embeddings(self, text_chunks: List[Dict]) -> List[Dict]:
        """
        Generates embeddings for each text chunk.

        Args:
            text_chunks (List[Dict]): List of dicts with 'text' key.

        Returns:
            List[Dict]: List with embeddings added.
        """
        print(" Generating embeddings...")
        embeddings_data = []

        for chunk in text_chunks:
            embedding = self.model.encode(chunk["text"], convert_to_numpy=True, show_progress_bar=False)
            embeddings_data.append({
                "page": chunk["page"],
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"],
                "embedding": embedding
            })

        print(f"Generated {len(embeddings_data)} embeddings.")
        return embeddings_data

    def save_embeddings(self, embeddings_data: List[Dict], output_path: str = "embeddings_store.pkl"):
        """
        Saves embeddings locally using pickle.
        """
        with open(output_path, "wb") as f:
            pickle.dump(embeddings_data, f)

        print(f" Embeddings saved to {output_path}")

    def load_embeddings(self, path: str = "embeddings_store.pkl") -> List[Dict]:
        """
        Loads saved embeddings from disk.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Embeddings file not found: {path}")

        with open(path, "rb") as f:
            data = pickle.load(f)

        print(f" Loaded {len(data)} embeddings from {path}")
        return data


# Example usage (standalone)
if __name__ == "__main__":
    pdf_path = "sample_pdf.pdf"
    chunks = prepare_chunks_from_pdf(pdf_path)

    emb_gen = EmbeddingGenerator()
    embeddings_data = emb_gen.generate_embeddings(chunks)
    emb_gen.save_embeddings(embeddings_data)