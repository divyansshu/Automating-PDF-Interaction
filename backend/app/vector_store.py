"""
vector_store.py
---------------
FAISS-based vector store helper for storing/searching embeddings.
Falls back to a basic in-memory search if FAISS is not available.
Saves/loads index and metadata (pickle) for persistence.

Functions:
- build_faiss_index(embeddings, index_path, meta_path)
- add_embeddings_to_index(embeddings_list, index, metadata_list)
- save_index(index, index_path)
- load_index(index_path)
- save_metadata(metadata_list, meta_path)
- load_metadata(meta_path)
- search_index(query_vec, index, metadata_list, top_k=5)
"""

import os
import pickle
import numpy as np

# Try to import faiss; if not available, fallback to in-memory
try:
    import faiss
    _FAISS_AVAILABLE = True
except Exception:
    faiss = None
    _FAISS_AVAILABLE = False
    print("Warning: FAISS not available. Falling back to in-memory search (slower).")

# ---------------------------
# Persistence helpers
# ---------------------------
def save_metadata(metadata_list, meta_path="meta_store.pkl"):
    with open(meta_path, "wb") as f:
        pickle.dump(metadata_list, f)
    print(f"💾 Saved metadata to {meta_path}")


def load_metadata(meta_path="meta_store.pkl"):
    if not os.path.exists(meta_path):
        raise FileNotFoundError(f"Metadata file not found: {meta_path}")
    with open(meta_path, "rb") as f:
        metadata_list = pickle.load(f)
    print(f"📦 Loaded {len(metadata_list)} metadata records from {meta_path}")
    return metadata_list


def save_index(index, index_path="faiss_index.idx"):
    if not _FAISS_AVAILABLE:
        raise RuntimeError("FAISS not available; cannot save FAISS index.")
    faiss.write_index(index, index_path)
    print(f"💾 FAISS index saved to {index_path}")


def load_index(index_path="faiss_index.idx"):
    if not _FAISS_AVAILABLE:
        raise RuntimeError("FAISS not available; cannot load FAISS index.")
    if not os.path.exists(index_path):
        raise FileNotFoundError(f"FAISS index file not found: {index_path}")
    index = faiss.read_index(index_path)
    print(f"📦 FAISS index loaded from {index_path}")
    return index


# ---------------------------
# Build index from embeddings
# ---------------------------
def build_faiss_index(embeddings: np.ndarray, normalize: bool = True):
    """
    Create a FAISS flat (inner-product) index from embeddings.
    Args:
        embeddings: numpy array shape (n, d)
        normalize: if True, L2-normalize embeddings (useful for cosine similarity)
    Returns:
        faiss.Index object
    """
    if not _FAISS_AVAILABLE:
        raise RuntimeError("FAISS not available in environment.")

    if embeddings.ndim != 2:
        raise ValueError("Embeddings must be a 2D numpy array (n_samples, dim)")

    n, d = embeddings.shape
    # Normalize for cosine similarity if requested
    if normalize:
        faiss.normalize_L2(embeddings)

    # Use IndexFlatIP (inner product on normalized vectors = cosine similarity)
    index = faiss.IndexFlatIP(d)
    index.add(embeddings.astype(np.float32))
    print(f"✅ Built FAISS index with {index.ntotal} vectors (dim={d})")
    return index


# ---------------------------
# Add embeddings to existing index (and metadata)
# ---------------------------
def add_embeddings_to_index(embeddings_list, metadata_list, index=None, normalize=True):
    """
    Add embeddings (list of numpy arrays or stacked array) and metadata to a FAISS index.
    If index is None and FAISS is available, it will create a new FAISS index.
    Returns: index (faiss.Index or None), combined_metadata_list
    """
    # Prepare numpy array
    if isinstance(embeddings_list, list):
        embeddings = np.stack(embeddings_list, axis=0)
    else:
        embeddings = np.asarray(embeddings_list)

    if _FAISS_AVAILABLE:
        if index is None:
            index = build_faiss_index(embeddings, normalize=normalize)
        else:
            if normalize:
                faiss.normalize_L2(embeddings)
            index.add(embeddings.astype(np.float32))
            print(f"✅ Added {embeddings.shape[0]} vectors to existing FAISS index (total={index.ntotal})")
        return index, metadata_list
    else:
        # In-memory fallback: return None index and metadata combined
        print("⚠️ FAISS not available — using in-memory storage for search. Memory usage may be high.")
        return None, metadata_list


# ---------------------------
# Search
# ---------------------------
def search_index(query_vec: np.ndarray, index, metadata_list, top_k: int = 5, normalize: bool = True):
    """
    Search FAISS index (or in-memory fallback) for top_k nearest neighbors.
    Args:
        query_vec: numpy array shape (d,) or (1,d)
        index: faiss.Index or None (for in-memory fallback)
        metadata_list: list of metadata dicts corresponding to vectors order
        top_k: number of top results
    Returns:
        List of tuples: (metadata, score)
    """
    if isinstance(query_vec, list):
        query_vec = np.array(query_vec)

    if query_vec.ndim == 1:
        query_vec = query_vec.reshape(1, -1)

    # Normalize if needed
    if normalize and _FAISS_AVAILABLE:
        faiss.normalize_L2(query_vec)

    if _FAISS_AVAILABLE and index is not None:
        # perform search
        distances, indices = index.search(query_vec.astype(np.float32), top_k)
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < 0 or idx >= len(metadata_list):
                continue
            meta = metadata_list[idx]
            score = float(dist)  # inner product or similarity
            results.append((meta, score))
        return results
    else:
        # In-memory brute-force search using cosine similarity
        # Build matrix from metadata embeddings if available
        matrix = []
        for rec in metadata_list:
            vec = rec.get("embedding")
            if vec is None:
                raise ValueError("Metadata records must contain 'embedding' for in-memory search fallback.")
            matrix.append(np.asarray(vec))
        matrix = np.stack(matrix, axis=0)  # shape (n, d)

        # normalize
        if normalize:
            matrix = matrix / (np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-12)
            q = query_vec / (np.linalg.norm(query_vec, axis=1, keepdims=True) + 1e-12)
        else:
            q = query_vec

        sims = (matrix @ q.T).squeeze(axis=1)  # cosine sim if normalized
        # get top_k indices
        top_idx = np.argsort(-sims)[:top_k]
        results = []
        for idx in top_idx:
            results.append((metadata_list[int(idx)], float(sims[int(idx)])))
        return results


# ---------------------------
# Example usage helper
# ---------------------------
if __name__ == "__main__":
    # Quick demo (requires an embeddings_store.pkl created by embeddings_generator)
    EMB_PATH = "embeddings_store.pkl"
    META_PATH = "meta_store.pkl"
    IDX_PATH = "faiss_index.idx"

    if not os.path.exists(EMB_PATH):
        print("Place embeddings_store.pkl in the current folder (format: list of dicts with 'embedding' key).")
    else:
        with open(EMB_PATH, "rb") as f:
            embeddings_data = pickle.load(f)

        # Build numpy array and metadata list
        vectors = []
        metadatas = []
        for rec in embeddings_data:
            vectors.append(np.asarray(rec["embedding"], dtype=np.float32))
            # keep text + page + chunk_id in metadata
            metadatas.append({
                "page": rec.get("page"),
                "chunk_id": rec.get("chunk_id"),
                "text": rec.get("text"),
                "source": rec.get("source", None)
            })

        vectors = np.stack(vectors, axis=0)
        if _FAISS_AVAILABLE:
            idx = build_faiss_index(vectors)
            save_index(idx, IDX_PATH)
            save_metadata(metadatas, META_PATH)
            print("FAISS index built and saved.")
        else:
            # fallback: just save metadata (embeddings included)
            save_metadata(embeddings_data, META_PATH)
            print("FAISS not available: metadata saved with embeddings for in-memory search.")
