# Redmine MCP Server – Python Environment Setup Examples

This guide provides clear, actionable examples for setting up and running the Redmine MCP Server using **pyenv**, **uv**, or plain **python/venv**. Choose the method that best fits your workflow.

---

## ⚠️ Python Version Requirement

> This project (and its dependency `fastmcp`) requires **Python 3.10 or higher**.
> If you use Python 3.9 or lower, installation will fail with an error like:
> 
> `ERROR: Package 'fastmcp' requires a different Python: 3.9.20 not in '>=3.10'`

---

## 1. Using pyenv + pyenv-virtualenv

**Recommended for developers who use multiple Python versions or want isolated user-level environments.**

```bash
# Install Python 3.11.12 (or 3.10.x)
pyenv install 3.11.12
# Create and activate a dedicated virtualenv
pyenv virtualenv 3.11.12 rrmcpy
pyenv activate rrmcpy

# Install dependencies
pip install -e /ABSOLUTE/PATH/TO/fastmcp
pip install -r requirements.txt

# Run the server
python -m src.server
```

**Tips:**
- Do not use `uv pip` or `uv run` in the same shell session as pyenv.
- If a `.venv` exists in your project root, remove it or make sure it is not activated.

---

## 2. Using uv (Fast Python Installer)

**Recommended for fast, reproducible dependency management and modern workflows.**

```bash
# Check Python version (should be 3.10+)
python --version

# Install uv
curl -Ls https://astral.sh/uv/install.sh | sh

# Install fastmcp (choose one method):
# (A) Local checkout (editable mode)
uv pip install -e /ABSOLUTE/PATH/TO/fastmcp
# (B) Directly from GitHub
uv pip install -e 'git+https://github.com/jlowin/fastmcp.git#egg=fastmcp'

# Install other dependencies
uv pip install -r requirements.txt

# Run the server
uv run -m src.server
```

**Tips:**
- Do not activate another venv or pyenv when using uv.
- If you see warnings about `.venv` or VIRTUAL_ENV mismatches, deactivate other environments and use uv's default.

---

## 3. Using Plain Python venv

**For users who prefer the standard Python venv module.**

```bash
# Check Python version (should be 3.10+)
python3 --version

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e /ABSOLUTE/PATH/TO/fastmcp
pip install -r requirements.txt

# Run the server
python -m src.server
```

**Tips:**
- Make sure you are using Python 3.10+ for both venv creation and all commands.
- Avoid mixing venv/pyenv/uv in the same shell session.

---

## Troubleshooting

- **Python Version Errors:** Always check your Python version with `python --version` or `python3 --version`.
- **Environment Mismatch Warnings:** Only one environment (pyenv, venv, or uv) should be active at a time.
- **Missing fastmcp:** Ensure you install fastmcp either from a local checkout or from GitHub.
- **Server Import Errors:** Always run the server as a module: `python -m src.server` or `uv run -m src.server`.

---

For advanced configuration and server launch examples, see [`docs/mcp-servers-examples.md`](docs/mcp-servers-examples.md).
