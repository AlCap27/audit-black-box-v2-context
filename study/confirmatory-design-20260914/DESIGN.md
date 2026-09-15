# Proposta di design confermativo

14 settembre 2026. Nessun esperimento eseguito. Ambito intermedio adottato; parametri operativi sotto proposti per approvazione.

## Struttura

| Fattore | Livello 0 | Livello 1 |
|---|---|---|
| S | JSON-LD assente | Stessi fatti in JSON-LD |
| L | llms.txt assente | Prosa canonica in llms.txt |
| T | Prosa nel body una volta | La stessa prosa ripetuta due volte |

Otto combinazioni 000–111; 32 vendor, quattro per combinazione e uno per template in ciascuna cella. La sitemap è identica nel nucleo. Non si aggiungono fatti, prezzi migliori o autorità simulata. Ogni effetto principale confronta 16 vendor contro 16, con le altre caratteristiche marginalizzate. La ridondanza testuale è un trattamento esplicito: non va annullata da una normalizzazione successiva non dichiarata.

24 query fisse, 12 per intento; una risposta per query/assegnazione; tutte le condizioni presenti insieme. Ogni assegnazione costa 24 chiamate, non 24×8. Nuovi seed bloccati per template, senza riuso delle assegnazioni pilota. Nuova cartella, nuova versione di corpus e configurazione; sorgenti precedenti immutati.

## Opzione raccomandata per la massima difendibilità con assunzioni dichiarate

- Δ principale 5 pp, potenza minima 80% per l'effetto principale L sulla raccomandazione totale, α=0,025.
- **318 nuove assegnazioni**, 7632 chiamate inferenziali; 24 controlli separati, cap proposto **7656**. Test primario Hoeffding basato sul supporto e indipendenza fra assegnazioni. Garanzia conservativa con dati completi e media vera di modulo almeno 5 pp, non previsione che tale effetto esista.
- **1135 assegnazioni offline** per retrieval a Δ5 pp, α=0,003125, potenza conservativa almeno 80%. Le prime 318 sono condivise con la generazione; ulteriori 817 solo retrieval. Totale 27240 query-retrieval, nessun costo API aggiuntivo. L'effetto target è lo stesso meccanismo di assegnazione, ma le precisioni dei due stadi sono diverse.
- Condizionato al recupero: esito secondario prespecificato, con intervalli che possono essere ampi. Questo budget **non garantisce 80% di potenza per 5 pp condizionati**. Il proxy pilota suggerisce circa 380–1504 assegnazioni (9120–36096 chiamate inferenziali) a SD ×1–2; nuovo fattoriale e supporto possono modificarlo. Nessuna garanzia finita senza assunzioni sull'esposizione.
- Discovery: 16 benchmark locali prefissati, separati dal test statistico e senza chiamate LLM. La discovery del nucleo è fissata a uno dal manifest.

Per target 90% primario servono, nel limite conservativo, 367 assegnazioni e 8808 chiamate inferenziali (+24 controlli); retrieval 1288 assegnazioni offline. Tabella completa Δ2/5/10 in power-sensitivity.md.

## Alternativa più economica, non equivalente nelle garanzie

Un disegno di 40 assegnazioni (960 chiamate +24 controlli) appare potente per Δ5 nei modelli di contrasto ricavati dal pilot, anche raddoppiando la SD. Tuttavia una cella tecnica e il fattore T mancano nel pilot, il blocco per template cambia il disegno e le simulazioni non riproducono interamente il nuovo processo. Questa alternativa richiede accettare e verificare ipotesi più forti e scegliere ex ante un'altra analisi primaria. Non la presentiamo come dotata della stessa garanzia del disegno da 318.

Se l'obiettivo prioritario è un effetto causale sul generatore a esposizione fissata, proporre un modulo dedicato: stessi candidati/fatti/ordine bilanciato, rappresentazione randomizzata. Budget e potenza da dimensionare su tale protocollo; non è corretto promettere che 7656 chiamate lo includano o che τC lo sostituisca.

## Fattibilità e rischi

5 pp totali è un effetto grande rispetto alla baseline, ma compatibile con i vincoli massimi di output. Non cambiamo la soglia per avvicinarla al risultato pilota. I calcoli conservativi sono sufficienti, non minimi necessari. Con quota dichiarata 500/giorno il cap principale richiede almeno 16 giornate senza altri consumi; non è una verifica della quota attuale. La deriva di modello è un rischio concreto di un periodo lungo, da gestire nel piano temporale.

Assenza di dati per alcune celle rende inaffidabile una promessa precisa sulla potenza condizionata. Se l'utente richiede potenza uniforme 80% su tutti e tre gli estimandi, il design non è ancora pronto al lancio: approvare un budget maggiore o una revisione del disegno, mantenendo Δ5 finché non viene deliberato diversamente.

## Gate prima del lancio

Approvazione delle decisioni → implementazione separata e test dei fattori → revisione metodologica → freeze di query/corpus/parser/seed/analisi → preregistrazione → controlli tecnici generativi → campagna autorizzata. Nessun passaggio è stato eseguito automaticamente nella presente analisi. Non sono richieste modifiche a VPS o domini per preparare i file locali.
