const STOCKS = [
  {sym:'NVDA', name:'NVIDIA',           sector:'Technology'},
  {sym:'MSFT', name:'Microsoft',        sector:'Technology'},
  {sym:'AAPL', name:'Apple',            sector:'Technology'},
  {sym:'META', name:'Meta',             sector:'Technology'},
  {sym:'GOOGL',name:'Alphabet',         sector:'Technology'},
  {sym:'AMD',  name:'AMD',              sector:'Technology'},
  {sym:'CRWD', name:'CrowdStrike',      sector:'Technology'},
  {sym:'TSLA', name:'Tesla',            sector:'Technology'},
  {sym:'XOM',  name:'ExxonMobil',       sector:'Energy'},
  {sym:'CVX',  name:'Chevron',          sector:'Energy'},
  {sym:'COP',  name:'ConocoPhillips',   sector:'Energy'},
  {sym:'OXY',  name:'Occidental',       sector:'Energy'},
  {sym:'JPM',  name:'JPMorgan',         sector:'Finance'},
  {sym:'BAC',  name:'Bank of America',  sector:'Finance'},
  {sym:'GS',   name:'Goldman Sachs',    sector:'Finance'},
  {sym:'UNH',  name:'UnitedHealth',     sector:'Healthcare'},
  {sym:'LLY',  name:'Eli Lilly',        sector:'Healthcare'},
  {sym:'AMZN', name:'Amazon',           sector:'Consumer'},
  {sym:'COST', name:'Costco',           sector:'Consumer'},
  {sym:'CAT',  name:'Caterpillar',      sector:'Industrial'},
];

const FINNHUB = 'd6ligshr01qrq6i2ses0d6ligshr01qrq6i2sesg';

async function fetchQuote(sym) {
  const r = await fetch(`https://finnhub.io/api/v1/quote?symbol=${sym}&token=${FINNHUB}`);
  return r.json();
}

async function fetchMetrics(sym) {
  const r = await fetch(`https://finnhub.io/api/v1/stock/metric?symbol=${sym}&metric=all&token=${FINNHUB}`);
  return r.json();
}

function calcScore(quote, metrics, spyChg) {
  const price   = quote.c || 0;
  const dpct    = quote.dp || 0;
  const w52High = metrics?.metric?.['52WeekHigh'] || price * 1.2;
  const w52Low  = metrics?.metric?.['52WeekLow']  || price * 0.8;
  const beta    = metrics?.metric?.beta || 1;

  // Position in 52-week range (0–100)
  const rangePos = w52High > w52Low
    ? Math.min(100, Math.max(0, ((price - w52Low) / (w52High - w52Low)) * 100))
    : 50;

  // Momentum: recent % change drives this
  const momentum = Math.min(100, Math.max(0, 50 + dpct * 4));

  // Risk: lower beta = safer = higher score
  const risk = Math.min(100, Math.max(0, 100 - (beta - 0.5) * 35));

  // Quality: sweet spot is mid-range (not overbought, not beaten down)
  const quality = rangePos > 85 ? 55 : rangePos < 20 ? 50 : rangePos > 60 ? 78 : 88;

  // Market: based on SPY performance
  const market = spyChg > 1.5 ? 100 : spyChg > 0.5 ? 85 : spyChg > 0 ? 70 : spyChg > -1 ? 55 : 35;

  // News: neutral baseline
  const news = 70;

  const score = parseFloat(
    (momentum * 0.25 + risk * 0.20 + quality * 0.25 + market * 0.15 + news * 0.15).toFixed(1)
  );

  // Dynamic stop & target
  const stopPct   = beta > 1.5 ? 0.13 : 0.10;
  const targetPct = beta > 1.5 ? 0.22 : 0.16;
  const stop   = parseFloat((price * (1 - stopPct)).toFixed(2));
  const target = parseFloat((price * (1 + targetPct)).toFixed(2));

  // Safety check strings
  const overbought = rangePos > 80;
  const trending   = dpct > 0.3;
  const checks = [
    overbought ? 'Yes — price has jumped recently, be cautious' : 'No — price is at a reasonable level',
    trending   ? 'Yes — price is moving up steadily'            : 'Mixed — short-term momentum is unclear',
    rangePos > 75 ? 'Near its highest price in a year — elevated risk'
                  : rangePos < 30 ? 'Near yearly lows — potential opportunity but be careful'
                  : 'Healthy — not at extreme highs or lows',
  ];

  // AI commentary
  const aiWhy = score >= 80
    ? `${STOCKS.find(s=>true)?.sym || 'This stock'} scored high because momentum is strong and conditions look favorable right now.`
    : score >= 70
    ? `A solid company but the price needs a better entry point before committing.`
    : `Conditions are mixed — worth watching but not the time to buy yet.`;

  const aiWatch = overbought
    ? `Price is stretched — if it falls below $${stop.toFixed(2)}, sell to protect yourself.`
    : `If the price drops below $${stop.toFixed(2)}, sell immediately to cap your loss.`;

  return {
    score,
    stop,
    target,
    scoreBreakdown: {
      momentum: Math.round(momentum),
      risk:     Math.round(risk),
      quality:  Math.round(quality),
      market:   Math.round(market),
      news,
    },
    checks,
    aiWhy,
    aiWatch,
  };
}

export default async function handler(req, res) {
  if (req.method !== 'GET') return res.status(405).end();

  try {
    // Fetch SPY first for market context
    const spyQuote = await fetchQuote('SPY');
    const spyChg = spyQuote?.dp || 0;

    // Fetch all stocks in parallel (quote + metrics)
    const results = await Promise.all(
      STOCKS.map(async s => {
        try {
          const [quote, metrics] = await Promise.all([fetchQuote(s.sym), fetchMetrics(s.sym)]);
          const scored = calcScore(quote, metrics, spyChg);
          return {
            sym:    s.sym,
            name:   s.name,
            sector: s.sector,
            price:  quote.c || 0,
            ...scored,
          };
        } catch (e) {
          return null;
        }
      })
    );

    const stocks = results.filter(Boolean);
    res.status(200).json({ stocks, spyChg, updatedAt: new Date().toISOString() });
  } catch (e) {
    res.status(500).json({ error: 'Score fetch failed', message: e.message });
  }
}
