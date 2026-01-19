from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# --- CONFIGURATION ---
# Get these from Vercel Environment Variables for security
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# The specific model you requested
MODEL_NAME = "deepseek/deepseek-r1:free" 

def ask_openrouter(prompt):
    """Sends the user message to OpenRouter"""
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://telegram.org", 
                "X-Title": "TelegramBot",
            },
            data=json.dumps({
                "model": MODEL_NAME,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }),
            timeout=50 # Vercel free tier has limits, but we need to wait for response
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"Error from AI: {response.text}"
            
    except Exception as e:
        return f"Failed to contact AI: {str(e)}"

def send_telegram_message(chat_id, text):
    """Sends the response back to Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown" # Optional: allows bold/italic text
    }
    requests.post(url, json=payload)

@app.route('/', methods=['POST'])
def webhook():
    """Main function called by Telegram"""
    try:
        data = request.get_json()
        
        # Check if the update contains a message
        if 'message' in data:
            message = data['message']
            chat_id = message['chat']['id']
            
            # Check if message has text (ignore stickers/photos)
            if 'text' in message:
                user_text = message['text']
                
                # Get response from OpenRouter
                ai_response = ask_openrouter(user_text)
                
                # Send back to Telegram
                send_telegram_message(chat_id, ai_response)

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error"}), 500

# Required for Vercel
import json
