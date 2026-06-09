"""
Basic tests that run without any API keys.
Tests the health endpoint and config defaults only.
"""

import pytest
from fastapi.testclient import TestClient

from src.backend.api import app
from src.config.config import Config


# Config tests
def test_default_model_is_first_in_list():
    config = Config()
    assert config.DEFAULT_MODEL == config.GROQ_LLM_MODELS[0]


def test_models_list_is_not_empty():
    config = Config()
    assert len(config.GROQ_LLM_MODELS) > 0


def test_all_models_are_strings():
    config = Config()
    assert all(isinstance(m, str) for m in config.GROQ_LLM_MODELS)


# API tests


@pytest.fixture
def client():
    return TestClient(app)


def test_health_endpoint_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_health_endpoint_returns_ok(client):
    response = client.get("/health")
    assert response.json() == {"status": "ok"}


def test_chat_endpoint_rejects_invalid_model(client):
    payload = {
        "model": "not-a-real-model",
        "system_prompt": "You are helpful.",
        "messages": ["Hello"],
        "allow_web_search": False,
    }
    response = client.post("/chat", json=payload)
    assert response.status_code == 422  # pydantic validation error


def test_chat_endpoint_rejects_empty_messages(client):
    payload = {
        "model": "llama-3.3-70b-versatile",
        "system_prompt": "You are helpful.",
        "messages": [],
        "allow_web_search": False,
    }
    response = client.post("/chat", json=payload)
    assert response.status_code == 422
