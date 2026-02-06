import os
from dotenv import load_dotenv
from typing import Dict, Any

from .database import get_cart, get_session, get_all_anagrafica_articolo
from .models import *
from openai import OpenAI
import faiss
import numpy as np

from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain.tools import tool


load_dotenv()

_OPEN_API_KEY = os.getenv("OPENAI_API_KEY")
_DB = SQLDatabase.from_uri(os.getenv("DATABASE_URL")) #type: ignore

_model = ChatOpenAI(model="gpt-4", temperature=0.1, api_key=_OPEN_API_KEY) #type: ignore
_TRANSALATOR_MODEL = "text-embedding-3-large" #large pk prodotti molto simili ed è più facile da gestire le ambiguità

_cart_texts = [(el.prodotto, el.des_art) for el in get_cart(next(get_session()))]

_catalogo_texts = [ (el.cod_art, el.des_art) for el in get_all_anagrafica_articolo(next(get_session()))]
_client = OpenAI()

def _trova_vicini(distances, indices, texts, threshold):
    res = []
    for dist, indx in zip(distances, indices):
        for d, i in zip(dist, indx):
            if d <= threshold:
                cod_art, des_art = texts[i]
                res.append({"cod_art": cod_art, "des_art": des_art})
            else:
                break
    return res

@tool
def cerca_in_carrello(prodotto: str, threshold: float):
    """Cerca un prodotto nel carrello e restituisce i prodotti più vicini trovati.  Il threshold deve essere un valore compreso tra 0.55 e 1.5 in base a quanto specifico è il prodotto. Con prodotto specifico intendo quanto è argomentato, per esempio 'acqua' è il minimo della specificità, mentre 'acqua uliveto pet 150'"""
    cart_des = [el[1] for el in _cart_texts]
    embeddings_response = _client.embeddings.create(
        model= _TRANSALATOR_MODEL,
        input= cart_des
    )

    # estrai vettori in formato numpy array float32 (FAISS richiede float32)
    vectors = np.array([d.embedding for d in embeddings_response.data], dtype=np.float32)


    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)

    index.add(vectors)

    query_embedding = _client.embeddings.create(
        model= _TRANSALATOR_MODEL,
        input=prodotto
    )

    query_vector = np.array([query_embedding.data[0].embedding], dtype=np.float32)

    k = 5
    distances, indices = index.search(query_vector, k)

    parole = prodotto.strip().split(" ")
    if len(parole) == 1:
        threshold = 1.4
    elif len(parole) == 2:
        threshold = 0.85
    else:
        threshold = 0.55
    

    vicini = _trova_vicini(distances, indices, _cart_texts, threshold)
    print(indices, distances)
    if len(vicini) > 0:
        return vicini
    return "Non c'è il prodotto richiesto nel carrello"


# creazione statica, dato che il catalogo difficilmente cambia è più efficiente crearlo una sola volta
# la creazione dell'index è abbastanza, per questo lo faccio
_batch_size = 50  # 50 testi per batch, ridurre se rete lenta
_all_vectors = []

for i in range(0, len(_catalogo_texts), _batch_size):
    _batch = _catalogo_texts[i:i+_batch_size]
    _testi = [el[1] for el in _batch]
    _res = _client.embeddings.create(
        model= _TRANSALATOR_MODEL,
        input=_testi
    )
    # estrai i vettori e aggiungi a lista
    _all_vectors.extend([d.embedding for d in _res.data])

_vectors = np.array(_all_vectors, dtype=np.float32)

_dim = _vectors.shape[1]
_catalog_index = faiss.IndexFlatL2(_dim)
_catalog_index.add(_vectors)

@tool
def cerca_in_catalogo(prodotto: str):
    """Cerca un prodotto nel catalogo e restituisce i prodotti più vicini trovati. """
    query_embedding = _client.embeddings.create(
        model=_TRANSALATOR_MODEL,
        input=prodotto
    )
    query_vector = np.array([query_embedding.data[0].embedding], dtype=np.float32)

    k = 5
    distances, indices = _catalog_index.search(query_vector, k)

    parole = prodotto.strip().split(" ")
    if len(parole) == 1:
        threshold = 1.4
    elif len(parole) == 2:
        threshold = 0.85
    else:
        threshold = 0.55

    vicini = _trova_vicini(distances, indices, _catalogo_texts, threshold)
    if len(vicini) > 0:
        return vicini
    return "Non c'è il prodotto richiesto nel carrello"

tools = SQLDatabaseToolkit(db=_DB, llm=_model).get_tools()
tools.append(cerca_in_carrello)
tools.append(cerca_in_catalogo)

cart_prompt = """
Sei un assistente SQL esperto. Devi generare query **solo** per aggiornare la tabella "carrello". 
Non inventare codici prodotto: usa esclusivamente i codici restituiti dai tool.

Tool disponibili:

- cerca_in_carrello(prodotto: str) → restituisce lista di prodotti trovati nel carrello
- cerca_in_catalogo(prodotto: str) → restituisce lista di prodotti trovati nel catalogo

Logica da seguire:

1. Estrai tutti i prodotti menzionati dall’utente.  
   - Se ci sono più di 10 prodotti distinti, rispondi solo:  
     "Puoi gestire al massimo 10 prodotti per messaggio."  
     e interrompi l’esecuzione.

2. Per ciascun prodotto menzionato:

   a. Chiama `cerca_in_carrello(prodotto)`.  
      - Se trova uno o più match:  
        - Se c’è un solo match sicuro, genera **UPDATE** o **DELETE** usando i codici restituiti.  
          - "metti X" → `SET quantita = X`  
          - "aggiungi X" → `SET quantita = quantita + X`  
          - "rimuovi" → elimina il prodotto dal carrello  
        - Se ci sono più match possibili per lo stesso prodotto, segnala all’utente e attendi conferma prima di generare la query.
      
      - Se non trova nulla nel carrello:  
        - Chiama `cerca_in_catalogo(prodotto)`.  
        - Se trova uno o più match sicuri, genera **INSERT** nel carrello con la quantità indicata.  
        - Se ci sono più match possibili, segnala all’utente e attendi conferma prima di generare la query.

3. Non fare mai UPDATE, INSERT o DELETE su altre tabelle.

4. Risposta all’utente:  
   - Indica solo l’esito finale: prodotto aggiornato, inserito o rimosso.  
   - Non descrivere né mostrare la query SQL né il processo interno.

"""



cart_agent = create_agent( #type: ignore
    model=_model,
    tools=tools,
    system_prompt=cart_prompt
)

def invoke_cart_agent(question: str) -> Dict[str, Any]:
    return cart_agent.invoke(
        {"messages": [HumanMessage(content=question)]},
        {"configurable": {"thread_id": "1"}}
    )