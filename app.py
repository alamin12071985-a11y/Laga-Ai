from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

# বাংলা ফন্ট যাতে ভেঙ্গে না যায় (খুব গুরুত্বপূর্ণ)
app.config['JSON_AS_ASCII'] = False 

# Render Env তে নাম হবে: GROQ_API_KEY
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Groq এর সবচেয়ে শক্তিশালী ফ্রি মডেল
MODEL_NAME = "llama-3.3-70b-versatile"

# --- শক্তিশালী গোপন নির্দেশ (AI Brain) ---
SYSTEM_INSTRUCTION = """
You are an expert Telegram Bot Developer (Telegraf JS).
Your task is to generate 'ctx.reply' code based on the user's request.

RULES FOR OUTPUT:
1. **Language Detection:** If the user asks in BENGALI, the message text inside the code MUST be in BENGALI. If English, use English.
2. **Professional Look:** Use Emojis (👋, 🚀, 📢, 🔹), Bold Text (*Text*), and clean formatting.
3. **Format:** Output ONLY the raw JavaScript code. No markdown (```), no explanations.
4. **Structure:** Always include `parse_mode: "Markdown"` and an `inline_keyboard`.

EXAMPLE INPUT: "বিকাশ পেমেন্ট মেসেজ বানাও"
EXAMPLE OUTPUT:
ctx.reply(
  `*💸 পেমেন্ট মেথড*

  আমাদের সার্ভিসটি কেনার জন্য নিচে দেওয়া নাম্বারে পেমেন্ট করুন।

  🔹 *বিকাশ:* 017xxxxxxxx
  🔹 *নগদ:* 018xxxxxxxx

  পেমেন্ট করা হলে নিচের বাটনে ক্লিক করুন ⬇️`,
  {
    parse_mode: "Markdown",
    reply_markup: {
      inline_keyboard: [
        [{ text: "✅ পেমেন্ট কনফার্ম করুন", callback_data: "confirm_payment" }],
        [{ text: "❌ বাতিল করুন", callback_data: "cancel" }]
      ]
    }
  }
);
"""

@app.route('/api', methods=['GET'])
def generate_code():
    # 1. ইউজারের কমান্ড নেওয়া
    user_prompt = request.args.get('q')

    if not user_prompt:
        return jsonify({
            "status": "error",
            "message": "Please provide a query. Example: /api?q=Welcome Message"
        }), 400

    try:
        # 2. AI এর কাছে পাঠানো
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
                    {"role": "user", "content": f"User Request: {user_prompt}"}
                ],
                "temperature": 0.6 # একটু ক্রিয়েটিভ করার জন্য
            })
        )
        
        # 3. রেসপন্স প্রসেস করা
        if response.status_code == 200:
            ai_content = response.json()['choices'][0]['message']['content']
            
            # মার্কডাউন বা অপ্রয়োজনীয় টেক্সট রিমুভ করা
            clean_code = ai_content.replace("```javascript", "").replace("```js", "").replace("```", "").strip()

            return jsonify({
                "status": "success",
                "input_language": "detected",
                "generated_code": clean_code
            })
        else:
            return jsonify({"status": "error", "details": response.text}), 500

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
