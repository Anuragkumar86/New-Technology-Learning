import logging
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_random_exponential,
)

# Configure basic logging so you can see when tenacity retries a 429 error!
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()
client = genai.Client(http_options=types.HttpOptions(api_version="v1beta"))


# ==============================================================================
# 1. Helper Function: Decide WHICH Gemini Errors Deserve a Retry
# ==============================================================================
def is_retryable_gemini_error(exc: BaseException) -> bool:
    """Returns True ONLY for temporary Rate Limits (429) or Server Overload (503)."""
    if isinstance(exc, errors.APIError):
        # 429 = Rate limit exceeded (RPM/TPM), 503 = Google server temporarily overloaded
        return exc.code in (429, 503)
    return False


# ==============================================================================
# 2. Production-Safe Gemini Call With Automatic Exponential Backoff + Fallback
# ==============================================================================
@retry(
    stop=stop_after_attempt(4),  # Try up to 4 times total (1 initial + 3 retries)
    wait=wait_random_exponential(multiplier=2, min=2, max=30),  # Waits ~2s, ~4s, ~8s...
    retry=retry_if_exception(is_retryable_gemini_error),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,  # Raises the real Gemini APIError if all 4 attempts fail
)
def call_gemini_with_retry(prompt: str, model: str = "gemini-2.5-flash") -> str:
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.0,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        ),
    )
    return response.text.strip()


def call_gemini_resilient(prompt: str) -> str:
    """Tries primary model with retries; falls back to Flash-Lite if primary quota is exhausted."""
    try:
        return call_gemini_with_retry(prompt, model="gemini-2.5-flash")
    except errors.APIError as err:
        if err.code == 429:
            logger.warning("Primary model 429 quota hit! Falling back to gemini-2.5-flash-lite...")
            return call_gemini_with_retry(prompt, model="gemini-2.5-flash-lite")
        raise


# ==============================================================================
# 3. Demo: Safely Processing Multiple Prompts Without Triggering 429 Bursts
# ==============================================================================
if __name__ == "__main__":
    topics = [
        "Explain RPM in 1 short sentence.",
        "Explain TPM in 1 short sentence.",
        "Explain RPD in 1 short sentence.",
    ]

    for idx, topic in enumerate(topics, start=1):
        answer = call_gemini_resilient(topic)
        print(f"[{idx}/{len(topics)}] {answer}")

        # Simple pacing delay between batch requests so we stay comfortably under free-tier RPM!
        if idx < len(topics):
            time.sleep(1.0)