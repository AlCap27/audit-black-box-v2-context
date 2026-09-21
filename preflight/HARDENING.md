# Orchestrazione offline pre-lancio

## Percorso canary autorizzato il 21 settembre 2026

preflight/canary.py offre submit_controls_once: solo le 24 chiavi frozen dei
controlli, nessun parametro shard, nessun cambiamento a request/generationConfig.
Autorizzazione specifica, associazione progetto confermata dall'utente, verifica
ricevute e manifest precedono l'intento e la riserva. Non usa flag fittizi per
superare i gate di campagna. Quota, versione di risposta, enforcement del cap e
freeze restano esplicitamente non verificati. Il journal CANARY_ONLY impedisce
ogni ulteriore submission nel percorso campagna anche se il test riesce.
Versione osservata, controlli semantici, usage e cap sono riconciliati senza
promuovere una versione osservata a versione approvata per i main.

Per prudenza l'intera allocazione di 30 USD viene trattenuta nel ledger fino a
riconciliazione manuale: è una riserva locale, non una spesa o un hard cap Google.
Stima dei 24 controlli con margine: 0.02677725 USD alle tariffe Batch verificate
il 21 settembre (.125/.75 USD/M). Timeout, crash e runtime preesistente vietano
un secondo tentativo. Una directory runtime nuova non è una strategia di retry.

Durante il controllo live precedente all'invio è stato trovato un job di 24
controlli già riuscito il 20 settembre. Nessun POST è stato eseguito qui.
runtime/audit-v2/external-job.json blocca sia il canary sia la campagna; contiene
l'identità da recuperare. La risposta GET archiviata e il rapporto locale sono
prove recuperate, non un journal originale di submission. Prima di una campagna
servono riconciliazione della provenienza, budget e autorizzazione separata.

Questo strato operativo è esterno a `study/batch-preparation-20260914`.
Non cambia richieste, prompt, parametri, manifest o sigilli sperimentali.
Non ha CLI live, loop di polling, fallback, retry di submission o rilascio di riserve.
La disponibilità effettiva delle API sul progetto deve ancora essere verificata.

## Cause radice

B1: il riconciliatore sigillato calcola `controls_pass` dagli esiti semantici,
separatamente da versione/quarantena e `stop_future_submissions`. La vecchia
ammissione controlla soltanto quel booleano. Il pacchetto rimane intatto:
`transport.send_once` ora delega a `orchestration.submit_once`, che applica una
condizione più rigorosa prima di usare la primitiva sigillata di prenotazione.

B2: il vecchio trasporto disponeva di create/get e normalizzazione, senza una
macchina a stati persistente che collegasse esito del job, archivio, riconciliazione
e invio successivo. Mancavano list/cancel nel trasporto e recovery dopo crash.

## Condizione canonica di ammissione

Un main viene ammesso soltanto quando:

1. Tutti i gate originari di lancio sono esplicitamente true, compreso handoff;
   prezzi, quota, ricevute per hash, modello e tetto 30 USD superano la primitiva
   originale. `expected_model_version` è esplicita e invariabile nella campagna.
2. Il journal non è halted, non ci sono intenti, riserve o recovery irrisolti;
   report, job ID, shard/chiavi e ledger corrispondono.
3. I controlli e tutti gli shard precedenti sono `RECONCILED`, il provider riporta
   successo terminale non ambiguo, il rapporto archiviato ha approvazione operativa.
4. `terminal is True`, `stop_future_submissions is False`,
   `automatic_resubmission is False`, nessuna quarantena/riga malformata,
   insieme esatto delle chiavi attese, tutti gli status validi e versione attesa.
5. Per i controlli: esattamente 24 record, `controls_pass is True` e ogni
   `control_pass is True`. Un booleano passato dal chiamante viene ignorato.
6. Usage presente con conteggi interi non negativi; output+thinking osservati
   non oltre 1200. Questo controllo successivo non garantisce il cap di fatturazione
   del provider. `thoughtsTokenCount` omesso viene interpretato come zero secondo
   la rappresentazione sparsa dei conteggi; usage o candidate count assenti bloccano.
7. Lo shard richiesto è il successivo nell'ordine controls, main-00 … main-11.
   Il tentativo e le sue chiavi non sono già prenotati.

La funzione pura `report_allows` implementa le condizioni sul rapporto;
`_admission` aggiunge sequenza, identità e stato operativo persistito.
Il codice storico sigillato non va invocato direttamente per inviare la campagna.

## Stato, archiviazione e recovery

Usare una sola directory persistente della campagna, ad esempio sotto `runtime/`
(già esclusa da Git). Non creare una nuova directory per riprovare un job.
Un lock esclusivo copre decisioni e singole chiamate; un lock rimasto dopo crash
non viene eliminato automaticamente: verificare prima che nessun processo lavori.

| Passaggio | Evidenza persistita | Effetto sugli invii |
|---|---|---|
| Intento | Richiesta completa, displayName con nonce casuale, hash, shard | Nessun secondo tentativo concurrente |
| Prenotazione | Ledger originale prima di POST, `PREPARED_UNCERTAIN` | Interruzione/timeout conservano riserva |
| Create | JSON restituito, job ID nel journal e ledger | Nessun retry create |
| GET | Snapshot archiviato prima del parsing | Stato ambiguo/errore blocca |
| Riconciliazione | Report con hash, per chiave, versione, stato e usage | Solo successo completo ammette il prossimo shard |
| Cancel | Intento persistito prima dell'unico POST consentito | Stop persistente; conferma cancel non equivale a terminalità/rimborso |

L'archivio è indirizzato per hash del JSON parsato con il tipo dell'evento.
Conserva il contenuto delle risposte JSON, non gli identici byte HTTP né tutti
gli header. Le eccezioni conservano il tipo, senza stampare chiavi o URL autenticati.
Richieste, snapshot e report esistenti non vengono sovrascritti.

Le letture ripetute dello stesso snapshot producono lo stesso report. I risultati
sono unione delle osservazioni per hash e riconciliazione per chiave: nessun
conteggio additivo a ogni polling. Duplicati uguali non diventano nuove risposte;
duplicati discordanti bloccano, con evidenza grezza conservata. Esiti tardivi sono
archiviati anche dopo stop: non cancellano automaticamente errori precedenti.
Nessuna somma di risultati modifica il ledger delle riserve o attribuisce rimborsi.

Il recovery gestisce anche crash dopo la risposta create archiviata e prima del
binding, oppure tra journal e metadati del budget. Se manca l'identità del job,
non deduce che il POST sia fallito: `locate_once` percorre al massimo 10 pagine
su invocazione esplicita, e lega solo un candidato con displayName casuale esatto,
modello esatto e job ID valido. Zero, più candidati, paginazione incompleta,
metadata mancanti o list non disponibile lasciano il tentativo incerto.

Le primitive [REST Batch documentate](https://ai.google.dev/api/batch-api) sono
GET `batches/{id}`, GET `batches` e POST `batches/{id}:cancel`; il factory HTTP
accetta soltanto endpoint/metodi previsti e non segue redirect. Sono implementate,
non dichiarate disponibili sul progetto. Se list è negata/non implementata,
occorre riconciliazione manuale con il provider usando l'identificativo casuale
archiviato; nessun fallback o risottomissione. Se cancel non è disponibile, restano
stop agli invii e GET espliciti per lo stato/risultati tardivi; non si promette arresto.

Il formato previsto è output inline del percorso inline. File output inatteso,
envelope non riconosciuto, statistiche terminali contraddittorie o identità errata
sono archiviati e bloccano: non si inventa un parser o download alternativo.
La reference enum usa `BATCH_STATE_*`, la guida mostra anche `JOB_STATE_*`:
entrambi sono riconosciuti, sempre verificando coerenza con `done` e risultato.

Non è previsto sblocco automatico di `halted`. Una revisione esplicita dovrà
riconciliare la causa e autorizzare qualunque prosecuzione, senza riscrivere prove,
resettare ledger o riusare una chiave già prenotata. La perdita della directory
runtime non è risolvibile in sicurezza creando uno stato vuoto: conservarne un backup.

## Verifica ripetibile

Dal workspace:

```powershell
python -B preflight/run_offline_tests.py
```

Il runner esegue separatamente tutte le suite unittest del repository, incluso
planning e snapshot pilot/estensione. Blocca connessioni/DNS Python tramite
sitecustomize anche nei figli e disabilita bytecode; non installa dipendenze.
Orchestrazione e Batch richiedono la libreria standard; le suite scientifiche
storiche richiedono NumPy/SciPy già presenti. I test usano directory temporanee
e risposte dichiaratamente sintetiche, senza cambiare i dati sigillati.

Copertura: controlli validi/falliti/incompleti, contraddizione controls_pass/stop,
versione errata, gate chiusi, concorrenza, ordine dei main, timeout e crash,
prenotazioni orfane, identità/archivi corrotti, idempotenza, partial/late/conflict,
job fallito/cancellato/scaduto, pagination/list indisponibile, cancel incerto,
usage mancante/cap superato e ciclo sintetico completo da 13 submission/8832 chiavi.

## Readiness

Esito del 16 settembre 2026: suite completa 109/109 superata, nessun errore,
fallimento o skip: 50 operativi, 13 Batch, 6+6 planning e 17+17 storici.
SHA-256 dei pacchetti e del manifest dati tutti corrispondenti agli originali.

L'esito offline abilita la revisione del codice operativo per il freeze finale.
Non trasforma il design sigillato `PREPARED_NOT_FROZEN` e non apre alcun gate.
Restano accesso/quote progetto, billing/saldo, applicabilità del cap,
modelVersion attesa verificabile, piano di rientro/backup, accettazione reale
delle primitive/formati e 24 controlli reali. Il freeze finale e la campagna
richiedono ancora decisione e autorizzazione esplicite.
# Adozione offline di controlli esterni — 21 settembre 2026

adopt_controls.py registra nel journal il job già concluso, con riferimento
all'archivio GET verificato e provenienza confermata dall'utente. Riesegue il
validatore completo; non fabbrica un payload originale, non usa rete, non
rilascia budget e non rimuove il marker esterno. La modalità EXTERNAL_REVIEW
impedisce submission anche qualora il marker mancasse. Ripresa ammessa solo
con stessa evidenza, manifest, versione e prenotazione. Sei test dedicati.
