"""
view_embeddings.py
------------------
Simple utility to inspect the contents of embeddings_store.pkl
"""

import pickle
import numpy as np

def view_embeddings(path="embeddings_store.pkl", show_text=True, limit=3):
    """
    Load and display embeddings data.

    Args:
        path (str): Path to the .pkl file.
        show_text (bool): Whether to print text content.
        limit (int): Number of records to display.
    """
    with open(path, "rb") as f:
        data = pickle.load(f)

    print(f"\n Loaded {len(data)} records from {path}\n")

    for i, record in enumerate(data[:limit], start=1):
        print(f"🔹 Record {i}")
        print(f"  Page: {record['page']} | Chunk ID: {record['chunk_id']}")
        print(f"  Embedding shape: {np.array(record['embedding']).shape}")
        if show_text:
            print(f"  Text: {record['text'][:200]}...")  # Print first 200 chars
        print("-" * 60)

if __name__ == "__main__":
    view_embeddings("embeddings_store.pkl", show_text=True, limit=5)
