# Freeze operativo finale — 21 settembre 2026

Ambito: snapshot immutabile locale di codice operativo, configurazioni, piano,
parametri e runtime dopo riconciliazione economica dei controlli. Il pacchetto
sperimentale e i suoi manifest/sigilli originali restano invariati.

## Controlli e budget

24 controlli conclusi, validi, adottati e riconciliati nel journal. Non ripetere,
rigenerare o reinviare. Il limite Codex non annulla un job provider.
Costo da usage: 0.001836375 USD. Accantonamento locale conservativo applicato:
0.03 USD. Budget residuo: 29.97 USD su tetto globale 30 USD. Il flag di fattura
definitiva resta falso; nessun rimborso o modifica billing è stato effettuato.
Registro originale archiviato prima della mutazione atomica. Ripetere la stessa
riconciliazione non cambia saldo, chiavi o stato; prove diverse vengono rifiutate.
Non rieseguire l'adozione iniziale, che richiedeva il vecchio registro da 30 USD.

## Piano congelato

Un solo modello: gemini-3.1-flash-lite. Versione attesa nelle risposte:
gemini-3.1-flash-lite. Nessun fallback, nessun retry automatico.
Parametri: temperature 0.7, maxOutputTokens 1200, thinkingLevel minimal,
responseMimeType application/json. Tutti i parametri aggiuntivi restano quelli
dei payload sigillati; i default provider non esplicitati non garantiscono
riproducibilità bit-per-bit. L'alias modello non equivale a snapshot provider
immutabile; controllare modelVersion su ogni risposta e fermarsi se cambia.

12 Batch principali sequenziali main-00…main-11, 734 richieste ciascuno:
8808 generazioni, 5778785 token input da ricevute esatte. Stima al cap output:
8.649548125 USD, 10.37945775 USD includendo margine 20%. Con accantonamento
controlli: 10.40945775 USD. Nessun rinnovo automatico o invio concorrente.
Prezzi di riferimento verificati il 21 settembre: 0.125/0.75 USD per milione
input/output Batch. Ricontrollare prima del lancio se cambia giorno/listino.

Prima di ogni invio: verificare hash congelati, autorizzazione finale, tutti i
gate di ammissione e costo riservato. Dopo ogni invio conservare job ID, risposta
create, journal e ledger; recuperare via GET e riconciliare completamente prima
del main successivo. Qualsiasi errore, parziale, troncamento, versione inattesa,
usage mancante, cap superato o stato incerto blocca gli invii successivi.
L'incertezza trattiene la riserva: non equivale a fallimento e non consente retry.
Alla ripresa usare lo stesso runtime; mai creare un runtime vuoto per reinviare.

## Gate ancora chiusi

Capacità Batch residua specifica del progetto: NOT_VERIFIED. La lettura elenco
completa archiviata mostra solo il job controlli concluso, ma non espone quota
residua. Il Tier 1 osservato e la quota pubblicata non costituiscono una misura
per il progetto. Non effettuare una submission per sondarla e non ripetere i
controlli. Il massimo main richiede 753451 token input accodabili.

Il percorso sigillato di ammissione esige batch_quota_verified=true e un numero
di token disponibili verificato. Non attribuire questi valori per inferenza.
Il cap 1200 pensiero+risposta è documentato, non provato al confine dal canary.
L'associazione credenziale/progetto è attestata dall'utente, non da API admin.
Queste distinzioni sono preservate; nessun gate viene dichiarato vero dal freeze.

Giudizio di lancio: NOT_READY, per capacità residua non verificata e conseguente
gate quota non soddisfatto. Lo snapshot operativo è congelato; il runtime vivo
mantiene external-job.json e modalità EXTERNAL_REVIEW, senza autorizzare main.
Se le evidenze o il piano cambiano, creare un nuovo snapshot operativo, senza
riscrivere questo né i sigilli sperimentali. Il freeze non approva eccezioni.

Commit e push del checkpoint sono un gate esplicito prima della campagna:
non eseguiti, in attesa di autorizzazione. Anche dopo il push occorre la distinta
autorizzazione finale ai main. Nessun documento costituisce una submission.

## Conservazione e verifiche

freeze-20260921.json contiene impronte SHA-256 di codice operativo, ricevute,
configurazioni, piano, manifest/sigilli e runtime, con conteggi e costi ricalcolati.
Lo snapshot privato del runtime è in runtime/final-freeze-20260921/runtime.zip,
verificato file per file. Il runtime non va pubblicato automaticamente in Git;
la copia locale protegge dalle interruzioni, non dalla perdita del dispositivo.
Prima della campagna conservare una copia privata anche su altro dispositivo.

Quattro test economici nuovi PASS con rete bloccata: idempotenza, crash prima
della scrittura, rifiuto stato incompleto, autorizzazione/evidenza discordanti.
Suite operativa precedente 61/61 PASS; codice di submission non cambiato in
questa fase. Verifica completa dei sei manifest/sigilli senza rigenerazione.
