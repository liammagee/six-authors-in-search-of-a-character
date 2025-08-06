"""
High-level AI client interface that supports multiple providers:
- OpenAI (GPT models)
- Anthropic (Claude models)
- OpenRouter (Various models)
- Grok (X.AI models)
"""

import os
import requests
import json
from typing import Dict, List, Any, Optional
from openai import OpenAI
import anthropic
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

class AIResponse:
    """Standardized response format across all providers"""
    def __init__(self, content: str, model: str, provider: str, tokens_used: Optional[int] = None):
        self.content = content
        self.model = model
        self.provider = provider
        self.tokens_used = tokens_used

class UniversalAIClient:
    """Universal AI client that works with multiple providers"""
    
    def __init__(self):
        # Initialize clients for different providers
        self.openai_client = None
        self.anthropic_client = None
        # Don't setup clients immediately - do it on first use to ensure env vars are loaded
        
        # Model mappings
        self.model_mappings = {
            # OpenAI models
            "gpt-4o": {"provider": "openai", "model": "gpt-4o"},
            "gpt-4o-mini": {"provider": "openai", "model": "gpt-4o-mini"},
            "gpt-4": {"provider": "openai", "model": "gpt-4"},
            "gpt-3.5-turbo": {"provider": "openai", "model": "gpt-3.5-turbo"},
            
            # Anthropic models
            "claude-3.5-sonnet": {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022"},
            "claude-3-opus": {"provider": "anthropic", "model": "claude-3-opus-20240229"},
            "claude-3-haiku": {"provider": "anthropic", "model": "claude-3-haiku-20240307"},
            
            # OpenRouter models
            "gpt-oss-120b": {"provider": "openrouter", "model": "openai/gpt-oss-120b"},
            "horizon-beta": {"provider": "openrouter", "model": "openrouter/horizon-beta"},
            "claude-opus-4.1": {"provider": "openrouter", "model": "anthropic/claude-opus-4.1"},
            "llama-3.1-70b": {"provider": "openrouter", "model": "meta-llama/llama-3.1-70b-instruct"},
            "mixtral-8x7b": {"provider": "openrouter", "model": "mistralai/mixtral-8x7b-instruct"},
            "gemini-pro": {"provider": "openrouter", "model": "google/gemini-pro"},
            
            # Groq models
            "llama-3.1-8b-groq": {"provider": "groq", "model": "llama-3.1-8b-instant"},
            "llama-3.1-70b-groq": {"provider": "groq", "model": "llama-3.1-70b-versatile"},
            "llama-3.2-1b-groq": {"provider": "groq", "model": "llama-3.2-1b-preview"},
            "llama-3.2-3b-groq": {"provider": "groq", "model": "llama-3.2-3b-preview"},
            "mixtral-8x7b-groq": {"provider": "groq", "model": "mixtral-8x7b-32768"},
            "gemma-7b-groq": {"provider": "groq", "model": "gemma-7b-it"},
            
            # Grok models (via OpenRouter for now)
            "grok-beta": {"provider": "openrouter", "model": "x-ai/grok-beta"},
        }
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """Get list of available models grouped by provider"""
        models = {
            "openai": [],
            "anthropic": [],
            "openrouter": [],
            "groq": [],
            "grok": []
        }
        
        for model_name, config in self.model_mappings.items():
            provider = config["provider"]
            if provider == "openrouter" and "grok" in model_name:
                models["grok"].append(model_name)
            else:
                models[provider].append(model_name)
        
        return models
    
    def chat_completion(self, 
                       model: str, 
                       messages: List[Dict[str, str]], 
                       temperature: float = 0.7, 
                       max_tokens: int = 500) -> AIResponse:
        """Universal chat completion method"""
        
        if model not in self.model_mappings:
            raise ValueError(f"Model '{model}' not supported. Available models: {list(self.model_mappings.keys())}")
        
        config = self.model_mappings[model]
        provider = config["provider"]
        actual_model = config["model"]
        
        try:
            if provider == "openai":
                return self._openai_completion(actual_model, messages, temperature, max_tokens)
            elif provider == "anthropic":
                return self._anthropic_completion(actual_model, messages, temperature, max_tokens)
            elif provider == "openrouter":
                return self._openrouter_completion(actual_model, messages, temperature, max_tokens)
            elif provider == "groq":
                return self._groq_completion(actual_model, messages, temperature, max_tokens)
            else:
                raise ValueError(f"Provider '{provider}' not implemented")
        
        except Exception as e:
            raise Exception(f"Error with {provider} ({model}): {str(e)}")
    
    def _openai_completion(self, model: str, messages: List[Dict], temperature: float, max_tokens: int) -> AIResponse:
        """Handle OpenAI API calls"""
        # Initialize OpenAI client if not already done
        if not self.openai_client:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise Exception("OpenAI API key not configured")
            self.openai_client = OpenAI(api_key=api_key)
        
        response = self.openai_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        content = response.choices[0].message.content
        tokens_used = response.usage.total_tokens if response.usage else None
        
        return AIResponse(content, model, "openai", tokens_used)
    
    def _anthropic_completion(self, model: str, messages: List[Dict], temperature: float, max_tokens: int) -> AIResponse:
        """Handle Anthropic Claude API calls"""
        # Initialize Anthropic client if not already done
        if not self.anthropic_client:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise Exception("Anthropic API key not configured")
            self.anthropic_client = anthropic.Anthropic(api_key=api_key)
        
        # Convert OpenAI format to Anthropic format
        system_message = ""
        user_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                user_messages.append(msg)
        
        response = self.anthropic_client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_message,
            messages=user_messages
        )
        
        content = response.content[0].text
        tokens_used = response.usage.input_tokens + response.usage.output_tokens
        
        return AIResponse(content, model, "anthropic", tokens_used)
    
    def _openrouter_completion(self, model: str, messages: List[Dict], temperature: float, max_tokens: int) -> AIResponse:
        """Handle OpenRouter API calls"""
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise Exception("OpenRouter API key not configured")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/your-repo",
            "X-Title": "Discord AI Bot"
        }
        
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            data=json.dumps(data)
        )
        
        if response.status_code != 200:
            raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")
        
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        tokens_used = result.get("usage", {}).get("total_tokens")
        
        return AIResponse(content, model, "openrouter", tokens_used)
    
    def _groq_completion(self, model: str, messages: List[Dict], temperature: float, max_tokens: int) -> AIResponse:
        """Handle Groq API calls"""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise Exception("Groq API key not configured")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            data=json.dumps(data)
        )
        
        if response.status_code != 200:
            raise Exception(f"Groq API error: {response.status_code} - {response.text}")
        
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        tokens_used = result.get("usage", {}).get("total_tokens")
        
        return AIResponse(content, model, "groq", tokens_used)

# Global AI client instance
ai_client = UniversalAIClient()