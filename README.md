# WebChat

A real-time AI chat application powered by OpenRouter, built with Next.js 16 and Python FastAPI.

## Features

- **Real-time streaming**: AI responses arrive token-by-token via Server-Sent Events and render instantly as they're generated.
- **Markdown rendering**: Bold, italic, headers, lists, code blocks, and tables are rendered with react-markdown.
- **Responsive layout**: Desktop shows a sidebar alongside the chat. Mobile switches between Chat and About views via a pill toggle.
- **Anchored sidebar**: The About panel stays visible as the chat scrolls, with LLM-generated content describing the app.
- **Auto-scroll**: Automatically scrolls to the latest message, keeping up with fast token streaming.
- **Rose Pine theme**: Warm, cohesive light and dark mode with CSS variables.
- **Floating input bar**: The text input and send button sit in a floating card at the bottom of the chat.

## Tech stack

- **Frontend**: Next.js 16, React 19, Tailwind CSS v4, react-markdown
- **Backend**: Python 3.13+, FastAPI, uvicorn, openai (OpenRouter SDK)
- **API**: OpenRouter Chat Completions API with SSE streaming
- **Dev tooling**: TypeScript, pyright, ruff

## Project structure

```
WebChat/
├── FrontEnd/
│   ├── app/
│   │   ├── page.tsx           # Single-file chat UI component
│   │   ├── layout.tsx         # Root layout with metadata & fonts
│   │   ├── globals.css        # Rose Pine theme CSS variables
│   │   └── favicon.ico        # Old favicon (replaced by chat.svg)
│   ├── public/
│   │   ├── chat.svg           # Chat-bubble SVG favicon
│   │   └── *.svg              # Next.js default SVGs
│   ├── package.json           # Deps: next, react, react-markdown, tailwindcss
│   └── README.md              # Next.js-generated readme
├── BackEnd/
│   ├── server.py              # FastAPI app — /sidebar and /chat endpoints (dev)
│   ├── response.py            # OpenRouter API wrapper
│   ├── main.py                # CLI chatbot (Rich-based)
│   ├── custom_args.py         # Argparse config for CLI
│   ├── prompts.py             # System prompt & app description
│   └── pyproject.toml         # Project config & dependencies
├── api/
│   ├── index.py               # Vercel serverless entry (/api/ route prefix)
│   └── backend/
│       ├── response.py        # OpenRouter API wrapper (production)
│       └── prompts.py         # Prompts (production)
├── README.md
└── LICENSE
```

## Getting Started

### Backend

1. **Clone the repo**

   ```bash
   git clone https://github.com/your-username/WebChat.git
   cd WebChat/BackEnd
   ```

2. **Set up environment**

   Create a `.env` file in the `BackEnd/` directory:

   ```bash
   OPENROUTER_API_KEY=your-openrouter-api-key
   MODEL=openai/gpt-4o-mini
   ```

   Get a key from [openrouter.ai/keys](https://openrouter.ai/keys).

3. **Create a virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

4. **Install dependencies**

   ```bash
   pip install .
   ```

   Or if you use uv:

   ```bash
   uv sync
   ```

5. **Run the server**

   ```bash
   uvicorn server:app --reload
   ```

   The API will be available at `http://localhost:8000`.
   The `/health` endpoint returns `{"status": "ok"}`.
   Send chat requests to `/chat`.

### Frontend

1. **Navigate to the frontend directory**

   ```bash
   cd WebChat/FrontEnd
   ```

2. **Install dependencies**

   ```bash
   npm install
   ```

3. **Set the API URL** (optional — defaults to `http://localhost:8000`)

   Create a `.env.local` file:

   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. **Run the development server**

   ```bash
   npm run dev
   ```

   Open [http://localhost:3000](http://localhost:3000) in your browser.

### Running both together

Start the backend in one terminal:

```bash
cd BackEnd && uvicorn server:app --reload
```

Start the frontend in another:

```bash
cd FrontEnd && npm run dev
```

## CLI usage

You can also chat from the terminal without a frontend:

```bash
cd BackEnd && python main.py
```

This uses the Rich library for a formatted chat experience in your terminal — useful for debugging and quick testing.

## License

MIT — see [LICENSE](./LICENSE) for details.
