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

- **Real-time streaming**: Tokens arrive via Server-Sent Events (SSE) and render as they come in — no waiting for a full response. Multi-line tokens are handled correctly with proper SSE event framing.
- **Markdown rendering**: AI responses are rendered with react-markdown, supporting bold, italic, headers, lists, code blocks, and tables.
- **Responsive layout**: The UI adapts to every screen size. Desktop shows a sidebar alongside the chat. Mobile switches between Chat and About views via a pill toggle at the top.
- **Anchored sidebar**: The About panel stays visible as the chat scrolls, with LLM-generated content describing the app.
- **Auto-scroll**: The chat automatically scrolls to the latest message, keeping up with fast token streaming via requestAnimationFrame.
- **Rose Pine theme**: Warm, cohesive light and dark mode colors using the Rose Pine palette. The interface uses CSS variables for seamless theme switching based on system preference.
- **Floating input bar**: The text input and send button sit in a floating card at the bottom of the chat — rounded, shadowed, with a subtle border — giving a modern, elevated feel.

## Architecture

```
Browser (Next.js)  --POST /api/chat-->  FastAPI Backend  --POST /v1/chat/completions-->  OpenRouter
           <--SSE stream--                 <--streaming chunks--
```

- Frontend sends user messages as JSON to `POST /api/chat`.
- Backend builds a system prompt + conversation history, calls `client.chat.completions.create(stream=True)`.
- Each token's line fragments are yielded as separate `data:` lines within a single SSE event, preserving newlines.
- The frontend reads the stream with `ReadableStream.getReader()`, buffering events and appending tokens to state as they arrive.
- A separate `GET /api/sidebar` endpoint streams a summary of the app's features for the sidebar About panel.

## Design Decisions

- **No database**: The app is stateless between page refreshes. Simple for development and single-user use. Could be swapped for SQLite/Redis later.
- **No build step**: Tailwind CSS v4 is used with the CSS-first `@import "tailwindcss"` approach — no config file needed.
- **Minimal dependencies**: Backend only needs `openai`, `fastapi`, `uvicorn`, `python-dotenv`. Frontend adds `react-markdown` and `remark-gfm`.
- **Single-file frontend**: The entire chat UI is one component in `page.tsx` — no complex component tree to navigate.
"""

sidebar_prompt = f"""You are describing the WebChat application to a new user who just opened the app.

Read the app description below, then write exactly 5 bullet points covering ALL of these aspects (one bullet each):

1. Architecture & stack — how the frontend and backend connect
2. Real-time streaming — how tokens stream via SSE
3. Session persistence — how conversation history is maintained
4. Design & theming — Rose Pine palette and responsive layout
5. Developer experience — minimal dependencies, no database, no build step

Put each bullet on its own line separated by newlines. Keep each bullet brief and scannable. No greetings, sign-offs, or markdown headers. Use plain dashes. Output exactly 5 bullets — no more, no fewer.

## App Description

{app_description}"""
