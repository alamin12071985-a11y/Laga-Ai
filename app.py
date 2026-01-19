from flask import Flask, request, Response
from flask_cors import CORS  # <--- নতুন ইমপোর্ট
import requests
import json
import os

app = Flask(__name__)

# --- CORS চালু করা হলো (যাতে টেলিগ্রাম বা যেকোনো জায়গা থেকে কাজ করে) ---
CORS(app) 

# Render Env থেকে Key নিবে
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
MODEL_NAME = "llama-3.3-70b-versatile"

SYSTEM_INSTRUCTION = """
You are an expert Telegram Bot Developer using Telegraf (JavaScript).
Your task is to generate valid 'ctx.reply' code blocks.

RULES:
1. Output ONLY the JavaScript code. No markdown (```), no explanations.
2. If the user asks in Bengali, the text inside the code MUST be in Bengali.
3. Use Emojis and Bold text for styling.
4. Always include 'parse_mode: "Markdown"'.
5. Always include an 'inline_keyboard'.
"""

@app.route('/api', methods=['GET'])
def generate_code():
    topic = request.args.get('q')

    if not topic:
        error_json = json.dumps({"error": "Please provide a topic"}, ensure_ascii=False)
        return Response(error_json, status=400, mimetype='application/json; charset=utf-8')

    try:
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
                    {"role": "user", "content": f"Write code for: {topic}"}
                ],
                "temperature": 0.5
            })
        )
        
        if response.status_code == 200:
            ai_code = response.json()['choices'][0]['message']['content']
            clean_code = ai_code.replace("```javascript", "").replace("```js", "").replace("```", "").strip()

            result_data = {
                "status": "success",
                "topic": topic,
                "generated_code": clean_code
            }
            
            json_response = json.dumps(result_data, ensure_ascii=False, indent=4)
            return Response(json_response, status=200, mimetype='application/json; charset=utf-8')
            
        else:
            return Response(json.dumps({"error": "Groq Error"}, ensure_ascii=False), status=500, mimetype='application/json; charset=utf-8')

    except Exception as e:
        return Response(json.dumps({"error": str(e)}, ensure_ascii=False), status=500, mimetype='application/json; charset=utf-8')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
