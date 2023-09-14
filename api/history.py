import abc
import logging
import time
import urllib
from datetime import datetime

import pydantic
import requests
from pydantic_core import ValidationError
import pytz

logger = logging.getLogger(__name__)


class Message(pydantic.BaseModel):
    user: str
    content: str
    timestamp: float

    @property
    def datetime(self) -> datetime:
        """Convert timestamp to datetime"""
        return datetime.fromtimestamp(
            self.timestamp, tz=pytz.timezone("Europe/Amsterdam")
        )


class HistoryInterface(abc.ABC):
    @abc.abstractmethod
    def insert(self, user: str, content: str) -> None:
        """Insert one history message."""
        pass

    @abc.abstractmethod
    def get_items(self, limit: int) -> list[Message]:
        """Get history messages limited by limit arg."""
        pass


class HistoryFirebase(HistoryInterface):
    TABLE_PATH = "history"

    def __init__(self, dsn: str, auth_token: str) -> None:
        self.dsn = dsn
        self.auth_token = auth_token

    def __get_url(self) -> str:
        path = f"{HistoryFirebase.TABLE_PATH}.json"
        return urllib.parse.urljoin(self.dsn, path)

    @staticmethod
    def __get_current_timestamp() -> float:
        return time.time()

    def insert(self, user: str, content: str) -> None:
        timestamp = HistoryFirebase.__get_current_timestamp()
        message = Message(user=user, content=content, timestamp=timestamp)
        url = self.__get_url()

        params = {"auth": self.auth_token}
        data = message.model_dump()
        try:
            response = requests.post(url, params=params, json=data)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(
                f"Error insert history message, {e}",
            )

    def get_items(self, limit: int) -> list[Message]:
        url = self.__get_url()

        params = {
            "orderBy": '"timestamp"',
            "limitToLast": limit,
            "auth": self.auth_token,
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()

        except requests.exceptions.RequestException as e:
            logger.error(
                f"Error get history, {e}",
            )
            return []

        data = response.json()
        if not data:
            return []
        messages = []

        for key, item_data in data.items():
            try:
                message = Message(**item_data)
            except ValidationError as e:
                logger.error(f"Error parse history message, id={key}, {e}")
                continue
            messages.append(message)

        messages.sort(key=lambda message: message.timestamp)
        return messages
