import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import OpenAI

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# setup Model
llm = OpenAI(api_key=openai_api_key, model="gpt-5.4-nano")

messages = [
    SystemMessage(content="You are a helpful programming assistant."),
    HumanMessage(content="Write a short Python function to calculate percentage of a given number.")
]

# call the Model
result = llm.invoke(messages)


print(result)

