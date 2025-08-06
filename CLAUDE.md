# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This project contains two AI-powered applications using OpenAI's GPT models:

1. **Flask Web Chatbot**: A web application that creates a customizable chatbot through a clean web interface
2. **Discord Bot**: A Discord bot that provides AI chat functionality with per-channel conversations

## Architecture

### Flask Web Application
- **Backend**: Python Flask application (`app.py`) with CORS enabled
- **Frontend**: Single-page application in `templates/index.html` with vanilla JavaScript
- **State Management**: In-memory chat history storage (keyed by chat ID)

### Discord Bot
- **Bot File**: `discord_bot.py` using discord.py library
- **Commands**: Prefix-based commands (`!chat`, `!reset`, `!system`, `!help_bot`)
- **State Management**: Per-channel conversation history with automatic cleanup
- **Features**: Custom system prompts, message splitting, error handling

### Shared Components
- **AI Integration**: OpenAI GPT-4o model via the official OpenAI Python client
- **Environment**: Virtual environment (`venv/`) with dependencies in `requirements.txt`
- **Configuration**: Environment variables in `.env` file

## Development Commands

### Setup and Installation
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Applications

#### Flask Web Application
```bash
# Activate virtual environment first
source venv/bin/activate

# Start development server
python app.py
# Application runs on http://localhost:5001
```

#### Discord Bot
```bash
# Activate virtual environment first
source venv/bin/activate

# Start Discord bot
python discord_bot.py
```

### Environment Configuration
- Create `.env` file with:
  - `OPENAI_API_KEY=your_api_key_here`
  - `DISCORD_BOT_TOKEN=your_discord_bot_token_here`
  - `AI_CHANNEL_NAME=ai-chat` (optional, defaults to "ai-chat")
- Both applications require a valid OpenAI API key
- Discord bot requires a Discord bot token (see `DISCORD_SETUP.md` for setup instructions)

## Key Components

### Flask Routes
- `/` - Serves the main chat interface (`templates/index.html`)
- `/chat` (POST) - Handles chat messages and returns AI responses

### Chat System
- Each browser session gets a unique chat ID for maintaining conversation context
- System prompts are configurable per chat session
- Chat history is stored in-memory and persists per chat ID
- Uses GPT-4o model with 1000 max tokens and 0.7 temperature

### Frontend Features
- Real-time chat interface with typing indicators
- Customizable system prompts
- Responsive design for desktop and mobile
- Auto-resizing textarea for user input
- Enter to send, Shift+Enter for new lines

### Discord Bot Behavior
- **Multiple Characters**: Each channel can have an active character with unique parameters (temperature, max tokens, system prompt)
- **Auto-response in AI channel**: Responds to all messages in the configured AI channel (default: `#ai-chat`) without requiring commands
- **Command-based in other channels**: Uses various commands in all other channels (see below)
- **Channel-specific conversations**: Each channel maintains separate conversation history and active character
- **Character persistence**: Characters and active character per channel are saved to `characters.json`

### Discord Bot Commands
- `!chat <message>` - Chat with the AI bot (not needed in AI channel)
- `!reset` - Reset conversation history for current channel
- `!character [name]` - Switch to character or show current character
- `!characters` - List all available characters
- `!create_character` - Create new custom character with parameters
- `!delete_character` - Delete custom character
- `!system <prompt>` - Set custom system prompt for channel
- `!preset [name]` - Use preset prompt or list available presets
- `!prompt` - Show current system prompt for channel
- `!help_bot` - Show all available commands

### Available Default Characters
5 built-in characters with different parameters:
- **default** (Assistant): Balanced assistant (temp: 0.7, tokens: 500)
- **scholar** (Scholar): Academic expert (temp: 0.3, tokens: 800)
- **creative** (Muse): Creative assistant (temp: 0.9, tokens: 600)
- **analyst** (Analyst): Logical problem solver (temp: 0.2, tokens: 700)
- **sage** (Sage): Philosophical insights (temp: 0.6, tokens: 500)

### Available Preset Prompts
8 built-in personality presets: default, coding, creative, tutor, pirate, professional, casual, scientist

## Important Notes

- No test suite currently exists in the project
- Chat history is stored in-memory only (resets on application restart)
- Flask app CORS is configured for localhost development only
- Discord bot maintains per-channel conversation history
- Uses OpenAI's latest Python client (v1.x)
- Discord bot requires "Message Content Intent" to be enabled in Discord Developer Portal