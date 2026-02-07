import os
from dotenv import load_dotenv
from typing import Dict, Any, List

from .database import get_cart, get_session, get_all_anagrafica_articolo
from .models import *
from openai import OpenAI
import faiss #type: ignore
import numpy as np

from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain_openai import ChatOpenAI
from sentence_transformers import SentenceTransformer #type: ignore

_transformer_model = SentenceTransformer('all-MiniLM-L6-v2')


load_dotenv()

_OPEN_API_KEY = os.getenv("OPENAI_API_KEY")
_DB = SQLDatabase.from_uri(os.getenv("DATABASE_URL")) #type: ignore

_model = ChatOpenAI(model="gpt-4", temperature=0.1, api_key=_OPEN_API_KEY) #type: ignore

_cart_texts = [
    (el.prodotto, el.des_art) 
    for el in get_cart(next(get_session())) 
    if el.des_art is not None
]

_catalogo_texts = [
    (el.cod_art, el.des_art) 
    for el in get_all_anagrafica_articolo(next(get_session()))
    if el.des_art is not None
]

from typing import List, Dict, Tuple, Any
import numpy as np
import numpy.typing as npt

def _trova_vicini(
    distances: npt.NDArray[np.float32], 
    indices: npt.NDArray[np.int64], 
    texts: List[Tuple[str, str]], 
    threshold: float
) -> List[Dict[str, str]]:
    res: List[Dict[str, str]] = []
    for dist, indx in zip(distances, indices):
        for d, i in zip(dist, indx):
            if d <= threshold:
                cod_art, des_art = texts[i]
                res.append({"cod_art": cod_art, "des_art": des_art})
            else:
                break
    return res

def cerca_in_carrello(prodotto: str) -> List[Dict[str, str]] | str:
    """Cerca un prodotto nel carrello e restituisce i prodotti più vicini trovati. """
    # Il threshold deve essere un valore compreso tra 0.55 e 1.5 in base a quanto specifico è il prodotto. Con prodotto specifico intendo quanto è argomentato, per esempio 'acqua' è il minimo della specificità, mentre 'acqua uliveto pet 150'
    # testi del carrello
    cart_des = [el[1] for el in _cart_texts]

    # embedding del carrello → (N, 384)
    vectors = _transformer_model.encode(
        cart_des,
        convert_to_numpy=True,
        normalize_embeddings=True
    ).astype(np.float32)

    # inizializza FAISS
    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)

    # embedding della query → (1, 384)
    query_vector = _transformer_model.encode(
        prodotto,
        convert_to_numpy=True,
        normalize_embeddings=True
    ).astype(np.float32)

    if query_vector.ndim == 1:
        query_vector = query_vector.reshape(1, -1)

    # search
    k = 5
    distances, indices = index.search(query_vector, k)

    # soglie (ok tenerle così)
    parole = prodotto.strip().split(" ")
    if len(parole) == 1:
        threshold = 1.4
    elif len(parole) == 2:
        threshold = 0.85
    else:
        threshold = 0.55

    vicini = _trova_vicini(distances, indices, _cart_texts, threshold)

    print(indices, distances)

    if vicini:
        return vicini

    return "Non c'è il prodotto richiesto nel carrello"

print(cerca_in_carrello("acqua"))

# creazione statica, dato che il catalogo difficilmente cambia è più efficiente crearlo una sola volta
# la creazione dell'index è abbastanza, per questo lo faccio

catalogo_des = [el[1] for el in _catalogo_texts]
vectors = _transformer_model.encode(
    catalogo_des,
    convert_to_numpy=True,
    normalize_embeddings=True
).astype(np.float32)

# inizializza FAISS
dim = vectors.shape[1]
_catalog_index = faiss.IndexFlatL2(dim)
_catalog_index.add(vectors)

def cerca_in_catalogo(prodotto: str) -> List[Dict[str, str]] | str:
    """Cerca un prodotto nel catalogo e restituisce i prodotti più vicini trovati. """
    query_vector = _transformer_model.encode(
        prodotto,
        convert_to_numpy=True,
        normalize_embeddings=True
    ).astype(np.float32)

    if query_vector.ndim == 1:
        query_vector = query_vector.reshape(1, -1)

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
tools.append(cerca_in_carrello) #type: ignore
tools.append(cerca_in_catalogo) #type: ignore

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