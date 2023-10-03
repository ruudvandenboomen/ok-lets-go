import abc

import pydantic
from extensions import db


class PushSubscriptionDTO(pydantic.BaseModel):
    endpoint: str
    keys: dict


class PushSubscription(db.Model):
    __tablename__ = "push_subscriptions"

    id = db.Column(db.Integer, primary_key=True)
    endpoint = db.Column(db.String(255), nullable=False, unique=True)
    auth_key = db.Column(db.Text, nullable=False)
    p256dh_key = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.String)

    def __init__(self, endpoint, auth_key, p256dh_key, user_id):
        self.endpoint = endpoint
        self.auth_key = auth_key
        self.p256dh_key = p256dh_key
        self.user_id = user_id


class SubscriptionInterface(abc.ABC):
    @abc.abstractmethod
    def insert(self, endpoint: str, auth: str, p256dh: str, user_id: str) -> None:
        """Insert one subscription."""
        pass

    @abc.abstractmethod
    def remove(self, user_id: str) -> None:
        """Remove one subscription."""
        pass

    @abc.abstractmethod
    def is_subscribed(self, user_id: str) -> bool:
        """Returns if the user is subscribed."""
        pass

    @abc.abstractmethod
    def get_all_other_users(self, user_id: str) -> list[PushSubscriptionDTO]:
        """Get all other subscriptions so they can be notified about an action."""
        pass


class SubscriptionRepository(SubscriptionInterface):
    def insert(self, endpoint: str, auth: str, p256dh: str, user_id: str) -> None:
        """Insert one subscription."""
        subscription = PushSubscription(endpoint, auth, p256dh, user_id)
        db.session.add(subscription)
        db.session.commit()

    def remove(self, user_id: str) -> None:
        """Remove one subscription."""
        return PushSubscription.query.filter_by(user_id=user_id).delete()

    def is_subscribed(self, user_id: str) -> bool:
        """Returns if the user is subscribed."""
        return PushSubscription.query.filter_by(user_id=user_id).first() is not None

    def get_all_other_users(self, user_id: str) -> list[PushSubscriptionDTO]:
        """Get all other subscriptions so they can be notified about an action."""
        subscriptions = PushSubscription.query.filter(
            PushSubscription.user_id != user_id
        ).all()
        subscriptions_dto = []
        for subscription in subscriptions:
            subscriptions_dto.append(
                PushSubscriptionDTO(
                    endpoint=subscription.endpoint,
                    keys={
                        "auth": subscription.auth_key,
                        "p256dh": subscription.p256dh_key,
                    },
                )
            )
        return subscriptions_dto
