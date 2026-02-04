import os
from dotenv import load_dotenv


from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.messages import HumanMessage

load_dotenv()

OPEN_API_KEY = os.getenv("OPENAI_API_KEY")
DB = SQLDatabase.from_uri(os.getenv("DATABASE_URL"))

model = ChatOpenAI(model="gpt-4o-mini", temperature=0.1, api_key=OPEN_API_KEY) #type: ignore

tools = SQLDatabaseToolkit(db=DB, llm=model).get_tools()


system_prompt = """
You are a SQL expert. Use this exact database schema:


IMPORTANT RULES:
- Write SQL queries directly using the schema above
- DO NOT list tables with sql_db_list_tables
- DO NOT check schema with sql_db_schema
- DO NOT use sql_db_query_checker
- Execute queries immediately with sql_db_query
- Limit results to 5 unless specified

Respond in Italian.
"""

agent = create_agent(
    model=model,
    tools=tools,
    system_prompt=system_prompt,
)


def invoke_agent(question: str):
    return agent.invoke({
        "messages": [HumanMessage(content=question)],
    }, {
        "configurable": {"thread_id": "1"}
    })
