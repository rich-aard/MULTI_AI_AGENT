from langchain.agents import create_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import AIMessage
from src.config.config import configs
from src.common.logger import get_logger
from src.common.custom_exception import CustomException

logger = get_logger(__name__)


async def get_ai_response(
    query: str,
    model: str = configs.DEFAULT_MODEL,
    allow_web_search: bool = False,
    system_prompt: str = "You are a helpful assistant.",
) -> str:
    """
    Invokes a ReAct agent and returns the final AI response.

    Args:
        query:            The user's input message.
        model:            Groq model string to use.
        allow_web_search: Whether to equip the agent with Tavily search.
        system_prompt:    System-level instruction for the agent.

    Returns:
        The last AIMessage content string.
    """
    try:
        tools = (
            [
                TavilySearchResults(
                    max_results=3,
                    tavily_api_key=configs.TAVILY_API_KEY,
                )
            ]
            if allow_web_search
            else []
        )

        agent = create_agent(
            model=f"groq:{model}",
            tools=tools,
            system_prompt=system_prompt,
        )

        logger.info(
            "Invoking agent | model=%s | web_search=%s", model, allow_web_search
        )

        response = await agent.ainvoke(
            {"messages": [{"role": "user", "content": query}]}
        )

        ai_messages = [
            msg.content
            for msg in response.get("messages", [])
            if isinstance(msg, AIMessage)
        ]

        if not ai_messages:
            raise CustomException("Agent returned no AIMessage in response.")

        logger.info("Agent response received successfully.")
        return ai_messages[-1]

    except Exception as e:
        raise CustomException("Agent invocation failed.", original_error=e) from e
