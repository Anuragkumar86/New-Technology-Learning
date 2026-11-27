# File: my-ai-app/gemini_helper.py
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# Configured ONCE here—you never have to type HttpOptions again!
client = genai.Client(http_options=types.HttpOptions(api_version="v1beta"))


def ask_fast(prompt: str, temperature: float = 0.0) -> str:
    """Fast, cheap call with thinking OFF (great for JSON, classification, simple chat)."""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=temperature,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        ),
    )
    return response.text.strip()