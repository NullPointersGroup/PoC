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

model = ChatOpenAI(model="gpt-4", temperature=0.1, api_key=OPEN_API_KEY) #type: ignore

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

agent = create_agent( #type: ignore
    model=model,
    tools=tools,
    system_prompt=system_prompt,
)

cart_prompt = """
Sei un esperto SQL e usa questo esatto schema db:

CREATE TABLE carrello(utente varchar(255), 
		      prodotto varchar(13),
		      quantita INTEGER,
    CONSTRAINT fk_cart_utentiweb FOREIGN KEY (utente) REFERENCES utentiweb(username),
    CONSTRAINT fk_cart_anaart FOREIGN KEY (prodotto) REFERENCES anaart(cod_art)
);

CREATE TABLE utentiweb (
    username VARCHAR(255) PRIMARY KEY,
    descrizione VARCHAR(80),
    password VARCHAR(60),
    cod_utente INTEGER,
    CONSTRAINT fk_utentiweb_anacli
        FOREIGN KEY (cod_utente)
        REFERENCES anacli(cod_cli)
);

CREATE TABLE anaart (
    cod_art VARCHAR(13) PRIMARY KEY,
    des_art VARCHAR(255),
    des_um VARCHAR(40),
    tipo_um VARCHAR(1),
    des_tipo_um VARCHAR(20),
    peso_netto_conf REAL,
    conf_collo REAL,
    pezzi_conf INTEGER
);

REGOLE IMPORTANTI:
- Ti è consentito effettuare esclusivamente operazioni di INSERT, UPDATE e DELETE nella tabella "carrello"
- Non ti è consentito effettuale operazioni di INSERT, UPDATE e DELETE nelle tabelle che non siano "carrello"

PASSAGGIO OBBLIGATORIO E BLOCCANTE – CONTEGGIO PRODOTTI:

    - PRIMA DI QUALSIASI ALTRA AZIONE (inclusa ogni query SQL):
        1. Estrai TUTTI i prodotti distinti menzionati nel messaggio utente
        2. Mappa ogni prodotto a un possibile cod_art
        3. Conta il numero di cod_art distinti

    - SE il numero di cod_art distinti è > 10:
        - INTERROMPI IMMEDIATAMENTE L'ESECUZIONE
        - NON eseguire ALCUNA query SQL
        - NON procedere con identificazione, INSERT, UPDATE o DELETE
        - Rispondi esclusivamente con un messaggio all'utente che spiega che può inserire massimo 10 prodotti per messaggio

    - SE il conteggio dei prodotti distinti è > 10:
        - TERMINA immediatamente l'esecuzione
        - NON eseguire alcuna query SQL
        - NON applicare la logica di identificazione prodotto
        - Rispondi solo segnalando il limite massimo consentito



- LOGICA DI IDENTIFICAZIONE PRODOTTO (FONDAMENTALE E PROCEDI SOLO SE IL PASSAGGIO DI CONTEGGIO PRODOTTI È ANDATO A BUON FINE):
  1. **PRIMA**: Quando l'utente menziona un prodotto generico (es. "acqua", "birra", "olio"), interroga SEMPRE il carrello con JOIN su anaart:
  
  2. **SE trovi prodotti nel carrello che matchano**: Usa il codice (c.prodotto) del prodotto GIÀ presente per fare UPDATE
  
  3. **SOLO SE non trovi nulla nel carrello**: Cerca in anaart e fai INSERT di un nuovo prodotto

- Quando aggiorni quantità già presenti:
  * Operazione DISTRUTTIVA: "metti 5 bottiglie" = SET quantita = 5
  * Operazione INTEGRATIVA: "aggiungi 3 bottiglie" = SET quantita = quantita + 3

- Eseguire immediatamente le query con sql_db_query
- Limitare i risultati a 5, salvo diversamente specificato
- In anaart des_art è scritta in upper case

CASO CARRELLO VUOTO O NESSUN PRODOTTO TROVATO:

Se l’utente chiede di modificare, aggiornare o rimuovere prodotti
e non esiste alcun prodotto corrispondente nel carrello:

- NON dire che l’operazione è stata eseguita
- NON dire che è stato eliminato o aggiornato qualcosa
- Rispondi chiaramente che il carrello è vuoto oppure che non ci sono prodotti da modificare

Considera un’operazione "andata a buon fine" SOLO se almeno una quantità è stata
effettivamente inserita, aggiornata o rimossa.
In caso contrario, segnala che il carrello è vuoto o che non ci sono prodotti corrispondenti.

"""

cart_agent = create_agent( #type: ignore
    model=model,
    tools=tools,
    system_prompt=cart_prompt
)


def invoke_agent(question: str) -> Dict[str, Any] | Any: 
    return agent.invoke({
        "messages": [HumanMessage(content=question)],
    }, {
        "configurable": {"thread_id": "1"}
    })

def invoke_cart_agent(question: str) -> Dict[str, Any] | Any:
    return cart_agent.invoke({
        "messages": [HumanMessage(content=question)],
    }, {
        "configurable": {"thread_id": "1"}
    })
