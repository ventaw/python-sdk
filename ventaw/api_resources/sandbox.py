
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

    def _mcp_post(self, tool_name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Call MCP tools endpoint directly and return content list."""
        base = getattr(self._client, "base_url", None) or getattr(self._client, "baseUrl", None)
        if not base:
            raise RuntimeError("Client base URL not available for MCP request")
        root = base.rsplit("/", 1)[0]
        url = f"{root}/mcp/tools"
        resp = self._client.session.post(url, json={"name": tool_name, "arguments": arguments})
        if not 200 <= resp.status_code < 300:
            self._client._handle_error(resp)
        return resp.json().get("content", [])

    def _parse_mcp_text(self, content: List[Dict[str, Any]]) -> str:
        parts: List[str] = []
        for item in content:
            if item.get("type") == "text":
                parts.append(item.get("text", ""))
        return "\n".join(parts)

    # Lifecycle
    def start(self, use_mcp: bool = False) -> bool:
        if not self.id:
            raise ValueError("Sandbox ID is missing.")
        if use_mcp:
            self._mcp_post("start_sandbox", {"sandbox_id": str(self.id)})
            return True
        self._client.request("POST", f"/sandboxes/{self.id}/start")
        return True

    def pause(self, use_mcp: bool = False) -> bool:
        if not self.id:
            raise ValueError("Sandbox ID is missing.")
        if use_mcp:
            self._mcp_post("pause_sandbox", {"sandbox_id": str(self.id)})
            return True
        self._client.request("POST", f"/sandboxes/{self.id}/pause")
        return True

    def terminate(self, use_mcp: bool = False) -> bool:
        if not self.id:
            raise ValueError("Sandbox ID is missing.")
        if use_mcp:
            self._mcp_post("stop_sandbox", {"sandbox_id": str(self.id)})
            return True
        self._client.request("POST", f"/sandboxes/{self.id}/terminate")
        return True

    # SSH tokens
    def create_ssh_token(self, ttl_minutes: int = 60) -> Dict[str, Any]:
        if not self.id:
            raise ValueError("Sandbox ID is missing.")
        return self._client.request("POST", f"/sandboxes/{self.id}/ssh-token", params={"ttl_minutes": ttl_minutes})

    def list_ssh_tokens(self) -> List[Dict[str, Any]]:
        if not self.id:
            raise ValueError("Sandbox ID is missing.")
        return self._client.request("GET", f"/sandboxes/{self.id}/ssh-token")

    def revoke_ssh_token(self, token: str) -> bool:
        if not self.id:
            raise ValueError("Sandbox ID is missing.")
        self._client.request("DELETE", f"/sandboxes/{self.id}/ssh-token", params={"token": token})
        return True

    # Execute + PTY
    def execute(self, code: str, language: str = "bash", use_mcp: bool = False) -> Dict[str, Any]:
        if not self.id:
            raise ValueError("Sandbox ID is missing.")
        if use_mcp:
            content = self._mcp_post("execute_command", {"sandbox_id": str(self.id), "command": code})
            return {"stdout": self._parse_mcp_text(content)}
        return self._client.request("POST", f"/sandboxes/{self.id}/execute", json={"code": code, "language": language})

    def create_pty(self, command: str = "/bin/bash", cwd: Optional[str] = None, cols: int = 80, rows: int = 24):
        return self._client.request("POST", f"/sandboxes/{self.id}/pty", json={"command": command, "cwd": cwd, "cols": cols, "rows": rows})

    def send_pty_input(self, pty_id: str, data: str):
        return self._client.request("POST", f"/sandboxes/{self.id}/pty/{pty_id}/input", json={"input": data})

    def resize_pty(self, pty_id: str, cols: int, rows: int):
        return self._client.request("POST", f"/sandboxes/{self.id}/pty/{pty_id}/resize", json={"cols": cols, "rows": rows})

    def get_pty_logs(self, pty_id: str, offset: int = 0):
        return self._client.request("GET", f"/sandboxes/{self.id}/pty/{pty_id}/logs", params={"offset": offset})

    def delete_pty(self, pty_id: str):
        return self._client.request("DELETE", f"/sandboxes/{self.id}/pty/{pty_id}")

    # Background sessions
    def list_sessions(self):
        return self._client.request("GET", f"/sandboxes/{self.id}/sessions")

    def create_session(self, command: str, cwd: Optional[str] = None, name: Optional[str] = None):
        return self._client.request("POST", f"/sandboxes/{self.id}/sessions", json={"command": command, "cwd": cwd, "name": name})

    def get_session_logs(self, session_id: str, offset: int = 0):
        return self._client.request("GET", f"/sandboxes/{self.id}/sessions/{session_id}/logs", params={"offset": offset})

    def delete_session(self, session_id: str):
        return self._client.request("DELETE", f"/sandboxes/{self.id}/sessions/{session_id}")

    # FileIO aliases (convenience wrappers around self.files)
    def list_files(self, path: str = ".", recursive: bool = False):
        return self.files.list(path=path, recursive=recursive)

    def read_file(self, path: str, encoding: str = "utf-8", use_mcp: bool = False):
        if use_mcp:
            content = self._mcp_post("read_file", {"sandbox_id": str(self.id), "path": path, "encoding": encoding})
            return self._parse_mcp_text(content)
        return self.files.read(path=path, encoding=encoding)

    def write_file(self, path: str, content: str, encoding: str = "utf-8", use_mcp: bool = False):
        if use_mcp:
            self._mcp_post("write_file", {"sandbox_id": str(self.id), "path": path, "content": content, "encoding": encoding})
            return True
        return self.files.write(path=path, content=content, encoding=encoding)

    def create_dir(self, path: str):
        return self.files.create_directory(path)

    def delete_file_or_dir(self, path: str, recursive: bool = False):
        if recursive:
            return self.files.delete_directory(path)
        return self.files.delete_file(path)

    def __repr__(self):
        return f"<Sandbox id={self.id} name={self.name} state={self.state}>"
