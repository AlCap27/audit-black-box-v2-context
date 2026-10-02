# Checkpoint di revisione — 22 settembre 2026

Raccolta conclusa: 8808 main, 24 controlli originali; nessuna richiesta da
ripetere. Il repository privato contiene il materiale per la revisione offline.
Git trasferisce i file, non la conversazione nell'app. Su un altro PC clonare
AlCap27/audit-black-box-v2-context oppure aggiornare main con git pull --ff-only,
quindi leggere START-HERE.md e current-state.md. Non riattivare il runner.

## Materiale da esaminare

- Risultati e limiti: ../analysis/results-20260922/REPORT.md e JSON/JSONL accanto.
- Revisione umana del parsing (ESEGUITA): review-giudizi.csv (70 casi giudicati,
  seed 20260922) e vendor-canonici.csv (tabella di riferimento dei 32 nomi);
  dettagli in REPORT.md, sezione "Discovery e controllo del parser".
- Codice analitico post-raccolta: ../analysis/ e relativi test.
- Protocollo Batch: ../study/batch-preparation-20260914/PROTOCOL-BATCH.md;
  protocollo e funzioni statistiche frozen nella sottocartella source-protocol/.
- Disegno, fixture, assegnazioni, tracce e richieste: stessa cartella study/.
  Manifest e sigilli originali sono invariati.
- Architettura: ../architecture.md. Freeze operativo:
  ../preflight/FINAL-FREEZE-20260921-v2.md e freeze-20260921-v2.json.
- Evidenze grezze: collection-complete-20260922.zip, copia esatta del backup
  runtime locale, 97 file: 92 oggetti di archivio, journal operations.json,
  budget.json, collection-summary.json e due registri di riconciliazione esterna.

SHA-256 dello ZIP:
56c4396611a591358aaa0029a1094ca90f8ae275fd65b3c7902d4c9024a63324

Archivio controllato per credenziali: nessuna chiave/API token presente nei
controlli eseguiti; include identificativi dei job e autorizzazioni operative
storiche, non segreti di autenticazione. Mantenere privata la repository.
backup-receipt.json descrive il backup locale al momento della creazione:
off_device=false è storico, non una verifica dello stato attuale del remoto.

## Riproduzione offline

Python 3.13.5 è il runtime registrato nel freeze. Nessuna credenziale necessaria.
Su una copia nuova della repository, verificare lo SHA-256 sopra ed estrarre
lo ZIP in runtime/audit-v2, solo se la directory non esiste ancora. Non
sovrascrivere un journal già presente. I file operations.json e budget.json
devono risultare direttamente dentro runtime/audit-v2.

Dalla radice del repository:

```text
python -m unittest discover -s analysis -p test_analysis.py -v
python analysis/analyze.py runtime/review-reproduction
```

La destinazione deve essere nuova. analyze.py blocca le connessioni di rete,
verifica i manifest e il freeze operativo e rilegge le risposte grezze. Confrontare
le tabelle riprodotte con analysis/results-20260922/. Non eseguire launch.py,
submit, driver di campagna o comandi provider per revisionare questo lavoro.

## Domande al revisore

Verificare aderenza al protocollo, denominatori e trattamento delle astensioni,
intervalli e correzione per molteplicità, plausibilità dell'indipendenza dei
cluster e limiti delle conclusioni nel disegno sintetico BM25. Analisi di
sensibilità post-raccolta e confronti descrittivi non sostituiscono i test frozen.
Revisione umana di un campione di parsing: ESEGUITA, zero discrepanze semantiche
(vedi REPORT.md e review-giudizi.csv). Costo usage
stimato 1.24666525 USD; fattura definitiva non verificata.
