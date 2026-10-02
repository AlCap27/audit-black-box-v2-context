# Audit Black Box V2 — fonte persistente del progetto

Leggere prima `current-state.md`, `architecture.md`, `next-steps.md` e `AGENTS.md`.
La repository è la memoria condivisa; ogni conversazione Codex è una sessione
operativa locale. Non si presume sincronizzazione delle conversazioni.

Obiettivo: valutare effetti di JSON-LD, llms.txt e ridondanza testuale sul retrieval
BM25 e sulla raccomandazione del vendor nella pipeline controllata. Tre stadi
distinti: discovery, retrieval, recommendation. Non generalizzare agli agenti
di acquisto nel loro complesso. Riportare anche effetti nulli e contrari alle attese.

Stato 22 settembre 2026: raccolta e analisi offline completate, 8808 main validi
e 24 controlli originali non ripetuti. Report in
`analysis/results-20260922/REPORT.md`; pacchetto e istruzioni di revisione in
`review/README.md`, inclusi dati grezzi e journal archiviati. Non avviare nuovi
Batch. Budget 30 USD totale; costo usage stimato 1.24666525 USD, fattura non
verificata. Generatore gemini-3.1-flash-lite; assistente esclusivamente Astra.

`study/batch-preparation-20260914/` contiene corpus, richieste, tracce, codice e
protocollo. Le campagne precedenti sono prove pilot sigillate, non dati confermativi.
Il punto di ripresa attuale prevale su proposte superate nella cronologia.

## Sul [rimosso]

1. Repository privata pubblicata e trasferita sul [rimosso] il 16 settembre 2026.
   Workspace su `main`, upstream `origin/main`, commit verificato
   `2c4631ead0b0c19e4a3148e0000d27f93b691b60`; manifest e sigilli verificati
   integralmente prima degli aggiornamenti documentali. Vedere `current-state.md`.
   Per altri dispositivi, clonare `AlCap27/audit-black-box-v2-context`.
2. Selezionare Astra e incollare il prompt in `START-HERE.md`.
3. Eseguire `git pull --ff-only` prima di lavorare; a fine sessione aggiornare stato
   e attività, fare commit e push. Non lavorare simultaneamente sullo stesso ramo
   da duePC senza coordinamento.
4. Configurare eventuali credenziali separatamente sul dispositivo. Nessuna chiave
   viene trasferita conGit. Non attivare fatturazione o campagna senza il gate previsto.

Il link condiviso del vecchio thread resta sospeso: il registro grezzo contiene
occorrenze di [rimosso]. La copia Markdown depurata è la modalità trasferibile
predisposta. Il registro originale resta sul [rimosso].
