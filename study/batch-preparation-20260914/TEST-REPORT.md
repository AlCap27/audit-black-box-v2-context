# Rapporto verifiche offline

Ambiente Python3.14.3, libreria standard. Script e materiali sono nel pacchetto;
nessuna installazione, generazione Gemini o chiamata countTokens effettuata.
Documentazione pubblica e quote ordinarie AI Studio lette separatamente.

## Verifica integrale

`verify_all.py`: PASS, dettagli in `verification.json`.
- 1.479file del pilot sigillato,2.152dell'estensione e9del protocollo precedente
  corrispondono ancora ai rispettivi SHA256.
- 919file del manifest dati verificati.
- Tutte367assegnazioni bilanciate per template e cella.
- Tutti367indici ricostruiti dalle fixture e confrontati con gli snapshot.
- Tutti8.808retrieval BM25 ricalcolati; ranking, chunk, fonti mostrate e prompt
  coincidono con le tracce salvate.
- Tutte8.832chiavi univoche; corrispondenza richiesta/traccia/hash verificata.

## Test automatici

`test_offline.py`:13test. Output completo in `test-output.txt`.
La rigenerazione in due directory nuove produce lo stesso hash del manifest;
il test è su due assegnazioni. La verifica integrale sopra copre invece tutte367.

Copertura: bilanciamento e isolamentoT;16benchmarkdiscovery; formato richieste e
contesti; ordine arbitrario; duplicati identici e conflittuali; pending e missing
terminale; versioni discordanti; errori provider; troncamento distinto da astensione;
righeJSON malformate e chiavi malformate in quarantena; raw preservato; controlli
positivi/negativi sintetici; persistenza riserve al riavvio; rifiuto doppio tentativo,
NaN e superamento30USD; gate chiusi; conteggi per hash; capacità batch e calcolo
automatico della riserva. Gli esiti simulati sono marcati sintetici nei test.

## Limiti del collaudo

Non ancora provati: accettazione reale deiJSONL daGoogle; effettiva quota batch
del progetto; conteggi token provider; durata file output e costo massimo thinking;
stabilitàmodelVersion; controlli generativi reali. Non si presentano come test
superati. Il live submitter non è attivato/collegato: il pacchetto ammette solo
preparazione, verifica e importazione offline. Non effettua retry.

La validità scientifica dei controlli non è dimostrata dalle fixture sintetiche:
queste verificano il parser. I24controlli reali dovranno precedere i main.
Indipendenza tra cluster e assenza di deriva non sono certificabili da test unitari.
Il costo10,80USD è provvisorio; i gate impediscono di usarlo come autorizzazione.
