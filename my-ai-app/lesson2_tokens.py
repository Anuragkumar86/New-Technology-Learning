from dotenv import load_dotenv
from google import genai
import tiktoken

load_dotenv()

# ==============================================================================
# PART 1: Exploring Local Tokenization with 'tiktoken' (100% Offline & Free)
# ==============================================================================

# Load a standard modern tokenizer encoding ('cl100k_base' or 'o200k_base')
encoder = tiktoken.get_encoding("o200k_base")

sample_text = "Hello Anurag! Learning AI engineering in 2026 is awesome 🚀"

# 1. ENCODE: Convert human string -> list of integer Token IDs
token_ids = encoder.encode(sample_text)

print(f"Original Text: {sample_text}")
print(f"Total Tokens:  {len(token_ids)}")
print(f"Token IDs:     {token_ids}\n")

# 2. INSPECT EACH CHUNK: Decode each individual ID to see how the AI chopped the text!
print("How the tokenizer split each piece:")
for tid in token_ids:
    # decode_single_token_bytes shows the exact raw characters/spaces inside each token
    piece = encoder.decode([tid])
    print(f"  ID {tid:<8} -> {repr(piece)}")

# 3. DECODE: Convert integer Token IDs back -> original human string
reconstructed_text = encoder.decode(token_ids)
assert reconstructed_text == sample_text  # Always lossless!


# ==============================================================================
# PART 2: Exact Token Counting with Google Gemini (Free API Call)
# ==============================================================================

client = genai.Client()

# Count exact tokens BEFORE sending a real generation request (doesn't charge generation quota!)
token_info = client.models.count_tokens(
    model="gemini-2.5-flash",
    contents=sample_text,
)

print("\n--- Comparison ---")
print(f"tiktoken estimate:   {len(token_ids)} tokens")
print(f"Gemini exact count:  {token_info.total_tokens} tokens")