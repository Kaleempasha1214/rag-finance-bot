import json, random, re
from llm import chat, JUDGE_MODEL

NAMES = {"AAPL": "Apple", "MSFT": "Microsoft", "TSLA": "Tesla",
         "NVDA": "NVIDIA", "AMZN": "Amazon"}
norm = lambda s: re.sub(r"\W+", " ", s.lower()).strip()

chunks = json.load(open("chunks.json"))
random.seed(1)
pool = [c for c in chunks if len(c["text"].split()) >= 300]
random.shuffle(pool)

SYSTEM = ("You write test questions for a document Q&A system. Reply with "
          "JSON only, no other text.")
drafts = []
for c in pool[:90]:
    name = NAMES.get(c["ticker"], c["ticker"])
    prompt = (f"Passage from {name}'s 10-K filed in {c['year']}:\n{c['text']}\n\n"
              f"Write ONE specific question this passage answers. The question "
              f"must name {name} and the filing year {c['year']}. Give a short "
              f"correct answer, and an evidence phrase of 6-12 words copied "
              f"EXACTLY from the passage. If the passage is mostly tables or "
              f"boilerplate, return {{\"skip\": true}}. Otherwise return "
              f"{{\"question\": ..., \"answer\": ..., \"evidence\": ...}}")
    try:
        raw = chat(JUDGE_MODEL, SYSTEM, prompt)
        d = json.loads(raw[raw.index("{"): raw.rindex("}") + 1])
    except Exception:
        continue
    if d.get("skip") or not d.get("evidence"):
        continue
    if norm(d["evidence"]) not in norm(c["text"]):
        continue  # evidence was not a real quote, so drop it
    d.update(ticker=c["ticker"], year=c["year"], chunk_id=c["chunk_id"])
    d["passage"] = c["text"]
    drafts.append(d)
    print(len(drafts), d["question"])
    if len(drafts) >= 65:
        break

json.dump(drafts, open("draft_questions.json", "w"), indent=1)
with open("review.txt", "w", encoding="utf-8") as f:
    for i, d in enumerate(drafts):
        f.write(f"#{i}  Q: {d['question']}\nANSWER: {d['answer']}\n"
                f"EVIDENCE: {d['evidence']}\n\nPASSAGE: {d['passage']}\n"
                + "=" * 80 + "\n")