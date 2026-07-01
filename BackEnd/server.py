import uuid

from dotenv import load_dotenv
from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel

from prompts import system_prompt
from response import get_response

load_dotenv()

app = FastAPI()
sessions: dict[str, list[ChatCompletionMessageParam]] = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    messages: list[ChatCompletionMessageParam]


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/chat")
async def chat(request: ChatRequest, x_session_id: str | None = Header(None)):
    messages = request.messages

    if x_session_id is None:
        session_id = str(uuid.uuid4())
    else:
        session_id = x_session_id

    if session_id not in sessions:
        sessions[session_id] = []
    history = sessions[session_id]
    full_messages = [
        {"role": "system", "content": system_prompt},
        *history,
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

        history.append({"role": "assistant", "content": "".join(collected)})

    history.extend(messages)
    response = StreamingResponse(stream(), media_type="text/event-stream")
    response.headers["X-Session-ID"] = session_id
    return response
