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