export default async function handler(req, res) {
  if (req.method !== "POST") return res.status(405).end();
  const { messages } = req.body;

  // 1. Fetch live global news
  let newsContext = "";
  try {
    const topics = [
      "stock market today",
      "Middle East oil",
      "Federal Reserve interest rates",
      "global economy 2026",
      "energy prices"
    ];
    const query = topics.join(" OR ");
    const newsRes = await fetch(
      "https://newsapi.org/v2/everything?q=" + encodeURIComponent(query) +
      "&sortBy=publishedAt&pageSize=8&language=en",
      { headers: { "X-Api-Key": process.env.NEWS_API_KEY } }
    );
    if (newsRes.ok) {
      const newsData = await newsRes.json();
      const headlines = (newsData.articles || [])
        .slice(0, 8)
        .map(a => "- " + a.title + " (" + a.source.name + ")")
        .join("\n");
      newsContext = "\n\nLIVE NEWS RIGHT NOW (use this to inform your advice):\n" + headlines;
    } else {
      const errText = await newsRes.text();
      newsContext = "\n\n[News fetch failed: " + newsRes.status + " " + errText + "]";
    }
  } catch(e) {
    newsContext = "\n\n[News fetch exception: " + e.message + "]";
  }

  // 2. Inject live news + strict rules into system prompt
  if (messages[0]?.role === "system") {
    messages[0].content = messages[0].content + newsContext +
      "\n\nCRITICAL RULES:" +
      "\n- You ONLY know prices and scores from the portfolio context above — never use your own memory for prices." +
      "\n- Use the live news headlines above to connect global events (war, oil, Fed, economy) to the stocks." +
      "\n- If oil news is relevant to energy stocks like COP, XOM, OXY — say so directly." +
      "\n- If there is market fear or geopolitical risk — factor it into your advice." +
      "\n- If asked if you are up to date, say: I use live portfolio data and real-time news fed to me right now." +
      "\n- MAX 4 sentences. Talk like a smart friend texting — direct, simple, no jargon." +
      "\n- Never say 'consult a financial advisor'.";
  }

  // 3. Call Groq with full context
  try {
    const r = await fetch("https://api.groq.com/openai/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": "Bearer " + process.env.GROQ_API_KEY,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        model: "llama-3.3-70b-versatile",
        messages: messages,
        max_tokens: 180,
        temperature: 0.35
      })
    });
    const data = await r.json();
    if (!r.ok) {
      return res.status(r.status).json({ error: "Groq error", details: data });
    }
    res.status(200).json(data);
  } catch(e) {
    res.status(500).json({ error: "Groq fetch failed", message: e.message });
  }
}
