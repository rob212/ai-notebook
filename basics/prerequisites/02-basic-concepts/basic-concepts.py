## Simple call through to OpenAI via the openai python library


import os

from dotenv import find_dotenv, load_dotenv
from openai import OpenAI

load_dotenv(find_dotenv())
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


response = client.chat.completions.create(
    model="gpt-5-mini",
    messages=[{"role": "user", "content": "My name is Rob"}]
)
print(response.choices[0].message.content)

## --------------------------------------------------------------

## Introducing liteLLM as a wrapper around or LLM provider call 

from litellm import completion
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

## Basic call to LLM via LiteLLM wrapper

response1 = completion(
    model="gpt-5-mini", messages=[{"role": "user", "content": "My name is Rob"}]
)
print(response1.choices[0].message.content)

## ---------------------------------------------------------------

## LLMs are stateless, therefore you need tp accumulate conversation content an provide it
## to subsequent LLM prompts

messages = []

# First Exchange
messages.append({"role": "user", "content": "My name is Rob."})
response2 = completion(model="gpt-5-mini", messages=messages)
assistant_message1 = response2.choices[0].message.content
messages.append({"role": "assistant", "content": assistant_message1})
print(assistant_message1)

# Second Exchange - includes previous conversation history
messages.append({"role": "user", "content": "What is my name?"})
response3 = completion(model="gpt-5-mini", messages=messages)
assistant_message2 = response3.choices[0].message.content
print(assistant_message2)


## ---------------------------------------------------------------

## Structured Output - modern LLM support Structured Output which allows you to
## specifiy the LLM's response format, e.g. JSON.
## Here we use Pydantic (Python library for data validation) to define our desired data structure
## that we want the LLM to adhere to in it's response. In this case the LLM should respond
## in a JSON format.

from litellm import completion
from pydantic import BaseModel


class ExtractedInfo(BaseModel):
    name: str
    email: str
    phone: str | None = None


response4 = completion(
    model="gpt-5-mini",
    messages=[
        {
            "role": "user",
            "content": "My name is John Smith, my email is john@example.com, and my phone number is 07712345678",
        }
    ],
    response_format=ExtractedInfo,
)

result = response4.choices[0].message.content
print(result)


## ---------------------------------------------------------------

## Asynchronous calls - You may which to process multiple LLM requests simultaneously.
## Sending multiple requests sequentially will increase the total execution time. We can handle
## asynchronous programming with async/await syntax and te asyncio library. LiteLLM supports
## this through the `acompletion` function

## When sending many requests simultaneously, two issues can arise: rate limits from the API provider
## and transient failures from network issues or server overload. LiteLLM's `num_retries` parameter
## handles transient failures with automatice exponential backoff. For rate limiting we can use Python's
## asyncio.Semaphore to limit how many requests run concurrently. By wrapping the `acompletion` call
## we can ensure that no matter how many tasks are runningm only a limited number of actual API calls happen
## at once.

import asyncio

from litellm import acompletion

# Limit to 10 concurrent requests
semaphore = asyncio.Semaphore(10)


async def call_llm(prompt: str) -> str:
    """LLM call with rate limiting and automatic retry."""
    async with semaphore:
        response = await acompletion(
            model="gpt-5-mini",
            messages=[{"role": "user", "content": prompt}],
            num_retries=3,  # Automatic rety with exponential backoff
        )
        return response.choices[0].message.content


# Even if we had 100 prompts, only 10 API calls run at a time
prompts = [
    "What is 2 + 2?",
    "What is the capital of Japan?",
    "Who wrote Romeo and Juliet?",
]

# Execute all requests concurrently
## `return_exceptions=True` argument prevents a single failure from cancelling all other tasks,
## Instead, exceptions are returned as values in the results list, allowing us to handle failures gracefully
## while still getting results from successful calls.
tasks = [call_llm(p) for p in prompts]
results = await asyncio.gather(*tasks, return_exceptions=True)

for prompt, result in zip(prompts, results):
    print(f"Q: {prompt}")
    print(f"A: {result}\n")