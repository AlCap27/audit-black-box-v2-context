# Revisione di lancio — 21 settembre 2026

Stato: PREPARAZIONE OPERATIVA, NON AUTORIZZA SUBMISSION.

## Evidenze e provenienza

L'utente conferma che il payload dei controlli appartiene al test avviato il
20 settembre e interrotto nella sessione Codex per limite di utilizzo.
Il job Google è invece terminato con successo: 24/24 controlli validi,
senza quarantena, tutti STOP. Dettagli e archivio in CANARY-20260921.md.
Non ripetere i controlli. La conferma dell'utente attesta la provenienza;
non sostituisce il confronto byte-per-byte, impossibile senza il payload originale.

Lo screenshot Spesa del progetto audit black-box mostra Livello 1 e un costo
di 0,00158 EUR nel grafico del 20–21 settembre; il totale arrotondato è 0,00 EUR.
Il limite mensile mostra un trattino. Non risulta quindi provato un tetto di
spesa Google di 30 USD. La pagina avverte di ritardi fino a 24 ore sui costi.
Il progetto atteso è gen-lang-client-0393363402; l'associazione della chiave
resta confermata dall'utente, non verificata tramite API amministrativa.

## Piano e budget proposto

- Generatore invariato: gemini-3.1-flash-lite; versione osservata nelle risposte:
  gemini-3.1-flash-lite. Nessun fallback.
- 12 main sequenziali, 734 richieste ciascuno: 8808 generazioni.
- Input dei main da ricevute countTokens: 5778785 token.
- Parametri invariati: temperature 0.7, thinking minimal, maxOutputTokens 1200.
- Listino Batch verificato: 0.125 USD/M input, 0.75 USD/M output.
- Scenario main al cap: 8.649548125 USD; con margine 20%: 10.37945775 USD.
- Accantonamento proposto per controlli già completati: 0.03 USD, maggiore
  della stima da usage di 0.001836375 USD. Non è una riconciliazione contabile.
- Totale pianificato con tale accantonamento: 10.40945775 USD, entro 30 USD.

Il registro reale resta invariato, con 30 USD trattenuti per il job recuperato.
Nessun rilascio automatico della riserva. Eventuali altre spese o tentativi
incerti devono restare inclusi nel budget complessivo.

## Capacità e limite output

La [tabella ufficiale](https://ai.google.dev/gemini-api/docs/rate-limits)
riporta per Tier 1 e questo modello 10 milioni di token Batch accodati e
100 job concorrenti. Il main più grande richiede 753451 token input.
Il Tier 1 è osservato nello screenshot; la capacità residua specifica del
progetto non è osservata. Le quote RPM/TPM/RPD ordinarie non la sostituiscono.

La [guida GenerateContent](https://ai.google.dev/gemini-api/docs/generate-content/thinking)
documenta max_output_tokens come limite complessivo di pensiero e risposta.
Questa è evidenza documentale: i controlli, con massimo 91 token riportati,
non hanno esercitato il confine 1200. Non dichiarare enforcement misurato al
confine, né un limite di fatturazione garantito. Input escluso da tale cap.

## Passaggi operativi ancora necessari

Aggiornamento: il punto 1 è completato da adopt_controls.py. Il journal conserva
modalità EXTERNAL_REVIEW, report riconciliato, riferimento all'archivio originale
GET e attestazione utente; nessun payload di submission ricostruito viene
presentato come originale. Marker e budget restano intatti. Sei regressioni
dedicate coprono idempotenza, ripresa dopo crash, provenienza/identità, risultati
incompleti, conflitti del journal/budget e archivio corrotto; nessuna rete.
GET elenco aggiornato: soltanto il job controlli concluso, senza altre pagine.
Backup locale runtime verificato in runtime/checkpoints/20260921T081723Z.
Restano i punti 2–4; la copia locale non protegge dalla perdita del dispositivo.

1. Integrare il job esterno nel journal con una procedura esplicita e testata
   di adozione, conservando archivio, provenienza e contabilizzazione unica.
   Non cancellare external-job.json per eludere il blocco; non inizializzare
   un runtime vuoto e non risottomettere i controlli.
2. Riconciliare la riserva sulla base della revisione, senza chiamarla rimborso,
   e verificare eventuali altri job/spese pendenti mediante sole letture.
3. Chiudere il freeze operativo di codice, configurazione e versione attesa;
   preservare manifest e sigilli originali. Conservare una copia recuperabile
   del runtime, incluse ricevute, journal e ledger, prima delle submission.
4. Presentare l'approvazione finale del lancio dei main con eventuali limiti
   ancora NOT_VERIFIED chiaramente indicati. Questo documento non la concede.

Ogni main successivo richiede riconciliazione completa del precedente.
Errore, parziale, versione inattesa, usage mancante, superamento cap, troncamento
o stato incerto bloccano gli invii successivi. Nessun retry automatico.
Un limite di utilizzo Codex non annulla un job Google: alla ripresa recuperare
il job persistito tramite GET prima di prendere qualsiasi decisione di invio.
