CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
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

CREATE TABLE anacli (
    cod_cli INTEGER PRIMARY KEY,
    rag_soc VARCHAR(255)
);

CREATE TYPE RoleEnum AS ENUM('user', 'assistant');

CREATE TABLE conversazioni(
    id SERIAL PRIMARY KEY,
    data_creazione TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE messaggi(
    id SERIAL PRIMARY KEY,
    conversazione_id INTEGER REFERENCES conversazioni(id) ON DELETE CASCADE,
    ruolo RoleEnum NOT NULL,
    testo TEXT NOT NULL,
    data_invio TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messaggi_conversazione_id ON messaggi(conversazione_id);
CREATE INDEX idx_messaggi_data_invio ON messaggi(data_invio);

CREATE TABLE utentiweb (
    username VARCHAR(255) PRIMARY KEY,
    descrizione VARCHAR(80),
    password VARCHAR(60),
    cod_utente INTEGER,
    CONSTRAINT fk_utentiweb_anacli
        FOREIGN KEY (cod_utente)
        REFERENCES anacli(cod_cli)
);

CREATE TABLE ordclidet (
    id SERIAL PRIMARY KEY,
    cod_cli INTEGER,
    cod_art VARCHAR(13),
    data_ord DATE,
    qta_ordinata INTEGER,
    rif TEXT,
    CONSTRAINT fk_ordclidet_anacli
        FOREIGN KEY (cod_cli) REFERENCES anacli(cod_cli),
    CONSTRAINT fk_ordclidet_anaart
        FOREIGN KEY (cod_art) REFERENCES anaart(cod_art)
);

CREATE TABLE carrello(utente varchar(255), 
		      prodotto varchar(13),
		      quantita INTEGER,
    CONSTRAINT fk_cart_utentiweb FOREIGN KEY (utente) REFERENCES utentiweb(username),
    CONSTRAINT fk_cart_anaart FOREIGN KEY (prodotto) REFERENCES anaart(cod_art)
);