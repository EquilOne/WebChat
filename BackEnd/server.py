from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel

from prompts import app_description, sidebar_prompt, system_prompt
from response import get_response

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    messages: list[ChatCompletionMessageParam]


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/chat")
async def chat(request: ChatRequest):
    messages = request.messages

    full_messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "system",
            "content": f"## About This Application\n\n{app_description}",
        },
        *messages,
    ]

    collected = []

    async def stream():
        completion = await get_response(full_messages, stream=True)
        async for chunk in completion:
            token = chunk.choices[0].delta.content
            if token:
                collected.append(token)
                yield f"data: {token}\n\n"
        yield "data: [DONE]\n\n"

    response = StreamingResponse(stream(), media_type="text/event-stream")
    return response


@app.get("/sidebar")
async def sidebar():
    async def stream():
        completion = await get_response(
            [{"role": "system", "content": sidebar_prompt}],
            stream=True,
        )
        async for chunk in completion:
            token = chunk.choices[0].delta.content
            if token:
                yield f"data: {token}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")
