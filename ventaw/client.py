
import requests
from typing import Optional, Any, Dict

import ventaw
from ventaw.error import APIError, AuthenticationError, APIConnectionError

class Client:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or ventaw.api_key
        self.base_url = (base_url or ventaw.api_base).rstrip("/")
        
        if not self.api_key:
            raise AuthenticationError("No API key provided. Set ventaw.api_key or pass api_key to Client constructor.")
            
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": "VentawPythonSDK/0.1.0"
        })

    def request(self, method: str, path: str, **kwargs) -> Any:
        url = f"{self.base_url}{path}"
        try:
            response = self.session.request(method, url, **kwargs)
        except requests.exceptions.RequestException as e:
            raise APIConnectionError(f"Connection error: {e}")

        if not 200 <= response.status_code < 300:
            self._handle_error(response)
            
        try:
            return response.json()
        except ValueError:
            return None # Empty body

    def _handle_error(self, response):
        try:
            data = response.json()
            message = data.get("detail", response.text)
        except ValueError:
            message = response.text
            
        if response.status_code == 401:
            raise AuthenticationError(message)
        else:
            raise APIError(message, status_code=response.status_code)

# Singleton instance helper
_default_client = None

def get_default_client() -> Client:
    global _default_client
    if _default_client is None:
        _default_client = Client()
    return _default_client
