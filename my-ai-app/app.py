# File: my-ai-app/app.py
import json
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from google import genai
from google.genai import errors, types
from pydantic import BaseModel, Field

from config import settings


# 1. Lifespan: Initialize ONE shared Gemini client at startup using the key from settings
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.gemini_client = genai.Client(
        api_key=settings.gemini_api_key,  # Explicitly read from Pydantic Settings!
        http_options=types.HttpOptions(api_version="v1beta"),
    )
    print(f"Gemini client initialized using model: {settings.gemini_model}")
    yield
    print("Shutting down Gemini chat backend...")


app = FastAPI(title="Gemini Streaming Chat API", lifespan=lifespan)


# 2. Request Schema for POST /v1/chat
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000, examples=["Explain Docker in 3 short sentences."])
    system_prompt: str = Field(
        default="You are a helpful, concise AI engineering assistant.",
        max_length=1000,
    )
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)


# 3. Async SSE Generator: Streams Gemini tokens live as they arrive
async def stream_gemini_sse(
    request: Request,
    payload: ChatRequest,
) -> AsyncGenerator[str, None]:
    client: genai.Client = request.app.state.gemini_client

    try:
        # Non-blocking async streaming call so FastAPI can serve multiple users concurrently
        stream = await client.aio.models.generate_content_stream(
            model=settings.gemini_model,
            contents=payload.message,
            config=types.GenerateContentConfig(
                system_instruction=payload.system_prompt,
                temperature=payload.temperature,
                thinking_config=types.ThinkingConfig(thinking_budget=0),  # Instant TTFT!
            ),
        )

        async for chunk in stream:
            # Stop immediately if the client closed the curl/browser connection
            if await request.is_disconnected():
                print("Client disconnected mid-stream.")
                break

            if chunk.text:
                # Strict SSE wire format: 'data: <json>\n\n'
                event_data = json.dumps({"token": chunk.text})
                yield f"data: {event_data}\n\n"

        # Signal to the frontend/client that generation finished cleanly
        yield "data: [DONE]\n\n"

    except errors.APIError as api_err:
        # Since HTTP 200 headers already started streaming, send errors as an SSE error event
        error_payload = json.dumps({"error": api_err.message, "code": api_err.code})
        yield f"data: {error_payload}\n\n"

    finally:
        print("SSE stream lifecycle finished.")


# 4. POST /v1/chat Endpoint
@app.post("/v1/chat")
async def chat_stream(payload: ChatRequest, request: Request):
    return StreamingResponse(
        stream_gemini_sse(request, payload),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Prevents reverse proxies (Nginx) from buffering tokens
        },
    )