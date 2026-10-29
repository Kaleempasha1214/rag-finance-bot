import json, re
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, CrossEncoder
from qdrant_client import QdrantClient

chunks = json.load(open("chunks.json"))
embedder = SentenceTransformer("BAAI/bge-small-en-v1.5")
client = QdrantClient("localhost", port=6333)
QP = "Represent this sentence for searching relevant passages: "

tok = lambda s: re.findall(r"\w+", s.lower())
bm25 = BM25Okapi([tok(c["text"]) for c in chunks])
_reranker = None

def dense_ids(q, n):
    vec = embedder.encode(QP + q, normalize_embeddings=True).tolist()
    return [p.id for p in client.query_points("filings", query=vec, limit=n).points]

def bm25_ids(q, n):
    s = bm25.get_scores(tok(q))
    return sorted(range(len(s)), key=lambda i: s[i], reverse=True)[:n]

def rrf(lists, k=60):
    score = {}
    for lst in lists:
        for rank, i in enumerate(lst):
            score[i] = score.get(i, 0) + 1 / (k + rank + 1)
    return sorted(score, key=score.get, reverse=True)

def retrieve(question, k=5, mode="dense"):
    global _reranker
    if mode == "dense":
        ids = dense_ids(question, k)
    elif mode == "hybrid":
        ids = rrf([dense_ids(question, 30), bm25_ids(question, 30)])[:k]
    elif mode == "rerank":
        if _reranker is None:
            _reranker = CrossEncoder("BAAI/bge-reranker-base")
        cand = rrf([dense_ids(question, 30), bm25_ids(question, 30)])[:20]
        sc = _reranker.predict([(question, chunks[i]["text"]) for i in cand])
        ids = [i for _, i in sorted(zip(sc, cand), key=lambda x: x[0], reverse=True)][:k]
    else:
        raise ValueError("unknown mode: " + mode)
    return [{"id": i, **chunks[i]} for i in ids]