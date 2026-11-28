import asyncio
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# Initialize Gemini client (v1beta so ThinkingConfig works cleanly)
client = genai.Client(http_options=types.HttpOptions(api_version="v1beta"))


# ==============================================================================
# PART 1: Synchronous Streaming (Great for CLI scripts & sync functions)
# ==============================================================================
def demo_sync_stream():
    print("--- PART 1: Live Token Streaming (Sync) ---...❤️❤️❤️")
    start_time = time.perf_counter()
    first_token_time = None
    collected_chunks: list[str] = []
    final_usage = None

    # Open the live streaming connection to Gemini
    stream = client.models.generate_content_stream(
        model="gemini-2.5-flash",
        contents="Explain how Server-Sent Events (SSE) work in 4 short bullet points.",
        config=types.GenerateContentConfig(
            temperature=0.3,
            thinking_config=types.ThinkingConfig(thinking_budget=0),  # Instant TTFT!
        ),
    )

    # Loop yields each small text chunk the instant it arrives from Google
    for chunk in stream:
        if chunk.text:
            # Record Time To First Token (TTFT) on the very first chunk!
            if first_token_time is None:
                first_token_time = time.perf_counter() - start_time

            # Print immediately without adding newlines; flush=True forces terminal to display right away
            print(chunk.text, end="", flush=True)
            collected_chunks.append(chunk.text)

        # Keep updating final_usage so we capture the complete count from the last chunk
        if chunk.usage_metadata:
            final_usage = chunk.usage_metadata

    total_time = time.perf_counter() - start_time
    full_response_text = "".join(collected_chunks)

    print("\n\n--- Stream Metrics ---")
    print(f"Time To First Token (TTFT): {first_token_time:.2f}s")
    print(f"Total Stream Time:          {total_time:.2f}s")
    print(f"Saved Full Text Length:     {len(full_response_text)} chars")
    if final_usage:
        print(f"Total Tokens Used:          {final_usage.total_token_count}")


# ==============================================================================
# PART 2: Async Streaming with 'client.aio' (Required for async FastAPI SSE routes!)
# ==============================================================================
async def demo_async_stream():
    print("\n--- PART 2: Async Token Streaming (client.aio) ---⭐⭐⭐")

    # Notice 'client.aio' + 'await' + 'async for' (non-blocking for FastAPI Event Loop!)
    stream = await client.aio.models.generate_content_stream(
        model="gemini-2.5-flash",
        contents="Write a 2-sentence motivational quote for a backend developer learning AI.",
        config=types.GenerateContentConfig(
            temperature=0.7,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        ),
    )

    async for chunk in stream:
        if chunk.text:
            print(chunk.text, end="", flush=True)
    print("\n")


if __name__ == "__main__":
    demo_sync_stream()
    asyncio.run(demo_async_stream())