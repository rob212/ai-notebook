---
title: "Welcome to AI Notebook: Documenting my journey AI"
seoDescription: "Introduction to my AI notebook learning blog for beginners interested in learning about AI and LangChain"
datePublished: 2026-06-02T14:00:58.896Z
cuid: cmpwpgrny002k1sk53jk27db0
slug: welcome-to-ai-notebook-documenting-my-journey-ai
cover: https://cdn.hashnode.com/uploads/covers/6a1ed89dc5484173f87dd5bd/154cb062-9fbb-4239-8234-5c85e2fae9e6.jpg
tags: ai, python, beginners, langchain

---

I'm a developer learning to build AI-powered applications, and this blog is where I document that journey. Every post covers something I've built and experimented with for my learning - sharing my learnings for my benefit, but if it helps anyone else, then all the better.

The initial focus will primarily be on **LangChain** and **LangGraph**, two of the most widely used frameworks for building LLM-powered applications in Python. If you're on a similar path, I hope this saves you some of the head-scratching I went through.

All code is available in my GitHub repo: [**ai-notebook**](https://github.com/rob212/ai-notebook)

* * *

## My Setup

Before diving into posts, here's the environment I'm using so you can code along.

**Language:** Python 3.12  
**Editor:** VSCode (with the Python and Ruff extensions)  
**Package manager:** [uv](https://docs.astral.sh/uv/) — a fast, modern replacement for pip/venv

If you don't have `uv` installed:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

To run any example from the repo:

```bash
git clone https://github.com/rob212/ai-notebook.git
cd ai-notebook
uv sync
```

* * *

## You'll need LLM API account(s

Most examples use a cloud LLM. You'll need at least one of:

*   [**OpenAI**](https://platform.openai.com/) — GPT-4o-mini is cheap and capable
    
*   [**Anthropic**](https://console.anthropic.com/) — Claude models, excellent for reasoning tasks
    

Some examples use [**Ollama**](https://ollama.com/) to run models locally for free — I'll flag when that's an option.

* * *

## Handling API Keys Safely with dotenv

Never hardcode API keys in your source code or commit them to GitHub. I use the [python-dotenv](https://pypi.org/project/python-dotenv/) pattern instead.

**1\. Create a** `.env` **file** (this is gitignored — never committed):

```bash
cp .env.example .env
```

Then open `.env` and fill in your real keys:

```bash
OPENAI_API_KEY="sk-..."
ANTHROPIC_API_KEY="sk-ant-..."
```

**2\. The** [**.env.example**](cci:7://file:///Users/rob.mcbryde/code/ai/genai_langchain/chapter_2/.env.example:0:0-0:0) **file** is committed to the repo. It shows which variables are needed without exposing real values:

```bash
OPENAI_API_KEY="insert_API_Key_Here"
ANTHROPIC_API_KEY="insert_API_Key_Here"
```

**3\. Load them in your code:**

```python
import os
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
```

This pattern means you can share your code publicly without ever accidentally leaking credentials.

* * *

## What's Coming

Posts will follow the structure of my `ai-notebook` repo, building from the basics up:

*   **LangChain** — prompts, models, chains, agents, memory
    
*   **LangGraph** — stateful multi-step agents and workflows
    

Each post will have a link to the full working code in the repo. See you in the next one.