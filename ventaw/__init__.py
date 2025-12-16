
from typing import Optional

# Global Configuration
api_key: Optional[str] = None
api_base: str = "http://localhost:8000/v1"

from ventaw.client import Client
from ventaw.api_resources.sandbox import Sandbox
from ventaw.api_resources.template import Template
