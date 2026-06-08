FROM python:3.12-slim

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

COPY . .

ENV PYTHONPATH=/app

EXPOSE 8000 8501

# Run both backend and frontend
CMD ["uv", "run", "python", "src/main.py"]