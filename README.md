# PoC
Repository del codice sorgente per il Proof Of Concept (PoC)

---

## Build
Per avviare il processo di build ed eseguire sia backend che frontend è necessario avere docker installato sul proprio dispositivo ed eseguire `docker compose up`.
Una volta che docker ha finito di creare tutti i container e le relative immagini, si potrà trovare:
- Database: (work in progress ancora non è definito)
- API: http://0.0.0.0:8000, documentazione api sta in http://0.0.0.0:8000/docs
- Frontend: http://0.0.0.0:5173

---
## Python Virtual Environment
Per evitare di installare globalmente nel sistema le librerie necessarie per il PoC è stato creato un virtual environment (cartella .venv).
Per avere la funzione di code completion del proprio editor/IDE è necessario avviare il venv.
Per farlo bisogna:
1. Eseguire `source .venv/bin/activate` ==all'interno della cartella backend==.
2. Eseguire `python install -r requirements.txt`
3. Riavviare VsCode

Se VsCode ancora non fornisce suggerimenti alle funzioni allora continuare a seguire i passaggi
1. Premere `Ctrl+shift+P` (`Cmd+shift+P` Mac)
2. Cercare e selezionare l'opzione **Python: Select Interpreter** > **"Enter interpreter path"**
3. A quel punto navigare la cartella .venv fino a selezionare il file `.venv/bin/python3.xx` o `.venv\Scripts\python3.xx.exe` dove xx è la versione più recente installata nel vostro sistema (in teoria 13 o 14)

