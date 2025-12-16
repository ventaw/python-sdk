
from typing import List, Dict, Any, Union
import base64

class FileIO:
    def __init__(self, client, sandbox_id: str):
        self.client = client
        self.sandbox_id = sandbox_id

    def list(self, path: str = ".") -> List[Dict[str, Any]]:
        """List files and directories."""
        data = self.client.request(
            "POST", 
            f"/sandboxes/{self.sandbox_id}/files/list",
            json={"path": path}
        )
        return data.get("items", [])

    def read(self, path: str) -> str:
        """Read file content (text)."""
        data = self.client.request(
            "POST",
            f"/sandboxes/{self.sandbox_id}/files/read",
            json={"path": path}
        )
        return data.get("content", "")

    def write(self, path: str, content: str) -> int:
        """Write content to file."""
        data = self.client.request(
            "POST",
            f"/sandboxes/{self.sandbox_id}/files/write",
            json={"path": path, "content": content}
        )
        return data.get("bytes_written", 0)

    def create_dir(self, path: str) -> bool:
        """Create a directory (recursive)."""
        self.client.request(
            "POST",
            f"/sandboxes/{self.sandbox_id}/files/create_dir",
            json={"path": path}
        )
        return True

    def delete(self, path: str) -> bool:
        """Delete a file."""
        self.client.request(
            "POST",
            f"/sandboxes/{self.sandbox_id}/files/delete",
            json={"path": path}
        )
        return True

    def delete_dir(self, path: str) -> bool:
        """Delete a directory (recursive)."""
        self.client.request(
            "POST",
            f"/sandboxes/{self.sandbox_id}/files/delete_dir",
            json={"path": path}
        )
        return True
