---
title: "What is LangChain/LangGraph?"
seoTitle: "What is LangChain and LangGraph"
seoDescription: "Introduction to what LangChain and LangGraph the AI Frameworks are. "
datePublished: 2026-06-09T15:16:23.906Z
cuid: cmq6s8ptt00000cj90xtb3bs8
slug: what-is-langchain-langgraph
cover: https://cdn.hashnode.com/uploads/covers/6a1ed89dc5484173f87dd5bd/efac060f-4137-41f2-b499-26f57d0832b1.jpg
tags: ai, python, begineer, langchain, langgraph

---

[LangChain](https://www.langchain.com/) exists as both an open-source framework and a venture-backed company. The framework, introduced in 2022 by Harrison Chase, streamlines the development of LLM-powered applications with support for multiple programming languages including Python, JavaScript/TypeScript, Go Rust and Ruby.

The company behind the framework, LangChain Inc, maintains and expands the framework while offering enterprise solutions LLM application development.

While the core framework remains open source, the company provides additional enterprise features and support for commercial uses. Both share the same mission: accelerating LLM application development by providing robust tools and infrastructure.

LangChain is a structured framework with tested solutions, which simplifies AI application development and enables more sophisticated use cases.

In a blog series, I have explored [Building an AI Agent from Scratch](https://ai-notebook.uk/series/building-an-ai-agent-from-scratch). This was purely for my learning, in order to understand the fundamental building blocks on agentic AI. In practice, there are very few instances where I would hand build such an agent, instead opting to use a framework such as LangChain.  
  
Building from scratch would be the web development equivalent of hand crafting your web application in HTML, CSS and JavaScript, instead of leveraging modern frameworks such as Next.js, Nuxt.js or Angular.

**LangGraph** is **<mark class="bg-yellow-200 dark:bg-yellow-500/30">a low-level orchestration framework built on top of LangChain</mark>**, designed for building stateful, multi-agent, and complex AI applications. While LangChain executes workflows sequentially in straight lines, LangGraph allows for branching, feedback loops, and parallel processing. It was released as another open-source framework in January 2024 and is maintained by the LangChain company alongside LangChain the open source framework.

* * *

## How LangChain enables AI agent development

LangChain provides the foundations for building sophisticated AI applications through its modular architecture and composable patterns.

*   **Composable workflows:** The LangChain Expression Language (LCEL) allows developers to break down complex tasks into modular components that can be assembled and reconfigured. This composability enables systematic reasoning through the orchestration of multiple processing steps.
    
*   **Integration ecosystem:** LangChain offers battle-tested abstract interfaces for all generative AI components (LLMs, embeddings, vector databases, document loaders, search engines). This lets you build applications that can easily switch between providers without rewriting core logic.
    
*   **Unified model access:** The framework provides consistent interfaces to diverse language and embedding models, allowing seamless switching between providers while maintaining application logic.
    
*   **Memory and State management:** For applications requiring persistent context across interactions, **LangGraph** now serves as the recommended solution. It maintains conversation history and application state with purpose-built persistence mechanisms.
    
*   **Agent architecture:** Though LangChain contains agent implementations, LangGraph has become the preferred framework for building sophisticated agents, it provides:
    
    *   Graph-based workflow definition for complex decision paths
        
    *   Persistent state management across multiple interactions
        
    *   Streaming support for real-time feedback during processing
        
    *   Human-in-the-loop capabilities for validation and corrections.
        

Together, LangChain and LangGraph and their companion projects like LangSmith form a comprehensive ecosystem that transforms LLMs from simple text generators into systems capable of sophisticated real-world tasks, combining strong abstractions with practical implementation patters optimised for production use.