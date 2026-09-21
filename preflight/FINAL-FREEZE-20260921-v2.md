# Freeze operativo finale v2 — 21 settembre 2026

Sostituisce come piano di lancio la v1 NOT_READY, che resta immutata.
Non modifica alcun artefatto sperimentale, parametro, manifest o sigillo originale.

## Capacità risolta

Verifica diretta nella sezione API Batch di Google AI Studio, con progetto
gen-lang-client-0393363402 / audit black-box selezionato: Gemini 3.1 Flash Lite,
Livello 1, limite 100 job simultanei e 10000000 token batch in coda.
I valori 1 e 5.49K sono picchi storici, non occupazione corrente.
GET completo aggiornato: un solo job, controlli già SUCCEEDED, zero job attivi,
nessuna pagina ulteriore. Quota residua calcolata: 10000000 token, contro
753451 necessari al main più grande. Evidenza in quota-20260921.json.
VERIFIED_AT_CHECK non è una promessa di disponibilità futura del provider.
Ripetere solo la lettura elenco prima di ogni main; se compare un job attivo,
se l'elenco è incompleto o se la richiesta viene rifiutata, arrestare gli invii.

## Piano e contabilità

24 controlli già completati, validi, adottati e contabilizzati una sola volta.
Nessun reinvio, nuovo test o retry. Costo stimato da usage 0.001836375 USD;
accantonamento applicato 0.03 USD, budget residuo 29.97 USD. Fattura definitiva
non attestata. Il registro originale e il marker esterno vengono preservati.

12 main sequenziali main-00…main-11, 734 richieste ciascuno: 8808 generazioni.
Input esatto 5778785 token. Scenario al cap 8.649548125 USD;
10.37945775 USD con margine 20%; totale con controlli accantonati 10.40945775 USD.
Tetto 30 USD comprese prove e tentativi; nessuna riserva incerta viene liberata.
Prezzi Batch .125 input / .75 output USD/M verificati il 21 settembre.

Modello esclusivo gemini-3.1-flash-lite; versione risposte attesa omonima.
Temperature 0.7, maxOutputTokens 1200, thinkingLevel minimal, JSON output.
Cap combinato thinking+risposta verificato documentalmente, non stressato al
confine dal canary. Gli alias e i default del provider non garantiscono identità
bit-per-bit. I parametri e i prompt dei payload sigillati restano identici.

## Attivazione ed esecuzione

L'utente ha autorizzato verifica, commit + push del freeze, poi avvio esperimento.
Attivare esclusivamente dopo aver verificato commit remoto uguale a HEAD e
working tree pulito. launch.activate controlla hash di codice, runtime e stato
economico/controlli; archivia l'approvazione e promuove il journal a CAMPAIGN.
Solo allora rinomina il marker esterno conservandolo; interruzione tra scritture
resta bloccante e riprendibile. Nessun payload originale fittizio è creato.

launch.submit_main rifiuta controls, richiede elenco Batch completo senza job
attivi e passa attraverso l'ammissione canonica esistente, senza modificare
il protocollo sigillato. Riserva atomica prima del singolo POST. Main successivo
solo dopo riconciliazione completa del precedente. Errori, parziali, troncamento,
versione inattesa, usage mancante, cap superato, timeout o stato incerto fermano
la sequenza. Nessun retry automatico. Recupero mediante GET del job persistito.

Conservare runtime/audit-v2 e lo snapshot privato runtime/final-freeze-20260921-v2.
Non inizializzare uno stato vuoto dopo stop Codex; il provider può continuare.
La copia locale non sostituisce un backup su altro dispositivo. Nessun segreto
in Git; freeze pubblico contiene impronte dei file, non credenziali o runtime.

READY_FOR_LAUNCH dopo verifiche del checkpoint e pubblicazione; gli artefatti
precedenti restano storici. launch-gates.json esplicita l'origine di ogni gate.
Una modifica successiva al codice/parametri richiede nuovo snapshot operativo.
