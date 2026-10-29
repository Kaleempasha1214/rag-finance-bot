from llm import chat, GEN_MODEL
from retrieval import retrieve

SYSTEM = (
    "You answer questions about SEC 10-K filings using ONLY the numbered "
    "context passages. Cite passages like [1] or [2]. If the context does not "
    "contain the answer, reply exactly: I can't find this in the documents."
)

def ask(question, k=5, mode="dense"):
    ctx = retrieve(question, k, mode)
    context = "\n\n".join(
        f"[{i+1}] ({c['ticker']} 10-K filed {c['year']}, chunk {c['chunk_id']})\n{c['text']}"
        for i, c in enumerate(ctx))
    answer = chat(GEN_MODEL, SYSTEM,
                  f"Context:\n{context}\n\nQuestion: {question}")
    return {"answer": answer, "sources": ctx}

if __name__ == "__main__":
    out = ask("What are Apple's main risk factors?")
    print(out["answer"], "\n")
    for i, s in enumerate(out["sources"], 1):
        print(f"[{i}] {s['ticker']} {s['year']} chunk {s['chunk_id']}")