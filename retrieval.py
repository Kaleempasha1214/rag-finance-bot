import json
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

chunks = json.load(open("chunks.json"))
embedder = SentenceTransformer("BAAI/bge-small-en-v1.5")
client = QdrantClient("localhost", port=6333)
QP = "Represent this sentence for searching relevant passages: "

def retrieve(question, k=5, mode="dense"):
    vec = embedder.encode(QP + question, normalize_embeddings=True).tolist()
    pts = client.query_points("filings", query=vec, limit=k).points
    return [{"id": p.id, **chunks[p.id]} for p in pts]