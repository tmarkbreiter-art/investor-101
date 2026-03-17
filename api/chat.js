export default async function handler(req, res) {
  if (req.method !== "POST") return res.status(405).end();

  const { messages } = req.body;

  if (!messages || !Array.isArray(messages)) {
    return res.status(400).json({ error: "Invalid messages" });
  }

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

    const text = await r.text();

    if (!r.ok) {
      return res.status(500).json({ error: "Groq failed", status: r.status, body: text });
    }

    const data = JSON.parse(text);
    res.status(200).json(data);
  } catch(e) {
    res.status(500).json({ error: e.message, stack: e.stack });
  }
}
