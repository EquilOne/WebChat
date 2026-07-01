# WebChat

A personal learning project: an LLM chat webapp powered by OpenRouter, with a Python/FastAPI backend and a planned React/Next.js frontend.

## What this does

WebChat is a streaming chat interface for language models served through the OpenRouter API.
The backend exposes a FastAPI server with a `/chat` endpoint that streams responses via Server-Sent Events (SSE), and a `/health` endpoint for readiness checks.
There's also a CLI chatbot you can run from the terminal for quick testing without a browser.

## Tech stack

- **Backend**: Python 3.13+, FastAPI, uvicorn, openai (OpenRouter SDK)
- **Frontend (planned)**: React / Next.js (port 5173)
- **Dev tooling**: pyright, ruff
- **API**: OpenRouter Chat Completions API with SSE streaming

## Project structure

```
WebChat/
├── BackEnd/               # Python FastAPI backend (functional)
│   ├── server.py          # FastAPI app — /health and /chat endpoints, CORS
│   ├── response.py        # OpenRouter API wrapper
│   ├── main.py            # CLI chatbot (Rich-based)
│   ├── custom_args.py     # Argparse config for CLI
│   ├── prompts.py         # System prompt definitions
│   └── pyproject.toml     # Project config & dependencies
├── FrontEnd/              # React/Next.js frontend (not yet built)
├── PLAN.md                # Project plan
└── LICENSE                # MIT license
```

## Getting Started (Backend)

1. **Clone the repo**

```bash
git clone https://github.com/your-username/WebChat.git
cd WebChat/BackEnd
```

2. **Set up environment**

Create a `.env` file in the `BackEnd/` directory:

```bash
OPENAI_API_KEY=your-openrouter-api-key
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

## CLI usage

You can also chat from the terminal without a frontend:

```bash
python main.py
```

This uses the Rich library for a formatted chat experience in your terminal — useful for debugging and quick testing.

## Frontend

A React / Next.js frontend is planned but not yet implemented.
The `FrontEnd/` directory is a placeholder for future work.
Once built, it will run on port 5173 and the backend CORS is already configured to allow requests from `localhost:5173`.

## What I Learned

This project was built as a learning exercise.

## Future Ideas

- Implement the React/Next.js frontend with real-time streaming UI
- Add conversation history persistence (SQLite or similar)
- Support model selection and parameter tuning from the UI
- Add multi-turn conversation support on the backend
- Explore tool calling and structured output modes

## License

MIT — see [LICENSE](./LICENSE) for details.