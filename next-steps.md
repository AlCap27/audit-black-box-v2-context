# Prossime attività — aggiornamento 22 settembre 2026

## Analisi offline completata — prossimo passo: revisione del report

Leggere analysis/results-20260922/REPORT.md e le tabelle/provenienze collegate.
Controllo umano di un campione di parsing: ESEGUITO (70 casi, seed 20260922,
zero discrepanze; vedi REPORT.md e review/review-giudizi.csv). Prima della
diffusione resta la revisione scientifica/metodologica indipendente delle
assunzioni; non cambiare test, esclusioni o soglie in base ai risultati.
Commit/push dell'analisi e delle note autorizzati il 22 settembre;
archivio della raccolta incluso in review/ per trasferimento e revisione.
Su un altro PC usare clone/pull e review/README.md, senza riavviare il runner.
Nessuna generazione o nuovo Batch necessario; non ripetere controlli o main.
Fattura finale ancora da confrontare con la stima usage di 1.24666525 USD;
nessun rilascio automatico della riserva. Le attività di raccolta sotto sono
storiche e superate da questo stato.

## Raccolta conclusa — non avviare altri Batch

12/12 main conclusi e riconciliati, 8808/8808 validi, zero quarantena; controlli
24 originali, mai ripetuti. Driver terminato con successo. Stato autorevole:
runtime/audit-v2/operations.json e collection-summary.json. Nessun job da
reinviare o driver da riavviare. Le indicazioni di polling sotto sono storiche.
Conservazione locale e analisi statistica del protocollo frozen completate,
senza modifiche a esclusioni, ipotesi, soglie o prompt.
Costo stimato complessivo 1.24666525 USD, fattura finale non verificata;
riserva locale 10.40945775 USD ancora conservata. Nessun nuovo commit/push.

## Driver attivo — non duplicare la sequenza

runtime/continue_campaign.py prosegue i main autorizzati in sequenza; processo
54773, letture ogni 30s, limite un'ora, nessun retry POST. Ultimo checkpoint:
main-00 e main-01 validi (1468 risultati); main-02 RUNNING. Non avviare un
secondo driver: verificare prima processo e journal, che possono essere più
avanzati di queste note. Se il driver si ferma, recuperare il job pendente;
se è halted, indagare senza ripetere generazioni o modificare protocollo.
Questa nota sostituisce l'indicazione precedente di assenza polling automatico.

## Campagna avviata: recuperare main-00, non reinviarlo

Freeze pubblicato f7606d529d0a4c44f628eb11286c8b6d1088747d.
main-00 è già inviato: batches/8sme2gcrcsvztcpvv0w1c85mrlg17ark5ebv,
tentativo audit-v2-main-00, 734 richieste. Ultimo GET RUNNING.
Alla ripresa eseguire solo recover_once sul runtime/audit-v2 esistente; se
completato, verificare rapporto completo. Solo allora main-01, secondo
l'autorizzazione e il piano sequenziale già registrati. Nessun controllo da
ripetere, nessun retry del main-00 e nessun runtime nuovo.
La sessione non ha lasciato un processo di polling o invio automatico attivo.

## Ripresa dal freeze v2 READY_FOR_LAUNCH

Quota verificata nella sezione API Batch del progetto: 10000000 token,
100 job; elenco completo senza job attivi. Non ripetere questa indagine né
i 24 controlli. Prima di ogni main basta la nuova lettura completa dei job;
se la quota/tier del progetto cambia occorre una nuova verifica.
L'utente autorizza commit + push del freeze operativo e poi la campagna.
Pubblicare il checkpoint, verificare origin/main = HEAD e working tree pulito,
poi attivare tramite preflight/launch.py sul runtime/audit-v2 esistente.
Il file preflight/freeze-20260921-v2.json e launch-gates.json definiscono lo
stato approvato; i main sono 12, sequenziali, da main-00 a main-11.
Prima di inviare controllare journal/ledger: se il tentativo esiste recuperarlo,
non reinviarlo. Nessun main successivo prima del rapporto completo del precedente.
In caso di stop Codex il job provider può proseguire; recupero GET dal job ID
persistito. Nessun retry, fallback o modifica dei prompt per aggirare anomalie.
Le sezioni successive sono storia e non revocano questa autorizzazione.

## Punto di ripresa attuale — prevale sulle note storiche sotto

Economia riconciliata e freeze locale completati. Non rifare adozione, controlli
o riconciliazione: 0.03 USD accantonati, 29.97 USD residui, main stimati
10.37945775 USD con margine. Vedere preflight/FINAL-FREEZE-20260921.md e
preflight/freeze-20260921.json. Backup privato runtime e codice verificato in
runtime/final-freeze-20260921. Non sovrascrivere lo snapshot.

Blocker attuale: capacità Batch residua NOT_VERIFIED; il percorso sigillato
richiede batch_quota_verified=true e available_batch_tokens verificato.
Acquisire evidenza non generativa specifica del progetto, se disponibile;
altrimenti mantenere NOT_VERIFIED e NOT_READY. Non sondare con nuovi controlli
o main, non usare la quota pubblicata come misura della capacità residua e
non modificare il gate/protocollo senza autorizzazione.

Prima della campagna: autorizzazione per commit + push del freeze operativo,
copia privata runtime anche su altro dispositivo, poi distinta autorizzazione
finale ai main. Nel frattempo nessun commit/push o lancio autorizzato.

Revisione aggiornata: preflight/LAUNCH-REVIEW-20260921.md. Provenienza del test
del 20 settembre ora confermata dall'utente; non ripetere i controlli.
Livello 1 e spesa 0.00158 EUR nel grafico osservati nello screenshot Spesa.
Completata adozione esplicita del job esterno nel journal EXTERNAL_REVIEW,
con contabilizzazione unica e conservazione del blocco. GET lista aggiornato:
solo i controlli conclusi, nessun altro job visibile. Backup runtime verificato
in runtime/checkpoints/20260921T081723Z. Non ripetere questi passaggi.
Prossimo passaggio: revisione della riserva (0.03 USD proposti per i controlli,
non ancora applicati), chiusura delle evidenze residue e freeze operativo;
poi autorizzazione finale ai main. Non cancellare marker o cambiare modalità
del journal per aggirare questa sequenza.

Priorità: non inviare altri controlli. Il 21 settembre è stato recuperato il job
batches/bnse2tr3db6kvqm3mzp4uyru0d6h271pceqz già riuscito il 20 settembre:
24/24 controlli validi. Nessun nuovo POST. Vedere preflight/CANARY-20260921.md.
Il percorso canary separato è implementato e testato; external-job.json blocca
nuove submission. Conservare runtime/audit-v2 e non creare runtime vuoti per retry.
Prima dei main: revisione della provenienza dell'invio originale, riconciliazione
budget/billing, capacità Batch per campagna, piano di recupero, freeze e nuova
autorizzazione esplicita. Non promuovere automaticamente il test a campagna.

Checkpoint hardening pubblicato: `2c920ede1c958105c3aff4188ac70a6613b8d3f5`,
main con upstream origin/main. Migrazione pubblicata e verificata; non ripeterla.
Hardening offline B1/B2 implementato: dettagli in current-state.md e preflight/HARDENING.md.
Suite completa: 109/109 test superati, nessun errore o skip; sigilli invariati.
Astra è l'assistente; Gemini 3.1 Flash-Lite resta il generatore Batch, come
confermato dall'utente. Nessun cambio di modello o protocollo autorizzato.

1. **Push hardening completato; preflight A parziale, letture autenticate riuscite.** B1/B2 corretti
   tramite orchestration esterna: rapporto completo per ammissione, journal,
   archivio JSON/hash, recupero GET/list, cancel singolo, stop persistente.
   Test e mock offline documentati; nessuna prova di accettazione reale provider.
   Approvare il codice e il piano di persistenza/backup runtime prima del freeze.
   Non usare direttamente le primitive legacy sigillate per inviare lavori.
   Proseguire solo le letture autorizzate della fase A: preflight online
   non generativo (autenticazione, progetto, modello/versione, quota, Batch,
   billing/saldo/limiti ed endpoint), e B: canary minimo soltanto dopo A e
   autorizzazione esplicita. Nessuna generazione o modifica billing/quote in A.
   Un Batch di controlli era autorizzato, ma non è stato inviato perché quello
   preesistente è stato trovato e recuperato. Il confronto documentale è completato,
   GET modello e lista Batch riusciti; quote e capacità effettive NOT_VERIFIED.
   Lo screenshot precedente mostrava Livello gratuito; il 21 settembre l'utente
   comunica billing attivato. Nessuna ulteriore modifica billing autorizzata.
2. Il pacchetto study/batch-preparation-20260914 è sigillato e invariato.
   Conservare l'integrazione operativa esterna; non modificare
   protocollo, prompt, manifest o sigilli originali. Se serve rigenerare un
   manifest/sigillo, fermarsi e chiedere autorizzazione prima di farlo.
3. GEMINI_API_KEY configurata e valida per le due letture; progetto
   gen-lang-client-0393363402 (audit black-box), associazione chiave confermata
   dall'utente e non verificata via API amministrativa. Non richiedere la chiave.
   Acquisire solo i limiti Batch visibili per il modello nella pagina
   Limitazione di frequenza di questo progetto; nessuna modifica o generazione.
   Verificare progetto, tier e quota Batch effettiva, separata dai 500 RPD ordinari;
   servono almeno 753451 token liberi per il main più grande. La quota pubblicata
   per Tier 1 non attesta la quota del progetto. Nessuna modifica fatturazione.
4. Chiarire l'applicabilità del cap complessivo 1200 thinking+risposta al modello
   3.1 Flash-Lite sull'endpoint Batch prima di dichiarare un massimo garantito.
   La guida specifica GenerateContent ora conferma documentalmente il cap
   combinato; enforcement sul progetto Batch NOT_VERIFIED. Input escluso dal cap.
   Prezzi documentati riconfermati: 0.125/0.75 USD per milione input/output.
   Scenario completo 8.6718625 USD, 10.406235 USD con margine 20%, condizionato
   al cap e a un solo tentativo; tetto progetto 30 USD incluse prove/tentativi.
   Validare saldo/spese e policy per usage assente/tentativi incerti.
5. Freeze operativo finale ancora mancante: preservare temperature 0.7,
   thinking minimal, maxOutputTokens 1200, prompt e parametri del disegno.
   Documentare default provider e versione attesa, rischi di troncamento e
   variabilità generativa; non cambiare parametri per fare passare i controlli.
   Formalizzare hash di input/codice/config, gate, timestamp privato e piano
   di rientro/download/archivio e recupero. OSF solo con autorizzazione esplicita.
6. I 24 controlli reali sono recuperati e validi; non ripeterli. Verificare
   provenienza della submission originale e decidere l'utilizzabilità del test
   per il freeze. Qualunque anomalia blocca i main. Per qualsiasi ulteriore prova
   potenzialmente fatturabile, prima presentare scopo, necessità, costo massimo,
   dati inviati e risultato atteso; nessuna chiamata autorizzata da questo file.
7. Campagna principale soltanto dopo autorizzazione finale esplicita: 12 job da
   734 richieste, totale 8808 generazioni principali oltre ai 24 controlli.
   Push del solo checkpoint hardening completato. Nessun lancio. Gli aggiornamenti
   documentali della fase A restano non committati; nessun ulteriore push autorizzato.

Non cambiare modello, Δ, primaria, esclusioni o pipeline per ottenere significatività.
Non risottomettere richieste il cui tentativo precedente non sia riconciliato.
Non attivare o modificare fatturazione, infrastruttura, VPS, DNS o domini.
