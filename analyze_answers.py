import json

rows = [json.loads(l) for l in open("eval/answers_rerank.jsonl", encoding="utf-8")]
ref = [r for r in rows if r["refused"]]
ans = [r for r in rows if not r["refused"]]
pct = lambda a, b: round(100 * a / b, 1) if b else 0

print("total", len(rows), "| refused", len(ref), "| answered", len(ans))
print("faithful among answered:", pct(sum(r["faithful"] for r in ans), len(ans)), "%")
print("correct among answered:", pct(sum(r["correct"] for r in ans), len(ans)), "%")
print("refusals flagged unfaithful:", sum(not r["faithful"] for r in ref), "of", len(ref))

bad = [r for r in ans if not r["faithful"]]
print("\nAnswered but flagged UNFAITHFUL:", len(bad), "\n")
for r in bad[:6]:
    print("Q:", r["question"])
    print("A:", r["answer"][:400].replace("\n", " "))
    print("-" * 60)