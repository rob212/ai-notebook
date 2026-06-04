---
title: "🔧 LLM Tools"
seoTitle: "Adding Tools to your AI Agent"
seoDescription: "A blog post for beginners who are learning about what Tools are in the context of AI Agents with examples of how to build them."
datePublished: 2026-06-04T14:22:23.753Z
cuid: cmpzl40ec00061sha0dis05i1
slug: llm-tools
cover: https://cdn.hashnode.com/uploads/covers/6a1ed89dc5484173f87dd5bd/8d3a2158-b380-4232-bb7c-001b800d1507.jpg
tags: ai, python, beginners, ai-tools, ai-agents

---

Despite their impressive capabilities, LLMs have inherent limitations that prevent them from functioning as fully autonomous agents. These limitations fall into three categories: *temporal*, *interaction*, and *functional*.

### 🕰️ Temporal limitation

They cannot access information beyond their training data or retrieve data that changes in real time. This makes them unreliable for tasks requiring current knowledge, such as answering questions about recent events or live market conditions.

### ➡️ Interaction limitation

They cannot directly influence the external world. While they can generate text describing an action, they cannot actually book a flight, send an email, or control a device.

### 🧮 Functional limitations

In specialised domains certain tasks requiring precise computation, code execution, or media generation often exceed what language models can reliably accomplish through text prediction alone.

Tools can address each of these limitations.

**Temporal tools** augment information to bridge the temporal gap by injecting up-to-date knowledge into the agent's context. They can be used to extend the LLM's awareness beyond its training cutoff date. These can include tooling to allow your Agent web access, real-time APIs such as weather or stock prices, or custom databases.

**Action-executing tools** overcome the interaction limitation by enabling agents to affect the real world. Examples include booking systems for hotels and flights, communication tools for emails and calendar management, automation tools for document generation, and IoT controllers for smart devices. These tools trigger Actions and receive Observations in return, forming a feedback loop with the environment.

**Domain-specialised tools** address functional limitations by handling tasks where LLMs fall short. Calculators, code interpreters, format converters, image generators, and voice synthesis engines allow hybrid problem-solving—combining the LLM's reasoning with reliable execution in specialised domains.

Common LLM providers such as OpenAI and Anthropic already offer some tooling, for example OpenAI's web search feature and Anthropic's web search tool. These tools are available for us to use immediately without any development effort. The trade off is that they cannot be easily modified or extended, and they can be changed at the providers discretion. LLM providers will list the available non-custom, tools available to you.

## Custom tools

We are going to focus on building custom tooling for our learning and to provide understanding to help debug and build fully bespoke Agents for our needs. However, it's good to be aware that provider tools exist for rapid prototyping or if they fit your business need.

## How does an LLM use tools?

So how can an LLM, that generates text based on probabilities, actually select and execute a tool? This is made possible by a feature called **Tool Calling**. We are able to define tools via structured descriptions that tell the LLM what tools (functions, APIs or actions) are available, what parameters they expect and what they do. Once the LLM receives this information, it can reason about which tool may be appropriate for a given task and how to use it, purely through text generation. If the LLM decides to use a tool, it generates a tool call; a structured output that includes the name of the tool and the arguments required to invoke it. This tool call is passed to an external executor, which actually runs the tool with the arguments in the real world (i.e. our code).

## How tool calling works

Tool calling is a multi-step process. It starts with the developer sending the users prompt along with tool definitions to the LLM. Note: the LLM itself **does not** execute the tool(s) itself, it generates a textual response indicating which tool (if any) should be called and with what parameters.

Think of the LLM like a mediator between the user prompt and the available tools.

Our code, will then execute the tool identified by the LLM with the parameters provided also by the LLM. Once the tool has executed, the result is returned to the LLM, along with all prior messages, which then interprets the output and continues to conversation, assessing if a final result can be returned or further tools are required.

So within our agent, we must:

1.  Define the tool definitions we will provide to the LLM.
    
2.  Define the actual tool implementation.
    
3.  Provide the LLM with the task to perform and tool definitions from step 1.
    
4.  Build a systems that can execute the tools based on the tool call generated by the LLM.
    
5.  Reflect the execution results back into the LLM's context.
    

* * *

## Step 1: Tool Definitions

We will start by creating a basic calculator tool, with the capability to add, subtract, multiply and divide any two numbers. Let's examine the **structured definition** of our calculator tool. Think of this like the "instruction manual" for the LLM.

*   **"type: function"** - indicates to the LLM that this is a callable tool
    
*   **"name:"** - the tool's identifier that the LLM will use to reference it ("calculator")
    
*   **"description:"** - When and why to use this tool (perform basic arithmetic operations)
    
*   **"parameters:"** - The specification of inputs needed to use the tool
    

```python
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
```

## Step 2: Set up the tool

This is a pure python function that matches the input schema provided in our calculator tool definition. Notice the function name matches that provided to the LLM in the tool definition so the correct function is invoked with the appropriate parameters.

```python
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
```

## Step 3: Executing the tool call

When we call our LLM we provide our tool definitions (calculator) alongside the user's prompt. The LLM decides whether a tool is needed to answer the prompt and if our definition contains an appropriate tool to use. For example, suppose the first prompt asks "What is the capital of Scotland?" it is highly probable the LLM can answer this with a plain text answer from it's training data. However a subsequent prompt of "What is 1234 \* 5678?", the LLM may choose to respond by generating a Tool Call, including the correct operator (multiply) and operands (1234, 5678).

> If you want to skip ahead and see the full example of this in code, you can do so in `agent_2_`[`tools.py`](http://tools.py). I'll break down the steps used to build this for the remainder of this article.

I have created a `prerequisites/03-tools-concepts/tools_concepts.py` file in the accompanying [code repo](https://github.com/rob212/ai-notebook) that captures some of the concepts of tools in isolation. The following snippet of code can be run to query our LLM, with a question that should not require it to select our calculator tool:

```python
## tools_concepts.py

# Calling our LLM with a basic question that it should know the answer to via it's training data and NOT require 
# a tool that we provide. The LLM makes the decision not to call the tool.

from dotenv import load_dotenv, find_dotenv
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
```

The response from the LLM is as follows:

```python
Message(
    content='The capital of Scotland is Edinburgh.',
    role='assistant',
    tool_calls=None,
    function_call=None,
    provider_specific_fields={'refusal': None},
    annotations=[]
)
```

The `tool_calls` is `None` indicating the LLM decided not to use one of our provided tools. On the contrary, the `content` will be `None` and the `tools_call` will be populated if the LLM identifies a tool available to it should be called, in this instance the calculator tool. Lets run the same experiment, but this time with a question that might result in the LLM deciding to use our calculator tool:

```python
# tools_concepts.py
## as before, but this time asking a different question

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
```

This time when we inspect the message response from the LLM, notice that the `content` is `None` indicating the LLM could not answer the question directly, but has responded with a request to call the 'calculator' tool. The LLM has provided the relevant arguments that it was able to determine due to the structured output we provided for our 'calculator' tool.

```python
Message(
    content=None,
    role='assistant',
    tool_calls=[
        ChatCompletionMessageToolCall(
            function=Function(
                arguments='{"operator":"multiply","first_number":1234,"second_number":5678}',
                name='calculator'
            ),
            id='call_mOLPsBCiEUqQAALLZ6rMGHXI',
            type='function'
        )
    ],
    function_call=None,
    provider_specific_fields={'refusal': None},
    annotations=[]
)
```

## Step 4: Executing the tool in our code

It is up to our code to call the 'calculator' function with the parameters provided from the LLM and add this back to the context and inform the LLM of the response.

See excerpt from `agent_2_`[`tools.py`](http://tools.py) :

```python
   if ai_message.tool_calls:
        for tool_call in ai_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            if function_name == "calculator":
                result = calculator(**function_args)
```

We extract 'function\_name' and 'function\_args' from the LLM response and use them to call the corresponding tool function, passing it the arguments.

## Step 5: Reflect the results of the tool back to the LLM

We then pass the results of our tools output (the calculator function) to the LLM. We ensure we append a new message to the conversation (remember LLM's are stateless, so we need to provide the updated context). The new message defines the role of "tool" and includes the output in the content. This is then passed back to the LLM to determine if further tooling is required or there is enough information to merit a final response which will be returned to the users initial prompt.

See excerpt from `agent_2_`[`tools.py`](http://tools.py) :

```python
 messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(result),  # the result of the calculator tool execution
                    }
                )

    final_response = completion(model="gpt-5-mini", messages=messages) # call the LLM with this new context
```

* * *

## Summary

To summarise the journey of the "What is 1234 x 5678?" prompt from the user.

We pass this question along with the calculator tool definition to the LLM. The LLM responds to our Agent stating the calculator tool should be called with the multiply operator and the operands 1234 and 5678. Our Agent calls the calculator function we defined and adds the result to the context and once more calls the LLM with this updated context. The LLM then determines no further tool calls are required and responds with the final answer, our agent can then present this to the user.

The final code for our `agent_2_`[`tools.py`](http://tools.py) is as follows and can be run via the `src` directory via the command:

```shell
uv run python agents.agent_2_tools
```

```python
## agents/agent_2_tools.py

import json

from dotenv import find_dotenv, load_dotenv
from litellm import completion

load_dotenv(find_dotenv())

# Structured definition of the calculator tool. 
# Think of this like the "instruction manual" for the LLM.
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


# Pure python function that matches the input schema provided in our 
# calculator tool definition.
# Notice the function name matches that provided to the LLM in the tool definition so 
# the correct function is invoked with the appropriate parameters
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


if __name__ == "__main__":
    tools = [calculator_tool_definition]
    messages = []

    QUESTION_1 = "What is the capital of Scotland?"
    QUESTION_2 = "What is 1234 x 5678?"

    response_without_tool = completion(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": QUESTION_1}],
        tools=tools,
    )

    print(f"{QUESTION_1}")
    print(
        f"Response from LLM: {response_without_tool.choices[0].message.content or 'No answer from LLM'}"
    )  # The capital of Scotland is Edinburgh.
    print(
        f"Tools LLM decided to use: {response_without_tool.choices[0].message.tool_calls or 'None'}"
    )  # None
    print("\n")

    # update context
    messages.append({"role": "user", "content": QUESTION_1})
    messages.append(
        {
            "role": "assistant",
            "content": response_without_tool.choices[0].message.content,
            "tool_calls": response_without_tool.choices[0].message.tool_calls,
        }
    )

    response_with_tool = completion(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": QUESTION_2}],
        tools=tools,
    )
    print(f"{QUESTION_2}")
    print(
        f"Response from LLM: {response_with_tool.choices[0].message.content or 'No answer from LLM'}"
    )  # None
    print(
        f"Tools LLM decided to use: {response_with_tool.choices[0].message.tool_calls or 'None'}"
    )
    print("\n")
    # [ChatCompletionMessageFunctionToolCall(id='call_viaOEiQJ5VEB9YvKl95qlDjM', function=Function(arguments='{"operator":"multiply","first_number":1234,"second_number":5678}', name='calculator'), type='function')]

    # update context
    messages.append({"role": "user", "content": QUESTION_2})
    ai_message = response_with_tool.choices[0].message
    messages.append(
        {
            "role": "assistant",
            "content": ai_message.content,
            "tool_calls": ai_message.tool_calls,
        }
    )

    if ai_message.tool_calls:
        for tool_call in ai_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            if function_name == "calculator":
                result = calculator(**function_args)

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(result),
                    }
                )

    final_response = completion(model="gpt-5-mini", messages=messages)
    print("all messages (the context):", messages)
    print("\n")
    print("Final Answer:", final_response.choices[0].message.content)
```

* * *

## 🪜 Next steps

We have learned how to define a custom tool in the form of a calculator. Next we will define another custom tool to allow our LLM to access the web, to do so we will leverage a third party library. Let's get started with our Web Search tool