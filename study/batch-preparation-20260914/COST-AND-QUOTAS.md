# Preventivo e quote — verifiche 14 settembre 2026

## Prezzi documentati e disponibilità

Per gemini-3.1-flash-lite il listino Batch consultato riporta **0,125 USD/M token
input e 0,75 USD/M output, incluso thinking**. Nella colonna free il listino oggi
indica gratuità; questo non certifica l'abilitazione batch del singolo progetto.
Il preventivo usa integralmente il prezzo paid, senza fare affidamento su crediti
gratuiti. [Listino Google](https://ai.google.dev/gemini-api/docs/pricing).

La scheda del modello indica Batch supportato. Il livello minimal è supportato ma
non garantisce zero thinking. Non è previsto cambio automatico di modello.
[Modello](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite),
[parametri Gemini 3](https://ai.google.dev/gemini-api/docs/gemini-3).

## Quote del progetto e limiti pubblici

Osservazione diretta in AI Studio, progetto `gen-lang-client-0393363402`,
nome audit black-box, piano gratuito: Gemini 3.1 Flash Lite **15 RPM, 250.000 TPM,
500 RPD**. La pagina è sui picchi di28giorni: 13RPM,6,89kTPM,494RPD sono picchi
storici, non contatori residui oggi. Nessuna generazione eseguita per verificarli.
[Pagina consultata](https://aistudio.google.com/rate-limit?timeRange=last-28-days&project=gen-lang-client-0393363402).

La pagina non espone token batch accodabili effettivi. La tabella pubblica indica
10milioni per3.1FlashLite al primo livello elencato, ma non la si attribuisce al
progetto free. Batch ha quote separate: limite100job concorrenti,2GB per file,
20GB storage; capacità token condivisa fra tutti i job attivi dello stesso modello.
Prima dell'invio serve evidenza della quota batch del progetto e della capacità
libera, senza trasformare500RPD in un limite batch.
[Quote Google](https://ai.google.dev/gemini-api/docs/rate-limits).

## Preventivo sui materiali prodotti

| Voce | Quantità |
|---|---:|
| Nuove assegnazioni |367|
| Generazioni main |8.808|
| Controlli separati |24|
| Totale richieste |8.832|
| Proxy input, byte UTF-8/3 arrotondati per richiesta |6.854.683token|
| Riserva input provvisoria, byte UTF-8+256 per richiesta |22.813.086token|
| Output massimo ipotizzato,1.200×8.832 |10.598.400token|
| Stima a150token output medi |1,850435USD|
| Riserva provvisoria input prudente+output massimo |10,800436USD|
| Stessa riserva con margine20% |12,960524USD|
| Residuo prudenziale sul tetto30USD |17,039476USD|
| Spesa di questa preparazione |0USD|

Il proxy è ricavato dai prompt reali, non dal numero di parole del pilot. Non è
un tokenizzatore Gemini. Byte+256 è una riserva cautelativa, **non un limite
matematico certificato dal provider**. Nessuna delle due stime abilita l'invio.
La stima output150 è uno scenario esplicito, non un dato confermativo osservato.

Il conteggio Google `countTokens` dei payload esatti va archiviato per hash prima
della raccolta. Verificare inoltre che maxOutputTokens1200 limiti l'intero output
fatturabile, compreso thinking, per questo modello/endpoint. `minimal` non basta
a provarlo. Se non documentabile, mantenere il blocco e ricalcolare con un limite
fatturabile giustificato; non presentare10,80USD come massimo garantito.

`admit_shard` richiede ricevute conteggio per tutte le chiavi del lotto, modello e
hash corrispondenti, prezzi attuali, capacità batch, controlli completati per i
main e tutte le autorizzazioni. Riserva il120% del costo massimo calcolato in un
ledger atomico con lock. Somma tutte le riserve incluse quelle incerte e rifiuta
superamenti di30USD. Test, controlli, campagne ed extra devono usare lo stesso
ledger: niente registri separati per aggirare il tetto. Nessun rilascio automatico
di fondi e nessun retry automatico. Altri consumi nel medesimo progetto devono
essere esclusi o contabilizzati prima del lancio.

Questo è un controllo applicativo sui nostri invii, non un hard cap imposto a
Google. In questo pacchetto manca deliberatamente il trasporto live; occorre
collegarlo al gate, testarlo con mock e preflight prima dell'uso. Nessuno script
nuovo può attivare fatturazione o spendere.

## Esecuzione e durata

Il formato scelto usa file JSONL con chiave univoca e oggetto request. La raccolta
avviene su Google dopo accettazione del job; il PC può essere spento. La guida
indica turnaround obiettivo24ore e stati terminali di successo/errore/cancel/
scadenza. Conservare anche completamenti parziali/tardivi, senza assumere cancel
istantaneo. [Batch](https://ai.google.dev/gemini-api/docs/batch-api).

I file caricati hanno conservazione48ore secondo Files API; verificare i metadati
del file risultato senza supporne la stessa durata o una conservazione indefinita.
Proposta: un breve controllo/download entro24ore da ogni invio, quindi PC di nuovo
spento. Non è un sistema autonomo di archiviazione mentre il PC è spento.
[Files API](https://ai.google.dev/gemini-api/docs/files).

Nessuna fatturazione attivata. Se batch free è realmente utilizzabile non occorre
attivarla preventivamente; altrimenti serve la decisione esplicita prevista dal
mandato. La disponibilità effettiva resta un gate tecnico, non un'assunzione.
