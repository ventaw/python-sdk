
from typing import List, Optional, Any, Dict
from ventaw.client import get_default_client

class Subscription:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.topic_id = kwargs.get("topic_id")
        self.name = kwargs.get("name")
        self.webhook_url = kwargs.get("webhook_url")
        self.created_at = kwargs.get("created_at")
        self._client = get_default_client()

    def delete(self) -> bool:
        """Delete this subscription."""
        topic_id = self.topic_id
        self._client.request("DELETE", f"/topics/{topic_id}/subscriptions/{self.id}")
        return True

class Topic:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.region = kwargs.get("region")
        self.connection_string = kwargs.get("connection_string")
        self.created_at = kwargs.get("created_at")
        self._client = get_default_client()

    @classmethod
    def create(cls, name: str) -> "Topic":
        """Create a new messaging topic."""
        client = get_default_client()
        payload = {"name": name}
        data = client.request("POST", "/topics", json=payload)
        return cls(**data)

    @classmethod
    def get(cls, id: str) -> "Topic":
        """Get a topic by ID."""
        client = get_default_client()
        data = client.request("GET", f"/topics/{id}")
        return cls(**data)

    @classmethod
    def list(cls) -> List["Topic"]:
        """List all topics."""
        client = get_default_client()
        data = client.request("GET", "/topics")
        return [cls(**item) for item in data]

    def delete(self) -> bool:
        """Delete this topic."""
        self._client.request("DELETE", f"/topics/{self.id}")
        return True

    def publish(self, body: Any) -> str:
        """Publish a message to the topic."""
        payload = {"body": body}
        data = self._client.request("POST", f"/topics/{self.id}/publish", json=payload)
        return data.get("message_id")

    def subscribe(self, name: str, webhook_url: Optional[str] = None) -> Subscription:
        """Subscribe to this topic."""
        payload = {
            "name": name,
            "webhook_url": webhook_url
        }
        data = self._client.request("POST", f"/topics/{self.id}/subscriptions", json=payload)
        return Subscription(**data)

    def list_subscriptions(self) -> List[Subscription]:
        """List all subscriptions for this topic."""
        data = self._client.request("GET", f"/topics/{self.id}/subscriptions")
        return [Subscription(**item) for item in data]
