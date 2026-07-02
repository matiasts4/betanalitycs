import os
import json
import requests

DEVHUB_CONFIG_PATH = "/home/matias/ArxonLabs/devhub/data/llm-providers-config.json"

def load_dotenv():
    # Try to load from pl-web/.env or pl-web/.env.local
    for env_name in [".env.local", ".env"]:
        env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../../{env_name}"))
        if os.path.exists(env_path):
            try:
                with open(env_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, val = line.split("=", 1)
                            val = val.strip().strip("'\"")
                            os.environ[key.strip()] = val
            except Exception as e:
                print(f"[Assistant] Error reading {env_name}: {e}")

def load_api_keys():
    load_dotenv()
    keys = {
        "minimax": os.environ.get("MINIMAX_API_KEY"),
        "openrouter": os.environ.get("OPENROUTER_API_KEY"),
        "openai": os.environ.get("OPENAI_API_KEY"),
        "anthropic": os.environ.get("ANTHROPIC_API_KEY")
    }
    
    # Try reading from devhub config as fallback
    if os.path.exists(DEVHUB_CONFIG_PATH):
        try:
            with open(DEVHUB_CONFIG_PATH, "r") as f:
                config = json.load(f)
                providers = config.get("providers", {})
                
                if not keys["minimax"]:
                    keys["minimax"] = providers.get("minimax", {}).get("MINIMAX_API_KEY")
                if not keys["openrouter"]:
                    keys["openrouter"] = providers.get("openrouter", {}).get("OPENROUTER_API_KEY")
        except Exception as e:
            print(f"[Assistant] Error reading devhub config: {e}")
            
    return keys

class BaseLLMProvider:
    def __init__(self, api_key):
        self.api_key = api_key

    def generate(self, system_prompt, user_prompt, model):
        raise NotImplementedError()

class MiniMaxProvider(BaseLLMProvider):
    def generate(self, system_prompt, user_prompt, model):
        if not self.api_key:
            raise ValueError("MINIMAX_API_KEY is not configured.")
            
        url = "https://api.minimax.io/anthropic/v1/messages"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        body = {
            "model": model or "minimax-coding-plan/MiniMax-M3",
            "max_tokens": 2048,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": user_prompt}
            ]
        }
        
        response = requests.post(url, headers=headers, json=body)
        if not response.ok:
            raise Exception(f"MiniMax API error {response.status_code}: {response.text}")
            
        data = response.json()
        return data["content"][0]["text"]

class OpenRouterProvider(BaseLLMProvider):
    def generate(self, system_prompt, user_prompt, model):
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is not configured.")
            
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        body = {
            "model": model or "qwen/qwen3.6-plus:free",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        }
        
        response = requests.post(url, headers=headers, json=body)
        if not response.ok:
            raise Exception(f"OpenRouter API error {response.status_code}: {response.text}")
            
        data = response.json()
        return data["choices"][0]["message"]["content"]

class OpenAIProvider(BaseLLMProvider):
    def generate(self, system_prompt, user_prompt, model):
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not configured.")
            
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        body = {
            "model": model or "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        }
        
        response = requests.post(url, headers=headers, json=body)
        if not response.ok:
            raise Exception(f"OpenAI API error {response.status_code}: {response.text}")
            
        data = response.json()
        return data["choices"][0]["message"]["content"]

class AnthropicProvider(BaseLLMProvider):
    def generate(self, system_prompt, user_prompt, model):
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is not configured.")
            
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        body = {
            "model": model or "claude-3-5-sonnet-20241022",
            "max_tokens": 2048,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": user_prompt}
            ]
        }
        
        response = requests.post(url, headers=headers, json=body)
        if not response.ok:
            raise Exception(f"Anthropic API error {response.status_code}: {response.text}")
            
        data = response.json()
        return data["content"][0]["text"]

def get_provider(provider_name):
    keys = load_api_keys()
    
    if provider_name == "minimax":
        return MiniMaxProvider(keys["minimax"])
    elif provider_name == "openrouter":
        return OpenRouterProvider(keys["openrouter"])
    elif provider_name == "openai":
        return OpenAIProvider(keys["openai"])
    elif provider_name == "anthropic":
        return AnthropicProvider(keys["anthropic"])
    else:
        raise ValueError(f"Unknown provider: {provider_name}")
