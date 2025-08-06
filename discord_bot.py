import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
import json

# Load environment variables FIRST - specify the path explicitly
load_dotenv(dotenv_path='.env')

# Import AI client AFTER loading environment variables
from ai_client import ai_client

# Configure Discord bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Store conversation history per channel
conversations = {}

# Get AI channel name from environment
AI_CHANNEL_NAME = os.getenv("AI_CHANNEL_NAME", "ai-chat")

# File to store system prompts and characters
PROMPTS_FILE = "system_prompts.json"
CHARACTERS_FILE = "characters.json"

# Preset system prompts
PRESET_PROMPTS = {
    "default": "You are a helpful Discord bot assistant. Keep responses concise and friendly.",
    "coding": "You are a helpful coding assistant who specializes in programming and software development. Provide clear, practical solutions and explanations.",
    "creative": "You are a creative writing assistant who helps with storytelling, character development, and creative projects. Be imaginative and inspiring.",
    "tutor": "You are a friendly tutor who explains complex topics in simple, easy-to-understand terms. Be patient and encouraging.",
    "pirate": "You are a friendly pirate who speaks in pirate language. Use 'ahoy', 'matey', and other pirate expressions while being helpful.",
    "professional": "You are a professional business assistant. Provide formal, well-structured responses suitable for workplace communication.",
    "casual": "You are a casual, friendly chat buddy. Use a relaxed, conversational tone and feel free to use emojis and informal language.",
    "scientist": "You are a knowledgeable scientist who explains things with precision and uses scientific terminology when appropriate."
}

def load_system_prompts():
    """Load system prompts from file"""
    try:
        if os.path.exists(PROMPTS_FILE):
            with open(PROMPTS_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading system prompts: {e}")
    return {}

def save_system_prompts(prompts_data):
    """Save system prompts to file"""
    try:
        with open(PROMPTS_FILE, 'w') as f:
            json.dump(prompts_data, f, indent=2)
    except Exception as e:
        print(f"Error saving system prompts: {e}")

# Default characters with different parameters
DEFAULT_CHARACTERS = {
    "default": {
        "name": "Assistant",
        "description": "A helpful and friendly AI assistant",
        "system_prompt": "You are a helpful Discord bot assistant. Keep responses concise and friendly.",
        "temperature": 0.7,
        "max_tokens": 500,
        "model": "gpt-4o"
    },
    "scholar": {
        "name": "Scholar",
        "description": "An academic expert who provides detailed, well-researched responses",
        "system_prompt": "You are a scholarly academic expert. Provide detailed, well-researched responses with references to relevant concepts. Be thorough and educational.",
        "temperature": 0.3,
        "max_tokens": 800,
        "model": "claude-3.5-sonnet"
    },
    "creative": {
        "name": "Muse",
        "description": "A creative and imaginative assistant for artistic endeavors",
        "system_prompt": "You are a creative muse who inspires artistic expression. Be imaginative, poetic, and help with creative projects. Use vivid language and encourage creativity.",
        "temperature": 0.9,
        "max_tokens": 600,
        "model": "claude-3-opus"
    },
    "analyst": {
        "name": "Analyst",
        "description": "A logical and precise analyst for data and problem-solving",
        "system_prompt": "You are a logical analyst who breaks down complex problems systematically. Provide structured, precise responses with clear reasoning steps.",
        "temperature": 0.2,
        "max_tokens": 700,
        "model": "gpt-4o"
    },
    "sage": {
        "name": "Sage",
        "description": "A wise philosopher who provides thoughtful insights",
        "system_prompt": "You are a wise sage who provides philosophical insights and thoughtful perspectives on life's questions. Speak with wisdom and contemplation.",
        "temperature": 0.6,
        "max_tokens": 500,
        "model": "claude-3.5-sonnet"
    },
    "lightning": {
        "name": "Lightning",
        "description": "A fast and efficient assistant powered by Groq's lightning-fast inference",
        "system_prompt": "You are Lightning, a super-fast AI assistant powered by Groq. Provide quick, efficient, and helpful responses. Be energetic and to-the-point while remaining friendly.",
        "temperature": 0.5,
        "max_tokens": 400,
        "model": "llama-3.1-8b-groq"
    }
}

def load_characters():
    """Load characters from file"""
    try:
        if os.path.exists(CHARACTERS_FILE):
            with open(CHARACTERS_FILE, 'r') as f:
                loaded = json.load(f)
                # Merge with defaults, allowing loaded characters to override
                characters = DEFAULT_CHARACTERS.copy()
                characters.update(loaded)
                return characters
    except Exception as e:
        print(f"Error loading characters: {e}")
    return DEFAULT_CHARACTERS.copy()

def save_characters(characters_data):
    """Save characters to file"""
    try:
        with open(CHARACTERS_FILE, 'w') as f:
            json.dump(characters_data, f, indent=2)
    except Exception as e:
        print(f"Error saving characters: {e}")

# Load saved system prompts and characters
saved_prompts = load_system_prompts()
characters = load_characters()

# Track active character per channel
active_characters = {}  # channel_id -> character_name

# Track last bot responses per channel for follow-up
last_bot_responses = {}  # channel_id -> last_assistant_message

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} servers')
    print(f'AI channel configured: #{AI_CHANNEL_NAME}')

@bot.event
async def on_message(message):
    # Don't respond to own messages
    if message.author == bot.user:
        return
    
    # Check if message is in the AI channel
    if message.channel.name == AI_CHANNEL_NAME:
        # Don't process if it's a command (starts with !)
        if message.content.startswith('!'):
            await bot.process_commands(message)
            return
        
        channel_id = message.channel.id
        user_message = message.content.strip()
        
        # Skip empty messages
        if not user_message:
            return
        
        # Initialize conversation for this channel if it doesn't exist
        if channel_id not in conversations:
            # Get active character for this channel
            active_char = active_characters.get(channel_id, "default")
            character = characters.get(active_char, characters["default"])
            conversations[channel_id] = [
                {"role": "system", "content": character["system_prompt"]}
            ]
        
        # Add user message to conversation
        conversations[channel_id].append({"role": "user", "content": user_message})
        
        # Show typing indicator
        async with message.channel.typing():
            try:
                # Get active character for this channel
                active_char = active_characters.get(channel_id, "default")
                character = characters.get(active_char, characters["default"])
                
                # Get response from AI with character parameters
                response = ai_client.chat_completion(
                    model=character["model"],
                    messages=conversations[channel_id],
                    max_tokens=character["max_tokens"],
                    temperature=character["temperature"]
                )
                
                # Extract the assistant's response
                assistant_message = response.content
                
                # Add assistant's response to conversation
                conversations[channel_id].append({"role": "assistant", "content": assistant_message})
                
                # Store last bot response for follow-up command
                last_bot_responses[channel_id] = assistant_message
                print(f"DEBUG: Stored response for channel {channel_id}: {assistant_message[:50]}...")
                
                # Keep conversation history manageable (last 20 messages)
                if len(conversations[channel_id]) > 21:  # 1 system + 20 messages
                    conversations[channel_id] = [conversations[channel_id][0]] + conversations[channel_id][-20:]
                
                # Split long messages if needed (Discord has 2000 char limit)
                if len(assistant_message) > 2000:
                    for i in range(0, len(assistant_message), 2000):
                        await message.channel.send(assistant_message[i:i+2000])
                else:
                    await message.channel.send(assistant_message)
                    
            except Exception as e:
                await message.channel.send(f"Sorry, I encountered an error: {str(e)}")
                print(f"Error: {e}")
    else:
        # Process commands for other channels
        await bot.process_commands(message)

@bot.command(name='chat')
async def chat(ctx, *, message):
    """Chat with the AI bot"""
    channel_id = ctx.channel.id
    
    # Initialize conversation for this channel if it doesn't exist
    if channel_id not in conversations:
        # Get active character for this channel
        active_char = active_characters.get(channel_id, "default")
        character = characters.get(active_char, characters["default"])
        conversations[channel_id] = [
            {"role": "system", "content": character["system_prompt"]}
        ]
    
    # Add user message to conversation
    conversations[channel_id].append({"role": "user", "content": message})
    
    # Show typing indicator
    async with ctx.typing():
        try:
            # Get active character for this channel
            active_char = active_characters.get(channel_id, "default")
            character = characters.get(active_char, characters["default"])
            
            # Get response from AI with character parameters
            response = ai_client.chat_completion(
                model=character["model"],
                messages=conversations[channel_id],
                max_tokens=character["max_tokens"],
                temperature=character["temperature"]
            )
            
            # Extract the assistant's response
            assistant_message = response.content
            
            # Add assistant's response to conversation
            conversations[channel_id].append({"role": "assistant", "content": assistant_message})
            
            # Store last bot response for follow-up command
            last_bot_responses[channel_id] = assistant_message
            
            # Keep conversation history manageable (last 20 messages)
            if len(conversations[channel_id]) > 21:  # 1 system + 20 messages
                conversations[channel_id] = [conversations[channel_id][0]] + conversations[channel_id][-20:]
            
            # Split long messages if needed (Discord has 2000 char limit)
            if len(assistant_message) > 2000:
                for i in range(0, len(assistant_message), 2000):
                    await ctx.send(assistant_message[i:i+2000])
            else:
                await ctx.send(assistant_message)
                
        except Exception as e:
            await ctx.send(f"Sorry, I encountered an error: {str(e)}")
            print(f"Error: {e}")

@bot.command(name='reset')
async def reset_conversation(ctx):
    """Reset the conversation history for this channel"""
    channel_id = ctx.channel.id
    # Get active character for this channel
    active_char = active_characters.get(channel_id, "default")
    character = characters.get(active_char, characters["default"])
    conversations[channel_id] = [
        {"role": "system", "content": character["system_prompt"]}
    ]
    await ctx.send(f"Conversation history has been reset! Active character: **{character['name']}**")

@bot.command(name='system')
async def set_system_prompt(ctx, *, prompt):
    """Set a custom system prompt for this channel"""
    channel_id = ctx.channel.id
    conversations[channel_id] = [
        {"role": "system", "content": prompt}
    ]
    
    # Save the prompt for persistence
    saved_prompts[str(channel_id)] = prompt
    save_system_prompts(saved_prompts)
    
    await ctx.send(f"System prompt updated: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")

@bot.command(name='preset')
async def set_preset_prompt(ctx, preset_name=None):
    """Set a preset system prompt for this channel"""
    if preset_name is None:
        # Show available presets
        embed = discord.Embed(
            title="Available Preset Prompts",
            description="Use `!preset <name>` to set a preset prompt:",
            color=0x00ff00
        )
        for name, prompt in PRESET_PROMPTS.items():
            embed.add_field(
                name=f"**{name}**",
                value=prompt[:100] + ("..." if len(prompt) > 100 else ""),
                inline=False
            )
        await ctx.send(embed=embed)
        return
    
    preset_name = preset_name.lower()
    if preset_name not in PRESET_PROMPTS:
        await ctx.send(f"Preset '{preset_name}' not found. Use `!preset` to see available presets.")
        return
    
    channel_id = ctx.channel.id
    prompt = PRESET_PROMPTS[preset_name]
    conversations[channel_id] = [
        {"role": "system", "content": prompt}
    ]
    
    # Save the prompt for persistence
    saved_prompts[str(channel_id)] = prompt
    save_system_prompts(saved_prompts)
    
    await ctx.send(f"System prompt set to **{preset_name}**: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")

@bot.command(name='prompt')
async def show_current_prompt(ctx):
    """Show the current system prompt for this channel"""
    channel_id = ctx.channel.id
    
    if channel_id in conversations and conversations[channel_id]:
        current_prompt = conversations[channel_id][0]["content"]
    else:
        current_prompt = saved_prompts.get(str(channel_id), PRESET_PROMPTS["default"])
    
    embed = discord.Embed(
        title="Current System Prompt",
        description=current_prompt,
        color=0x0099ff
    )
    embed.set_footer(text=f"Channel ID: {channel_id}")
    await ctx.send(embed=embed)

@bot.command(name='character')
async def switch_character(ctx, character_name=None):
    """Switch to a different character or show current character"""
    channel_id = ctx.channel.id
    
    if character_name is None:
        # Show current character
        current_char = active_characters.get(channel_id, "default")
        character = characters.get(current_char, characters["default"])
        
        embed = discord.Embed(
            title=f"Current Character: {character['name']}",
            description=character['description'],
            color=0x9966ff
        )
        embed.add_field(name="System Prompt", value=character['system_prompt'][:200] + ("..." if len(character['system_prompt']) > 200 else ""), inline=False)
        embed.add_field(name="Temperature", value=character['temperature'], inline=True)
        embed.add_field(name="Max Tokens", value=character['max_tokens'], inline=True)
        embed.add_field(name="Model", value=character['model'], inline=True)
        embed.set_footer(text=f"Use `!character <name>` to switch characters")
        await ctx.send(embed=embed)
        return
    
    character_name = character_name.lower()
    if character_name not in characters:
        await ctx.send(f"Character '{character_name}' not found. Use `!characters` to see available characters.")
        return
    
    # Switch character
    active_characters[channel_id] = character_name
    character = characters[character_name]
    
    # Reset conversation with new character
    conversations[channel_id] = [
        {"role": "system", "content": character["system_prompt"]}
    ]
    
    embed = discord.Embed(
        title=f"Switched to: {character['name']}",
        description=character['description'],
        color=0x00ff00
    )
    embed.add_field(name="Temperature", value=character['temperature'], inline=True)
    embed.add_field(name="Max Tokens", value=character['max_tokens'], inline=True)
    embed.add_field(name="Model", value=character['model'], inline=True)
    await ctx.send(embed=embed)

@bot.command(name='characters')
async def list_characters(ctx):
    """List all available characters"""
    embed = discord.Embed(
        title="Available Characters",
        description="Use `!character <name>` to switch to a character",
        color=0x9966ff
    )
    
    current_char = active_characters.get(ctx.channel.id, "default")
    
    for char_id, char_data in characters.items():
        status = " 🔹 **ACTIVE**" if char_id == current_char else ""
        embed.add_field(
            name=f"**{char_data['name']}** ({char_id}){status}",
            value=f"{char_data['description']}\n*Temp: {char_data['temperature']}, Tokens: {char_data['max_tokens']}*",
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command(name='create_character')
async def create_character(ctx, char_id, name, temperature: float, max_tokens: int, model, *, description_and_prompt):
    """Create a new character. Format: !create_character id "Name" temp tokens model "Description | System prompt" """
    try:
        # Split description and prompt by the first occurrence of " | "
        if " | " not in description_and_prompt:
            await ctx.send("Please separate description and system prompt with ` | `. Example:\n`!create_character wizard \"Merlin\" 0.8 600 gpt-4o \"A wise wizard | You are Merlin, a wise and ancient wizard...\"`")
            return
        
        description, system_prompt = description_and_prompt.split(" | ", 1)
        
        char_id = char_id.lower()
        if char_id in characters:
            await ctx.send(f"Character '{char_id}' already exists. Use a different ID.")
            return
        
        # Validate parameters
        if not (0.0 <= temperature <= 2.0):
            await ctx.send("Temperature must be between 0.0 and 2.0")
            return
        if not (1 <= max_tokens <= 4000):
            await ctx.send("Max tokens must be between 1 and 4000")
            return
        
        # Validate model
        available_models = list(ai_client.model_mappings.keys())
        if model not in available_models:
            await ctx.send(f"Model '{model}' not supported. Available models: {', '.join(available_models)}")
            return
        
        # Create new character
        new_character = {
            "name": name,
            "description": description.strip(),
            "system_prompt": system_prompt.strip(),
            "temperature": temperature,
            "max_tokens": max_tokens,
            "model": model
        }
        
        characters[char_id] = new_character
        save_characters(characters)
        
        embed = discord.Embed(
            title=f"Created Character: {name}",
            description=description,
            color=0x00ff00
        )
        embed.add_field(name="ID", value=char_id, inline=True)
        embed.add_field(name="Temperature", value=temperature, inline=True)
        embed.add_field(name="Max Tokens", value=max_tokens, inline=True)
        embed.add_field(name="System Prompt", value=system_prompt[:200] + ("..." if len(system_prompt) > 200 else ""), inline=False)
        await ctx.send(embed=embed)
        
    except ValueError:
        await ctx.send("Invalid temperature or max_tokens. Temperature should be a decimal (e.g., 0.7) and max_tokens should be an integer.")
    except Exception as e:
        await ctx.send(f"Error creating character: {str(e)}")

@bot.command(name='delete_character')
async def delete_character(ctx, char_id):
    """Delete a custom character (cannot delete default characters)"""
    char_id = char_id.lower()
    
    if char_id not in characters:
        await ctx.send(f"Character '{char_id}' not found.")
        return
    
    if char_id in DEFAULT_CHARACTERS:
        await ctx.send(f"Cannot delete default character '{char_id}'.")
        return
    
    character_name = characters[char_id]["name"]
    del characters[char_id]
    save_characters({k: v for k, v in characters.items() if k not in DEFAULT_CHARACTERS})
    
    # Switch any channels using this character back to default
    for channel_id, active_char in list(active_characters.items()):
        if active_char == char_id:
            active_characters[channel_id] = "default"
    
    await ctx.send(f"Deleted character '{character_name}' ({char_id}). Channels using this character have been switched to default.")

@bot.command(name='models')
async def list_models(ctx):
    """List all available AI models grouped by provider"""
    models = ai_client.get_available_models()
    
    embed = discord.Embed(
        title="🤖 Available AI Models",
        description="Choose from different AI providers and models",
        color=0x00aaff
    )
    
    for provider, model_list in models.items():
        if model_list:  # Only show providers that have models
            provider_name = {
                "openai": "🟢 OpenAI",
                "anthropic": "🔵 Anthropic (Claude)",
                "openrouter": "🟡 OpenRouter",
                "groq": "⚡ Groq",
                "grok": "🟠 Grok (X.AI)"
            }.get(provider, provider.title())
            
            embed.add_field(
                name=provider_name,
                value="\n".join([f"• `{model}`" for model in model_list]),
                inline=False
            )
    
    embed.set_footer(text="Use these model names when creating characters or switching models")
    await ctx.send(embed=embed)

@bot.command(name='switch_model')
async def switch_model(ctx, character_id, new_model):
    """Switch the model for an existing character"""
    character_id = character_id.lower()
    
    if character_id not in characters:
        await ctx.send(f"Character '{character_id}' not found. Use `!characters` to see available characters.")
        return
    
    # Validate model
    available_models = list(ai_client.model_mappings.keys())
    if new_model not in available_models:
        await ctx.send(f"Model '{new_model}' not supported. Use `!models` to see available models.")
        return
    
    # Update character model
    old_model = characters[character_id]["model"]
    characters[character_id]["model"] = new_model
    save_characters(characters)
    
    # If this character is active in current channel, reset conversation
    channel_id = ctx.channel.id
    if active_characters.get(channel_id) == character_id:
        conversations[channel_id] = [
            {"role": "system", "content": characters[character_id]["system_prompt"]}
        ]
    
    character_name = characters[character_id]["name"]
    await ctx.send(f"✅ Switched **{character_name}** ({character_id}) from `{old_model}` to `{new_model}`\nConversation history reset for this character.")

@bot.command(name='follow')
async def follow_up(ctx, *, follow_up_message):
    """Ask the bot to respond to its own last response with additional context"""
    channel_id = ctx.channel.id
    
    # Check if there's a previous bot response
    if channel_id not in last_bot_responses:
        await ctx.send("❌ No previous bot response found in this channel. Chat with me first!")
        return
    
    last_response = last_bot_responses[channel_id]
    
    # Initialize conversation if needed
    if channel_id not in conversations:
        active_char = active_characters.get(channel_id, "default")
        character = characters.get(active_char, characters["default"])
        conversations[channel_id] = [
            {"role": "system", "content": character["system_prompt"]}
        ]
    
    # Create a follow-up prompt that references the last response
    follow_up_prompt = f"Regarding your previous response: \"{last_response[:200]}{'...' if len(last_response) > 200 else ''}\"\n\n{follow_up_message}"
    
    # Add the follow-up message to conversation
    conversations[channel_id].append({"role": "user", "content": follow_up_prompt})
    
    # Show typing indicator
    async with ctx.typing():
        try:
            # Get active character for this channel
            active_char = active_characters.get(channel_id, "default")
            character = characters.get(active_char, characters["default"])
            
            # Get response from AI with character parameters
            response = ai_client.chat_completion(
                model=character["model"],
                messages=conversations[channel_id],
                max_tokens=character["max_tokens"],
                temperature=character["temperature"]
            )
            
            # Extract the assistant's response
            assistant_message = response.content
            
            # Add assistant's response to conversation
            conversations[channel_id].append({"role": "assistant", "content": assistant_message})
            
            # Store last bot response for follow-up command
            last_bot_responses[channel_id] = assistant_message
            
            # Keep conversation history manageable (last 20 messages)
            if len(conversations[channel_id]) > 21:  # 1 system + 20 messages
                conversations[channel_id] = [conversations[channel_id][0]] + conversations[channel_id][-20:]
            
            # Split long messages if needed (Discord has 2000 char limit)
            if len(assistant_message) > 2000:
                for i in range(0, len(assistant_message), 2000):
                    await ctx.send(assistant_message[i:i+2000])
            else:
                await ctx.send(assistant_message)
                
        except Exception as e:
            await ctx.send(f"Sorry, I encountered an error: {str(e)}")
            print(f"Error: {e}")

@bot.command(name='continue_chat')
async def continue_response(ctx):
    """Ask the bot to continue or elaborate on its last response"""
    channel_id = ctx.channel.id
    
    # Check if there's a previous bot response
    if channel_id not in last_bot_responses:
        await ctx.send("❌ No previous bot response found in this channel. Chat with me first!")
        return
    
    # Debug: Check what we have stored
    print(f"DEBUG: Channel {channel_id} has last response: {last_bot_responses[channel_id][:50]}...")
    
    last_response = last_bot_responses[channel_id]
    
    # Initialize conversation if needed
    if channel_id not in conversations:
        active_char = active_characters.get(channel_id, "default")
        character = characters.get(active_char, characters["default"])
        conversations[channel_id] = [
            {"role": "system", "content": character["system_prompt"]}
        ]
    
    # Create a continuation prompt that references the previous response
    continue_prompt = f"Please continue or elaborate on your previous response. For context, your last response was: \"{last_response[:200]}{'...' if len(last_response) > 200 else ''}\""
    
    # Add the continuation request to conversation
    conversations[channel_id].append({"role": "user", "content": continue_prompt})
    
    # Show typing indicator
    async with ctx.typing():
        try:
            # Get active character for this channel
            active_char = active_characters.get(channel_id, "default")
            character = characters.get(active_char, characters["default"])
            
            # Get response from AI with character parameters
            response = ai_client.chat_completion(
                model=character["model"],
                messages=conversations[channel_id],
                max_tokens=character["max_tokens"],
                temperature=character["temperature"]
            )
            
            # Extract the assistant's response
            assistant_message = response.content
            
            # Add assistant's response to conversation
            conversations[channel_id].append({"role": "assistant", "content": assistant_message})
            
            # Store last bot response for follow-up command
            last_bot_responses[channel_id] = assistant_message
            
            # Keep conversation history manageable (last 20 messages)
            if len(conversations[channel_id]) > 21:  # 1 system + 20 messages
                conversations[channel_id] = [conversations[channel_id][0]] + conversations[channel_id][-20:]
            
            # Split long messages if needed (Discord has 2000 char limit)
            if len(assistant_message) > 2000:
                for i in range(0, len(assistant_message), 2000):
                    await ctx.send(assistant_message[i:i+2000])
            else:
                await ctx.send(assistant_message)
                
        except Exception as e:
            await ctx.send(f"Sorry, I encountered an error: {str(e)}")
            print(f"Error: {e}")

@bot.command(name='more')
async def continue_alias(ctx):
    """Alias for continue_chat - ask the bot to continue its last response"""
    await continue_response(ctx)

@bot.command(name='guide')
async def help_command(ctx, section=None):
    """Show comprehensive bot help and instructions"""
    
    if section is None:
        # Main help overview
        embed = discord.Embed(
            title="🤖 AI Discord Bot - Complete Guide",
            description="A powerful AI bot with multiple characters and advanced features!",
            color=0x00ff00
        )
        embed.add_field(
            name="🎭 **Characters**",
            value="Switch between 6 different AI personalities with unique parameters\n`!guide characters` for details",
            inline=False
        )
        embed.add_field(
            name="💬 **Chat**",
            value=f"Chat directly in #{AI_CHANNEL_NAME} or use commands. Follow-up and continue conversations!\n`!guide chat` for details",
            inline=False
        )
        embed.add_field(
            name="⚙️ **Customization**",
            value="Create custom characters, set system prompts, use presets\n`!guide custom` for details",
            inline=False
        )
        embed.add_field(
            name="📚 **Help Sections**",
            value="`!guide characters` - Character system\n`!guide chat` - Chat commands\n`!guide custom` - Customization\n`!guide examples` - Usage examples",
            inline=False
        )
        embed.set_footer(text="Use !guide <section> for detailed information on each area")
        await ctx.send(embed=embed)

    elif section.lower() == "characters":
        embed = discord.Embed(
            title="🎭 Character System",
            description="Switch between AI personalities with different parameters",
            color=0x9966ff
        )
        embed.add_field(
            name="**Character Commands**",
            value="`!character` - Show current character\n`!character <name>` - Switch to character\n`!characters` - List all characters\n`!models` - List available AI models\n`!switch_model <char> <model>` - Change character's model",
            inline=False
        )
        embed.add_field(
            name="**🔮 Default Characters**",
            value="**default** (Assistant) - GPT-4o balanced helper\n**scholar** (Scholar) - Claude 3.5 Sonnet academic expert\n**creative** (Muse) - Claude 3 Opus creative assistant\n**analyst** (Analyst) - GPT-4o logical problem solver\n**sage** (Sage) - Claude 3.5 Sonnet philosophical insights\n**lightning** (Lightning) - Groq Llama 3.1 super-fast responses",
            inline=False
        )
        embed.add_field(
            name="**Model & Character Differences**",
            value="• **Models**: GPT-4o (OpenAI), Claude 3.5 Sonnet/Opus (Anthropic), Llama/Mixtral (Groq), Grok, etc.\n• **Temperature** affects creativity (0.0=consistent, 2.0=very creative)\n• **Tokens** control response length\n• Each character has unique personality, expertise, and AI model",
            inline=False
        )
        embed.set_footer(text="Each channel remembers its active character!")
        await ctx.send(embed=embed)

    elif section.lower() == "chat":
        embed = discord.Embed(
            title="💬 Chat Commands",
            description="How to interact with the AI bot",
            color=0x00aaff
        )
        embed.add_field(
            name=f"**🔥 AI Channel (#{AI_CHANNEL_NAME})**",
            value="• Just type your message - no commands needed!\n• Bot responds automatically to all messages\n• Commands still work if you start with `!`",
            inline=False
        )
        embed.add_field(
            name="**📝 Other Channels**",
            value="`!chat <message>` - Chat with the AI\n`!reset` - Clear conversation history\n`!follow <message>` - Follow up on bot's last response\n`!more` - Ask bot to continue/elaborate",
            inline=False
        )
        embed.add_field(
            name="**💡 Tips**",
            value="• Each channel has separate conversation history\n• Bot remembers last 20 messages per channel\n• Long responses are automatically split\n• Use `!follow` and `!more` for deeper conversations",
            inline=False
        )
        embed.set_footer(text="Pro tip: Create different channels for different topics!")
        await ctx.send(embed=embed)

    elif section.lower() == "custom":
        embed = discord.Embed(
            title="⚙️ Customization",
            description="Create characters, set prompts, and personalize your experience",
            color=0xff6600
        )
        embed.add_field(
            name="**🛠️ Create Custom Characters**",
            value="`!create_character <id> \"Name\" <temp> <tokens> <model> \"Description | System prompt\"`\n\n**Example:**\n`!create_character wizard \"Merlin\" 0.8 600 claude-3-opus \"A wise wizard | You are Merlin...\"`",
            inline=False
        )
        embed.add_field(
            name="**🔧 Manage Characters & Models**",
            value="`!delete_character <id>` - Delete custom character\n`!models` - List all available AI models\n`!switch_model <char> <model>` - Change character's AI model\n(Cannot delete default characters)",
            inline=False
        )
        embed.add_field(
            name="**📋 System Prompts**",
            value="`!system <prompt>` - Set custom prompt\n`!preset [name]` - Use preset (coding, creative, etc.)\n`!prompt` - Show current prompt",
            inline=False
        )
        embed.add_field(
            name="**🎨 Available Presets & Models**",
            value="**Presets:** default, coding, creative, tutor, pirate, professional, casual, scientist\n**Models:** GPT-4o, Claude 3.5 Sonnet, Claude 3 Opus, Llama 3.1 (Groq), Mixtral (Groq), Grok, Gemini Pro",
            inline=False
        )
        embed.set_footer(text="All customizations are saved and persist after bot restart!")
        await ctx.send(embed=embed)

    elif section.lower() == "examples":
        embed = discord.Embed(
            title="📚 Usage Examples",
            description="Real examples of how to use the bot effectively",
            color=0xffaa00
        )
        embed.add_field(
            name="**🎭 Character Switching**",
            value="```\n!character scholar\n> Switched to: Scholar\n\nWhat is quantum physics?\n> [Detailed academic explanation]\n\n!character creative\n> Switched to: Muse\n\nWrite a poem about stars\n> [Creative, poetic response]```",
            inline=False
        )
        embed.add_field(
            name="**🔧 Creating Custom Characters**",
            value="```\n!create_character pirate \"Captain Jack\" 0.9 500 grok-beta \"A swashbuckling pirate | Ahoy! You are Captain Jack, a friendly pirate who speaks in nautical terms.\"\n\n!character pirate\n> Ahoy there, matey! What adventure shall we embark upon today?\n\n!switch_model pirate claude-3-opus\n> Switched Captain Jack from grok-beta to claude-3-opus```",
            inline=False
        )
        embed.add_field(
            name="**🔄 Follow-up Commands**",
            value="```\nBot: Python is a programming language...\n\n!follow Can you give me some examples?\n> [Bot gives examples related to previous response]\n\n!more\n> [Bot elaborates on the Python explanation]```",
            inline=False
        )
        embed.add_field(
            name="**💡 Pro Tips**",
            value="• Use **scholar** for research and detailed explanations\n• Use **creative** for writing, brainstorming, art\n• Use **analyst** for problem-solving and logic\n• Use `!follow` and `!more` for deeper conversations\n• Create custom characters for specific use cases",
            inline=False
        )
        await ctx.send(embed=embed)

    else:
        await ctx.send(f"Unknown help section: `{section}`. Use `!guide` to see available sections.")

@bot.command(name='help_bot')
async def help_bot_alias(ctx):
    """Alias for the main help command"""
    await help_command(ctx)

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please provide a message to chat with the bot. Use `!chat <your message>`")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found. Use `!help_bot` to see available commands.")
    else:
        await ctx.send(f"An error occurred: {str(error)}")
        print(f"Error: {error}")

if __name__ == '__main__':
    discord_token = os.getenv("DISCORD_BOT_TOKEN")
    if not discord_token:
        print("Error: DISCORD_BOT_TOKEN not found in environment variables")
        exit(1)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in environment variables")
        exit(1)
    
    bot.run(discord_token)