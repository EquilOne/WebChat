from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from mangum import Mangum
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel, field_validator

from prompts import app_description, sidebar_prompt, system_prompt
from response import get_response

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    messages: list[ChatCompletionMessageParam]

    @field_validator("messages")
    @classmethod
    def cap_messages(cls, v):
        if len(v) > 50:
            raise ValueError("Message count exceeds limit of 50")
        total_chars = sum(len(str(m)) for m in v)
        if total_chars > 50000:
            raise ValueError("Total message characters exceed limit of 50000")
        return v


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.post("/api/chat")
async def chat(request: ChatRequest):
    messages = [m for m in request.messages if m.get("role") in ("user", "assistant")]

    full_messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "system",
            "content": f"## About This Application\n\n{app_description}",
        },
        *messages,
    ]

    async def stream():
        try:
            completion = await get_response(full_messages, stream=True)
            async for chunk in completion:
                token = chunk.choices[0].delta.content
                if token:
                    for line in token.split("\n"):
                        yield f"data: {line}\n"
                    yield "\n"
        except Exception as e:
            yield f'data: {{"error": "{str(e)}"}}\n\n'
        yield "data: [DONE]\n\n"

    response = StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"},
    )
    return response


@app.get("/api/sidebar")
async def sidebar():
    async def stream():
        completion = await get_response(
            [{"role": "system", "content": sidebar_prompt}],
            stream=True,
        )
        async for chunk in completion:
            token = chunk.choices[0].delta.content
            if token:
                for line in token.split("\n"):
                    yield f"data: {line}\n"
                yield "\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


handler = Mangum(app)
