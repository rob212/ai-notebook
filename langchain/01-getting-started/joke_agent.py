import os

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM

load_dotenv()

ollama_api_key = os.getenv("OLLAMA_API_KEY")

# Create components
prompt = PromptTemplate.from_template("Tell me a joke about {topic}")
llm = OllamaLLM(model="llama3.2", api_key=ollama_api_key)
output_parser = StrOutputParser()

# Chain them together using LCEL
chain = prompt | llm | output_parser

# Execute the workflow with a single call
result = chain.invoke({"topic": "programming"})
print(result)
