# Ventaw Python SDK

The official Python SDK for managing Ventaw sandboxes.

## Installation

```bash
pip install ventaw
```

Or for local development:

```bash
pip install -e .
```

## Configuration

You can configure the SDK globally or per-client (if using the Client class directly, though global config is the default convenience wrapper).

```python
import ventaw

ventaw.api_key = "your-api-key"
# ventaw.api_base = "https://ventaw.mmogomedia.com/v1"  # Default value
```

## Usage

### Managing Templates

List available templates to use for creating sandboxes.

```python
from ventaw import Template

templates = Template.list()
for template in templates:
    print(f"{template.name} ({template.code})")
```

### Managing Sandboxes

Create, list, and manage sandboxes.

```python
from ventaw import Sandbox

# Create a new sandbox
sandbox = Sandbox.create(template="nextjs", name="my-sandbox")
print(f"Created sandbox: {sandbox.id}")

# Wait for it to start
import time
while sandbox.state != "running":
    time.sleep(1)
    sandbox.refresh()

print(f"Sandbox running at: {sandbox.access_url}")

# List all sandboxes
for sb in Sandbox.list():
    print(sb)

# Delete a sandbox
sandbox.delete()
```

### File Operations

Interact with files inside the sandbox.

```python
# Create a directory
sandbox.files.create_dir("/app/data")

# Write a file
sandbox.files.write("/app/data/config.json", '{"env": "dev"}')

# Read a file
content = sandbox.files.read("/app/data/config.json")
print(content)

# List files
files = sandbox.files.list("/app")
for file in files:
    print(f"{file['name']} - {file['type']}")

# Delete a file
sandbox.files.delete("/app/data/config.json")
```
