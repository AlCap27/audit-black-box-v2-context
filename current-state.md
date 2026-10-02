# Stato corrente — aggiornamento 2 ottobre 2026

## PUBLICATION_CHECKPOINT — stato prevalente su tutte le note storiche

Quattro interventi documentali per lo stato "pubblicabile" committati e
pubblicati il 2 ottobre 2026: commit `31bcda1` su `origin/main`, push
verificato (ahead/behind 0/0, working tree pulito). Nessuna modifica a
parser, dati grezzi o analyze.py: solo documenti, più l'aggiunta di
evidenza della revisione.

1. Dichiarazione di conflitto d'interesse (l'autore sviluppa Agentabile,
   agentabile.dev) e nota di framing/ambito inserite in testa a
   `analysis/results-20260922/REPORT.md`, testo concordato verbatim con
   l'utente.
2. Chiusa nello stesso REPORT.md la discrepanza "revisione umana del
   parsing da fare": revisione ESEGUITA su un campione stratificato di 70
   casi (25 astensioni, 25 raccomandazioni, 20 lunghe/atipiche; seed fisso
   20260922) tratti dalle 8808 risposte confermative. Zero discrepanze
   semantiche: astensioni tutte genuine, mappature nome→vendor tutte
   esatte, coerente con unknown_names=0 e unsupported_recommendations=0
   sull'intero corpus.
3. `review/review-giudizi.csv` (i 70 giudizi umani, colonna giudizio_umano
   compilata "sì" su tutti i casi, nessuna nota) e
   `review/vendor-canonici.csv` (i 32 nomi canonici da identity-source.json)
   tracciati come evidenza della revisione. `.gitignore` verificato coerente:
   esclude solo il materiale di lavoro usa-e-getta
   `review/review-sample.html`, non le due CSV.
4. Allineati i riferimenti obsoleti che dichiaravano ancora la revisione del
   parsing "da effettuare" in `next-steps.md` e `review/README.md`.

Seguiti il 2 ottobre da due commit di allineamento minori sulla conclusione
di REPORT.md e next-steps.md. Avviata inoltre una pulizia privacy:
`conversation-history.md` (conteneva path locali personali) rimosso dal
working tree, dai riferimenti testuali in README.md/START-HERE.md e dalla
voce in transfer-manifest.json in questo stesso commit. La rimozione
dall'intera history dei commit tramite `git filter-repo` e il relativo
force-push a origin/main sono un passo separato, locale, eseguito solo dopo
che l'utente ha verificato l'esito; backup completo del repository
pre-riscrittura conservato fuori da esso. Repository privata.

Resta aperta, distinta dalla revisione semantica del parsing ora chiusa, la
revisione scientifica/metodologica indipendente delle assunzioni (vedi
"Domande al revisore" in `review/README.md`).

## Cronologia operativa — sintesi

Il dettaglio diaristico delle sessioni precedenti (16–22 settembre 2026:
trasferimento del workspace, hardening B1/B2, preflight A/B, canary,
riconciliazione economica, freeze v1/v2, lancio e raccolta) è stato tagliato
da questo file il 2 ottobre 2026: erano cronologia di processo (PID del
driver, sequenze GET/POST intermedie, stati di readiness ormai superati),
non stato attuale. Il dettaglio integrale resta nei documenti dedicati, non
toccati da questa sintesi: `preflight/CANARY-20260921.md`,
`preflight/HARDENING.md`, `preflight/LAUNCH-REVIEW-20260921.md`,
`preflight/FINAL-FREEZE-20260921.md`, `preflight/FINAL-FREEZE-20260921-v2.md`,
e il codice/test in `preflight/` e `study/`.

Fatti che restano operativamente rilevanti:

- Raccolta completata senza incidenti: 12/12 main riconciliati, 8808/8808
  risposte principali valide, 24/24 controlli validi, zero quarantena.
  Driver terminato con successo; nessun job da reinviare.
- Freeze operativo di lancio: `f7606d529d0a4c44f628eb11286c8b6d1088747d`.
- Budget: tetto 30 USD; costo usage stimato 1.24666525 USD (12 main più
  controlli); fattura definitiva mai verificata.
- Generatore: `gemini-3.1-flash-lite`, nessun fallback. Assistente di
  progetto: esclusivamente Astra.
- Nessuna credenziale è mai stata mostrata, salvata o committata nel
  repository; `runtime/` resta escluso da Git. I controlli sui checkpoint
  storici non hanno mai rilevato chiavi o pattern di credenziali.
- Repository privata, trasferita e verificata su un secondo dispositivo il
  16 settembre 2026 (commit `2c4631e`); manifest e sigilli originali
  verificati integralmente ad ogni checkpoint, zero discrepanze.

Nessuna nuova chiamata Google, generazione, Batch o modifica di fatturazione
è stata autorizzata dopo la raccolta. Non riattivare il runner; non ripetere
controlli o main.
