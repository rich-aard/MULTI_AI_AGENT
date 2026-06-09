from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

from src.common.custom_exception import CustomException
from src.common.logger import get_logger
from src.config.config import configs
from src.core.agent import get_ai_response

app = FastAPI()

logger = get_logger(__name__)


class RequestState(BaseModel):
    model: str
    system_prompt: str
    messages: list[str] = Field(..., min_length=1)
    allow_web_search: bool = False

    @field_validator("messages")
    @classmethod
    def messages_not_empty(cls, v: list[str]) -> list[str]:
        if not any(msg.strip() for msg in v):
            raise ValueError("messages list must contain at least one non-empty string.")
        return v

    @field_validator("model")
    @classmethod
    def model_must_be_valid(cls, v: str) -> str:
        if v not in configs.GROQ_LLM_MODELS:
            raise ValueError(
                f"Invalid model '{v}'. Valid options: {', '.join(configs.GROQ_LLM_MODELS)}"
            )
        return v


class ChatResponse(BaseModel):
    response: str
    model: str


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: RequestState) -> ChatResponse:
    logger.info(
        "Received request | model=%s | web_search=%s",
        request.model,
        request.allow_web_search,
    )

    query = "\n".join(request.messages)

    try:
        response = await get_ai_response(
            model=request.model,
            query=query,
            allow_web_search=request.allow_web_search,
            system_prompt=request.system_prompt,
        )

        logger.info("Response received | model=%s", request.model)

        return ChatResponse(response=response, model=request.model)

    except CustomException as e:
        logger.error("Exception during response generation: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e

    except Exception as e:
        logger.error("Unexpected error during response generation: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal server error.") from e
