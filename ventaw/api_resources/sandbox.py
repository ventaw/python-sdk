
from typing import List, Optional, Dict, Any
from ventaw.client import get_default_client
from ventaw.api_resources.file_io import FileIO

class Sandbox:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.template_id = kwargs.get("template_id")
        self.state = kwargs.get("state")
        self.ip_address = kwargs.get("ip_address")
        self.access_url = kwargs.get("access_url")
        self.created_at = kwargs.get("created_at")
        self._client = get_default_client() # Bind to current default client

    @property
    def files(self) -> FileIO:
        """Access file operations for this sandbox."""
        if not self.id:
            raise ValueError("Sandbox ID is missing.")
        return FileIO(self._client, self.id)

    @classmethod
    def create(cls, template: str, name: str, vcpu: int = 2, memory: int = 2048) -> "Sandbox":
        """Create a new sandbox."""
        client = get_default_client()
        payload = {
            "template_id": template,
            "name": name,
            "vcpu_count": vcpu,
            "mem_size_mib": memory
        }
        data = client.request("POST", "/sandboxes", json=payload)
        return cls(**data)

    @classmethod
    def get(cls, id: str) -> "Sandbox":
        """Get a sandbox by ID."""
        client = get_default_client()
        data = client.request("GET", f"/sandboxes/{id}")
        return cls(**data)

    @classmethod
    def list(cls) -> List["Sandbox"]:
        """List all sandboxes."""
        client = get_default_client()
        data = client.request("GET", "/sandboxes")
        # API returns list of dicts directly or {"items": []}? 
        # Checking sandboxes.py endpoint: returns `List[Sandbox]`.
        return [cls(**item) for item in data]

    def delete(self) -> bool:
        """Delete this sandbox."""
        if not self.id:
            raise ValueError("Sandbox ID is missing.")
        self._client.request("DELETE", f"/sandboxes/{self.id}")
        return True
    
    def refresh(self):
        """Refresh attributes from API."""
        if not self.id:
            raise ValueError("Sandbox ID is missing.")
        data = self._client.request("GET", f"/sandboxes/{self.id}")
        self.__init__(**data)

    def __repr__(self):
        return f"<Sandbox id={self.id} name={self.name} state={self.state}>"
