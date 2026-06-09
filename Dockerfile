FROM python:3.12-slim

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev --system

COPY src/ ./src/

ENV PYTHONPATH=/app

EXPOSE 8000 8501

# Run both backend and frontend
CMD ["python", "src/main.py"]