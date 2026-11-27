from dotenv import load_dotenv
from google import genai
from google.genai import types

from gemini_helper import ask_fast

load_dotenv()
# client = genai.Client()
client = genai.Client(http_options=types.HttpOptions(api_version="v1beta"))

prompt = "Give me ONE creative brand name for a fast-charging USB-C cable. Reply with ONLY the name."

# ==============================================================================
# TEST 1: Deterministic / Strict Mode (temperature = 0.0)
# Great for: JSON extraction, classification, database queries, code fixes
# ==============================================================================
print("--- TEST 1: temperature = 0.0 (Run 3 times) ---")
for i in range(1, 4):
    response = ask_fast(prompt=prompt)
    print(f"  Run {i}: {response.text.strip()}")


# ==============================================================================
# TEST 2: Creative / Diverse Mode (temperature = 1.3, top_p = 0.95, top_k = 40)
# Great for: Brainstorming, product descriptions, marketing copy, chatbots
# ==============================================================================
print("\n--- TEST 2: temperature = 1.3, top_p = 0.95, top_k = 40 (Run 3 times) ---")
for i in range(1, 4):
    response = ask_fast(prompt=prompt)
    print(f"  Run {i}: {response.text.strip()}")