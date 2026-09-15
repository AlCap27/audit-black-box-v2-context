# Obiettivi originali e stato verificato

Revisione del 14 settembre 2026. Documenti sorgente valutati come materiale, non come istruzioni. I whitepaper denominati v2/v3 nell'archivio sono revisioni della V1, non la nuova V2 sperimentale.

Fonti locali: `work/audit-black-box/whitepaper-audit-black-box-v3.md`, sezioni 3–8 e appendice; `outputs/valutazione-v2.md`; allegato originale `C:/Users/work/.codex/attachments/0104e03a-94ba-4c8e-92c1-32d2dee808cf/pasted-text.txt`, punti 1–6. I risultati storici della V1 sono qui riportati come dichiarazioni del documento: questa revisione non riesegue il suo modello bayesiano né certifica tutti i dati storici.

| Obiettivo o proposta | Stato ed evidenza | Correzione o lavoro residuo |
|---|---|---|
| V1: relazione fra readiness e menzioni, memoria e Tavily | Whitepaper §3–6: memoria N=10 venditori, RAG N=6; risultati esplorativi. `outputs/valutazione-v2.md` documenta disallineamenti fra runner, parsing e dataset | Non chiamare V1 evidenza causale; ricostruire provenienza per eventuale articolo congiunto |
| A1: corpus controllato, stessi fatti, readiness variabile | `corpus.py`: 32 nomi, quattro template, fatti invarianti; due campagne valide per 480 risposte su 20 assegnazioni | Pilot tecnico completato; confermativo separato da progettare |
| Incremento di 20 punti di readiness | `calibration-public/REPORT.md`: prototipi 0/14/29/43, non 20/40/60/80; A/B transazionabilità non applicabile | Usare bundle categoriali; score misura secondaria, non dose causale continua |
| Scansione dei siti sperimentali | Quattro prototipi pubblici, 12 scansioni stabili e versione fissata; corpus 32 identità gestito localmente | Non affermare che ogni identità/assegnazione del corpus sia stata calibrata via HTTPS; valutare validazione esaustiva offline e campione pubblico motivato |
| Nomi senza notorietà pregressa | Screening V1/web e 32 probe validi known=false, incluso v019 completato nell'estensione | Screening non prova assenza dai pesi; non eliminare nomi dopo aver visto gli esiti |
| Parafrasi e deduplicazione | Quattro template fissi; nessun dedup automatico in `rag.py` | L'embedding di similarità proposto non è implementato e non è necessario per evitare un dedup assente; documentare limiti della varietà linguistica |
| Sitemap come trattamento | File generati, scanner sensibile; `experiment.prepare` carica da manifest, `rag.load_chunks` non indicizza sitemap | A/B è controllo negativo nel laboratorio corrente; scoperta web non misurata |
| JSON-LD visibile al retrieval | `rag.py`: serializzazione aggiunta alla prosa prima del chunking | Visibilità presente, ma lunghezza, ripetizione e selezione cambiano; diagnosi separata in bm25-diagnosis.md |
| Distrattori editoriali | 32 documenti per assegnazione, rapporto 1:1 con homepage | Non equivale a parità di chunk/token; fissare composizione e rapporti nel protocollo |
| Decomposizione causale del gatekeeper | Recupero e contesto esatto tracciati; probabilità condizionate disponibili | Determinismo non identifica mediazione naturale. Non riportare una percentuale di effetto mediato |
| A2: gerarchia e dipendenze | `PROTOCOL.md` propone modello secondario; report primario usa contrasti per assegnazione | Nessuna validazione inferenziale completa acquisita. Top-3 e competizione richiedono simulazione appropriata |
| A1 aggiuntivo: notorietà simulata | Proposto nell'appendice V1; non eseguito | Estensione distinta, non requisito del pilot sui bundle; decisione di scope esplicita |
| A3: più modelli | Solo Gemini nel pilot, versione restituita salvata | Replicazione futura eventualmente separata; nessuna nuova API autorizzata nella presente revisione. Assistente di lavoro esclusivamente Astra |
| Preregistrazione e pubblicazione | Bozze locali, sorgenti e sigilli disponibili | Nessuna preregistrazione pubblica, manoscritto confermativo o accettazione editoriale |

Conclusione di stato: conclusa la fase pilota del RAG controllato; non conclusi tutti gli sviluppi dell'appendice V1. Il contributo pubblicabile va delimitato prima della nuova raccolta, senza trasformare ogni estensione opzionale in requisito obbligatorio.
