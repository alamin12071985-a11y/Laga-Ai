import OpenAI from 'openai';

// এখানে আমরা Groq এর কনফিগারেশন দিচ্ছি
const openai = new OpenAI({
  apiKey: process.env.GROQ_API_KEY, // নাম পরিবর্তন করেছি
  baseURL: "https://api.groq.com/openai/v1"
});

export default async function handler(req, res) {
  // CORS ফিক্স
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  const { q } = req.query;

  if (!q) {
    return res.status(400).json({ 
      error: "Please provide a question using ?q=..." 
    });
  }

  try {
    const completion = await openai.chat.completions.create({
      // Groq এর ফ্রি এবং ফাস্ট মডেল
      model: "llama3-8b-8192", 
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
    console.error(error);
    return res.status(500).json({ 
      error: "Server Error", 
      details: error.message 
    });
  }
}
