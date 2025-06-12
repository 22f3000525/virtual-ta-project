import faiss
import json
import numpy as np
import os

print(faiss.__version__)

def build_faiss_index(embedding_path, faiss_index_path):
    with open(embedding_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    embeddings = np.array(data["embeddings"]).astype("float32")
    index = faiss.IndexFlatL2(embeddings.shape[1])  # L2 = cosine-like distance

    print(f"Adding {len(embeddings)} vectors to index...")

    index.add(embeddings)

    # ✅ Create directory if it doesn't exist
    os.makedirs(os.path.dirname(faiss_index_path), exist_ok=True)

    faiss.write_index(index, faiss_index_path)
    print(f"✅ Saved FAISS index to {faiss_index_path}")

if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    
    build_faiss_index(
        os.path.join(base_dir, "../data/embeddings/course_embeddings.json"),
        os.path.join(base_dir, "../data/indexes/course_index.faiss")
    )

    build_faiss_index(
        os.path.join(base_dir, "../data/embeddings/discourse_embeddings.json"),
        os.path.join(base_dir, "../data/indexes/discourse_index.faiss")
    )
