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
        "You are an expert investing teacher and financial coach talking directly to a beginner investor. "
        "The rules-based model has ALREADY made its decisions — your job is to teach the investor WHY and WHAT TO DO NEXT. "
        "For each stock write exactly 3 sentences: "
        "(1) WHY the model scored it this way — explain the specific signals in plain English a beginner understands. "
        "(2) WHAT ACTION to take right now — be concrete: 'Buy X shares at $Y', 'Wait for price to dip to $Z before entering', 'Hold your position, do not add yet'. "
        "(3) WHAT TO WATCH — one specific number or event that would change the plan, e.g. 'If price drops below $168 sell immediately' or 'Watch earnings on April 23'. "
        "Use plain English. Use dollar amounts. Be a coach, not a disclaimer. Never say 'consult a financial advisor'. "
        "Market regime today: " + fear + ". Budget context: small retail investor, learning to grow wealth. "
        "Return JSON array: [{\"s\":\"NVDA\",\"why\":\"...\",\"watch\":\"...\"}]"
    )
    user_msg = "Teach me about these positions and what I should do:\n" + "\n".join(lines)

    raw = _call_ai(config, system_msg, user_msg, max_tokens=2000)
    items = _safe_json(raw, [])
    if not isinstance(items, list):
        items = []
    ai_map = {item.get("s", ""): item for item in items}

    for s in portfolio:
        ai = ai_map.get(s["symbol"], {})
        s["ai_why"] = ai.get("why", "Screened well on technical and quality factors.")
        s["ai_watch"] = ai.get("watch", "Monitor for trend deterioration or macro shift.")

    return portfolio
