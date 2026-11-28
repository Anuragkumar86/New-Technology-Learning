from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(http_options=types.HttpOptions(api_version="v1beta"))

# Realistic messy input coming from a user in your Shop API
raw_customer_ticket = """
Hi team, I ordered the Wireless Mechanical Keyboard (Order #8841) 3 days ago.
Today the package arrived, the outer box was crushed, and the spacebar key is broken!
I need a replacement shipped before Friday because I have a coding hackathon. Please help!
"""

# ==============================================================================
# PART 1: Weak / Vague Prompt (Unpredictable format, conversational fluff)
# ==============================================================================
weak_response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=f"Analyze this customer ticket:\n{raw_customer_ticket}",
    config=types.GenerateContentConfig(
        temperature=0.7,
        thinking_config=types.ThinkingConfig(thinking_budget=0),
    ),
)

print("--- PART 1: Weak Prompt Output (Messy for a Backend!) ---")
print(weak_response.text.strip())


# ==============================================================================
# PART 2: Production Engineered Prompt (Role + Task + Constraints + Output Spec)
# ==============================================================================
engineered_system_prompt = """
You are a backend support triage engine for TechShop.
Your job is to extract structured triage metadata from customer support messages.

Rules & Constraints:
1. Classify 'category' strictly as one of: [DAMAGED_ITEM, LATE_DELIVERY, BILLING, OTHER].
2. Classify 'urgency' strictly as one of: [LOW, MEDIUM, HIGH]. Mark HIGH if the customer mentions a deadline or damaged product.
3. Extract 'order_id' as a string (e.g., "#8841"), or "UNKNOWN" if not mentioned.
4. Write 'action_summary' in maximum 12 words.
5. Output ONLY valid raw JSON with no markdown code fences (no ```json) and no conversational text.
"""

engineered_response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=f"Customer Message:\n{raw_customer_ticket}",
    config=types.GenerateContentConfig(
        system_instruction=engineered_system_prompt,
        temperature=0.0,  # Deterministic output for backend parsing
        thinking_config=types.ThinkingConfig(thinking_budget=0),
    ),
)

print("\n--- PART 2: Engineered Prompt Output (Clean & Backend-Ready!) ---")
print(engineered_response.text.strip())