import OpenAI from 'openai';

const openai = new OpenAI({
  baseURL: "https://openrouter.ai/api/v1",
  apiKey: process.env.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,
  defaultHeaders: {
    "HTTP-Referer": "https://vercel.com",
    "X-Title": "Vercel AI API",
  },
});

export default async function handler(req, res) {
  // CORS সমস্যা সমাধানের জন্য
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');

  // ব্রাউজার যদি q প্যারামিটার না পাঠায়
  const { q } = req.query;
  if (!q) {
    return res.status(200).json({ 
      status: "Active", 
      message: "Please add ?q=YourQuestion to the URL" 
    });
  }

  try {
    const completion = await openai.chat.completions.create({
      model: "meta-llama/llama-3.1-8b-instruct:free", // ফ্রি মডেল
      messages: [
        { role: "system", content: "You are a helpful assistant." },
        { role: "user", content: q }
      ],
    });

    const answer = completion.choices[0]?.message?.content || "No response.";

    return res.status(200).json({
      question: q,
      answer: answer
    });

  } catch (error) {
    return res.status(500).json({ error: error.message });
  }
}
