import os
import subprocess
import threading
import time

import requests

from src.common.logger import get_logger
from src.common.custom_exception import CustomException

logger = get_logger(__name__)

BACKEND_URL = "http://127.0.0.1:8000/health"
BACKEND_STARTUP_TIMEOUT = 15

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env = os.environ.copy()
env["PYTHONPATH"] = PROJECT_ROOT


def wait_for_backend(timeout: int = BACKEND_STARTUP_TIMEOUT) -> bool:
    """
    Polls the backend health endpoint until it responds or timeout is reached.

    Returns:
        True if backend is healthy, False if timed out.
    """
    logger.info("Waiting for backend to become healthy...")
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            resp = requests.get(BACKEND_URL, timeout=2)
            if resp.status_code == 200:
                logger.info("Backend is healthy.")
                return True
        except requests.exceptions.ConnectionError:
            pass  # still starting up
        time.sleep(0.5)
    return False


def init_backend(error_event: threading.Event) -> None:
    """Starts the FastAPI backend via uvicorn. Sets error_event on failure."""

    try:
        logger.info("Initializing backend...")
        subprocess.run(
            ["uvicorn", "src.backend.api:app", "--host", "127.0.0.1", "--port", "8000"],
            check=True,
            env=env,
        )
    except subprocess.CalledProcessError as e:
        logger.error("Backend process exited with error: %s", str(e))
        error_event.set()
    except Exception as e:
        logger.error("Unexpected backend error: %s", str(e))
        error_event.set()


def init_frontend() -> None:
    """Starts the Streamlit frontend."""
    try:
        logger.info("Initializing frontend...")
        subprocess.run(["streamlit", "run", "src/frontend/ui.py"], check=True, env=env)
    except subprocess.CalledProcessError as e:
        raise CustomException("Frontend process failed.", original_error=e) from e
    except Exception as e:
        raise CustomException("Unexpected frontend error.", original_error=e) from e


if __name__ == "__main__":
    backend_error = threading.Event()

    backend_thread = threading.Thread(
        target=init_backend,
        args=(backend_error,),
        daemon=True,  # backend dies automatically when main process exits
    )
    backend_thread.start()

    # Wait for backend to be ready before launching frontend
    if not wait_for_backend():
        logger.error(
            "Backend did not become healthy within %s seconds. Aborting.",
            BACKEND_STARTUP_TIMEOUT,
        )
        raise SystemExit(1)

    if backend_error.is_set():
        logger.error("Backend reported an error before frontend could start. Aborting.")
        raise SystemExit(1)

    try:
        init_frontend()
    except CustomException as e:
        logger.error("Frontend failed: %s", str(e))
        raise SystemExit(1)
