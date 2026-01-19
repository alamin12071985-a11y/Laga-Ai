from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

# --- CONFIGURATION ---
# Get keys from Render Environment Variables
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
MODEL_NAME = "google/gemini-2.0-flash-lite-preview-02-05:free" 

def ask_openrouter(prompt):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://telegram.org", 
                "X-Title": "RenderBot",
            },
            data=json.dumps({
                "model": MODEL_NAME,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            })
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"Error from AI: {response.text}"
    except Exception as e:
        return f"Connection Failed: {str(e)}"

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

@app.route('/', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        
        if 'message' in data:
            message = data['message']
            chat_id = message['chat']['id']
            
            if 'text' in message:
                user_text = message['text']
                # 1. Send a "Thinking..." message (Optional, good for UX)
                send_telegram_message(chat_id, "🤔 Thinking...")
                
                # 2. Get AI Response
                ai_response = ask_openrouter(user_text)
                
                # 3. Send Final Response
                send_telegram_message(chat_id, ai_response)

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error"}), 500

if __name__ == '__main__':
    # Render assigns a port automatically
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
