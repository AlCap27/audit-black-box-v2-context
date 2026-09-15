# Protocollo per la fase successiva — bozza da deliberare

14 settembre 2026. Non preregistrato, non autorizza nuove API o deploy. I 480 esiti precedenti restano pilot esplorativo; non saranno inclusi nel test confermativo come se fossero dati nuovi.

## Domanda e ambito

Proposta di contributo principale: effetti di bundle tecnici e della loro rappresentazione nell'indice sulla visibilità di venditori sintetici in un RAG controllato. Il laboratorio non identifica il comportamento di Tavily, Google o tutti gli agenti. Il pool competitivo, le query, il retriever, il generatore e i limiti di output fanno parte della definizione del risultato.

Trattamenti A=prosa HTML, B=+sitemap, C=+JSON-LD, D=+llms. Fatti invarianti, identità e prosa fissate; score Agentabile come controllo di misura, mai come dose continua manipolata. Non ottimizzare i siti fino a ottenere un effetto sulle raccomandazioni.

## Tre domande separabili

1. **Recupero e pipeline completa, nucleo proposto.** Conservare il caricamento esplicito del corpus e confrontare una configurazione primaria congelata con sensibilità tecniche motivate. Esiti: recupero, presenza nel contesto, raccomandazione, astensione. L'assenza del meccanismo sitemap è dichiarata; A/B serve da controllo negativo.
2. **Raccomandazione a contesto controllato, modulo meccanicistico.** Costruire set di candidati fissati indipendentemente dal ranking, mantenere uguali fatti e budget, randomizzare rappresentazione e ordine con controbilanciamento. Fissare se il trattamento includa duplicazione: bilanciare i token può rimuovere proprio quel meccanismo. Stimare l'effetto sotto questo intervento, non una quota dell'effetto naturale del RAG.
3. **Scoperta, modulo distinto facoltativo.** Un crawler deve partire da punti d'ingresso identici e avere budget, politica link/sitemap e cache definiti. Misurare pagine scoperte rispetto a un insieme noto. Una sitemap non può aiutare a trovare un host mai raggiunto senza un percorso di scoperta. Con soli quattro host pubblici non trattare i path come repliche indipendenti di proprietà a livello host; usare snapshot isolati o un disegno di rotazione, da validare. Nessun ampliamento dei domini autorizzato qui.

Il manoscritto può delimitarsi al nucleo con controlli meccanicistici. Non occorre implementare tutte le estensioni V1 per presentare un contributo coerente; occorre evitare conclusioni sui meccanismi esclusi.

## Estimando e randomizzazione

Per ogni assegnazione bilanciata a del pool, definire d(a) come media sulle query della frequenza di raccomandazione fra gli otto D meno quella fra gli otto A. Il target è E[d(a)] sotto il meccanismo di assegnazione specificato, il pool finito e il servizio durante il periodo di raccolta. È un contrasto competitivo: cambiare assegnazione cambia anche i concorrenti e l'indice. Non è automaticamente l'effetto individuale di migliorare un singolo sito.

Generare nuovi seed prima della raccolta. Randomizzare l'ordine delle richieste e distribuire assegnazioni e intenti nei blocchi temporali. Richieste senza cronologia; registrare modello restituito e timestamp. Un nome commerciale di modello senza 'latest' non garantisce immutabilità dei pesi: una variazione della versione o del servizio va trattata come limite e gestita da regola prefissata, senza cancellare dati.

Unità primaria: assegnazione dell'intero pool. Query e venditori sono riusati; ripetizioni campionano la generazione, non moltiplicano le repliche del retrieval. Se si vuole generalizzare a nuove query o nuove identità, aggiungere campionamento indipendente di pool/query e ridimensionare il disegno. Non usare errori standard da righe venditore-query indipendenti.

## Analisi e numerosità

Un confronto primario D–A, bilaterale. Contrasti B–A e C–B e interazioni per intento sono secondari; fissare una correzione per confronti multipli se si intendono decisioni inferenziali su una famiglia. Pubblicare stime e intervalli, non soltanto p-value. Un risultato non significativo non prova equivalenza: per questa occorrono margine e disegno espliciti.

Non congelare oggi un test t o un modello gerarchico come automaticamente validato. La sensibilità del pilot con otto assegnazioni ha mostrato errori superiori al nominale nello scenario simulato. Simulare il procedimento completo includendo top-3, competizione, astensione, eterogeneità di query/template, effetti piccoli, asimmetria, errori e deriva temporale. Sotto più nulli e alternative riportare copertura, falsi positivi, potenza e incertezza Monte Carlo. Usare almeno 10000 simulazioni per gli scenari decisivi; fissare prima tolleranze di calibrazione e potenza (proposta 80% o 90%, da scegliere).

Gli effetti minimi 1/2/3 punti sono scenari, non una decisione scientifica già presa. Il budget segue effetto minimo e precisione desiderata; 500 chiamate disponibili non determinano la numerosità necessaria. Gli intervalli conservativi basati sul supporto sono riferimenti di robustezza, non una promessa di precisione pratica.

Un modello gerarchico secondario dovrà rappresentare scelta con astensione e massimo tre raccomandazioni, non soltanto Bernoulli indipendenti. Documentare prior predictive, posterior predictive, convergenza e recupero dei parametri su dati simulati. Una permutazione ingenua delle etichette con ranking fisso non ricrea l'intervento: per il retrieval occorre ricostruire l'indice; le risposte LLM controfattuali non sono disponibili gratuitamente.

## Esiti mancanti e integrità

Distinguere errore API, formato invalido, astensione valida, nome sconosciuto e fonte non supportata. Tutti gli slot pianificati restano nei denominatori. Salvare prima della chiamata il tentativo pending e non ripeterlo senza riconciliazione. Politica proposta: primo tentativo per slot nell'analisi primaria, eventuali retry separati e limitati da regola congelata. Quantificare missingness per blocco e braccio e limiti peggior caso; non imputare zero e non scegliere solo assegnazioni complete dopo errori. Stabilire ex ante quando il lotto è tecnicamente non interpretabile e come riportarlo.

Congelare corpus, query, parser, modello/configurazione, piano e codice; conservare manifest, hash, prompt, tracce e dati grezzi. Verifica manuale di un campione casuale di parsing definito prima dei risultati, più tutti i casi ambigui, senza usare il controllo per cancellare esiti sfavorevoli.

## Identificazione e trasparenza

P(raccomandato|recuperato,bundle) è descrittiva: il recupero seleziona popolazioni diverse e può non esserci sovrapposizione. Determinismo del retriever non elimina queste difficoltà e non autorizza una percentuale di mediazione naturale. La letteratura distingue randomizzazione del trattamento dall'identificazione del mediatore: Imai, Keele e Yamamoto (2010), https://imai.fas.harvard.edu/research/files/mediation.pdf. Il modulo a contesto controllato risponde a una diversa domanda interventistica.

Registrare protocollo e piano prima dei dati confermativi; dichiarare pilot e modifiche intervenute. Riferimento: https://www.cos.io/initiatives/prereg. Preparare materiali riproducibili e una revisione metodologica esterna prima della raccolta. Non è stata ancora condotta una ricerca sistematica di novità rispetto alla letteratura: non promettere accettazione editoriale.
