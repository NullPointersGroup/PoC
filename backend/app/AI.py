from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain.tools import tool



model = ChatOpenAI(
    model="gpt-5",
    temperature=0.1,
    max_tokens=1000,
    timeout=30
    # ... (other params)
)
agent = create_agent(model)