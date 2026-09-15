# Audit Black Box V2 — preparazione Batch offline

14 settembre 2026. Stato: **PREPARED_NOT_FROZEN — lancio bloccato**.
Assistente Astra. Zero chiamate Gemini, zero spesa di questa preparazione.

Il pacchetto contiene 367 nuove assegnazioni, 8 condizioni S×L×T, 32 vendor,
24 query fisse, 8.808 richieste confermative e 24 controlli separati. Ogni query
presenta un unico contesto ottenuto dall'intero corpus competitivo, non otto
chiamate separate. Il corpus usa URL `.invalid`: non richiede pubblicazione web.

## Documenti da leggere

- `PROTOCOL-BATCH.md`: aggiornamento scientifico e regole operative batch.
- `COST-AND-QUOTAS.md`: preventivo sui prompt, quote osservate e verifiche residue.
- `DECISIONS-LAUNCH.md`: sole decisioni residue per il lancio.
- `LITERATURE.md`: precedenti rilevanti e limite della rivendicazione di novità.
- `TEST-REPORT.md` e `verification.json`: verifiche eseguite.
- `source-protocol/`: copia immutata del protocollo e dei calcoli precedenti;
  le quantità e regole operative superate sono aggiornate in PROTOCOL-BATCH.md.

## Materiali

`data/corpus/` contiene 256 fixture vendor×cella, condivise tra assegnazioni
senza duplicare fisicamente i file. `assets.json` ne lega contenuto e hash.
`design.json` contiene tutte le assegnazioni, identità e query; `editorials.json`
i 32 distrattori. `indexes.jsonl` conserva chunk, frequenze e parametri BM25;
`traces.jsonl` conserva retrieval, testo mostrato e prompt esatti. `request-links.json`
lega chiavi batch, assegnazioni, query, hash della richiesta e della traccia.

`data/requests/controls.jsonl` è il lotto di controllo. I 12 `main-*.jsonl`
contengono ciascuno 734 richieste: due query per tutte le 367 assegnazioni.
Sono file JSONL `key`+`request`, con systemInstruction e generationConfig;
il modello fisso viene specificato nella futura creazione del job.
Compatibilità documentale verificata; accettazione server non ancora collaudata.

`data/manifest.json` verifica i byte dei materiali. `package-sha256.json` copre
codice, documentazione, risultati dei test e materiali (esclusi cache Python e
il sigillo stesso). I sorgenti originali usati sono copiati in `source/`;
`prepare.py`, `batch_state.py` e `verify_all.py` sono il nuovo codice offline.
Nessuna chiave è inclusa. Non eseguire `source/experiment.py`: è solo uno snapshot
del codice storico. Gli entrypoint nuovi non inviano richieste.

## Riproduzione

Da questa cartella, con Python 3.14 e libreria standard:

```powershell
python test_offline.py
python verify_all.py
python prepare.py NUOVA_CARTELLA_VUOTA
```

Il builder rifiuta directory esistenti; non rigenerare dentro `data`.
Per importare in futuro risultati scaricati senza alterare gli originali:

```powershell
python batch_state.py data RISULTATI.jsonl NUOVA_CARTELLA_IMPORT --shard main-00 --terminal --version VERSIONE_VERIFICATA
```

Usare `--terminal` soltanto dopo aver archiviato lo stato terminale Google.
Importare solo il file associato al job/shard verificato. Senza versione attesa,
l'importazione censisce le versioni ma non certifica stabilità del modello.
Archiviare separatamente anche risposta create/get, nome job e metadati file.
Risultati locali sintetici dei test non entrano mai nei dati confermativi.

Il modulo di ammissione calcola una riserva sui conteggi Google dei prompt
identificati per hash, conserva i tentativi incerti e rifiuta sovrapposizioni e
budget oltre 30 USD. **Non contiene un inviatore live**: verrà collegato al
trasporto Batch solo dopo il preflight e l'autorizzazione del lancio.

Le campagne sigillate, il VPS, i servizi, DNS e domini sono immutati.
Non è stato creato un repository GitHub né attivata la fatturazione.
