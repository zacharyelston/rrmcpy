# MCP Server Launch Examples

This document provides instructions and configuration examples for launching MCP servers using both standard Python and [uv](https://github.com/astral-sh/uv), a fast Python runtime and package manager.

---

## Prerequisites

- Ensure you have Python installed (3.8+ recommended).
- To use `uv`, install it from [astral-sh/uv](https://github.com/astral-sh/uv):
  ```bash
  curl -Ls https://astral.sh/uv/install.sh | sh
  ```
  Or see the [official uv installation instructions](https://github.com/astral-sh/uv#installation).

---

## Python-Based MCP Server Example

```json
{
  "mcpServers": {
    "redmine": {
      "command": "python",
      "args": ["-m", "src.server"],
      "env": {
        "REDMINE_URL": "https://your-redmine.com",
        "REDMINE_API_KEY": "your-api-key"
      }
    }
  }
}
```

---

## uv-Based MCP Server Example

This example shows how to launch `src/server.py` using `uv` for improved performance and dependency management. Adjust the paths as needed for your environment.

```json
{
  "mcpServers": {
    "redmine": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/rrmcpy",
        "run",
        "-m",
        "src.server"
      ],
      "env": {
        "REDMINE_URL": "https://your-redmine.com",
        "REDMINE_API_KEY": "your-api-key"
      }
    }
  }
}
```

- `command`: Use `uv` to run the server.
- `args`: 
  - `--directory`: Sets the working directory for the server process (should be the root of your rrmcpy repo).
  - The script to run (e.g., `src/server.py`).
- `env`: Set required environment variables for the server.

For more details on `uv` usage and options, see the [uv documentation](https://github.com/astral-sh/uv#usage).

---

## Tips
- Always use absolute paths for reliability.
- Set required environment variables in the `env` section if needed.
- Ensure dependencies are installed in the target environment (for `uv`, use `uv pip install -r requirements.txt`).

---

If you have additional server types or need help with advanced configuration, please update this file or contact the project maintainers.
