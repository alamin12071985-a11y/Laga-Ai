from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

# Render Environment Variable থেকে Key নিবে
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

# এই মডেলটি ইনস্ট্রাকশন খুব ভালো ফলো করে
MODEL_NAME = "meta-llama/llama-3.3-70b-instruct:free"

# --- গোপন নির্দেশ (AI কে শেখানো হচ্ছে কিভাবে কোড লিখবে) ---
SYSTEM_INSTRUCTION = """
You are an expert Telegram Bot Developer. 
Your task is to convert the user's request into a 'ctx.reply' JavaScript code block using Telegraf syntax.

RULES:
1. Output ONLY the code. No explanations, no markdown (```), no "Here is your code".
2. Use valid JavaScript format for Telegraf.
3. The message text must be in Bengali (or the language requested) with beautiful styling (Bold, Italic).
4. Use appropriate Emojis (👋, 📢, ⬇️, 🔹) to make it look professional.
5. Always include 'parse_mode: "Markdown"'.
6. Always include an 'inline_keyboard' with relevant buttons based on the topic.

EXAMPLE FORMAT TO FOLLOW:
ctx.reply(
  `*HEADER TOPIC* 📢
  
  Body text goes here with details...
  
  👇 Select an option below:`,
  {
    parse_mode: "Markdown",
    reply_markup: {
      inline_keyboard: [
        [{ text: "Button 1", callback_data: "btn_1" }, { text: "Button 2", callback_data: "btn_2" }],
        [{ text: "❌ Close", callback_data: "cancel" }]
      ]
    }
  }
);
"""

@app.route('/api', methods=['GET'])
def generate_code():
    # 1. URL থেকে টপিক নেওয়া (?q=...)
    topic = request.args.get('q')

    if not topic:
        return jsonify({"error": "Please provide a topic. Example: /api?q=Welcome Message"}), 400

    try:
        # 2. AI কে রিকোয়েস্ট পাঠানো
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": SYSTEM_INSTRUCTION},
                {"role": "user", "content": f"Write a Telegram code for: {topic}"}
            ],
            "temperature": 0.5 # ক্রিয়েটিভ কিন্তু সঠিক ফরম্যাটের জন্য
        }

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://render.com",
                "X-Title": "CodeGenerator"
            },
            data=json.dumps(payload)
        )
        
        # 3. রেসপন্স হ্যান্ডেল করা
        if response.status_code == 200:
            ai_code = response.json()['choices'][0]['message']['content']
            
            # ক্লিন করা (যদি AI ভুল করে ```js দিয়ে দেয়, সেটা মুছে ফেলা)
            clean_code = ai_code.replace("```javascript", "").replace("```js", "").replace("```", "").strip()

            return jsonify({
                "status": "success",
                "topic": topic,
                "generated_code": clean_code
            })
        else:
            return jsonify({"error": "AI Provider Error", "details": response.text}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
