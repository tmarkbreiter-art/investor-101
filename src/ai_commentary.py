"""
AXIOM US — vNext AI Commentary
AI explains ALREADY DECIDED verdicts. Never changes them.
"""
import re, json, requests


def _call_ai(config, system, user, max_tokens=600):
    if config.GROQ_API_KEY:
        try:
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {config.GROQ_API_KEY}",
                         "Content-Type": "application/json"},
                json={"model": "llama-3.3-70b-versatile",
                      "messages": [{"role":"system","content":system},
                                   {"role":"user","content":user}],
                      "max_tokens": max_tokens, "temperature": 0.3},
                timeout=45,
            )
            if r.ok: return r.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"  Groq: {e}")
    if config.GEMINI_API_KEY:
        try:
            r = requests.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
                params={"key": config.GEMINI_API_KEY},
                json={"contents":[{"parts":[{"text":f"{system}

{user}"}]}],
                      "generationConfig":{"maxOutputTokens":max_tokens,"temperature":0.3}},
                timeout=45,
            )
            if r.ok: return r.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            print(f"  Gemini: {e}")
    return ""


def _safe_json(raw, fallback):
    if not raw: return fallback
    cleaned = re.sub(r"```(?:json)?|```","",raw).strip()
    try: return json.loads(cleaned)
    except: pass
    for oc, cc in [("[","]"),("{","}")]:
        s = cleaned.find(oc)
        if s < 0: continue
        depth = 0
        for i, ch in enumerate(cleaned[s:], s):
            if ch == oc: depth += 1
            elif ch == cc:
                depth -= 1
                if depth == 0:
                    try: return json.loads(cleaned[s:i+1])
                    except: break
    return fallback


def add_commentary(config, portfolio, pulse):
    fear = pulse.get("fear_level", "NEUTRAL")
    lines = []
    for s in portfolio:
        fs = s["factor_score"]; gr = s["guardrails"]
        dev_str = f"{gr.deviation_pct:+.1f}%" if gr.deviation_pct is not None else "unknown"
        lines.append(
            f"{s['symbol']} ({s['sector']}): VERDICT={fs.verdict} SCORE={fs.total:.0f} "
            f"Tech={fs.technical:.0f} Risk={fs.risk:.0f} Quality={fs.quality:.0f} Macro={fs.macro:.0f} "
            f"Trend={gr.alignment.upper()} MA20_dev={dev_str} "
            f"News: {'; '.join(n['headline'][:60] for n in s.get('news',[])[:2]) or 'none'}"
        )

    system = (
        "You are an equity analyst explaining pre-computed, rules-based investment verdicts. "
        "Verdicts and scores are ALREADY SET by a deterministic model. "
        "Write 2 sentences per stock: (1) why the rules gave this score, (2) what could invalidate it. "
        "NEVER suggest changing the verdict. "
        f"Market fear: {fear}. "
        'Return JSON array: [{"s":"NVDA","why":"...","watch":"..."}]'
    )
    raw   = _call_ai(config, system, f"Explain:\n" + "
".join(lines), max_tokens=2000)
    items = _safe_json(raw, [])
    if not isinstance(items, list): items = []
    ai_map = {item.get("s",""): item for item in items}

    for s in portfolio:
        ai = ai_map.get(s["symbol"], {})
        s["ai_why"]   = ai.get("why",   "Screened well on technical and quality factors.")
        s["ai_watch"] = ai.get("watch", "Monitor for trend deterioration or macro shift.")
    return portfolio
