import os
from dotenv import load_dotenv
from google import genai

# 1. Load GEMINI_API_KEY from your local .env file
load_dotenv()

# 2. Initialize the Gemini client (automatically reads GEMINI_API_KEY from os.environ)
client = genai.Client()

# 3. Send a quick test prompt to Gemini 2.5 Flash (fast & included in the free tier)
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Say 'Gemini AI Engineering environment is ready!' in one short sentence.",
)

print(response.text)