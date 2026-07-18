from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

from src.common.custom_exception import CustomException
from src.common.logger import get_logger
from src.config.config import configs
from src.core.agent import get_ai_response

app = FastAPI(
    title="Multi-Agent AI API",
    description="A RAG based system with multiple models and web search",
)

logger = get_logger(__name__)


class RequestState(BaseModel):
    """Request model for chat endpoint.

    Attributes:
        model: Groq model identifier (must be in GROQ_LLM_MODELS).
        system_prompt: System message to guide LLM behavior.
        messages: List of user queries (must contain at least one non-empty message).
        allow_web_search: Whether to enable Tavily web search tool.
    """

    model: str
    system_prompt: str
    messages: list[str] = Field(..., min_length=1)
    allow_web_search: bool = False

    @field_validator("messages")
    @classmethod
    def messages_not_empty(cls, v: list[str]) -> list[str]:
        """Validate that messages list contains at least one non-empty string.
        Args:
            v: List of message strings to validate.
        Returns:
            The validated messages list.
        Raises:
            ValueError: If all messages are empty or whitespace-only.
        """
        if not any(msg.strip() for msg in v):
            raise ValueError("messages list must contain at least one non-empty string.")
        return v

    @field_validator("model")
    @classmethod
    def model_must_be_valid(cls, v: str) -> str:
        """Validate that model is in the allowed list.

        Args:
            v: Model identifier to validate.

        Returns:
            The validated model identifier.

        Raises:
            ValueError: If model is not in GROQ_LLM_MODELS.
        """
        if v not in configs.GROQ_LLM_MODELS:
            raise ValueError(
                f"Invalid model '{v}'. Valid options: {', '.join(configs.GROQ_LLM_MODELS)}"
            )
        return v


class ChatResponse(BaseModel):
    """Response model for chat endpoint.

    Attributes:
        response: LLM-generated response text.
        model: Model identifier used for generation.
    """

    response: str
    model: str


@app.get("/health")
async def health():
    """Health check endpoint.

    Returns:
        Dictionary with status indicator.
    """
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: RequestState) -> ChatResponse:
    """Process a user query and return LLM response.

    Handles optional web search tool invocation and error recovery.

    Args:
        request: Validated chat request containing model, prompts, and messages.

    Returns:
        ChatResponse with LLM response and model used.

    Raises:
        HTTPException: If agent invocation fails or returns empty response.
    """
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
