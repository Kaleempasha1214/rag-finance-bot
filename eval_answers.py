import json, sys, os, time
from rag import ask
from llm import chat, JUDGE_MODEL

mode = sys.argv[1] if len(sys.argv) > 1 else "rerank"
n = int(sys.argv[2]) if len(sys.argv) > 2 else 50
qs = json.load(open("eval/questions.json"))[:n]

ckpt = f"eval/answers_{mode}.jsonl"
done = {}
if os.path.exists(ckpt):
    for line in open(ckpt, encoding="utf-8"):
        r = json.loads(line)
        done[r["i"]] = r
print(f"Resuming: {len(done)} already done" if done else "Starting fresh")

def yes(t): return t.strip().upper().startswith("YES")
SYS = "You are a strict grader. Reply with only YES or NO."

try:
    for i, q in enumerate(qs):
        if i in done:
            continue
        out = ask(q["question"], k=5, mode=mode)
        ans = out["answer"]
        ctx = "\n\n".join(s["text"] for s in out["sources"])
        refused = "can't find this" in ans.lower()
        f = yes(chat(JUDGE_MODEL, SYS,
            f"Context:\n{ctx}\n\nAnswer:\n{ans}\n\nIs every factual claim in the "
            f"answer supported by the context?"))
        c = yes(chat(JUDGE_MODEL, SYS,
            f"Question: {q['question']}\nCorrect answer: {q['answer']}\n"
            f"Given answer: {ans}\n\nDoes the given answer match the correct answer?"))
        r = {"i": i, "question": q["question"], "answer": ans,
             "faithful": f, "correct": c, "refused": refused}
        with open(ckpt, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(r) + "\n")
        done[i] = r
        print(i + 1, "faithful" if f else "UNFAITHFUL",
              "correct" if c else "WRONG", flush=True)
        time.sleep(2)
except RuntimeError as e:
    print("\nStopped:", e)
    print(f"Progress saved ({len(done)}/{len(qs)}). Run the same command again later to continue.")
    sys.exit(1)

m = len(qs)
res = {"mode": mode, "questions": m,
       "faithfulness": round(sum(r["faithful"] for r in done.values()) / m, 3),
       "answer_correctness": round(sum(r["correct"] for r in done.values()) / m, 3),
       "refusal_rate": round(sum(r["refused"] for r in done.values()) / m, 3)}
print(res)
path = "eval/answer_results.json"
allr = json.load(open(path)) if os.path.exists(path) else {}
allr[mode] = res
json.dump(allr, open(path, "w"), indent=1)
print("Saved to", path)