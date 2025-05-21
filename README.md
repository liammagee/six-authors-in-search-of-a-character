# Custom Chatbot

A web application that allows you to create a chatbot with a custom system prompt. You can define the bot's personality and behavior through the system prompt.

## Features

- Customize your chatbot's behavior with system prompts
- Simple and clean web interface
- Real-time chat functionality
- Responsive design that works on desktop and mobile

## Setup

1. Make sure you have Python 3.7+ installed
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project root and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Running the Application

1. Start the Flask development server:
   ```
   python app.py
   ```
2. Open your web browser and navigate to `http://localhost:5000`
3. Customize the system prompt and start chatting!

## How It Works

The application uses:
- **Backend**: Python with Flask
- **Frontend**: HTML, CSS, and vanilla JavaScript
- **AI**: OpenAI's GPT-3.5-turbo model

## License

This project is licensed under the MIT License.