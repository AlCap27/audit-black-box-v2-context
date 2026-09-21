# Stato corrente — aggiornamento 21 settembre 2026

## Checkpoint di lancio v2 — quota del progetto verificata

Questo aggiornamento sostituisce lo stato NOT_READY sotto. Verifica diretta
Google AI Studio, progetto gen-lang-client-0393363402 selezionato, sezione API
Batch: Gemini 3.1 Flash Lite, Livello 1, 100 job simultanei, 10000000 token in
coda. GET completo aggiornato: solo controlli SUCCEEDED, zero job attivi.
Residuo calcolato 10000000 token, maggiore dei 753451 del main più grande.
I picchi storici 1 e 5.49K non sono stati trattati come occupazione corrente.
Evidenza in preflight/quota-20260921.json. Capacità VERIFIED_AT_CHECK;
nessuna promessa contro congestione o cambiamenti futuri del provider.

Freeze v2 READY_FOR_LAUNCH in preflight/freeze-20260921-v2.json, SHA-256
a1f9a3d5a31f6cb92f84b4cfa17b5ddca743dcbb1de2a7873e76e33142957541.
Piano preflight/FINAL-FREEZE-20260921-v2.md; parametri invariati, v1 preservata.
Snapshot privati runtime/codice in runtime/final-freeze-20260921-v2.
Economia invariata: 0.03 USD controlli, 29.97 residui, main 10.37945775 USD
con margine. 24 controlli riconciliati: nessun reinvio o nuova fatturazione.

L'utente ha autorizzato verifica, commit + push del freeze, poi avvio esperimento.
launch.py abilita esclusivamente i main dopo verifica degli hash del freeze,
stato economico e controlli; conserva il marker originale e archivia
l'approvazione. Nessun cambiamento al protocollo/gate sigillato. Prima di
ogni main richiede elenco API completo privo di job attivi. Il gate output
è supportato dalla documentazione GenerateContent, senza dichiarare una prova
di stress non eseguita. Nessun fallback o retry automatico.
Alla creazione del checkpoint nessun main è ancora inviato: attivazione solo
dopo push verificato e working tree pulito. Esito operativo successivo nel
runtime persistente, da controllare prima di qualunque tentativo di invio.
Suite completa offline prima del commit: 128 test PASS, zero errori/fallimenti/
skip, rete bloccata anche nei sottoprocessi. git diff --check PASS; tutti i
manifest/sigilli originali verificati integralmente senza discrepanze.
I record freeze JSON conservano terminatori Windows CRLF: la verifica staged
usa core.whitespace con cr-at-eol per preservarne gli hash; nessuno spazio
finale reale o errore di patch. Il controllo segreti sui 20 file del checkpoint
non rileva la chiave configurata né pattern di chiavi Google.

## Checkpoint finale della sessione: economia riconciliata e freeze locale

Questo aggiornamento prevale sulle sezioni storiche successive. Riconciliazione
economica autorizzata completata: 24 controlli conservati nello stesso tentativo,
costo stimato da usage 0.001836375 USD, accantonamento conservativo 0.03 USD,
budget operativo residuo 29.97 USD. Registro precedente archiviato; aggiornamento
atomico, idempotente, nessuna nuova submission o doppia contabilizzazione.
La fattura definitiva non è verificata: billing_reconciled resta false, mentre
budget_reconciled è true e lo stato economico è COMPLETED_ACCOUNTED.

Freeze locale finale in preflight/freeze-20260921.json, piano in
preflight/FINAL-FREEZE-20260921.md; snapshot runtime e codice in
runtime/final-freeze-20260921, entrambi verificati SHA-256 file per file.
SHA-256 del record freeze:
72733294f3d7f67f71071cccd85a1582ade755c544f3edfb2ac277c532954a36.
Parametri, 8832 chiavi e relative ricevute hash/token verificati; 8808 main,
5778785 token input, 8.649548125 USD al cap, 10.37945775 USD con margine 20%.
Sei manifest/sigilli originali verificati integralmente: zero discrepanze,
nessuna rigenerazione. Solo il nuovo snapshot operativo è stato creato.

Quattro nuovi test economici PASS con rete bloccata; suite precedente operativa
61/61 PASS. Il builder iniziale ha rifiutato la lettura con encoding Windows
implicito; dopo lettura UTF-8 esplicita tutte le ricevute combaciano. Nessun
payload, receipt o file sigillato è stato cambiato per superare il controllo.

Giudizio NOT_READY: capacità Batch residua del progetto NOT_VERIFIED e gate
sigillato batch_quota_verified non soddisfatto. Il freeze non converte questo
dato in true. Restano distinti il cap documentato e l'enforcement non provato al
confine. Journal EXTERNAL_REVIEW e marker impediscono nuovi invii; controlli
definitivamente riconciliati, da non ripetere. Commit/push del freeze e lancio
dei main sono gate successivi, ciascuno soggetto ad autorizzazione dell'utente.
Nessun commit, push, invio main, chiamata generativa o modifica billing.

## Ultimo aggiornamento: provenienza controlli e preparazione lancio

L'utente conferma che i controlli recuperati appartengono al test avviato il
20 settembre e interrotto nella sessione Codex. Google ha completato il job:
24/24 controlli validi. Non ripeterli. Manca ancora l'archivio originale del
payload per un confronto byte-per-byte; provenienza confermata dall'utente.

Screenshot Spesa: progetto audit black-box, Livello 1, grafico 0.00158 EUR,
totale arrotondato 0.00 EUR, nessun limite mensile numerico mostrato.
Questa evidenza aggiorna i riferimenti storici sotto a billing non attivato.
Ritardo dichiarato dei costi fino a 24 ore; nessuna modifica billing eseguita.

Piano concreto in preflight/LAUNCH-REVIEW-20260921.md: 12 main sequenziali,
8808 richieste, 10.37945775 USD con margine 20% più accantonamento proposto
0.03 USD per controlli. Budget globale 30 USD. Ledger effettivo ancora bloccato
con riserva 30 USD: nessuna riduzione o promozione automatica dei controlli.
Il job è ora adottato nel journal in modalità EXTERNAL_REVIEW, con validazione
completa dei 24 controlli dall'archivio GET e provenienza attestata dall'utente.
La procedura è offline, idempotente e riprendibile dopo interruzione; non crea
un payload originale fittizio. Conservati marker e riserva di 30 USD; il nuovo
blocco di modalità impedisce main e ripetizione controlli anche senza marker.
Restano riconciliazione della riserva, freeze operativo e autorizzazione finale
ai main. Capacità Batch residua
specifica del progetto NOT_VERIFIED; cap combinato documentato, non stressato
dal test. Nessuna nuova submission, modifica al pacchetto sigillato, commit o push.

GET elenco Batch aggiornato il 21 settembre: un solo job, i controlli conclusi;
nessuna pagina ulteriore o risorsa irraggiungibile riportata. Archivio lettura:
5732675ab96b3af52005d99278f1101e72aa8863e4b7cef68fc5867c9bba38f1.
Non equivale a verifica quota residua o fattura definitiva.
Backup locale verificato del runtime (9 file) e impronte del codice operativo:
runtime/checkpoints/20260921T081723Z. È un checkpoint di preparazione, non final
freeze né backup su un altro dispositivo. Sigilli ricontrollati: 1479 pilot,
2152 estensione, 9 protocollo, 9 copia protocollo, 949 pacchetto, 919 manifest
dati: zero discrepanze. Nessun sigillo rigenerato.
Suite operativa preflight rieseguita dopo l'adozione: 61/61 test PASS,
rete Python bloccata, zero errori. Include i 6 nuovi test di adozione.
Le suite storiche immutate non sono state ripetute in questa sessione.

Le sezioni seguenti conservano la cronologia; questo aggiornamento prevale
sulle indicazioni storiche relative a billing e assenza di job.

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

### Push hardening e preflight A parziale — 16 settembre 2026

Push autorizzato completato: main, origin/main e refs/heads/main letto da GitHub
coincidono con 2c920ede1c958105c3aff4188ac70a6613b8d3f5. Ahead/behind 0/0;
working tree pulito subito dopo il push. Solo dopo queste verifiche sono stati
aggiornati current-state.md e next-steps.md, lasciandoli non committati.

Preflight A autorizzato esclusivamente non generativo. Non completato sul progetto:
GEMINI_API_KEY, GOOGLE_API_KEY, GOOGLE_APPLICATION_CREDENTIALS e le variabili
progetto GOOGLE_CLOUD_PROJECT/GCLOUD_PROJECT/CLOUDSDK_CORE_PROJECT assenti nel
processo; gcloud non disponibile nel PATH. .env, credentials/, secrets/ e runtime/
assenti nel workspace. Nessuna ricerca di segreti altrove né chiave letta.
Richiesti all'utente project ID/numero atteso e percorso credenziale esterna o
sessione Google autenticata. Autenticazione, account/progetto effettivo, associazione
credenziale-progetto, tier, quota residua, job attivi, billing/saldo/spend cap:
NOT_VERIFIED. Non sono state effettuate richieste autenticate Google.

Il file model.json conserva l'evidenza storica del 15 settembre: modello
gemini-3.1-flash-lite, versione metadati 3.1-flash-lite-05-2026, metodo Batch.
Non è una verifica live attuale né prova del progetto associato; modelVersion
delle future risposte resta NOT_VERIFIED. Il trasporto riceve una API key e
non lega esplicitamente un project ID: tale associazione deve essere dimostrata.

Controllo locale su tutte le 8832 richieste: identica generationConfig con
temperature 0.7, maxOutputTokens 1200, responseMimeType application/json,
thinkingConfig.thinkingLevel minimal; nessun campo tools o cachedContent.
Confronto con documentazione ufficiale pubblica letto in questa sessione:
- [Scheda modello](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite):
  modello stabile, Batch supportato, limiti input 1048576/output 65536.
- [REST Batch](https://ai.google.dev/api/batch-api): endpoint v1beta configurato
  corrispondente, richieste GenerateContentRequest e generationConfig supportati.
  Nessuna submission usata per provare accesso o validazione del payload.
- [Guida GenerateContent](https://ai.google.dev/gemini-api/docs/generate-content/gemini-3):
  minimal supportato, non equivale a thinking disabilitato. Temperature 0.7
  resta nel range REST ma sotto il valore 1.0 raccomandato; nessuna modifica.
- [Thinking per GenerateContent](https://ai.google.dev/gemini-api/docs/generate-content/thinking):
  la sezione Token limits ora consultata specificamente per questo percorso
  descrive max_output_tokens come cap combinato thinking+output e troncamento
  MAX_TOKENS, con link alla reference GenerateContent. Supera il precedente
  limite documentale della sola guida Interactions. Poiché Batch accoda richieste
  generateContent, è evidenza documentale favorevole all'applicabilità di 1200;
  enforcement effettivo sul progetto e sull'esatto modello Batch: NOT_VERIFIED.
  Non aperto automaticamente output_cap_verified. I token input si pagano
  separatamente: 1200 NON è un limite di tutti i token fatturabili input+output.
- [Quote](https://ai.google.dev/gemini-api/docs/rate-limits): 100 job concorrenti
  e 10 milioni di token accodati per questo modello a Tier 1 sono valori
  pubblicati, non capacità osservata del progetto. Lo shard massimo richiede
  753451 token input secondo le ricevute archiviate. Nessuna quota modificata.
- [Billing](https://ai.google.dev/gemini-api/docs/billing): sono descritti cap
  mensili account/progetto, con ritardi e possibili superamenti per Batch.
  Non dimostrano un hard cap di 30 USD né billing attivo nel progetto corrente.

Discrepanze residue: le evidenze storiche non certificano l'ambiente corrente;
la guida generale Gemini 3 conserva indicazioni preview mentre la scheda modello
indica stable; usare il modello configurato senza fallback e verificare metadati
autenticati. Accettazione reale dei parametri, formato risposte e permessi Batch
restano NOT_VERIFIED. Nessun costo intenzionale, generazione, job, canary,
variazione quote/billing, codice, artefatto frozen, manifest o sigillo in questa fase.
Blocker immediato: accesso autenticato e identificativo del progetto atteso mancanti.
Fase A non superata; fermarsi prima di B e attendere i dati di accesso richiesti.

### Aggiornamento preflight A dopo configurazione credenziale

GEMINI_API_KEY disponibile nel processo, mai mostrata o salvata nel repository.
Due GET non generativi riusciti: metadati models/gemini-3.1-flash-lite e
batches?pageSize=1. Versione metadati 3.1-flash-lite-05-2026; limiti input
1048576/output 65536; thinking=true; batchGenerateContent fra i metodi supportati.
Elenco Batch vuoto, nessuna pagina successiva o indicazione unreachable.
Questo verifica autenticazione per tali letture, non diritto/capacità di submission.

Progetto atteso: audit black-box, ID gen-lang-client-0393363402, osservato nello
screenshot Google AI Studio fornito dall'utente. L'utente conferma che la chiave
configurata appartiene a questo progetto; associazione attestata dall'utente,
non verificata indipendentemente via API amministrativa. Nello screenshot:
Livello gratuito, Configura la fatturazione, spesa mensile '-'. Il trattino non
è interpretato come saldo o spesa zero. Nessuna configurazione billing modificata.

Restano NOT_VERIFIED: project number, account billing/saldo/limiti, quote Batch
effettive, permesso create, accettazione dei parametri e cap effettivo 1200 sul
Batch. Disponibilità documentale/metadati non prova capacità operativa sul free tier.
Prossimo dato minimo: limiti Batch osservabili per gemini-3.1-flash-lite nella
pagina Limitazione di frequenza del progetto indicato. Nessun canary autorizzato.
Solo current-state.md e next-steps.md aggiornati, non committati; nessun codice,
prompt, manifest o sigillo modificato. Nessuna nuova richiesta Google in questo
aggiornamento; le due letture sopra sono quelle già eseguite nella ripresa precedente.

### Ripresa 21 settembre 2026 — allineamento fra PC

L'utente comunica di avere attivato la fatturazione Google per questo progetto
e che sull'altro PC si era arrivati alla preparazione dei 24 controlli, con budget
complessivo massimo 30 USD. Billing attivo dichiarato dall'utente, non verificato
in questa sessione. Il precedente screenshot free tier è quindi storico.
Verifica locale: main a 2c920ede1c958105c3aff4188ac70a6613b8d3f5, soltanto
current-state.md e next-steps.md modificati; nessuna directory runtime locale.
L'assenza di runtime su questo PC non dimostra assenza di submission sull'altro.
Occorre acquisire l'ultimo checkpoint operativo dell'altra conversazione prima
di decidere qualsiasi invio: gate verificati, eventuale job ID e tentativo/ledger.
Nessuna nuova chiamata Google, generazione, submission, test, commit o push.

### Autorizzazione dei 24 controlli e verifica del percorso di invio

L'utente chiarisce che nessun nuovo lavoro è stato completato sull'altro PC.
Screenshot del progetto: limiti ordinari Gemini 3.1 Flash Lite 4000 RPM,
4000000 TPM, 150000 RPD; quota Batch non mostrata. Successivamente autorizza
esplicitamente un solo Batch dei 24 controlli entro il budget complessivo 30 USD,
senza main e senza retry automatico. Tale autorizzazione resta valida.

Verifica del codice prima di inviare: anche controls passa attraverso reserve()
nel batch_state.py sigillato, che richiede protocol_frozen, batch_quota_verified,
output_cap_verified e retention_plan_confirmed, oltre agli altri gate. Il wrapper
richiede inoltre expected_model_version esplicita, che non può essere ricavata
con certezza dalla sola versione dei metadati. Il percorso corrente non distingue
un test autorizzato per verificare assunzioni da una campagna già verificata.
Non impostati flag non dimostrati e non aggirato il percorso hardened.
Nessun POST, job o riserva creati. Occorre un percorso operativo di canary
esplicitamente separato, preservando journal, lock, budget e blocco permanente
dei main, oppure completare tutti i prerequisiti del percorso corrente.
La precedente proposta di poter inviare immediatamente i 24 controlli ometteva
questo vincolo operativo. Non è un problema di ulteriore consenso alla spesa.

### Esito effettivo del 21 settembre: controlli già eseguiti e recuperati

Autorizzata e implementata l'integrazione operativa canary, separata dai gate main,
senza toccare il pacchetto sigillato. Prima di inviare, Google ha mostrato un job
già concluso il 20 settembre: batches/bnse2tr3db6kvqm3mzp4uyru0d6h271pceqz,
abbv2-controls-20260920-01. Questo dato corregge l'ipotesi di nessun invio precedente.
Non è stato creato alcun nuovo Batch. Recupero via GET: 24/24 richieste riuscite;
riconciliazione locale 24/24 controlli validi, zero quarantena, tutte STOP.
Versione effettiva gemini-3.1-flash-lite, input 5715, output 1496, totale 7211;
thinking separato non riportato. Stima costo usage 0.001836375 USD, non fattura.

Dettagli, provenienza, limiti e percorsi delle prove in preflight/CANARY-20260921.md.
Runtime persistente runtime/audit-v2 escluso da Git; marker external-job.json
impedisce nuovi invii. Ledger ricostruito trattiene 30 USD fino a revisione manuale.
Manca l'archivio originale della submission: corrispondenza delle 24 chiavi e input
non equivale a prova byte-per-byte del payload originariamente inviato.
Main e final freeze restano bloccati. Suite operativa offline: 55/55 PASS.
Nessun nuovo costo generativo in questa sessione, nessun commit o push.
