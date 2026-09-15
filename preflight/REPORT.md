# Preflight15settembre2026

GetModel riuscito con la chiave del progetto: modello gemini-3.1-flash-lite,
versione metadati3.1-flash-lite-05-2026, metodo batchGenerateContent disponibile.
ElencoBatch leggibile e vuoto. Queste letture non certificano quota/diritto create.

CountTokens riuscito per1834payload unici. Gli8832requestID sono riconciliati per
hash con lo stesso payload (nessuna approssimazione per conteggi riutilizzati).
Totaleinput5.784.500token.1834chiamate di conteggio,2GET,**zero generazioni**.
Nessun limite500RPD ordinario usato per dimensionare la campagnaBatch.

ListinoBatch0,125USD/Minput,0,75USD/Moutput. Scenario150output/richiesta:1,716663USD.
Scenario1200output/richiesta:8,671863USD; con20%margine10,406235USD.
Il conteggioinput ora è effettivo; il cap complessivo thinking+risposta resta
da validare. Non dichiarare questo scenario un massimo assoluto certificato.
Fonti: https://ai.google.dev/api/tokens e https://ai.google.dev/api/generate-content

Trasporto `transport.py` implementato separatamente dal pacchetto sigillato:
converteJSONL in batchinline <20MB preservando ogni key inmetadata; nessuna modifica
ai prompt. Riserva budgetprimaPOST, conserva rawcreate e jobid, lascia tentativi
incerti prenotati, non ripete su timeout. NessunaCLI live attivata.4testmock passati.
Il controllo quota/cap, freeze e handoffrepo sono chiusi: nessun job creato.

Verifiche residue: capacità batch effettiva sulprogetto; limite fatturabile output;
eventuale fatturazione; collaudo reale24controlli; versione effettiva nelle risposte.
Le versioni delmetadatoGET e modelVersion della risposta non sono necessariamente
la stessa stringa. Registrare entrambe senza equipararle a priori.

L'invioMain resta vietato sino a freeze/preflight/handoff e autorizzazione finale.
Lettura della documentazione non ha risolto il capthinking con sufficiente certezza:
non impostare output_cap_verified=true per comodità.
