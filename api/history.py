import abc
import logging
import time
import urllib
from datetime import datetime

import pydantic
import pytz
import requests
from extensions import db
from pydantic_core import ValidationError

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


class PostgresMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String())
    content = db.Column(db.String())
    timestamp = db.Column(db.Float())

    def __init__(self, user: str, content: str, timestamp: float):
        self.user = user
        self.content = content
        self.timestamp = timestamp

    def __repr__(self):
        return f"<Message {self.content}>"


class HistoryInterface(abc.ABC):
    def _get_current_timestamp(self) -> float:
        return time.time()

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

    def insert(self, user: str, content: str) -> None:
        timestamp = self._get_current_timestamp()
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


class HistoryPostgres(HistoryInterface):
    def insert(self, user: str, content: str) -> None:
        timestamp = self._get_current_timestamp()
        message = PostgresMessage(user=user, content=content, timestamp=timestamp)
        db.session.add(message)
        db.session.commit()

    def get_items(self, limit: int) -> list[Message]:
        database_messages = (
            PostgresMessage.query.order_by(PostgresMessage.timestamp).limit(limit).all()
        )
        messages = []
        for message in database_messages:
            try:
                message = Message(**message.__dict__)
            except ValidationError as e:
                logger.error(f"Error parse history message, id={message}, {e}")
                continue
            messages.append(message)

        return messages
