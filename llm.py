import os, time
from groq import Groq, RateLimitError

_client = Groq(api_key=os.environ["GROQ_API_KEY"])
GEN_MODEL = "openai/gpt-oss-20b"
JUDGE_MODEL = "openai/gpt-oss-120b"

def chat(model, system, user, retries=6):
    for attempt in range(retries):
        try:
            r = _client.chat.completions.create(
                model=model, temperature=0,
                reasoning_effort="low",
                messages=[{"role": "system", "content": system},
                          {"role": "user", "content": user}])
            return (r.choices[0].message.content or "").strip()
        except RateLimitError:
            time.sleep(20 * (attempt + 1))
    raise RuntimeError("Still rate limited, try again later")