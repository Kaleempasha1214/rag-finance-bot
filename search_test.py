import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

model = SentenceTransformer("BAAI/bge-small-en-v1.5")
client = QdrantClient("localhost", port=6333)

q = "Represent this sentence for searching relevant passages: " \
    "What are Apple's main risk factors?"
vec = model.encode(q, normalize_embeddings=True).tolist()

for r in client.query_points("filings", query=vec, limit=5).points:
    print(round(r.score, 3), r.payload["ticker"], r.payload["year"])
    print(r.payload["text"][:200], "\n")
client.close()