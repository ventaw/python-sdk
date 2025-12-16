
from typing import List, Optional
from ventaw.client import get_default_client

class Template:
    def __init__(self, **kwargs):
        self.code = kwargs.get("code")
        self.name = kwargs.get("name")
        self.description = kwargs.get("description")
        self.default_cpu = kwargs.get("default_cpu")
        self.default_memory = kwargs.get("default_memory")

    @classmethod
    def list(cls) -> List["Template"]:
        """List all available templates."""
        client = get_default_client()
        data = client.request("GET", "/templates")
        # API returns {"templates": [...], "total": ...}
        items = data.get("templates", [])
        return [cls(**item) for item in items]

    def __repr__(self):
        return f"<Template code={self.code} name={self.name}>"
