# Prossime attività — 16 settembre 2026

Checkpoint di partenza pubblicato: `29c1f2127e45f4a485cd175b68f6ff36101babd3`,
main con upstream origin/main. Migrazione pubblicata e verificata; non ripeterla.
Hardening offline B1/B2 implementato: dettagli in current-state.md e preflight/HARDENING.md.
Suite completa: 109/109 test superati, nessun errore o skip; sigilli invariati.
Astra è l'assistente; Gemini 3.1 Flash-Lite resta il generatore Batch, come
confermato dall'utente. Nessun cambio di modello o protocollo autorizzato.

1. **Dopo il commit locale di hardening fermarsi e attendere conferma per il push.** B1/B2 corretti
   tramite orchestration esterna: rapporto completo per ammissione, journal,
   archivio JSON/hash, recupero GET/list, cancel singolo, stop persistente.
   Test e mock offline documentati; nessuna prova di accettazione reale provider.
   Approvare il codice e il piano di persistenza/backup runtime prima del freeze.
   Non usare direttamente le primitive legacy sigillate per inviare lavori.
   Dopo il push autorizzato, separare la fase successiva in A: preflight online
   non generativo (autenticazione, progetto, modello/versione, quota, Batch,
   billing/saldo/limiti ed endpoint), e B: canary minimo soltanto dopo A e
   autorizzazione esplicita. Nessuna generazione o modifica billing/quote in A.
   Questo checkpoint non autorizza né A né B.
2. Il pacchetto study/batch-preparation-20260914 è sigillato e invariato.
   Conservare l'integrazione operativa esterna; non modificare
   protocollo, prompt, manifest o sigilli originali. Se serve rigenerare un
   manifest/sigillo, fermarsi e chiedere autorizzazione prima di farlo.
3. Individuare una credenziale del progetto fuori Git, senza inviarla in chat.
   Le variabili GEMINI_API_KEY/GOOGLE_API_KEY del processo sono assenti.
   Verificare progetto, tier e quota Batch effettiva, separata dai 500 RPD ordinari;
   servono almeno 753451 token liberi per il main più grande. La quota pubblicata
   per Tier 1 non attesta la quota del progetto. Nessuna modifica fatturazione.
4. Chiarire l'applicabilità del cap complessivo 1200 thinking+risposta al modello
   3.1 Flash-Lite sull'endpoint Batch prima di dichiarare un massimo garantito.
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
6. Solo dopo risoluzione blocker e autorizzazione separata: 24 controlli reali
   come job distinto, verifica versione/usage/formato e riconciliazione completa,
   inclusi output tardivi. Qualunque anomalia blocca i main. Per qualsiasi prova
   potenzialmente fatturabile, prima presentare scopo, necessità, costo massimo,
   dati inviati e risultato atteso; nessuna chiamata autorizzata da questo file.
7. Campagna principale soltanto dopo autorizzazione finale esplicita: 12 job da
   734 richieste, totale 8808 generazioni principali oltre ai 24 controlli.
   Nessun lancio o push effettuato nel presente preflight. Il checkpoint dedicato
   all'hardening è autorizzato solo localmente; push dopo ulteriore conferma.

Non cambiare modello, Δ, primaria, esclusioni o pipeline per ottenere significatività.
Non risottomettere richieste il cui tentativo precedente non sia riconciliato.
Non attivare o modificare fatturazione, infrastruttura, VPS, DNS o domini.
