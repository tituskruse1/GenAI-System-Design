import os
import json
import random
import requests
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import HTTPException, Request
import redis
from pydantic import BaseModel

REDIS_CONFIG = {
    "host": os.getenv("REDIS_HOST", "127.0.0.1"),
    "port": int(os.getenv("REDIS_PORT", 6379)),
    "db": 0,
}

# Initialize Redis client
redis_client = redis.Redis(**REDIS_CONFIG, decode_responses=True)


class RedisABTestMiddleware(BaseHTTPMiddleware):
    """Middleware for handling the AB test switching."""

    async def dispatch(self, request: Request, call_next):
        """Overwriting dispatch function to wrap request."""
        experiments = await self.get_experiments("experiments")
        request.state.model = random.choice(experiments)
        response = await call_next(request)
        return response

    async def get_experiments(self, key: str):
        """Get experiments from Redis cache."""
        try:
            my_list = redis_client.lrange(key, 0, -1)
            return [item for item in my_list]
        except Exception as e:
            print(f"Error getting experiments: {e}")
            return None

    async def get_cache(self, key: str):
        """Get value from Redis cache."""
        try:
            value = redis_client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            print(f"Error getting cache: {e}")
            return None


def create_session():
    """
    Function creates a http request session to speed up dialup of calls to the same host.
    """
    session = requests.Session()
    retry_strategy = Retry(
        total=3,  # number of retries
        backoff_factor=1,  # wait 1, 2, 4 seconds between retries
        status_forcelist=[429, 500, 502, 503, 504],  # HTTP status codes to retry on
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


class VeniceApiWrapper(object):
    """This class is to handle interactions with the Venice API."""

    def __init__(self, session: Session):
        """Initialize the Venice API wrapper."""
        self.headers = {
            "Authorization": "Bearer " + os.environ.get("VENICE_API_KEY"),
            "Content-Type": "application/json",
        }
        self.base_url = "https://api.venice.ai/api/v1/chat/completions"
        self.session = session
        self.message_list = []

        self.body_base = {"messages": self.message_list, "model": ""}
        return

    def get_answer(self, model: str, prompt: str):
        """Call the Venice API to get the response for a prompt."""

        ###### TODO: Add context of previous messages.

        self.message_list.append({"role": "user", "content": prompt})
        self.body_base["model"] = model
        response = self.session.post(
            self.base_url, json=self.body_base, headers=self.headers
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail="Trouble answering your question: " + str(response.json()),
            )
        resp_obj = response.json()
        resp_message = resp_obj["choices"][0]["message"]
        ##### TODO store message lists by session or somethign # self.message_list.append(resp_message)
        return resp_message["content"]
