import json, os

drafts = json.load(open("draft_questions.json"))

DROP = []    # put your bad # numbers here, like [3, 7, 12]
FIX = {}     # optional: {5: "corrected answer"}

keep = []
for i, d in enumerate(drafts):
    if i in DROP:
        continue
    if i in FIX:
        d["answer"] = FIX[i]
    keep.append(d)

keep = keep[:50]
os.makedirs("eval", exist_ok=True)
json.dump(keep, open("eval/questions.json", "w"), indent=1)
print("Saved", len(keep), "questions")