---
title: "🔎 Implementing a web search tool"
seoTitle: "Implementing a Web Search Tool for your AI Agent"
seoDescription: "How to add a web search tool to your AI Agent using Tavily. "
datePublished: 2026-06-08T10:05:49.226Z
cuid: cmq51pgjz00040bjffiqw86ik
slug: implementing-a-web-search-tool
tags: ai, python, beginners, agentic-ai, tavily

---

Let's assume we are creating a 'Research Agent'. An essential capability might be the ability to access the web for up to date information that may not be part of our LLM's training data.

We will achieve this via [Tavily](https://www.tavily.com/). Tavily allows for up to 1,000 free API calls per month. In order to access Tavily you will need to sign up and retrieve your dev API key.

Install the Tavily Python client:

```shell
uv add tavily-python
```

Then, save your API key in your .env file:

```shell
TAVILY_API_KEY=<Your Tavily API KEY>
```

We'll start by the simplest possible implementation to confirm we can connect to the API and retrieve web search results.

First we load our environment variables from our `.env` file to retrieve our Tavily API key. Then we instantiate a Tavily client using our key. We define a simple `search_web` function that takes our query string and calls Tavily's `search()` method. By default we limit the `max_results` to 2 in order to reduce API costs and limit the returned data.

```python
import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

tavily_client = TavilyClient(os.getenv("TAVILY_API_KEY"))

def search_web(query: str, max_results: int = 2) -> list:
    response = tavily_client.search(query, max_results=max_results)
    return response.get("results")


search_web("Kipchoge's marathon world record")
```

> I have experimented with this call in `basics/prerequisites/03-tool-concepts/`[`tools-concepts.py`](http://tools-concepts.py) in the accompanying [code repo](https://github.com/rob212/ai-notebook/blob/main/basics/prerequisites/03-tools-concepts/tools_concepts.py) if you want to try the same.

When we examine the search results, we see each result includes a title, URL, content snippet and relevance score. The first result is his Wikipedia page, and the second an article from the BBC that references him. These snippets contain his official marathon best time is 2:01:09 in Berlin.

```python
[
    {'url': 'https://en.wikipedia.org/wiki/Eliud_Kipchoge',
  'title': 'Eliud Kipchoge',
  'content': 'On 16 September, Kipchoge won the 2018 Berlin Marathon in a time of 2:01:39, breaking the previous world record by 1 minute and 18 seconds ...',
  'score': 0.8832463,
  'raw_content': None},

 {'url': 'https://therunningchannel.com/eliud-kipchoge-record/',
  'title': "Eliud Kipchoge's Marathon Career Record",
  'content': 'Home > News > Eliud Kipchoge’s Marathon Career Record. Kenyan marathon running legend Eliud Kipchoge...',
  'score': 0.8810534,
  'raw_content': None}
  ]
```

* * *

## 🔭 Adding search options

Let's expand on our basic function to add more control via Tavily supported optional arguments. To keep our agent more focussed, we will restrict our web search tool by `topic`, `time_range` and results from a specific `country`.

`topic` allows the search to be focussed on a category such as 'general' for a broad web search, 'news' for recent articles or 'finance' for financial information. `time_range` filters results by recency, based on an enum value to allow for more specificity around recent or historical information. `country` prioritises content from a specific country.

See Tavily docs for more detailed information: [https://docs.tavily.com/documentation/api-reference/endpoint/search](https://docs.tavily.com/documentation/api-reference/endpoint/search)

```python
def search_web(
    query: str,
    max_results: int = 2,
    topic: str = "general",
    time_range: str | None = None,
    country: str | None = None,
) -> list:
 """Search the web for the given query."""
    response = tavily_client.search(
        query,
        max_results=max_results,
        topic=topic,
        time_range=time_range,
        country=country,
    )
    return response.get("results")


results = search_web(
    query="Kipchoge's marathon world record",
    topic="news",
    time_range="year",
    country="united kingdom",
)

print(results)
```

```python
[
    {'url': 'https://www.nytimes.com/athletic/6766413/2025/10/31/eliud-kipchoge-new-york-marathon-retire/',
    'title': 'Eliud Kipchoge, former double Olympic champion, says New York Marathon will be his last - The New York Times',
    'score': 0.84183896,
    'published_date': 'Fri, 31 Oct 2025 15:35:27 GMT',
    'content': '# Eliud Kipchoge, former double Olympic champion, says New York Marathon will be his last Eliud Kipchoge, the former double Olympic marathon champion and two-time world-record holder, has said that Sunday’s New York Marathon will be his final one. ...',
    'raw_content': None},

    {'url': 'https://www.independent.co.uk/sport/general/athletics/new-york-city-marathon-results-photo-finish-record-b2857028.html',
    'title': 'New York City Marathon results: Photo finish, course record and Eliud Kipchoge 17th - The Independent',
    'score': 0.71995544,
    'published_date': 'Sun, 02 Nov 2025 18:43:02 GMT',
    'content': '# New York City Marathon results: Photo finish, course record and Eliud Kipchoge 17th The elite men’s race at the New York City ...','raw_content': None}]
```

Tavily supports nearly 20 parameters, it is up to us to adjust them to find the balance between identifiying the most pertinent information for our agent's purpose, keeping the parameter count as low as possible to allow our LLM to use the web search tool correctly.

*ℹ️ The more complex your tool definition becomes, the harder it is for the LLM to use it correctly.*

* * *

## ⚠️ Handling errors

So far, we've assumed all will be well with our web search. But we need to consider how to handle errors gracefully. An invalid API key returning a 401 authentication error, a 429 rate limit error if we exceed out monthly usage allowance or a network issues causing a connection timeout, etc.

For brevity we will adopt a minimal catch all exceptions and return an error message, however, this should be considered further in a production grade implementation.

We will wrap the API call in a try-except block and return and error string if anything goes wrong. This results on the return type now being `list | str`, indicating a successful list of results or a string error message.

```python
def search_web(
    query: str,
    max_results: int = 2,
    topic: str = "general",
    time_range: str | None = None,
    country: str | None = None,
) -> list | str:
 """Search the web for the given query."""
    try:
        response = tavily_client.search(
            query,
            max_results=max_results,
            topic=topic,
            time_range=time_range,
            country=country,
        )
        return response.get("results")
    except Exception as e:
        return f"Error: Search failed - {e}
```

## Better defining our tool definitions

So far, we have created a web search tool and a calculator function. We make this accessible to an LLM via defining then using a standardised tool definition format as we saw when implementing our [calculator](https://github.com/rob212/ai-notebook/blob/main/basics/prerequisites/03-tools-concepts/tools_concepts.py).

As we expand our toolset, we should create a utility function that automatically converts as Python function into a tool definition.

We can extract the function's name, docstring, and parameter details using the Python `inspect` module. As an example, let's consider a sample function called `example_tool` that takes two parameters: `input_1` a string, and `input_2`, an integer with a default value of 1.

```python
import inspect

def example_tool(input_1:str, input_2:int=1):
    """docstring for example_tool"""
    return

print(f"function name: {example_tool.__name__}")
print(f"function docstring: {example_tool.__doc__}")
print(f"function signature: {inspect.signature(example_tool)}")
```

This outputs the following:

```python
function name: example_tool
function docstring: docstring for example_tool
function signature: (input_1: str, input_2: int = 1)
```

We can extract the function's name using the `__name__` attribute and it's description using the `__doc__` attribute. The parameter types and whether they're required can be determined using `inspect.signature`. I.e. we can see from the signature above that `input_1` is required, but `input_2` is optional, with a default value of 1.

This allows us to implement a utility function to return an object that summarises our tool function:

```python
import inspect

def function_to_input_schema(func) -> dict:
    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
        type(None): "null",
    }

    try:
        signature = inspect.signature(func)
    except ValueError as e:
        raise ValueError(
            f"Failed to get signature for function {func.__name__}: {str(e)}"
        )

    parameters = {}
    for param in signature.parameters.values():
        try:
            param_type = type_map.get(param.annotation, "string")
        except KeyError as e:
            raise KeyError(
                f"Unknown type annotation {param.annotation} for parameter {param.name}: {str(e)}"
            )
        parameters[param.name] = {"type": param_type}

    required = [param.name for param in signature.parameters.values()]

    return {
        "type": "object",
        "properties": parameters,
        "required": required,
    }
```

In our function we firstly extract the function signature using the `inspect` module. We then map Python types to JSON Schema types with string as default. Finally, parameters without default parameters are marked as required.

We can leverage this to create a `function_to_tool_definition` utility, and verify it by attempting to convert our `web_search` tool using it.

We implement the additional utility code:

```python
def format_tool_definition(name: str, description: str, parameters: dict) -> dict:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": parameters,
        },
    }

def function_to_tool_definition(func) -> dict:
    return format_tool_definition(
        func.__name__,
        func.__doc__ or "",
        function_to_input_schema(func)
    )
```

We verify this successfully returns a structured definition for our `search_web` function:

```python
search_tool_definition = function_to_tool_definition(search_web)
print(search_tool_definition)
```

```python
{
    'type': 'function',
    'function':
        {
            'name': 'search_web',
            'description': 'Search the web for the given query.',
            'parameters':
                {
                    'type': 'object',
                    'properties':
                        {
                            'query': {'type': 'string'},
                            'max_results': {'type': 'integer'},
                            'topic': {'type': 'string'},
                            'time_range': {'type': 'string'},
                            'country': {'type': 'string'}
                        },
                    'required': ['query', 'max_results', 'topic', 'time_range', 'country']
                }
            }
}
```

This will allow us to convert all our tools, and future ones, using this utility.

* * *

## Tool Execution utilities

Now let's put everything together. We have a working `web_search` function and a `function_to_tool_definition` utility that can be used to convert it into a tool definition. The missing piece is building the execution infrastructure that connects the LLM's tool calls to the *actual* function expression. I.e. when the LLM determines that it should call our `web_search` tool, it is up to us to call that function in our code.

We need to build two components:

1.  A function to execute tools based on LLM output.
    
2.  A control loop that manages the interaction betwween the LLM and our tools.
    

## 🔧 Building the tool execution system

We will define a utility function that executes a tool and returns its results.

This function takes a `tool_box` (which is a dictionary mapping tool names to their corresponding functions) and a `tool_call` from the LLM. The function then executres the appropriate function with the provided arguments from the LLM. Meaning any tool we want to make available to our LLM must be registered in our toolbox.

```python
def tool_execution(tool_box, tool_call):
    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments)

    tool_result = tool_box[function_name](**function_args)
    return tool_result
```

* * *

## 🔁 Building the control loop interaction

Next we build a function that sends the user's question to the LLM along with available tool definitions. If the LLM requests a tool call, we execute it and feed the results back into the context. This cycle repeats until the LLM returns a final reponse without requesting any tools.

Here is summary of the loop:

1.  The LLM receives the *system prompt*, *user question* and available *tool definitions*
    
2.  If the LLM determines it needs external information, it generates a tool call
    
3.  We append the "assistant" message (The LLM), containing the tool call, to the conversation history
    
4.  We execute the requested tool and append the results as a "tool" message to the conversation history
    
5.  The loop continues, sending the updated conversation back to the LLM
    
6.  When the LLM has enough information to answer, it returns a response without tool calls, and we exit the loop
    

```python
from litellm import completion

def simple_agent_loop(system_prompt, question):
    tools = [search_web]
    tool_box = {tool.__name__: tool for tool in tools}
    tool_definitions = [function_to_tool_definition(tool) for tool in tools]

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question}
    ]

    while True:
        response = completion(
            model="gpt-5-mini",
            messages=messages,
            tools=tool_definitions
        )

        assistant_message = response.choices[0].message

        if assistant_message.tool_calls:
            messages.append(assistant_message)
            for tool_call in assistant_message.tool_calls:
                tool_result = tool_execution(tool_box, tool_call)
                messages.append({
                    "role": "tool",
                    "content": str(tool_result),
                    "tool_call_id": tool_call.id
                })
        else:
            return assistant_message.content
```

I have opted to encapsulate the above logic in a `utilities/tool_`[`definition.py`](http://definition.py) file in [my code](https://github.com/rob212/ai-notebook/tree/main/basics/ai-agent-from-scratch/src/utilities/tool_definition.py). This allows me to re-use this code across future agents I make. It exposes the `function_to_tool_definition` and `simple_agent_loop` functions. The code from my `utilities/tool_`[`definition.py`](http://definition.py) can be seen here in it's entirety:

```python
# utilities/tool_definition.py

import inspect
import json
from litellm import completion


def _function_to_input_schema(func) -> dict:
    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
        type(None): "null",
    }

    try:
        signature = inspect.signature(func)
    except ValueError as e:
        raise ValueError(
            f"Failed to get signature for function {func.__name__}: {str(e)}"
        )

    parameters = {}
    for param in signature.parameters.values():
        try:
            param_type = type_map.get(param.annotation, "string")
        except KeyError as e:
            raise KeyError(
                f"Unknown type annotation {param.annotation} for parameter {param.name}: {str(e)}"
            )
        parameters[param.name] = {"type": param_type}

    required = [param.name for param in signature.parameters.values()]

    return {
        "type": "object",
        "properties": parameters,
        "required": required,
    }


def _format_tool_definition(name: str, description: str, parameters: dict) -> dict:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": parameters,
        },
    }


def _tool_execution(tool_box, tool_call):
    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments)

    tool_result = tool_box[function_name](**function_args)
    return tool_result


def function_to_tool_definition(func) -> dict:
    return _format_tool_definition(
        func.__name__, func.__doc__ or "", _function_to_input_schema(func)
    )


def simple_agent_loop(system_prompt: str, question: str, tooling, model: str):
    tools = tooling
    tool_box = {tool.__name__: tool for tool in tools}
    tool_definitions = [function_to_tool_definition(tool) for tool in tools]
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]

    while True:
        response = completion(model=model, messages=messages, tools=tool_definitions)

        assistant_message = response.choices[0].message

        if assistant_message.tool_calls:
            messages.append(assistant_message)
            for tool_call in assistant_message.tool_calls:
                tool_result = _tool_execution(tool_box, tool_call)
                messages.append(
                    {
                        "role": "tool",
                        "content": str(tool_result),
                        "tool_call_id": tool_call.id,
                    }
                )
        else:
            return assistant_message.content, messages
```

Our`simple_agent_loop` returns the final context purely for our learning purposes alongside our LLMs final answer.

* * *

## 🧪 Testing the agent loop

See `/src/agents/agent_3_`[`loop.py`](http://loop.py) for an implementation of the above structured tool definition utilities, agent loop and execution funtionality. Below is this `agent_3_`[`loop.py`](http://loop.py) in it's entirety. Note how it uses our 'simple\_agent\_loop' from `utilities/tool_definition`. This can be run for yourself from the `src` directory with the command:

```shell
uv run python -m agents.agent_3_loop
```

```python
# agents/agent_3_loop.py

import json
import os

from dotenv import find_dotenv, load_dotenv
from tavily import TavilyClient
from tools.calculator import calculator
from utilities.tool_definition import simple_agent_loop

load_dotenv(find_dotenv())

tavily_client = TavilyClient(os.getenv("TAVILY_API_KEY"))

SYSTEM_PROMPT = """ You are a helpful assistant.
Use the search tool when you need current information."""


## Search Web Tool function definition
def search_web(
    query: str,
    max_results: int = 2,
) -> list | str:
    """Search the web for the given query."""
    try:
        response = tavily_client.search(
            query,
            max_results=max_results,
        )
        return response.get("results")
    except Exception as e:
        return f"Error: Search failed - {e}"


## Define our Tools via our utility functions
tools = [search_web, calculator]

QUESTION = "Who won gold medal in the womans curling at 2026 winter olympics?"

# start our agent loop passing the system prompt, user question and list of
# availbale tools to our LLM, in this instace gpt-5-mini
result, context = simple_agent_loop(SYSTEM_PROMPT, QUESTION, tools, "gpt-5-mini")

print(result)
# print out the final context that took place in the agent loop to learn about how the LLM interacted with
# the tools we provided to it.
print(" ------------ context --------------------")
print(json.dumps(context, indent=2, default=str))
```

Note: I have purposefully defined the search\_web function in this agent for step-by-step learning, when in reality we work on a more elegant solution to defining tools later.

Our simple\_agent\_loop takes care of creating tool definitions for our provided tools, in this instance our search\_web function and our calculator function from previous learnings.

The LLM should have identified that it did not know that answer to our users question given the time constraint of it's training data (at the time of writing Feb 23rd 2025, the womens winter Olympics curling final had just been played). The LLM therefore should have reached out to our search\_web tool with appropriate arguements. Pay attention to how many calls the LLM makes to the search\_web function, remember that it is in charge of determining the number of calls and parameters it passes.

* * *

## Summary

Building our web search tool was relatively straight forward thanks to the Tavily client. However, Tavily was designed specifically for LLM applications, making the integration simple. If we were to consider building additional tools that searches your companies Slack workspace, or retrieves files from Google Drive, this begins to add significant complexity and maintenance. APIs evolve, services deprecate endpoints, change response formats and introduce new required parameters.

This problem is where Model Context Protocol (MCP) attempts to provide a solution. MCP is the concept we will explore next.