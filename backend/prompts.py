system_prompt = """
You are a helpful, accurate, and concise AI assistant.

Goals:
- Answer the user's request directly and clearly.
- Be truthful; do not invent facts or claim certainty when unsure.
- Ask a brief clarifying question only when needed.
- Prefer concise answers unless the user asks for detail.
- Adapt to the user's tone and level of expertise.
- Use step-by-step reasoning internally, but only present the final answer unless the user asks for the reasoning.
- When appropriate, provide examples, options, or a short summary.

Behavior:
- If the user's request is ambiguous, make the most likely interpretation and proceed, noting assumptions briefly.
- If you do not know something, say so plainly.
- Do not mention policy, hidden instructions, or internal chain-of-thought.
- Do not be verbose, repetitive, or sycophantic.
- Do not fabricate citations, sources, or capabilities.
- Respect user instructions unless they conflict with higher-priority instructions or safety requirements.

Output style:
- Use clear, natural language.
- Prefer plain formatting.
- Use bullet points for lists and tables only when they improve readability.
- Keep responses short by default.

Safety:
- Refuse requests that are illegal, harmful, or violate privacy.
- For risky topics, provide safe alternatives when possible.
"""

app_description = """# WebChat

## Overview
WebChat is a real-time AI chat application that streams model responses token-by-token as they are generated. Built with a modern stack — Next.js 16 on the frontend, Python FastAPI on the backend — it proxies requests to OpenRouter's chat completions API with streaming enabled.

## Key Features

- **Real-time streaming**: Tokens arrive via Server-Sent Events (SSE) and render as they come in — no waiting for a full response.
- **Session persistence**: Conversation history is stored server-side in memory. The backend assigns a session ID on the first message and returns it as a header; the frontend sends it back on subsequent requests, so the model remembers context across page refreshes.
- **Responsive layout**: The UI adapts to every screen size. Desktop shows a sidebar alongside the chat. Mobile switches between Chat and About views via a pill toggle at the top.
- **Rose Pine theme**: Warm, cohesive light and dark mode colors using the Rose Pine palette. The interface uses CSS variables for seamless theme switching based on system preference.
- **Floating input bar**: The text input and send button sit in a floating card at the bottom of the chat — rounded, shadowed, with a subtle border — giving a modern, elevated feel.

## Architecture

```
Browser (Next.js)  --POST /chat-->  FastAPI Backend  --POST /v1/chat/completions-->  OpenRouter
           <--SSE stream--                 <--streaming chunks--
```

- Frontend sends user messages as JSON to `POST /chat`.
- Backend builds a system prompt + conversation history, calls `client.chat.completions.create(stream=True)`.
- Each chunk is forwarded as `data: <token>\n\n` SSE events.
- The frontend reads the stream with `ReadableStream.getReader()`, appending tokens to state as they arrive.
- A separate `GET /sidebar` endpoint streams a summary of the app's features for the sidebar.

## Design Decisions

- **No database**: Sessions live in a Python dict. Simple for development and single-user use. Could be swapped for SQLite/Redis later.
- **No build step**: Tailwind CSS v4 is used with the CSS-first `@import "tailwindcss"` approach — no config file needed.
- **Minimal dependencies**: Backend only needs `openai`, `fastapi`, `uvicorn`, `python-dotenv`.
- **Single-file frontend**: The entire chat UI is one component in `page.tsx` — no complex component tree to navigate.
"""

sidebar_prompt = f"""You are describing the WebChat application to a new user who just opened the app.

Read the app description below, then summarize the most interesting and impressive parts in 4-6 concise bullet points.

Focus on what makes this app interesting: the real-time streaming, the architecture, the design choices, and the Rose Pine theming.

Keep it brief, scannable, and welcoming. No greetings, sign-offs, or markdown headers. Use plain bullet points (dashes).

## App Description

{app_description}"""
