from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(http_options=types.HttpOptions(api_version="v1beta"))

# ==============================================================================
# PART 1: Triggering a Classic Hallucination (Leading Question + No Context)
# ==============================================================================

# Subtle trap: plausible-sounding question where the model has to guess specific details!
tricky_prompt = (
    "In the Indian startup 'QuickCart Logistics Pvt Ltd' (founded in Pune in 2021), "
    "who is the current CTO and what is their customer support phone number? "
    "Give a direct answer."
)

unprotected_response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=tricky_prompt,
    config=types.GenerateContentConfig(
        temperature=0.8,  # Higher temperature encourages creative guessing!
        thinking_config=types.ThinkingConfig(thinking_budget=0),
    ),
)

print("--- PART 1: Unprotected Model (Watch it invent fake code!) ---")
print(unprotected_response.text.strip())


# ==============================================================================
# PART 2: Production Anti-Hallucination Guardrails (Strict Grounding + Fallback)
# ==============================================================================

# Real data fetched from your PostgreSQL 'products' table in a real backend!
database_context = """
<products>
  <product id="1" name="iPhone 16" price="799.99" stock="12" warranty="1 year standard" />
  <product id="2" name="Wireless Mechanical Keyboard" price="89.00" stock="0" warranty="2 years" />
</products>
"""

strict_system_prompt = """
You are a strict TechShop support assistant.
Rules:
1. Answer customer questions using ONLY the facts inside <products> tags.
2. NEVER guess, assume, or add outside knowledge (like free gifts or unmentioned specs).
3. If the answer is NOT explicitly stated in <products>, reply ONLY with:
   "I don't have that information in our store records."
"""

customer_question = "Does the iPhone 16 come with free AirPods, and is the Wireless Mechanical Keyboard in stock?"

grounded_response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=f"{database_context}\n\nCustomer Question: {customer_question}",
    config=types.GenerateContentConfig(
        system_instruction=strict_system_prompt,
        temperature=0.0,  # Zero randomness for strict factual faithfulness
        thinking_config=types.ThinkingConfig(thinking_budget=0),
    ),
)

print("\n--- PART 2: Grounded Production Model (Zero Hallucination!) ---")
print(grounded_response.text.strip())