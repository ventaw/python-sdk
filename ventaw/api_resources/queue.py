
from typing import List, Optional, Any, Dict
from ventaw.client import get_default_client

class Message:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.body = kwargs.get("body")
        self.ack_token = kwargs.get("ack_token")
        self.state = kwargs.get("state")
        self.attempt = kwargs.get("attempt")
        self.visible_at = kwargs.get("visible_at")

class Queue:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.backend = kwargs.get("backend")
        self.use_case = kwargs.get("use_case")
        self.region = kwargs.get("region")
        self.connection_string = kwargs.get("connection_string")
        self.created_at = kwargs.get("created_at")
        self._client = get_default_client()

    @classmethod
    def create(cls, name: str, use_case: str = "general_purpose", visibility_timeout: int = 30) -> "Queue":
        """Create a new message queue."""
        client = get_default_client()
        payload = {
            "name": name,
            "use_case": use_case,
            "visibility_timeout_seconds": visibility_timeout
        }
        data = client.request("POST", "/queues", json=payload)
        return cls(**data)

    @classmethod
    def get(cls, id: str) -> "Queue":
        """Get a queue by ID."""
        client = get_default_client()
        data = client.request("GET", f"/queues/{id}")
        return cls(**data)

    @classmethod
    def list(cls) -> List["Queue"]:
        """List all message queues."""
        client = get_default_client()
        data = client.request("GET", "/queues")
        items = data.get("items", []) if isinstance(data, dict) else data
        return [cls(**item) for item in items]

    def delete(self) -> bool:
        """Delete this queue."""
        self._client.request("DELETE", f"/queues/{self.id}")
        return True

    def send(self, body: Any, delay_seconds: int = 0) -> str:
        """Send a message to the queue."""
        payload = {
            "body": body,
            "delay_seconds": delay_seconds
        }
        data = self._client.request("POST", f"/queues/{self.id}/messages", json=payload)
        return data.get("message_id")

    def receive(self, consumer_id: Optional[str] = None) -> Optional[Message]:
        """Receive a message from the queue."""
        params = {}
        if consumer_id:
            params["consumer_id"] = consumer_id
            
        data = self._client.request("POST", f"/queues/{self.id}/receive", params=params)
        if not data:
            return None
        return Message(**data)

    def ack(self, ack_token: str) -> bool:
        """Acknowledge a message."""
        payload = {"ack_token": ack_token}
        self._client.request("POST", "/messages/ack", json=payload)
        return True
