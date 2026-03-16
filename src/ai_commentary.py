"""
AXIOM US - vNext AI Commentary
AI explains ALREADY DECIDED verdicts. Never changes them.
"""
import re, json, requests


def _call_ai(config, system, user, max_tokens=600):
    if config.GROQ_API_KEY:
        try:
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": "Bearer " + config.GROQ_API_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user}
                    ],
                    "max_tokens": max_tokens,
                    "temperature": 0.3
                },
                timeout=45,
            )
            if r.ok:
                return r.json()["choices"][0]["message"]["content"]
            else:
                print("Groq HTTP error: " + str(r.status_code) + " " + r.text[:200])
        except Exception as e:
            print("Groq error: " + str(e))
    if config.GEMINI_API_KEY:
        try:
            prompt = system + "\n\n" + user
            body = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.3}
            }
            r = requests.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
                params={"key": config.GEMINI_API_KEY},
                json=body,
                timeout=45,
            )
            if r.ok:
                return r.json()["candidates"][0]["content"]["parts"][0]["text"]
            else:
                print("Gemini HTTP error: " + str(r.status_code) + " " + r.text[:200])
        except Exception as e:
            print("Gemini error: " + str(e))
    return ""


def _safe_json(raw, fallback):
    if not raw:
        return fallback
    cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
    try:
        return json.loads(cleaned)
    except Exception:
        pass
    return fallback


def add_commentary(config, portfolio, pulse):
    fear = pulse.get("fear_level", "NEUTRAL")
    lines = []
    for s in portfolio:
        fs = s["factor_score"]
        gr = s["guardrails"]
        dev_str = str(round(gr.deviation_pct, 1)) + "%" if gr.deviation_pct is not None else "unknown"
        news_heads = "; ".join(n["headline"][:60] for n in s.get("news", [])[:2])
        line = (
            s["symbol"] + " (" + s["sector"] + "): "
            + "VERDICT=" + fs.verdict
            + " SCORE=" + str(round(fs.total, 0))
            + " Tech=" + str(fs.technical)
            + " Risk=" + str(fs.risk)
            + " Quality=" + str(fs.quality)
            + " Macro=" + str(fs.macro)
            + " Trend=" + gr.alignment.upper()
            + " MA20_dev=" + dev_str
            + (" News: " + news_heads if news_heads else "")
        )
        lines.append(line)

    system_msg = (
        "You are an expert investing coach teaching a beginner investor. "
        "The model has ALREADY decided verdicts - never change them. "
        "For each stock return a JSON object with exactly two keys: "
        "\"why\": 2 sentences - first explain in plain English WHY the model scored it this way using the actual signal data, "
        "then give a CONCRETE ACTION like 'Buy 1 share at $183 now' or 'Wait for a dip to $170 before entering' or 'Hold, do not add more yet'. "
        "\"watch\": 1 sentence - one specific price level or event to watch, e.g. 'If it drops below $168 sell immediately' or 'Watch earnings April 23 - a miss could drop it 10 percent'. "
        "Use real dollar amounts from the data. Be direct. No filler. Talk to the investor like a coach. "
        "Market today: " + fear + ". Small retail investor with limited budget learning to grow wealth. "
        "Return ONLY a valid JSON array: [{\"s\":\"SYMBOL\",\"why\":\"...\",\"watch\":\"...\"}]"
    )
    user_msg = "Coach me on these positions:\n" + "\n".join(lines)

    raw = _call_ai(config, system_msg, user_msg, max_tokens=2000)
    print("AI raw response: " + raw[:300])
    items = _safe_json(raw, [])
    if not isinstance(items, list):
        items = []
    ai_map = {item.get("s", ""): item for item in items}

    for s in portfolio:
        ai = ai_map.get(s["symbol"], {})
        s["ai_why"] = ai.get("why", "Screened well on technical and quality factors.")
        s["ai_watch"] = ai.get("watch", "Monitor for trend deterioration or macro shift.")

    return portfolio
