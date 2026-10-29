import json
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

chunks = json.load(open("chunks.json"))
model = SentenceTransformer("BAAI/bge-small-en-v1.5")
client = QdrantClient("localhost", port=6333)

if client.collection_exists("filings"):
    client.delete_collection("filings")
client.create_collection(
    "filings",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
)

B = 64
for i in range(0, len(chunks), B):
    batch = chunks[i:i+B]
    vecs = model.encode([c["text"] for c in batch],
                        normalize_embeddings=True)
    client.upsert("filings", points=[
        PointStruct(id=i+j, vector=v.tolist(), payload=c)
        for j, (c, v) in enumerate(zip(batch, vecs))
    ])
    print(f"Stored {i+len(batch)}/{len(chunks)}")