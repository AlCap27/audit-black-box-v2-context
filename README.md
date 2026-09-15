# Audit Black Box V2 — fonte persistente del progetto

Leggere prima `current-state.md`, `architecture.md`, `next-steps.md` e `AGENTS.md`.
La repository è la memoria condivisa; ogni conversazione Codex è una sessione
operativa locale. Non si presume sincronizzazione delle conversazioni.

Obiettivo: valutare effetti di JSON-LD, llms.txt e ridondanza testuale sul retrieval
BM25 e sulla raccomandazione del vendor nella pipeline controllata. Tre stadi
distinti: discovery, retrieval, recommendation. Non generalizzare agli agenti
di acquisto nel loro complesso. Riportare anche effetti nulli e contrari alle attese.

Stato15settembre2026: materiali offline completi; preflight tecnico in corso,
nessuna campagna confermativa avviata. Budget30USD totale, generatore esclusivamente
gemini-3.1-flash-lite tramite Batch; assistente esclusivamente Astra.

`study/batch-preparation-20260914/` contiene corpus, richieste, tracce, codice e
protocollo. Le campagne precedenti sono prove pilot sigillate, non dati confermativi.
`conversation-history.md` è un export testuale selezionato e depurato dei messaggi,
non contiene ragionamento interno, logstrumenti o allegati binari. Il punto di
ripresa attuale prevale su proposte superate nella cronologia.

## Sul [rimosso]

1. Clonare la repository privata quando pubblicata e aprire la cartella in Codex.
2. Selezionare Astra e incollare il prompt in `START-HERE.md`.
3. Eseguire `git pull --ff-only` prima di lavorare; a fine sessione aggiornare stato
   e attività, fare commit e push. Non lavorare simultaneamente sullo stesso ramo
   da duePC senza coordinamento.
4. Configurare eventuali credenziali separatamente sul dispositivo. Nessuna chiave
   viene trasferita conGit. Non attivare fatturazione o campagna senza il gate previsto.

Il link condiviso del vecchio thread resta sospeso: il registro grezzo contiene
occorrenze di [rimosso]. La copia Markdown depurata è la modalità trasferibile
predisposta. Il registro originale resta sul [rimosso].
