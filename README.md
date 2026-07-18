# Multi-Agent AI System

A production-grade LLM agent system with Groq inference, optional web search via Tavily, and a FastAPI backend + Streamlit frontend.

## Demo
- **API**: [https://multi-ai-agent-wc6v.onrender.com/docs] (Swagger UI)

- **Frontend**: [https://multi-ai-agent-21.streamlit.app/]

## Architecture
- **Backend**: FastAPI + async LangChain agents + Groq LLM + Tavily search
- **Frontend**: Streamlit with chat history
- **Deployment**: Docker containers on Render (API) + Streamlit Cloud (UI)
- **CI/CD**: GitHub Actions with linting, security, tests, Docker build & push

### Architecture Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                        User                                 │
└────────────────┬────────────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
   ┌────▼─────┐    ┌──────▼──────┐
   │ Streamlit │    │   FastAPI   │
   │ Frontend  │───▶│  Backend    │
   │(8501)     │    │  (8000)     │
   └──────────┘    └──────┬──────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
   ┌────▼────┐    ┌───────▼────────┐  ┌────▼────────┐
   │ Groq    │    │ LangChain      │  │ Tavily      │
   │ LLM API │    │ Agent Loop     │  │ Web Search  │
   └─────────┘    └────────────────┘  └─────────────┘
```

## Key Highlights

### Production-Ready Code
- **Async Tool Loop**: Manual tool invocation pattern (avoids deprecated `create_react_agent`)
- **Structured Logging**: Request/response tracking for production debugging
- **Error Handling**: Custom exceptions + HTTP error responses with context
- **Input Validation**: Pydantic schemas validate all inputs at API layer

### DevOps & Deployment
- **CI/CD Pipeline**: GitHub Actions (lint → security → test → docker → deploy)
- **Security Scanning**: Bandit checks for vulnerabilities
- **Containerization**: Docker with multi-stage builds and layer caching
- **Auto-Deploy**: Main branch pushes trigger automatic deployment to Render
- **Scalability**: API and frontend deployable independently


## Quick Start

### Prerequisites
- Python 3.12+
- `uv` package manager ([install](https://docs.astral.sh/uv/getting-started/))
- Groq API key ([free tier](https://console.groq.com))
- Tavily API key ([free tier](https://tavily.com))

### Local Development
```bash
# Clone & setup
git clone https://github.com/rich-aard/MULTI_AI_AGENT.git
cd MULTI_AI_AGENT

# Install dependencies
uv sync --group dev

# Configure environment
cat > .env << EOF
GROQ_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
APP_ENV=development
EOF

# Run both backend (8000) and frontend (8501)
python src/main.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

### Run Tests
```bash
uv run pytest tests/ -v
```

### Docker (Local)
```bash
docker build -t multi-agent .
docker run \
  -e GROQ_API_KEY=$GROQ_API_KEY \
  -e TAVILY_API_KEY=$TAVILY_API_KEY \
  -p 8000:8000 \
  multi-agent
```

## Features
- Multiple LLM models (LLaMA 3.3 70B, 3.1 8B, LLaMA Scout 17B, OPENAI GPT OSS 120B)
- Optional web search with Tavily API
- Custom system prompts for agent behavior
- Session-based chat history (browser-backed)
- Async tool invocation with streaming
- Production logging & error handling
- Full input validation with Pydantic

## Project Structure
```
src/
├── backend/              # FastAPI application
│   └── api.py           # Chat endpoint + request validation
├── core/                # LLM agent logic
│   └── agent.py         # LangChain async agent with tool loop
├── frontend/            # Streamlit UI
│   └── ui.py            # Chat interface + session management
├── config/              # Configuration management
│   └── config.py        # Environment variables & defaults
├── common/              # Shared utilities
│   ├── logger.py        # Structured logging (request/response tracking)
│   └── custom_exception.py  # Custom exception class
└── main.py              # Orchestrates backend + frontend startup

tests/
├── test_health.py       # Config & API validation tests
└── conftest.py          # Pytest fixtures

.github/
└── workflows/
    └── ci.yml           # GitHub Actions CI/CD pipeline

Dockerfile              # Production container (FastAPI only)
pyproject.toml         # uv + dependencies + tool config
```

## Tech Stack
- **Runtime**: Python 3.12 + uv
- **API**: FastAPI + Uvicorn
- **UI**: Streamlit
- **LLM**: LangChain + Groq API
- **Search**: Tavily API
- **Async**: asyncio + ThreadPoolExecutor
- **Validation**: Pydantic 2.x
- **Docker**: Multi-stage builds with caching
- **Testing**: Pytest + TestClient
- **Linting**: Ruff + Bandit

## Author
[Richard Khewa Limbu](https://github.com/rich-aard)

---
