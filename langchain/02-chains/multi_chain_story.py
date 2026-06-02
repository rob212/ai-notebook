import os

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

"""
Multi-chain story generator

1. Generate content with one LLM call.
2. Feed that content into a second LLM call.
3. Preserve and transform data throughout the chain.
"""

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize LLM
llm = ChatOpenAI(api_key=openai_api_key, model="gpt-4o-mini")


# First chain
story_prompt = PromptTemplate.from_template("Write a short story about {topic}")
story_chain = story_prompt | llm | StrOutputParser()

# Second chain - analyzes the story
