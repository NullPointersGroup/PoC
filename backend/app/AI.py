import os
from dotenv import load_dotenv
from typing import Dict, Any, List, Tuple

from .database import get_cart, get_session, get_all_anagrafica_articolo
from .models import *
from openai import OpenAI
import faiss #type: ignore
import numpy as np
import numpy.typing as npt

from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from sentence_transformers import SentenceTransformer #type: ignore

_transformer_model = SentenceTransformer('all-MiniLM-L6-v2')


load_dotenv()

_OPEN_API_KEY = os.getenv("OPENAI_API_KEY")
_DB = SQLDatabase.from_uri(os.getenv("DATABASE_URL")) #type: ignore

_model = ChatOpenAI(model="gpt-5", temperature=0.1, api_key=_OPEN_API_KEY) #type: ignore

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

@tool(description="Cerca un prodotto nel carrello e restituisce i prodotti più vicini trovati")
def cerca_in_carrello(prodotto: str) -> List[Dict[str, str]] | str:
    # Il threshold deve essere un valore compreso tra 0.55 e 1.5 in base alla specificità del prodotto
    
    if not _cart_texts:
        return []

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

    # soglie
    parole = prodotto.strip().split(" ")
    if len(parole) == 1:
        threshold = 1.4
    elif len(parole) == 2:
        threshold = 0.85
    else:
        threshold = 0.55

    vicini = _trova_vicini(distances, indices, _cart_texts, threshold)

    if vicini:
        return vicini

    return []

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

@tool(description="Cerca un prodotto nel catalogo e restituisce i prodotti più vicini trovati")
def cerca_in_catalogo(prodotto: str) -> List[Dict[str, str]]:
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
    
    # restituisce sempre lista; anche se non trova nulla, ritorna []
    return vicini

tools = SQLDatabaseToolkit(db=_DB, llm=_model).get_tools()
tools.append(cerca_in_carrello)
tools.append(cerca_in_catalogo)

cart_prompt = """
Sei un assistente SQL esperto. Devi generare query **solo** per aggiornare o fare SELECT sulla tabella "carrello". 
Non inventare codici prodotto: usa esclusivamente i codici restituiti dai tool.

Nel caso di testo non interpretabile, scrivi esattamente "Non ho capito la richiesta" e salta i passaggi successivi.

Tool disponibili:

- cerca_in_carrello(prodotto: str) → restituisce lista di prodotti trovati nel carrello
- cerca_in_catalogo(prodotto: str) → restituisce lista di prodotti trovati nel catalogo

Logica da seguire:

0. - Non descrivere né mostrare la query SQL né il processo interno.
   - È vietato usare futuro, intenzioni, promesse, spiegazioni di processo o frasi preliminari.
   - Ogni risposta deve descrivere esclusivamente lo stato finale già avvenuto.
   - Qualsiasi risposta che non sia un esito finale è da considerarsi non valida.

1. Estrai tutti i prodotti menzionati dall’utente.  
   - Se ci sono più di 10 prodotti distinti, rispondi solo:  
     "Puoi gestire al massimo 10 prodotti per messaggio."  
     e interrompi l’esecuzione.
   - Se ti chiede di fare vedere i prodotti del carrello, mostraglieli tutti e non guardare i passi successivi.
   - Rimozione di tutti gli articoli (regola obbligatoria)
   - Alla richiesta di rimozione totale:

    Esegui una SELECT sul carrello.

    Se e solo se la SELECT restituisce almeno una riga, è consentito:

    eseguire DELETE

    rispondere:
    Tutti i prodotti presenti nel carrello sono stati rimossi correttamente.

    Se la SELECT restituisce zero righe, è consentito solo:

    rispondere:
    Il carrello è vuoto. Nessun articolo è stato rimosso.

    Qualsiasi risposta di successo senza una SELECT con righe > 0 è non valida.

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