from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from typing import Any

model = ChatOpenAI(
    model="gpt-5",
    temperature=0.1,
    model_kwargs={"max_tokens": 1000},
    timeout=30
)
agent: Any = create_agent(model)