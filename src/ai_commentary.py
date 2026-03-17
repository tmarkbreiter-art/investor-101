"""
AXIOM US - AI Commentary
Plain English coaching for a beginner investor.
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
                print("Groq error: " + str(r.status_code) + " " + r.text[:200])
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
                print("Gemini error: " + str(r.status_code) + " " + r.text[:200])
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
            + " price=$" + str(s.get("price", 0))
            + " stop=$" + str(s.get("stop_loss", 0))
            + " target=$" + str(s.get("target", 0))
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
        "You are AXIOM Coach. You explain stocks in plain English to a complete beginner — "
        "someone who is just starting to invest and does not know any finance terms. "
        "Write like you are sending a text message to a smart friend who knows nothing about stocks. "
        "NEVER use jargon. If you must use a term, explain it immediately. "
        "Be SHORT and DIRECT — max 2 sentences per field. "
        "The model has ALREADY decided verdicts — never change or question them.\n\n"
        "For each stock return JSON with exactly two keys:\n"
        "\"why\": 2 sentences MAX. Sentence 1: explain in plain English why the system rated it this way "
        "(e.g. 'NVDA scored high because its price has been climbing steadily and the company makes a lot of money.'). "
        "Sentence 2: one simple concrete action with a real dollar amount "
        "(e.g. 'You can buy 1 share at $183 today.' or 'Wait — don\\'t buy yet, watch for the price to dip to $170 first.').\n"
        "\"watch\": 1 sentence MAX in plain English. Tell the investor ONE specific thing to watch for, "
        "what it means, and what they should do. "
        "Example: 'If the price falls below $168, sell immediately to stop yourself from losing more money.' "
        "or 'The company reports earnings on April 23 — if the numbers disappoint, the price could drop fast, so be ready.' "
        "Always explain what the investor should DO and WHY in plain everyday words.\n\n"
        "Market today: " + fear + ".\n"
        "Return ONLY valid JSON: [{\"s\":\"SYMBOL\",\"why\":\"...\",\"watch\":\"...\"}]"
    )
    user_msg = "\n".join(lines)

    raw = _call_ai(config, system_msg, user_msg, max_tokens=2000)
    print("AI raw: " + raw[:300])
    items = _safe_json(raw, [])
    if not isinstance(items, list):
        items = []
    ai_map = {item.get("s", ""): item for item in items}

    for s in portfolio:
        ai = ai_map.get(s["symbol"], {})
        s["ai_why"] = ai.get("why", "This stock scored well on price momentum and company quality.")
        s["ai_watch"] = ai.get("watch", "Watch for any big price drops — if it falls to the sell point, act quickly to protect yourself.")

    return portfolio
