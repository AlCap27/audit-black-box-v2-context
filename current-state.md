# Stato corrente — 16 settembre 2026

## Decisioni attuali

L'utente ha autorizzato di procedere con i passaggi proposti: design367assegnazioni,
8808generazioni+24controlli, fattoriale S/L/T, primaria L totale α.025 e secondarie
α.003125. La garanzia conservativa90% aΔ5pp richiede cluster indipendenti e dati
completi; non vale automaticamente per il condizionato. Retrieval sulle367assegnazioni.
Questa approvazione supera lo stato “proposto” nei documenti storici, che restano
immutati. Freeze operativo finale dopo preflight; nessuna registrazione pubblica fatta.

Sono approvati Batch, modello3.1flashlite senzafallback, limite30USD incluse prove e
tentativi, Astra soltanto. Prima della campagna: fermarsi e rendere la repository
fonte di verità per il trasferimento al [rimosso]. Nessuna modifica VPS/DNS.
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
study/ non sono modificati. Il commit documentale di migrazione segue il commit
importato sulla stessa storia di main. Nessun push degli aggiornamenti eseguito;
la pubblicazione di questo commit locale richiede conferma esplicita.

Questa sessione autorizza solo trasferimento, verifica e aggiornamento documentale.
Nessuna chiamata Google, invio Batch, attivazione fatturazione o controllo reale
eseguito. I test scientifici/offline precedenti non sono stati rieseguiti: qui sono
stati ricalcolati gli hash. Attendere conferma prima di altre attività operative;
il trasferimento non certifica quota, cap output, freeze o autorizzazione al lancio.

Nessun link condiviso del thread creato, poiché il registro grezzo contiene
[rimosso]; l'export depurato è disponibile nella repository.
