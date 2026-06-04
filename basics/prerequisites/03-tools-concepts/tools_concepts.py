# %%


# Concepts used in the [Tools](tool-definitions) Section of our learning.

## -----------------------------------------------------------------------

# Calling our LLM with a basic question that it should know the answer to via it's training data and NOT require 
# a tool that we provide. The LLM makes the decision not to call the tool.

from dotenv import find_dotenv, load_dotenv
from litellm import completion

load_dotenv(find_dotenv())

# Structured definition of the calculator tool. Think of this like the "instruction manual" for the LLM.
# "type: function" indicates to the LLM that this is a callable tool
# "name:" the tool's identifier that the LLM will use to reference it ("calculator")
# "description:" When and why to use this tool (perform basic arithmetic operations)
# "parameters:" The specification of inputs needed to use the tool
calculator_tool_definition = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "Perform basic arithmetic operations between two numbers.",
        "parameters": {
            "type": "object",
            "properties": {
                "operator": {
                    "type": "string",
                    "description": "Arithmetic operation to perform",
                    "enum": ["add", "subtract", "multiply", "divide"],
                },
                "first_number": {
                    "type": "number",
                    "description": "First number for the calculation",
                },
                "second_number": {
                    "type": "number",
                    "description": "Second number for the calculation",
                },
            },
            "required": ["operator", "first_number", "second_number"],
        },
    },
}


# Pure python function that matches the input schema provided in our calculator tool definition
# Notice the function name matches that provided to the LLM in the tool definition so the correct
# function is invoked with the appropriate parameters
def calculator(operator: str, first_number: float, second_number: float) -> float:
    if operator == "add":
        return first_number + second_number
    elif operator == "subtract":
        return first_number - second_number
    elif operator == "multiply":
        return first_number * second_number
    elif operator == "divide":
        if second_number == 0:
            raise ValueError("Cannot divide by zero")
        return first_number / second_number
    else:
        raise ValueError(f"Unsupported operator: {operator}")


tools = [calculator_tool_definition]

QUESTION = "What is the capital of Scotland?"
  

response_without_tool = completion(
    model="gpt-5-mini",
    messages=[{"role": "user", "content": QUESTION}],
    tools=tools,
)

print(f"{QUESTION}")
print(
    f"Response from LLM: {response_without_tool.choices[0].message}"
)  

# The 'content' of the LLM response contains the answer "The capital of Scotland is Edinburgh".
# The 'tools_call' is None, indicating the LLM has decided not to use any of the tools we provided.


## ------------------------------------------------------------------

# Calling our LLM with a question that might require using the tool we provided.
# The code from above is exactly the same, the only difference is the question we ask the LLM. 

from dotenv import find_dotenv, load_dotenv
from litellm import completion

load_dotenv(find_dotenv())

# Structured definition of the calculator tool. Think of this like the "instruction manual" for the LLM.
# "type: function" indicates to the LLM that this is a callable tool
# "name:" the tool's identifier that the LLM will use to reference it ("calculator")
# "description:" When and why to use this tool (perform basic arithmetic operations)
# "parameters:" The specification of inputs needed to use the tool
calculator_tool_definition = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "Perform basic arithmetic operations between two numbers.",
        "parameters": {
            "type": "object",
            "properties": {
                "operator": {
                    "type": "string",
                    "description": "Arithmetic operation to perform",
                    "enum": ["add", "subtract", "multiply", "divide"],
                },
                "first_number": {
                    "type": "number",
                    "description": "First number for the calculation",
                },
                "second_number": {
                    "type": "number",
                    "description": "Second number for the calculation",
                },
            },
            "required": ["operator", "first_number", "second_number"],
        },
    },
}


# Pure python function that matches the input schema provided in our calculator tool definition
# Notice the function name matches that provided to the LLM in the tool definition so the correct
# function is invoked with the appropriate parameters
def calculator(operator: str, first_number: float, second_number: float) -> float:
    if operator == "add":
        return first_number + second_number
    elif operator == "subtract":
        return first_number - second_number
    elif operator == "multiply":
        return first_number * second_number
    elif operator == "divide":
        if second_number == 0:
            raise ValueError("Cannot divide by zero")
        return first_number / second_number
    else:
        raise ValueError(f"Unsupported operator: {operator}")


tools = [calculator_tool_definition]

QUESTION_2 = "What is 1234 x 5678?"
  

response_with_tool = completion(
    model="gpt-5-mini",
    messages=[{"role": "user", "content": QUESTION_2}],
    tools=tools,
)

print(f"{QUESTION_2}")
print(
    f"Response from LLM: {response_with_tool.choices[0].message}"
)  

# This time our LLM opts to use our calulator tool. 

## ------------------------------------------------------------------


# Implementing a web search tool.
# An essential capability for a research agent is the ability to access the web for up to date information that may not
# be part of our LLM's training data.

# we will achieve this via [Tavily](https://www.tavily.com/). Tavily allows for up to 1,000 free API calls per month.

import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

tavily_client = TavilyClient(os.getenv("TAVILY_API_KEY"))


def search_web(query: str, max_results: int = 2) -> list:
    response = tavily_client.search(query, max_results=max_results)
    return response.get("results")


search_web("Kipchoge's marathon world record")


## -------------------------------------------------------

# Expanding a web search with additional search options and basic error handling


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
        return f"Error: Search failed - {e}"


results = search_web(
    query="Kipchoge's marathon world record",
    topic="news",
    time_range="year",
    country="united kingdom",
)

print(results)

## -------------------------------------------------------------

# Python `inspect` in order to extract a functions details as a building block for us
# creating a utility function that automatically converts a Python function into a tool
# definition

import inspect


def example_tool(input_1: str, input_2: int = 1):
    """docstring for example_tool"""
    return


print(f"function name: {example_tool.__name__}")
print(f"function docstring: {example_tool.__doc__}")
print(f"function signature: {inspect.signature(example_tool)}")


## -------------------------------------------------------------

# Our utility function to automatically define out Structured Output tool definition for a given
# function is as follows.


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
        func.__name__, func.__doc__ or "", function_to_input_schema(func)
    )


# We test our new `function_to_tool_definition()` with our `search_web` function.

search_tool_definition = function_to_tool_definition(search_web)
print(search_tool_definition)


# This results in the following Python dictionary
# {'type': 'function', 'function': {'name': 'search_web', 'description': 'Search the web for the given query.', 'parameters': {'type': 'object', 'properties': {'query': {'type': 'string'}, 'max_results': {'type': 'integer'}, 'topic': {'type': 'string'}, 'time_range': {'type': 'string'}, 'country': {'type': 'string'}}, 'required': ['query', 'max_results', 'topic', 'time_range', 'country']}}}


## -----------------------------------------