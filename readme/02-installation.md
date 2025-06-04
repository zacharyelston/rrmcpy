# Installation

## Prerequisites

- Python 3.10+ (required by fastmcp dependency)
- Access to a Redmine instance
- Redmine API key

## Environment Methods

Choose one of the following installation methods:

### 1. Using uv (Recommended)

```bash
# Install uv
curl -Ls https://astral.sh/uv/install.sh | sh

# Install dependencies
uv pip install -e /path/to/fastmcp
uv pip install -r requirements.txt

# Run server
uv run -m src.server
```

### 2. Using pyenv

```bash
# Create and activate environment
pyenv install 3.11.12
pyenv virtualenv 3.11.12 rrmcpy
pyenv activate rrmcpy

# Install dependencies
pip install -e /path/to/fastmcp
pip install -r requirements.txt

# Run server
python -m src.server
```

### 3. Using standard venv

```bash
# Create and activate environment
python3.10 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e /path/to/fastmcp
pip install -r requirements.txt

# Run server
python -m src.server
```

For detailed setup instructions, see [README-python.md](../README-python.md).

For MCP server launch configurations, see [MCP Servers Examples](../docs/mcp-servers-examples.md).
