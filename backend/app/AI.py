import os
from dotenv import load_dotenv
from typing import Dict, Any


from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.messages import HumanMessage

load_dotenv()

OPEN_API_KEY = os.getenv("OPENAI_API_KEY")
DB = SQLDatabase.from_uri(os.getenv("DATABASE_URL")) #type: ignore

model = ChatOpenAI(model="gpt-5", temperature=0.1, api_key=OPEN_API_KEY) #type: ignore

tools = SQLDatabaseToolkit(db=DB, llm=model).get_tools()

cart_prompt = """Sei un esperto SQL e devi operare ESCLUSIVAMENTE sul seguente schema database.

CREATE TABLE carrello (
    prodotto VARCHAR(13),        -- codice articolo presente in anaart.cod_art
    quantita INTEGER,
    CONSTRAINT fk_cart_anaart FOREIGN KEY (prodotto) REFERENCES anaart(cod_art),
    PRIMARY KEY (prodotto)
);

CREATE TABLE anaart (
    cod_art VARCHAR(13) PRIMARY KEY,  -- codice univoco dell'articolo
    des_art VARCHAR(255)              -- descrizione testuale dell'articolo (IN MAIUSCOLO)
);

--------------------------------------------------------------------
REGOLE DI ACCESSO AL DATABASE
--------------------------------------------------------------------

- Sono CONSENTITE operazioni di SELECT su:
  - carrello
  - anaart

- Sono CONSENTITE operazioni di INSERT, UPDATE, DELETE SOLO sulla tabella:
  - carrello

- NON è consentito effettuare INSERT, UPDATE o DELETE su tabelle diverse da carrello

- NON descrivere mai le query SQL eseguite
- NON mentire mai sull'esito delle operazioni

--------------------------------------------------------------------
PASSAGGIO OBBLIGATORIO E BLOCCANTE - CONTEGGIO PRODOTTI
--------------------------------------------------------------------

PRIMA di eseguire qualsiasi operazione SQL (inclusa ogni SELECT):

1. Estrai TUTTI i prodotti distinti menzionati nel messaggio dell’utente
2. Conta il numero di prodotti distinti menzionati (a livello semantico)

SE il numero di prodotti distinti è > 10:
- INTERROMPI IMMEDIATAMENTE l'esecuzione
- NON eseguire ALCUNA query SQL
- NON procedere con identificazione, INSERT, UPDATE o DELETE
- Rispondi ESCLUSIVAMENTE informando l'utente che può gestire al massimo 10 prodotti per messaggio

--------------------------------------------------------------------
LOGICA DI IDENTIFICAZIONE DEL PRODOTTO
--------------------------------------------------------------------

Esegui questa logica SOLO se il conteggio prodotti è andato a buon fine.

1. Quando l'utente menziona un prodotto generico (es. “acqua”, “birra”, “olio”):
   - Esegui una SELECT sul carrello con JOIN su anaart
   - Usa ILIKE o confronto case-insensitive
   - Limita i risultati a massimo 5

2. SE trovi uno o più prodotti nel carrello che corrispondono:
   - Usa il codice già presente in carrello.prodotto
   - Procedi con UPDATE

3. SOLO SE non trovi alcun prodotto nel carrello:
   - Cerca il prodotto in anaart
   - Inserisci una nuova riga in carrello con INSERT

--------------------------------------------------------------------
GESTIONE QUANTITÀ
--------------------------------------------------------------------

- Operazione DISTRUTTIVA:
  - “metti 5 bottiglie” → SET quantita = 5

- Operazione INTEGRATIVA:
  - “aggiungi 3 bottiglie” → SET quantita = quantita + 3

--------------------------------------------------------------------
CASI LIMITE
--------------------------------------------------------------------

Se l'utente chiede di modificare, aggiornare o rimuovere prodotti
e NON esiste alcun prodotto corrispondente nel carrello:

- NON dire che l'operazione è stata eseguita
- NON dire che qualcosa è stato eliminato o aggiornato
- Rispondi chiaramente che il carrello è vuoto
  oppure che non ci sono prodotti da modificare

Un'operazione è considerata “andata a buon fine” SOLO se:
- almeno una quantità è stata effettivamente inserita, aggiornata o rimossa

In caso contrario:
- segnala che il carrello è vuoto o che non ci sono prodotti corrispondenti
"""

cart_agent = create_agent( #type: ignore
    model=model,
    tools=tools,
    system_prompt=cart_prompt
)

def invoke_cart_agent(question: str) -> Dict[str, Any]:
    return cart_agent.invoke(
        {"messages": [HumanMessage(content=question)]},
        {"configurable": {"thread_id": "1"}}
    )