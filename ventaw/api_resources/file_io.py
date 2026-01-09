
from typing import List, Dict, Any, Union
import base64

class FileIO:
    def __init__(self, client, sandbox_id: str):
        self.client = client
        self.sandbox_id = sandbox_id

    def list(self, path: str = ".", recursive: bool = False) -> List[Dict[str, Any]]:
        """List files and directories."""
        data = self.client.request(
            "GET", 
            f"/sandboxes/{self.sandbox_id}/files/list",
            params={"path": path, "recursive": str(recursive).lower()}
        )
        return data.get("items", [])

    def read(self, path: str, encoding: str = "utf-8") -> str:
        """
        Read file content.
        :param encoding: 'utf-8' (default) or 'base64'.
        """
        # The client.request method typically expects JSON response. 
        # But download endpoint returns stream/text. 
        # We need to bypass the auto-JSON parsing in client.request or handle it.
        # Let's check client.request implementation again.
        # It calls response.json(). This won't work for download.
        # We might need to access the session directly or add a raw flag.
        
        # Accessing session directly for now since request() enforces JSON.
        url = f"{self.client.base_url}/sandboxes/{self.sandbox_id}/files/download"
        resp = self.client.session.get(url, params={"path": path})
        
        if not 200 <= resp.status_code < 300:
             self.client._handle_error(resp)
             
        content_bytes = resp.content
        if encoding == "base64":
            return base64.b64encode(content_bytes).decode("utf-8")
        else:
            return content_bytes.decode("utf-8")

    def write(self, path: str, content: str, encoding: str = "utf-8") -> int:
        """
        Write content to file.
        :param content: Text or Base64 string.
        :param encoding: 'utf-8' (content is text) or 'base64' (content is b64).
        """
        url = f"{self.client.base_url}/sandboxes/{self.sandbox_id}/files/upload"
        
        if encoding == "base64":
            file_content = base64.b64decode(content)
        else:
            file_content = content.encode("utf-8")
            
        # Requests Multipart Upload
        files = {'file': (path.split('/')[-1], file_content, 'application/octet-stream')}
        
        resp = self.client.session.post(url, params={"path": path}, files=files)
        
        if not 200 <= resp.status_code < 300:
             self.client._handle_error(resp)
             
        # API returns {"bytes_written": N}
        return resp.json().get("bytes_written", len(file_content))

    def create_directory(self, path: str) -> bool:
        """Create a directory (recursive)."""
        self.client.request(
            "POST",
            f"/sandboxes/{self.sandbox_id}/files/mkdir",
            params={"path": path}
        )
        return True

    def delete_file(self, path: str) -> bool:
        """Delete a file."""
        self.client.request(
            "DELETE",
            f"/sandboxes/{self.sandbox_id}/files",
            params={"path": path}
        )
        return True

    def delete_directory(self, path: str) -> bool:
        """Delete a directory (recursive)."""
        self.client.request(
            "DELETE",
            f"/sandboxes/{self.sandbox_id}/files",
            params={"path": path, "recursive": "true"}
        )
        return True
