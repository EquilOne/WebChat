import os
from typing import Literal, overload

from dotenv import load_dotenv
from openai import AsyncOpenAI, AsyncStream
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")
_model = os.getenv("MODEL")
if api_key is None:
    raise RuntimeError("Api key not found")
if _model is None:
    raise RuntimeError("Model not found")
model = _model

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)


@overload
async def get_response(
    messages: list[ChatCompletionMessageParam], stream: Literal[True]
) -> AsyncStream[ChatCompletionChunk]: ...


@overload
async def get_response(
    messages: list[ChatCompletionMessageParam], stream: Literal[False]
) -> ChatCompletion: ...


@overload
async def get_response(
    messages: list[ChatCompletionMessageParam], stream: bool = True
) -> AsyncStream[ChatCompletionChunk] | ChatCompletion: ...


async def get_response(
    messages: list[ChatCompletionMessageParam], stream: bool = True
) -> AsyncStream[ChatCompletionChunk] | ChatCompletion:
    resp = await client.chat.completions.create(
        model=model,
        messages=messages,
        stream=stream,
    )
    if not resp:
        raise RuntimeError("No response returned")
    return resp
