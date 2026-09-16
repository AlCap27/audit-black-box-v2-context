# Stato corrente — 16 settembre 2026

## Decisioni attuali

L'utente ha autorizzato di procedere con i passaggi proposti: design367assegnazioni,
8808generazioni+24controlli, fattoriale S/L/T, primaria L totale α.025 e secondarie
α.003125. La garanzia conservativa90% aΔ5pp richiede cluster indipendenti e dati
completi; non vale automaticamente per il condizionato. Retrieval sulle367assegnazioni.
Questa approvazione supera lo stato “proposto” nei documenti storici, che restano
immutati. Freeze operativo finale dopo preflight; nessuna registrazione pubblica fatta.

Sono approvati Batch, modello3.1flashlite senzafallback, limite30USD incluse prove e
tentativi. Conferma utente del 16 settembre: Astra è l'assistente; Gemini
3.1 Flash-Lite resta il generatore sperimentale. Trasferimento e sincronizzazione
completati; nessuna autorizzazione al lancio da questo stato. Nessuna modifica VPS/DNS.
Fatturazione non attivata; eventuale attivazione richiede intervento esplicito.

## Completato

- Corpus256fixture,367assegnazioni bilanciate,8808tracce e24controlli.
- Indici ricostruiti e8808retrieval verificati.13test offline passati.
- Sigilli1479file pilot,2152estensione,9protocollo verificati.
- Quote ordinarie osservate:500RPD/15RPM/250kTPM, separate dal Batch.
- APIgetModel conferma gemini-3.1-flash-lite e batchGenerateContent.
- Lettura elenco Batch riuscita, nessun job esistente nella risposta.
- Conteggio Google completo:1834payload unici,8832richieste coperte,5.784.500token
  input. Ricevute in `preflight/`. Scenario1200output:8,671863USD,10,406235con20%.
- Trasporto aggiunto in `preflight/transport.py`,4testmockpassati, gatechiusi.

## Mancante / non inferibile

La lettura dei job non dimostra capacità di crearli né quota batch disponibile.
Limite fatturabile thinking+output da confermare. Il pacchetto del14settembre
non contiene trasporto live; il nuovo modulo inpreflight lo implementa congate
chiusi e non è stato usato controGoogle. I gate non vanno aggirati. Controlli reali
non eseguiti. IlPC può spegnersi durante il job, ma download richiede breve rientro
entro24ore; non esiste archiviatore remoto. Nessun lancio confermativo autorizzato
da questo file.

## Trasferimento verificato — 16 settembre 2026

Repository privata `AlCap27/audit-black-box-v2-context` pubblicata e accessibile.
Workspace del [rimosso] allineato a `main`, upstream `origin/main`, commit
`2c4631ead0b0c19e4a3148e0000d27f93b691b60`. Nessuna storia creata su `master`.
Remote origin: `https://github.com/AlCap27/audit-black-box-v2-context.git`.

Prima degli aggiornamenti documentali: working tree pulito; `git fsck --full`
senza errori; SHA-256 ricalcolati sui byte locali con esito completo:
- manifest di trasferimento: 4615/4615;
- pilot: 1479/1479; estensione: 2152/2152;
- protocollo: 9/9; copia source-protocol: 9/9;
- pacchetto Batch: 949/949; manifest dati: 919/919.
Nessun file mancante o hash discrepante. I 4617 file tracciati comprendono anche
`.gitattributes` e `transfer-manifest.json`, esclusi dall'elenco del manifest.

Il manifest di trasferimento originale resta immutato come riferimento del commit
importato. I successivi aggiornamenti autorizzati a README.md, current-state.md e
next-steps.md differiscono intenzionalmente dai suoi hash. Pacchetti e sigilli in
study/ non sono modificati. Il commit documentale di migrazione
`29c1f2127e45f4a485cd175b68f6ff36101babd3` segue il commit importato sulla stessa
storia di main ed è stato pubblicato su origin/main con autorizzazione utente.
Il presente preflight è iniziato da quel checkpoint con working tree pulito
e HEAD uguale al riferimento locale origin/main; nessun nuovo fetch o push.

La sessione di migrazione autorizzava solo trasferimento, verifica e documentazione.
Nessuna chiamata Google, invio Batch, attivazione fatturazione o controllo reale
eseguito. I test scientifici/offline precedenti non sono stati rieseguiti: qui sono
stati ricalcolati gli hash. Attendere conferma prima di altre attività operative;
il trasferimento non certifica quota, cap output, freeze o autorizzazione al lancio.

Nessun link condiviso del thread creato, poiché il registro grezzo contiene
[rimosso]; l'export depurato è disponibile nella repository.

## Preflight residuo locale — 16 settembre 2026

Esito: **NON PRONTO AL LANCIO**. Autorizzati controlli offline/mock e lettura della
documentazione pubblica; nessuna chiamata alle API Google, creazione Batch reale,
modifica fatturazione, controllo generativo o push. Nessuna credenziale letta.
In quella fase, precedente all'hardening sotto documentato, furono aggiornati
soltanto current-state.md e next-steps.md.

### Verifiche effettivamente eseguite

- Python 3.13.5, OpenSSL 3.0.16; import del trasporto e della pipeline riuscito.
  Analisi degli import: nessuna dipendenza esterna alla libreria standard per
  questo percorso. Il pacchetto storico indicava Python 3.14.3: non è necessario
  dedurre incompatibilità, poiché i controlli sotto passano sul runtime locale.
- 4 test di test_transport.py e 13 di test_offline.py: 17/17 PASS, rete bloccata
  tramite mock socket; dati sintetici soltanto in directory temporanee, Python -B.
- verify_all.main(): PASS, con il solo writer del rapporto sostituito in memoria
  da una funzione senza scritture. Verificati 367 bilanciamenti/indici, ricalcolati
  8808 retrieval, confrontati ranking, fonti, prompt, hash richieste e tracce.
  Il verification.json sigillato non è stato riscritto.
- 256 fixture, 32 identità, 8 celle, 24 query; 8808 tracce confermative e 24 controlli.
  8832 chiavi univoche; 1834 payload generativi distinti. Le ricevute archiviate
  contengono 8832 voci e dichiarano 1834 conteggi; ogni request_sha256 è stato
  riconfrontato con la richiesta locale. Somma token: 5784500; range 219–1120.
  La cache contiene 1834 risposte countTokens; non sono stati ripetuti conteggi
  provider né ricostruita l'associazione hash-cache del vecchio script di raccolta.
- 13 payload Batch costruiti in memoria preservano tutte le chiavi metadata.key
  e l'intero oggetto request: 24 controlli e 12 main da 734 richieste.
  Controlli: 30802 byte, 5715 token input. Main: 1645722–2804708 byte; massimo
  753451 token input per shard. Dimensioni riferite al display name offline-check.
  Tutti sotto 20 MB. Nessuna deduplicazione delle generazioni previste.
- Mock aggiuntivo send_once con ammissione reale ma trasporto sintetico: riserva
  persistita prima dell'unica chiamata mock, job ID conservato, stato ACCEPTED;
  riserva controlli 0.02677725 USD. Stato e gate fittizi soltanto in directory temp.
- Envelope REST inline documentato normalizzato e riconciliato: 24/24 controlli
  sintetici validi. Non è una prova di accettazione o qualità generativa del server.
- SHA-256 ricontrollati: pilot 1479/1479, estensione 2152/2152, protocollo 9/9,
  copia source-protocol 9/9, pacchetto Batch 949/949, dati 919/919. Nel manifest
  di trasferimento le sole differenze sono i tre documenti di stato già aggiornati
  dopo l'importazione; tutti gli altri 4612 file corrispondono. Nessun sigillo o
  manifest rigenerato. Codice, protocollo e prompt invariati.

### Trasporto, credenziali e blocker rilevati prima dell'hardening

Il percorso previsto è REST v1beta su generativelanguage.googleapis.com:
POST models/gemini-3.1-flash-lite:batchGenerateContent, poi GET batches/{id}.
Autenticazione tramite header x-goog-api-key; http_transport riceve la chiave
come argomento, non carica credenziali automaticamente. Input JSON inline con
request e metadata.key; output Operation con response.inlinedResponses e chiavi
preservate. Nessun SDK Google necessario. L'importatore offline usa JSONL per key.

GEMINI_API_KEY e GOOGLE_API_KEY risultano assenti dall'ambiente del processo;
.env, credentials/, secrets/ e runtime/ non esistono nel workspace. Questo non
prova l'assenza di una credenziale altrove: il percorso esterno va indicato
separatamente, senza copiarne il valore in chat o Git. Accesso, progetto, tier,
quota corrente e stato fatturazione non sono stati verificati live.

**B1 — Ammissione dei main non sufficientemente collegata alla riconciliazione.**
In batch_state.reconcile, 24 controlli con risposte semanticamente corrette ma
modelVersion diversa da quella attesa producono contemporaneamente
controls_pass=true e stop_future_submissions=true, con status version_mismatch.
Anche una riga aggiuntiva in quarantena lascia controls_pass=true. Riproduzione
locale eseguita; passando quel flag ad admit_shard, un main viene ammesso e
prenotato localmente nonostante la versione errata. Nessun invio nel test.
Il chiamante deve vincolare l'ammissione al rapporto completo, versione, stato
terminale e assenza di stop/quarantena; il solo booleano non basta. Il pacchetto
è sigillato: nessuna correzione in-place, nessun nuovo sigillo senza consenso.

**B2 — Ciclo di recupero operativo incompleto.** http_transport rifiuta gli
endpoint batches (elenco) e batches/{id}:cancel: verificato con mock senza rete.
Manca un entrypoint controllato che colleghi stato terminale/errore del job,
archiviazione raw con hash, normalizzazione, importazione, stop e prossimo invio.
La primitive GET restituisce JSON ma non archivia il risultato automaticamente.
La normalizzazione inline da sola non certifica successo o terminalità del job.
Dopo un create incerto senza ID, l'elenco è necessario per la riconciliazione;
non è ammesso risottomettere. Il recupero va collaudato offline prima del live.

### Parametri, capacità e costo

Tutte le 8832 richieste hanno identica generationConfig: temperature=0.7,
thinkingLevel=minimal, maxOutputTokens=1200, responseMimeType=application/json.
Nessun tool, grounding o cache esplicita. Non è impostato un seed di generazione;
202609140367 è il seed del design. topP/topK, safety e candidateCount non sono
esplicitati: dipendono dai default provider. JSON MIME non impone uno schema;
il parser locale è rigoroso e rifiuta output non conformi, versioni assenti e
finishReason diverso da STOP (incluso MAX_TOKENS), senza chiamarli astensioni.
I materiali sono riproducibili offline; identità bit-per-bit delle generazioni,
indipendenza dei cluster e stabilità del provider non sono certificabili dai mock.

Documentazione ufficiale consultata il 16 settembre 2026:
- [Modello](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite):
  Batch supportato, limiti 1048576 input e 65536 output. Non prova accesso progetto.
- [Guida Gemini 3](https://ai.google.dev/gemini-api/docs/gemini-3): minimal supportato
  ma non equivale a zero thinking; raccomandazione temperature=1.0 e possibili
  problemi sotto 1.0. Lo 0.7 preparato è mantenuto, non modificato automaticamente.
- [GenerateContent](https://ai.google.dev/api/generate-content) e
  [thinking](https://ai.google.dev/gemini-api/docs/thinking): la guida descrive un
  cap combinato thinking+risposta, ma nella sezione attuale Interactions API.
  La reference GenerateContent descrive maxOutputTokens per candidato. Esiste
  [un chiarimento sul forum Google](https://discuss.ai.google.dev/t/gemini-3-8-flash-high-does-maxoutputtokens-include-thinking-tokens/181077)
  sul cap combinato per 3.8 Flash generateContent, non un collaudo di questo
  3.1 Flash-Lite Batch. Evidenza favorevole, non certificazione specifica:
  output_cap_verified resta non soddisfatto. Un singolo test non proverebbe
  da solo un limite universale. Troncamenti possono essere fatturati.
- [Quote](https://ai.google.dev/gemini-api/docs/rate-limits): Tier 1 documentato
  100 batch concorrenti e 10000000 token accodati per 3.1 Flash Lite, distinti
  dalle quote ordinarie. Il massimo shard richiede 753451 token liberi; tier,
  capacità e occupazione effettive del progetto restano da verificare.
- [Batch](https://ai.google.dev/gemini-api/docs/batch-api) e
  [reference REST](https://ai.google.dev/api/batch-api): inline sotto 20 MB,
  creazione non idempotente; target 24 ore, possibile scadenza del job a 48 ore.
  Non inferire disponibilità indefinita dei risultati o successo della cancellazione.
  Manca ancora un piano approvato per rientro, archiviazione e recupero tardivo.
- [Prezzi](https://ai.google.dev/gemini-api/docs/pricing): Batch testo 0.125 USD/M
  input e 0.75 USD/M output, thinking incluso nel prezzo output; coincidono con
  le tariffe hardcoded nell'ammissione.

Stima per un solo tentativo delle 8832 richieste, senza servizi aggiuntivi:
input 0.7230625 USD; scenario 150 token fatturabili output/richiesta 1.7166625 USD;
scenario 1200 token complessivi thinking+risposta 8.6718625 USD, con margine 20%
10.406235 USD. Quest'ultimo resta un tetto condizionato al cap combinato, non una
certificazione di addebito massimo del progetto. Il ledger locale limita riserve
entro 30 USD ma non impone un hard cap cloud né conosce spese esterne pregresse.
Non liberare riserve per timeout, mancanza usage o cancellazione non riconciliata.
Spesa generativa di questa sessione: zero; saldo effettivo provider non verificato.

### Freeze finale e decisione

Design e addendum riportano ancora PREPARED_NOT_FROZEN. I sigilli conservano
l'integrità del pacchetto preparato, non attestano freeze operativo o lancio.
Nessun artefatto operativo verificato attesta tutti i gate: protocol_frozen,
launch_authorized, model_project_verified, batch_quota_verified,
token_count_verified, output_cap_verified, price_current,
billing_decision_recorded, retention_plan_confirmed; per il trasporto serve anche
repository_handoff_complete e per i main una riconciliazione controlli valida.
Non impostati gate reali. Nessun freeze aggiornato, timestamp finale o sigillo nuovo.

B1/B2 sono stati corretti nel successivo ciclo offline descritto sotto;
restano credenziale esterna, accesso/quota progetto e cap applicabile.
I 24 controlli reali restano non eseguiti e richiedono autorizzazione separata.
Nessuna chiamata fatturabile proposta/eseguita mentre restano blocker locali.

### Hardening operativo offline — 16 settembre 2026

Implementazione esterna al pacchetto sigillato in preflight/orchestration.py;
send_once usa ora questo percorso. Dettagli e limiti in preflight/HARDENING.md.
B1 risolto nel percorso operativo: ammissione dal rapporto completo archiviato,
job SUCCEEDED terminale, versione attesa, tutte le chiavi valide, usage e cap
coerenti, nessuna quarantena/errore/stop. controls_pass da solo non autorizza.
Gate, ordine dei main, identità del job e ledger devono essere coerenti.
Lo stato ambiguo blocca; uno stop persistito non viene revocato automaticamente.

B2 risolto offline: journal prima dell'invio, lock esclusivo, riserva conservata
anche su timeout, archivio JSON con hash, recupero via GET e riconciliazione
cumulativa per chiave. Il create incerto non viene ritentato. Elenco paginato
limitato e identità univoca permettono di cercare il job; elenco indisponibile o
ambiguo richiede revisione manuale. Cancel registra prima l'intento e non ripete
la richiesta; la risposta non prova terminalità né rimborso. Output tardivi
restano recuperabili senza doppia contabilizzazione o riapertura degli invii.
L'archivio conserva JSON ricevuto e normalizzato, non i byte HTTP originali.
Le primitive reali e la persistenza del runtime richiedono verifica operativa.

Suite completa tramite python -B preflight/run_offline_tests.py: 109 test,
zero failure/error/skip (50 operativi, 13 Batch, 6+6 planning, 17+17 storici).
Rete Python bloccata anche nei processi figli. Mock completo: 13 submission,
8832 chiavi, nessuna duplicazione, riserva totale sintetica 10.406235 USD.
Il runner risolve il common storico tramite il source già sigillato, senza
modificare le suite scientifiche. git diff --check superato.

SHA-256 ricalcolati integralmente: pilot 1479/1479, estensione 2152/2152,
protocollo 9/9, source-protocol 9/9, package 949/949, data 919/919.
Manifest di trasferimento originale: 4610/4615 corrispondenti; differenze attese
solo README.md (migrazione già committata), current-state.md, next-steps.md,
preflight/transport.py e preflight/test_transport.py. I nuovi file operativi sono
esterni al manifest originale. Nessun manifest, sigillo o file study modificato.

Readiness: codice operativo candidato alla revisione finale del freeze;
non dichiarato READY_FOR_FINAL_FREEZE finché restano le verifiche esterne.
PREPARED_NOT_FROZEN resta invariato. Nessuna chiamata reale, campagna, modifica
billing, commit o push nel ciclo. Lavoro locale su main, HEAD 29c1f2127e45f4a485cd175b68f6ff36101babd3.

### Chiusura con checkpoint Git locale

Autorizzato un commit dedicato all'hardening e alla documentazione, successivo
al checkpoint di migrazione sopra riportato, subordinato alla ripetizione della
suite offline completa e delle verifiche di integrità. Il suo hash è identificabile
dal log Git; non è inserito nel contenuto del commit stesso. Nessun push autorizzato.
Revisione del diff: soltanto ammissione, orchestration/recovery, persistenza,
idempotenza, test offline e documentazione; nessuna variazione sperimentale.
git fsck --full non rileva corruzione; quattro tree dangling non referenziati,
senza effetto sui file o sulla storia di main. Nessuna pulizia Git eseguita.
Prima di ogni verifica reale attendere conferma: prima eventuale push, poi
preflight online non generativo A; canary minimo B solo dopo A e autorizzazione
esplicita con scopo, dati, costo e risultato atteso. Nessun gate reale aperto.
