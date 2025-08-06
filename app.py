from flask import Flask, request, jsonify, render_template
from flask_cors import CORS, cross_origin
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={
    r"/*": {    
        "origins": ["http://localhost:5001", "http://127.0.0.1:5001"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configure OpenAI
client = OpenAI(
    # This is the default and can be omitted
    api_key=os.getenv("OPENAI_API_KEY"),
)

# Store chat history (in-memory, for demo purposes)
chat_history = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    prompt = data.get('prompt', 'You are a helpful assistant.')
    chat_id = data.get('chat_id', 'default')
    
    # Initialize chat history for this chat_id if it doesn't exist
    if chat_id not in chat_history:
        chat_history[chat_id] = [{"role": "system", "content": prompt}]
    
    # Add user message to history
    chat_history[chat_id].append({"role": "user", "content": user_message})
    
    try:
        # Get response from OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=chat_history[chat_id],
            max_tokens=1000,
            temperature=0.7
        )
        
        # Extract the assistant's response
        assistant_message = response.choices[0].message.content
        
        # Add assistant's response to history
        chat_history[chat_id].append({"role": "assistant", "content": assistant_message})
        
        return jsonify({
            'response': assistant_message,
            'chat_id': chat_id
        })
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
