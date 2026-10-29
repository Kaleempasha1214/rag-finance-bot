import json, re, sys, time, os
from retrieval import retrieve

mode = sys.argv[1] if len(sys.argv) > 1 else "dense"
norm = lambda s: re.sub(r"\W+", " ", s.lower()).strip()
qs = json.load(open("eval/questions.json"))

hits, lat = 0, []
for q in qs:
    t = time.time()
    res = retrieve(q["question"], k=5, mode=mode)
    lat.append(time.time() - t)
    if any(norm(q["evidence"]) in norm(r["text"]) for r in res):
        hits += 1

lat.sort()
out = {"mode": mode, "questions": len(qs),
       "recall_at_5": round(hits / len(qs), 3),
       "p95_latency_s": round(lat[int(len(lat) * 0.95) - 1], 2)}
print(out)

path = "eval/retrieval_results.json"
all_res = json.load(open(path)) if os.path.exists(path) else {}
all_res[mode] = out
json.dump(all_res, open(path, "w"), indent=1)