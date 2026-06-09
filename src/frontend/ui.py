import requests
import streamlit as st

from src.common.custom_exception import CustomException
from src.common.logger import get_logger
from src.config.config import configs

logger = get_logger(__name__)

API_URL = st.secrets.get("API_URL", "http://127.0.0.1:8000") + "/chat"

# page config
st.set_page_config(page_title="Multi Agent", layout="wide")
st.title("Multi Agent AI")
st.caption("Powered by Groq · Tavily · FastAPI")

# session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history: list[dict] = []

with st.sidebar:
    st.header("Configuration: ")
    model = st.selectbox("Select your LLM Model: ", configs.GROQ_LLM_MODELS)

    allow_web_search = st.checkbox("Allow web search")
    system_prompt = st.text_area(
        "System prompt",
        value="You are a helpful assistant.",
        height=120,
        help="Sets the behaviour/role of the AI agent.",
    )

    if st.button("Clear chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# display chat histroy
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_query = st.chat_input("Enter you query: ", height=120)

if user_query and user_query.strip():
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    payload = {
        "model": model,
        "system_prompt": system_prompt or "You are a helpful assistant.",
        "allow_web_search": allow_web_search,
        "messages": [user_query],
    }

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                logger.info("Sending request to backend | model=%s", model)

                response = requests.post(url=API_URL, json=payload, timeout=60)

                if response.status_code == 200:
                    ai_response = response.json().get("response", "")
                    logger.info("Response received from backend.")
                    st.markdown(ai_response)
                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": ai_response}
                    )

                else:
                    error_detail = response.json().get("detail", "Unknown error.")
                    logger.error(
                        "Backend error | status=%s | detail=%s",
                        response.status_code,
                        error_detail,
                    )
                    st.error(f"Backend error {response.status_code}: {error_detail}")

            except requests.exceptions.ConnectionError:
                logger.error("Could not connect to backend at %s", API_URL)
                st.error("Could not connect to the backend. Is the API running?")

            except requests.exceptions.Timeout:
                logger.error("Request to backend timed out.")
                st.error("Request timed out. Try again or use a smaller query.")

            except Exception as e:
                logger.error("Unexpected error: %s", str(e))
                st.error(str(CustomException("Unexpected error.", original_error=e)))
