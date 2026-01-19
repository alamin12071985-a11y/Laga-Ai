from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

# Render Env তে নাম হবে: GROQ_API_KEY
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Groq এর ফ্রি এবং পাওয়ারফুল মডেল
MODEL_NAME = "llama-3.3-70b-versatile"

SYSTEM_INSTRUCTION = """
You are an expert Telegram Bot Developer. 
Your task is to convert the user's request into a 'ctx.reply' JavaScript code block using Telegraf syntax.

RULES:
1. Output ONLY the code. No explanations, no markdown (```), no "Here is your code".
2. Use valid JavaScript format for Telegraf.
3. The message text must be in Bengali (or the language requested) with beautiful styling (Bold, Italic).
4. Use appropriate Emojis (👋, 📢, ⬇️, 🔹) to make it look professional.
5. Always include 'parse_mode: "Markdown"'.
6. Always include an 'inline_keyboard'.

EXAMPLE FORMAT:
ctx.reply(
  `*HEADER* 📢
  Body text...`,
  {
    parse_mode: "Markdown",
    reply_markup: {
      inline_keyboard: [
        [{ text: "Button", callback_data: "btn" }]
      ]
    }
  }
);
"""

@app.route('/api', methods=['GET'])
def generate_code():
    topic = request.args.get('q')

    if not topic:
        return jsonify({"error": "Please provide a topic."}), 400

    try:
        # --- GROQ API REQUEST ---
        response = requests.post(
            url="https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "model": MODEL_NAME,
                "messages": [
                    {"role": "system", "content": SYSTEM_INSTRUCTION},
                    {"role": "user", "content": f"Write a Telegram code for: {topic}"}
                ],
                "temperature": 0.5
            })
        )
        
        if response.status_code == 200:
            ai_code = response.json()['choices'][0]['message']['content']
            clean_code = ai_code.replace("```javascript", "").replace("```js", "").replace("```", "").strip()

            return jsonify({
                "status": "success",
                "topic": topic,
                "generated_code": clean_code
            })
        else:
            return jsonify({"error": "Groq Error", "details": response.text}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
