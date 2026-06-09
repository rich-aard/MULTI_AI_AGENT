import asyncio
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

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
    Invokes an LLM with optional tool use and returns the final response. Uses a manual tool loop to avoid create_agent formatting issues with Groq.
    """
    try:
        llm = ChatGroq(
            model=model,
            api_key=configs.GROQ_API_KEY,
            temperature=0,
        )

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

        runnable = llm.bind_tools(tools) if tools else llm

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=query),
        ]

        logger.info("Invoking LLM | model=%s | web_search=%s", model, allow_web_search)

        while True:
            response = await asyncio.get_event_loop().run_in_executor(
                None, runnable.invoke, messages
            )

            if not response.tool_calls:
                break

            messages.append(response)
            for tool_call in response.tool_calls:
                tool = next((t for t in tools if t.name == tool_call["name"]), None)
                if tool is None:
                    tool_result = f"Tool '{tool_call['name']}' not found."
                else:
                    tool_result = await asyncio.get_event_loop().run_in_executor(
                        None, tool.invoke, tool_call["args"]
                    )
                messages.append(
                    ToolMessage(
                        content=str(tool_result),
                        tool_call_id=tool_call["id"],
                    )
                )

        if not response.content:
            raise CustomException("LLM returned an empty response.")

        logger.info("Response received successfully.")
        return response.content

    except CustomException:
        raise

    except Exception as e:
        raise CustomException("Agent invocation failed.", original_error=e) from e
