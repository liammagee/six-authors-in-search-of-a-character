# Discord Bot Setup Guide

## Prerequisites
1. A Discord account
2. OpenAI API key (already configured)
3. Python environment with dependencies installed

## Creating a Discord Bot

### Step 1: Create a Discord Application
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Give your application a name (e.g., "AI Chatbot")
4. Click "Create"

### Step 2: Create a Bot
1. In your application, go to the "Bot" section in the left sidebar
2. Click "Add Bot"
3. Under "Token", click "Copy" to copy your bot token
4. **Important**: Keep this token secret!

### Step 3: Configure Bot Permissions
1. In the "Bot" section, scroll down to "Privileged Gateway Intents"
2. Enable "Message Content Intent" (required for the bot to read messages)
3. Save changes

### Step 4: Add Bot Token to Environment
1. Open the `.env` file in your project
2. Replace `your_discord_bot_token_here` with your actual bot token:
   ```
   DISCORD_BOT_TOKEN="your_actual_bot_token_here"
   AI_CHANNEL_NAME="ai-chat"
   ```
3. Optionally, change `AI_CHANNEL_NAME` to match your desired channel name

### Step 5: Invite Bot to Your Server
1. Go to the "OAuth2" section in the left sidebar
2. Click on "URL Generator"
3. Under "Scopes", select "bot"
4. Under "Bot Permissions", select:
   - Send Messages
   - Use Slash Commands
   - Read Message History
   - Add Reactions
5. Copy the generated URL and open it in your browser
6. Select the server you want to add the bot to
7. Click "Authorize"

## Running the Discord Bot

### Install Dependencies
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Start the Bot
```bash
source venv/bin/activate
python discord_bot.py
```

## Bot Behavior

### Special AI Channel
The bot automatically responds to **all messages** in the channel named in `AI_CHANNEL_NAME` (default: `#ai-chat`). No command prefix is needed!

1. Create a channel named `ai-chat` (or whatever you set in `AI_CHANNEL_NAME`)
2. Simply type any message in that channel and the bot will respond
3. The bot maintains conversation context within that channel

### Commands (Available in All Channels)
You can also use these commands in any channel:

**Chat Commands:**
- `!chat <message>` - Chat with the AI bot
- `!reset` - Reset conversation history for the current channel

**Character Commands:**
- `!character [name]` - Switch to a character or show current character
- `!characters` - List all available characters
- `!create_character` - Create a new custom character
- `!delete_character` - Delete a custom character

**System Prompt Commands:**
- `!system <prompt>` - Set a custom system prompt for the channel
- `!preset [name]` - Use a preset prompt (or list available presets)
- `!prompt` - Show the current system prompt for the channel

**Other Commands:**
- `!help_bot` - Show available commands

## Example Usage

### In the AI Channel (`#ai-chat`):
```
Hello, how are you today?
Can you help me with a Python function?
What's the weather like? (bot responds automatically)
```

### In Other Channels:
```
!chat Hello, how are you today?
!system You are a helpful coding assistant who specializes in Python
!chat Can you help me with a Python function?
!reset
```

### Character Examples:
```
# Switch to different characters
!character scholar    # Academic expert with detailed responses
!character creative   # Creative muse with high temperature
!character analyst    # Logical analyst with precise responses

# List all available characters
!characters

# View current character
!character

# Create a custom character
!create_character wizard "Merlin" 0.8 600 "A wise wizard | You are Merlin, the wise wizard of Camelot. Speak with ancient wisdom and magical knowledge."

# Delete a custom character
!delete_character wizard
```

### System Prompt Examples:
```
# Set a custom prompt
!system You are a creative storyteller who helps with writing fantasy novels

# Use a preset prompt
!preset coding
!preset creative
!preset pirate

# View available presets
!preset

# Check current prompt
!prompt
```

## Features

- **Multiple Characters**: Switch between different AI personalities with unique parameters
- **Per-channel conversations**: Each Discord channel maintains its own conversation history and active character
- **Individual character parameters**: Each character has custom temperature, max tokens, and system prompts
- **Character persistence**: Characters are saved and restored when the bot restarts
- **Custom character creation**: Create your own characters with specific parameters
- **Preset prompts**: Choose from 8 built-in personality presets (coding, creative, tutor, pirate, etc.)
- **Message length handling**: Automatically splits long responses
- **Error handling**: Graceful error messages for users
- **Conversation memory**: Remembers context within each channel (last 20 messages)

### Available Default Characters:
- **default** (Assistant): Helpful and friendly assistant (temp: 0.7, tokens: 500)
- **scholar** (Scholar): Academic expert with detailed responses (temp: 0.3, tokens: 800)
- **creative** (Muse): Creative and imaginative assistant (temp: 0.9, tokens: 600)  
- **analyst** (Analyst): Logical analyst for problem-solving (temp: 0.2, tokens: 700)
- **sage** (Sage): Wise philosopher with thoughtful insights (temp: 0.6, tokens: 500)

### Available Preset Prompts:
- **default**: Helpful and friendly assistant
- **coding**: Programming and software development specialist
- **creative**: Creative writing and storytelling assistant
- **tutor**: Patient teacher who explains complex topics simply
- **pirate**: Friendly pirate who speaks in pirate language
- **professional**: Formal business communication assistant
- **casual**: Relaxed, conversational chat buddy
- **scientist**: Knowledgeable scientist with precise explanations

## Troubleshooting

### Bot doesn't respond
- Check that the bot token is correct in `.env`
- Ensure "Message Content Intent" is enabled in Discord Developer Portal
- Verify the bot has permissions to read and send messages in the channel

### Permission errors
- Make sure the bot has the necessary permissions in your Discord server
- Check that the bot role is high enough in the server hierarchy

### API errors
- Verify your OpenAI API key is valid and has credits
- Check your internet connection