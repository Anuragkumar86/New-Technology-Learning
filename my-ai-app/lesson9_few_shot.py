from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(http_options=types.HttpOptions(api_version="v1beta"))

# ==============================================================================
# PART 1: Few-Shot Using XML <examples> Inside System Instruction
# Goal: Extract normalized product specs from messy, unstructured seller titles
# ==============================================================================

product_normalizer_system_prompt = """
You are a backend catalog normalizer for TechShop.
Convert messy seller product titles into clean, standardized JSON.
Follow the exact structure, units, and fallback rules shown in the examples below.

<examples>
  <example>
    <input>Apple MacBook Air M3 16gb ram 512 gb ssd space grey laptop</input>
    <output>{"brand": "Apple", "model": "MacBook Air M3", "ram_gb": 16, "storage_gb": 512}</output>
  </example>

  <example>
    <input>ASUS ROG Gaming Laptop - 32GB DDR5 / 1TB NVMe</input>
    <output>{"brand": "ASUS", "model": "ROG Gaming Laptop", "ram_gb": 32, "storage_gb": 1024}</output>
  </example>

  <example>
    <input>Logitech MX Master 3S Wireless Mouse Graphite</input>
    <output>{"brand": "Logitech", "model": "MX Master 3S", "ram_gb": null, "storage_gb": null}</output>
  </example>
</examples>

Output ONLY raw JSON matching the exact schema above.
"""

# Notice how tricky this new input is: "2TB" needs converting to 2048 GB, and RAM is missing!
new_messy_title = "Samsung Galaxy Book4 Pro 2TB SSD Silver Edition"

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=f"Normalize this product title:\n{new_messy_title}",
    config=types.GenerateContentConfig(
        system_instruction=product_normalizer_system_prompt,
        temperature=0.0,
        thinking_config=types.ThinkingConfig(thinking_budget=0),
    ),
)

print("--- PART 1: Few-Shot Product Normalizer ---")
print("Input: ", new_messy_title)
print("Output:", response.text.strip())


# ==============================================================================
# PART 2: Few-Shot Using Multi-Turn 'user' / 'model' Conversation Roles
# Goal: Sarcasm-aware review sentiment classifier
# ==============================================================================

few_shot_conversation = [
    # Example 1 (Positive)
    types.Content(role="user", parts=[types.Part.from_text(text="Review: Super fast shipping and works right out of the box!")]),
    types.Content(role="model", parts=[types.Part.from_text(text="POSITIVE")]),

    # Example 2 (Sarcastic Negative)
    types.Content(role="user", parts=[types.Part.from_text(text="Review: Oh awesome, the screen flickered and died in 10 minutes. Best money ever wasted!")]),
    types.Content(role="model", parts=[types.Part.from_text(text="NEGATIVE")]),

    # Example 3 (Mixed)
    types.Content(role="user", parts=[types.Part.from_text(text="Review: Camera quality is 10/10, but the battery barely survives half a day.")]),
    types.Content(role="model", parts=[types.Part.from_text(text="MIXED")]),

    # Real User Input to Classify:
    types.Content(role="user", parts=[types.Part.from_text(text="Review: Fantastic, another USB cable that stops charging after a single week.")]),
]

sentiment_response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=few_shot_conversation,
    config=types.GenerateContentConfig(
        system_instruction="Classify the product review strictly as POSITIVE, NEGATIVE, or MIXED.",
        temperature=0.0,
        thinking_config=types.ThinkingConfig(thinking_budget=0),
    ),
)

print("\n--- PART 2: Multi-Turn Few-Shot Sarcasm Classifier ---")
print("Classified Sentiment:", sentiment_response.text.strip())