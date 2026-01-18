import OpenAI from 'openai';

// Initialize the client pointing to OpenRouter
const openai = new OpenAI({
  baseURL: "https://openrouter.ai/api/v1",
  apiKey: process.env.OPENROUTER_API_KEY,
  defaultHeaders: {
    "HTTP-Referer": "https://vercel.com", // Optional: required by OpenRouter for rankings
    "X-Title": "Vercel AI API", // Optional
  },
});

export default async function handler(req, res) {
  // 1. Enable CORS (allows your API to be called from other websites)
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  // Handle preflight request for CORS
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  // 2. Get Query Parameter
  const { q } = req.query;

  // 3. Validation
  if (!q) {
    return res.status(400).json({ 
      error: "Missing query parameter 'q'. Example: /api?q=Tell+me+a+joke" 
    });
  }

  try {
    // 4. Call AI Provider (OpenRouter)
    // We use a free/cheap model here: Llama 3.1 8B Instruct
    const completion = await openai.chat.completions.create({
      model: "meta-llama/llama-3.1-8b-instruct:free",
      messages: [
        { role: "system", content: "You are a helpful and concise API assistant." },
        { role: "user", content: q }
      ],
      temperature: 0.7,
      max_tokens: 500,
    });

    const answer = completion.choices[0]?.message?.content || "No response generated.";

    // 5. Return Clean JSON
    return res.status(200).json({
      question: q,
      answer: answer.trim()
    });

  } catch (error) {
    console.error("API Error:", error);
    return res.status(500).json({ 
      error: "Failed to fetch AI response.",
      details: error.message 
    });
  }
}
