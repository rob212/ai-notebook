# AI Notebook

A hands-on learning journal documenting my exploration of AI. 

This will include popular frameworks like LangChain and LangGraph.
Each topic includes working code examples and a companion blog post explaining the concepts.

📝 **Blog:** [ai-notebook.uk](https://ai-notebook.uk/)

---
 
## Posts
 
| # | Title | Code | Post |
|---|-------|------|------|
| 01 | Welcome — Setup, Tools & How to Use This Repo | — | [Read →](https://robmcbryde.hashnode.dev/welcome-to-ai-notebook-documenting-my-journey-ai) |
| 02 | Getting Started with LangChain: LLMs, Prompts & Chains | [langchain/01-getting-started](./langchain/01-getting-started/) | Coming soon |
| 03 | Chains — Building Multi-Step Workflows with LCEL | [langchain/02-chains](./langchain/02-chains/) | Coming soon |



### LangChain

| # | Topic | Code | Post |
|---|-------|------|------|
| 01 | Getting Started — LLMs, Prompts & Output Parsers | [langchain/01-getting-started](./langchain/01-getting-started/) | Coming soon |
| 02 | Chains — Building Multi-Step Workflows with LCEL | [langchain/02-chains](./langchain/02-chains/) | Coming soon |

### LangGraph

| # | Topic | Code | Post |
|---|-------|------|------|
| — | Coming soon | — | — |

---

## Running the Examples

Each folder contains its own `README.md` with setup instructions. In general:

```bash
# Install dependencies (uses uv)
uv sync

# Copy and fill in your API keys
cp .env.example .env

# Run an example
uv run langchain/01-getting-started/joke_agent.py

## Tech Stack
LangChain — LLM orchestration framework
LangGraph — stateful, graph-based agents
uv — Python package manager
Models: OpenAI GPT-4o-mini, Ollama (local)

