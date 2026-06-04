# 01 — Local Setup: Python Project with uv & VSCode

This guide walks you through setting up a fresh Python project from scratch — the same way every example in this repo is structured. 

This is my opioniated setup for local Python development. There are many alternatives, but this has worked well for me.

---

## What You'll Need

Before starting, install these tools on your machine:

- **[uv](https://docs.astral.sh/uv/getting-started/installation/)** — a fast Python package manager (replaces pip + venv)
- **[VSCode](https://code.visualstudio.com/)** — code editor

### Install uv

On macOS/Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

On Windows (PowerShell):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Verify it worked:

```bash
uv --version
```

---

## Get Python 3.12

You don't need to install Python separately — `uv` can manage Python versions for you. This is the simplest approach since you already have `uv` installed.

```bash
uv python install 3.12
```

Verify it installed:

```bash
uv python list
```

further verification
```bash
python --version
```

You should see `3.12.x` in the output. That's it — `uv` will automatically use it when you create a project and run `uv python pin 3.12`.

> **Why 3.12?** It's a stable, widely-supported version. Most AI/ML libraries have full support for it. You can install multiple versions side-by-side with `uv python install` and switch between projects freely.

### Alternative: pyenv

If you prefer a dedicated Python version manager that works independently of `uv`, [pyenv](https://github.com/pyenv/pyenv) is the most popular choice:

```bash
# macOS (via Homebrew)
brew install pyenv

# Install Python 3.12
pyenv install 3.12

# Set it as the default globally
pyenv global 3.12

# Verify
python --version
```

For most beginners, **sticking with `uv python install` is simpler** — fewer tools to manage.

---

## Step 1 — Create a New Project

`uv` can scaffold a new project for you in one command:

```bash
uv init my-project
cd my-project
```

This creates a folder with:

```
my-project/
├── .python-version   # pins the Python version
├── pyproject.toml    # project config & dependencies
├── README.md
└── main.py
```

> **What is [pyproject.toml](cci:7://file:///Users/rob.mcbryde/code/ai-notebook/pyproject.toml:0:0-0:0)?** It's the standard Python configuration file. It describes your project name, which Python version it needs, and lists all its dependencies.

---

## Step 2 — Pin Your Python Version

Tell `uv` which Python version to use (3.12 is recommended):

```bash
uv python pin 3.12
```

This writes `3.12` to [.python-version](cci:7://file:///Users/rob.mcbryde/code/ai-notebook/.python-version:0:0-0:0) so every developer on the project uses the same version.

---

## Step 3 — Create a Virtual Environment

A virtual environment keeps your project's dependencies isolated from everything else on your machine. With `uv`, you create it and install dependencies in one step:

```bash
uv sync
```

This creates a [.venv/](cci:9://file:///Users/rob.mcbryde/code/ai-notebook/.venv:0:0-0:0) folder inside your project. You never need to activate it manually — `uv run` handles that automatically.

> **Why a virtual environment?** Without one, all Python packages install globally and projects start conflicting with each other. A [.venv](cci:9://file:///Users/rob.mcbryde/code/ai-notebook/.venv:0:0-0:0) keeps each project self-contained.

---

## Step 4 — Open in VSCode

```bash
code .
```

When VSCode opens, it may prompt you to **"Select a Python Interpreter"** — choose the one inside [.venv](cci:9://file:///Users/rob.mcbryde/code/ai-notebook/.venv:0:0-0:0) (it will show the path `./venv/bin/python`).

---

## Step 5 — Install VSCode Extensions

Open the Extensions panel (`Cmd+Shift+X` on Mac, `Ctrl+Shift+X` on Windows) and install:

### Python Extension
Search for **Python** by Microsoft — this gives you syntax highlighting, IntelliSense, and the ability to run Python files.

### Ruff Extension
Search for **Ruff** by Astral Software — this is a linter and formatter that keeps your code clean and consistent.

---

## Step 6 — Add Dependencies with uv

### Add `ruff` (linter/formatter)

```bash
uv add ruff
```

### Add `python-dotenv` (for loading `.env` files)

```bash
uv add python-dotenv
```

Both commands update [pyproject.toml](cci:7://file:///Users/rob.mcbryde/code/ai-notebook/pyproject.toml:0:0-0:0) and [uv.lock](cci:7://file:///Users/rob.mcbryde/code/ai-notebook/uv.lock:0:0-0:0) automatically. Your [pyproject.toml](cci:7://file:///Users/rob.mcbryde/code/ai-notebook/pyproject.toml:0:0-0:0) will look something like this:

```toml
[project]
name = "my-project"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "python-dotenv>=1.0.0",
    "ruff>=0.9.0",
]
```

> **What is [uv.lock](cci:7://file:///Users/rob.mcbryde/code/ai-notebook/uv.lock:0:0-0:0)?** It records the exact versions of every installed package so the project is perfectly reproducible on any machine. Commit this file to git.

---

## Step 7 — Set Up Your `.env` File

API keys and secrets must **never** be committed to git. The pattern used in this project is:

- [.env.example](cci:7://file:///Users/rob.mcbryde/code/ai-notebook/.env.example:0:0-0:0) — a template committed to the repo showing which variables are needed (with dummy values)
- `.env` — your real local file with actual secrets (git-ignored)

### Copy the example file

```bash
cp .env.example .env
```

Now open `.env` and fill in your real API keys:

```bash
# .env
OPENAI_API_KEY="your-real-key-here"
ANTHROPIC_API_KEY="your-real-key-here"
```

### Why is `.env` safe?

Check [.gitignore](cci:7://file:///Users/rob.mcbryde/code/ai-notebook/.gitignore:0:0-0:0) — it contains:

```
.env
```

This tells git to never track that file, so your secrets stay local to your machine only.

### Loading `.env` in Python

With `python-dotenv` installed, add this to the top of any Python file that needs the variables:

```python
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
print(api_key)
```

---

## Step 8 — Run Your Code

Use `uv run` instead of `python` directly — it automatically uses the virtual environment:

```bash
uv run main.py
```

---

## Project Structure Summary

After completing this setup, your project should look like this:

```
my-project/
├── .env              # ← your secrets (git-ignored, never commit this)
├── .env.example      # ← template showing required variables (committed to git)
├── .gitignore        # ← tells git what to ignore
├── .python-version   # ← pins Python 3.12
├── .venv/            # ← virtual environment (git-ignored)
├── main.py
├── pyproject.toml    # ← project config and dependencies
└── uv.lock           # ← exact dependency versions (commit this)
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Create new project | `uv init my-project` |
| Pin Python version | `uv python pin 3.12` |
| Install / sync dependencies | `uv sync` |
| Add a dependency | `uv add <package>` |
| Run a script | `uv run main.py` |
| Copy env template | `cp .env.example .env` |

## Summary 

This is my personal setup for working with AI projects locally using Python. Anytime I want to spin up a new AI learning experiment in a new project this is my approach.

Always welcome for feedback and suggestions for alternatives or improvements. But so far it's been working well for me. 🚀