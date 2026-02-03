import requests
import os
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from typing import Any

BASE_URL: str = "http://localhost:8000/ai"

load_dotenv()

@tool
def query_db(info: str) -> str:
    """
    Interroga il database per ottenere informazioni.
    
    Categorie disponibili:
    - 'utenti': ritorna tutti gli utenti del sistema
    - 'articoli': ritorna tutti gli articoli/prodotti disponibili
    
    Args:
        categoria: deve essere esattamente 'utenti' o 'articoli'
    
    Esempio: query_db('utenti') oppure query_db('articoli')
    """
    response = requests.get(f"{BASE_URL}/{info}", timeout=10.0)
    response.raise_for_status()
    return str(response.text)

system_prompt: str = """\
Possiedi l'accesso al database e in caso ti serva puoi effettuare query con la funzione query_db
"""

llm = ChatOpenAI(model="gpt-4", temperature=0, api_key=os.getenv("OPENAI_API_KEY")) #type: ignore

# Crea l'agente con create_agent
agent = create_agent( #type: ignore
    llm,
    tools=[query_db],
    system_prompt=system_prompt
)

# Usa l'agente
result: (dict[str, Any] | Any) = agent.invoke({
    "messages": [{"role": "user", "content": "Dammi le info sugli 'articoli'"}]
})

print(result["messages"][-1].content)