# Audit Black Box V2 — protocollo confermativo proposto

Data: 14 settembre 2026. Ambito intermedio approvato dall'utente. Documento per approvazione del disegno e budget, non preregistrazione pubblicata. Nessuna nuova raccolta autorizzata da questo documento. Le campagne sigillate restano immutate.

## 1. Obiettivo e fattori

Valutare gli effetti di caratteristiche tecniche definite su retrieval e raccomandazione in una pipeline controllata, senza generalizzare agli agenti AI di acquisto nel complesso. Non si stima l'effetto di un incremento continuo del punteggio Agentabile. Score e affidabilità delle scansioni sono controlli della manipolazione.

Proposta fattoriale 2×2×2, 32 identità, quattro vendor in ciascuna delle otto celle:

- S: JSON-LD assente/presente, ricodifica gli stessi fatti della prosa.
- L: llms.txt assente/presente, contiene la prosa canonica e nessun fatto aggiuntivo.
- T: prosa canonica una volta/duplicata una seconda volta nel body HTML. È un intervento sulla ridondanza del testo indicizzato, non sulla qualità o quantità dei fatti commerciali.

Sitemap identica in tutte le celle del nucleo. Template, fatti, nomi e URL della singola identità invariati fra assegnazioni. JSON-LD e llms codificano sempre la prosa canonica, non la sua duplicazione: T modifica soltanto il body. La configurazione 2×2 senza T è un'alternativa più stretta da approvare, non una modifica automatica in base ai risultati.

Il terzo fattore rende esplicita la componente testuale. Non isola completamente nome del file, numero di documenti, lunghezza e posizione: questi sono meccanismi del trattamento. Le ablation globali del preprocessing sono analisi di pipeline, non effetti dei singoli vendor a concorrenti invariati.

## 2. Discovery, retrieval, recommendation

Definire W=pagina scoperta, Z=vendor recuperato nel top-k, X=nome/fatti effettivamente mostrati al modello, Y=vendor raccomandato. Z e X non vanno confusi quando ci sono troncamenti. Y fuori dal retrieval è registrato come leakage, non cancellato.

**Discovery.** Nel nucleo da manifest W=1 per costruzione: la discovery è controllata, non stimata empiricamente. Un benchmark locale separato confronterà sitemap on/off in topologie di link prefissate, stesso punto d'ingresso e budget del crawler. Proposta: quattro topologie × due stati sitemap × due ordini deterministici =16 esecuzioni locali, nessuna API LLM. Positivo: pagina non linkata dal body ma raggiungibile tramite sitemap. Negativo: stesso grafo completamente raggiungibile con sitemap irrilevante. Riportare conteggi e differenze sul benchmark finito, senza intervalli di popolazione fittizi. Un crawler locale non rappresenta la discovery di Google o Tavily. Implementazione del benchmark ancora da approvare con il disegno.

**Retrieval.** Indicizzare tutti i documenti ammessi dal manifest nella configurazione primaria: BM25 k1=1,2, b=0,75; tokenizzazione e chunking fissati; chunk 100 parole, top-k=5, massimo un chunk per vendor. Schema conservato e serializzato come nel pilot; llms come documento distinto. Tracce complete e budget contesto 700 parole, intestazioni aggiuntive dichiarate. La sensibilità BM25 già osservata è proprietà di questa pipeline; non prova un effetto generale sul modello.

**Recommendation.** Nuovo contesto per richiesta, nessuna memoria di conversazione, stesso prompt strutturato e massimo tre vendor. Identificatore del generatore e parametri da riconfermare prima della preregistrazione; nessun alias latest. Salvare versione restituita e data. Un identificatore stabile non prova immutabilità dei pesi. Nessun passaggio automatico ad altro modello. L'assistente che prepara il lavoro rimane esclusivamente Astra.

## 3. Estimandi

Per ciascun fattore F∈{L,S,T}, confrontare F=1 e F=0, marginalizzando sugli altri due fattori secondo il disegno bilanciato. Ogni gruppo marginale contiene 16 vendor. La popolazione target primaria è il pool finito e le 24 query fissate, mediati sulla distribuzione di nuove assegnazioni e sulla variabilità generativa nel periodo dichiarato.

1. **Retrieval:** τR,F = P(Z=1|F=1,W=1) − P(Z=1|F=0,W=1).
2. **Recommendation condizionata al retrieval:** θf = P(Y=1,Z=1|F=f)/P(Z=1|F=f); τC,F = θ1 − θ0. Usare rapporto dei totali su tutti gli slot, non media dei rapporti per query né media di soli cluster con denominatore positivo.
3. **Recommendation totale nel laboratorio:** τY,F = P(Y=1|F=1,W=1) − P(Y=1|F=0,W=1), includendo tutti i vendor, anche mai recuperati. È totale per la pipeline a discovery controllata, non totale sul web naturale.

La condizione tecnica è randomizzata, ma Z è post-trattamento. τC confronta due popolazioni selezionate dal retrieval; è un contrasto condizionato identificabile quando i denominatori sono positivi, **non automaticamente un effetto causale diretto sul generatore**. La randomizzazione non risolve la selezione su Z. Per quest'ultimo obiettivo serve un modulo a candidati, ordine e fatti fissati indipendentemente dal recupero, con rappresentazione randomizzata; non è incluso nel budget principale e non si ottiene filtrando il pilot.

La decomposizione descrittiva corretta è P(Y|f)=P(Z|f)P(Y|Z,f)+P(non Z|f)P(Y|non Z,f). Il secondo termine non è assunto zero a priori. Nessuna percentuale di mediazione naturale. Fonte di riferimento sull'identificazione: [Imai, Keele e Yamamoto](https://imai.fas.harvard.edu/research/files/mediation.pdf).

Questi sono contrasti sotto un'allocazione competitiva: modificare un vendor modifica anche l'indice e la concorrenza. Non assumere assenza di interferenza entro pool o interpretare il contrasto come miglioramento isolato di un sito nel mercato reale.

## 4. Ipotesi e molteplicità

Primaria proposta: H0 τY,L=0 contro alternativa bilaterale. L è scelto come intervento definito nel nuovo disegno; non si usa il segno del pilot per imporre unilateralità. Δ di riferimento =5 pp assoluti; sensitivity 2 e 10 pp, immutati rispetto alla richiesta utente.

Allocazione proposta dell'errore familiare complessivo 5%: primaria α=0,025; otto secondarie ciascuna α=0,025/8=0,003125 (Bonferroni). Secondarie: τR,L, τC,L; τY,S, τR,S, τC,S; τY,T, τR,T, τC,T. Questa allocazione è una scelta da approvare, non derivata dai p-value pilota.

Interazioni fra fattori, intenti e template, singole celle e varianti del retriever sono esplorative con etichetta esplicita: nessuna promozione a ipotesi primaria dopo i risultati. Per renderle confermative occorre ridefinire famiglia e budget prima della raccolta.

Distinguere evidenza contro zero da rilevanza: un intervallo che esclude zero ma resta sotto 5 pp segnala un effetto piccolo; un punto stimato sopra 5 pp non prova che l'effetto superi la soglia. Riportare intervallo rispetto a zero e a ±5 pp. Non significatività non equivale ad assenza di effetto né equivalenza.

## 5. Unità, randomizzazione, dipendenze

Unità di assegnazione: vendor entro un pool. Unità indipendente usata per l'analisi: nuova assegnazione dell'intero pool, non una riga vendor-query. Le 24 query comprendono 12 basi linguistiche per due intenti, fissate; la loro dipendenza rimane nel cluster. Non dichiarare generalizzazione a query nuove.

Bloccare per i quattro template: ciascun template ha otto identità e riceve le otto condizioni una volta per assegnazione, con permutazione casuale indipendente. Ogni cella contiene così un vendor per template. Conservare seed e manifest prima dei risultati. Non forzare bilanciamento fra assegnazioni in cicli dipendenti senza cambiare l'analisi. La scelta evita che differenze casuali di composizione dei template guidino il confronto; il pilot era meno vincolato e le sue SD sono proxy.

Randomizzare lo schedule delle chiamate in blocchi temporali, mescolando query e assegnazioni. Loggare data, latenza, versione e errori. La costanza di modello non dimostra indipendenza fra richieste: riportare sensitivity per blocco temporale e deriva. Le garanzie di concentrazione richiedono cluster indipendenti; se questa assunzione non è sostenibile, non etichettare la garanzia come acquisita. Ripetizioni generative extra non sono nuove assegnazioni.

## 6. Analisi primaria proposta

Per ogni assegnazione calcolare dY,F=(numero raccomandazioni nei 16 F=1 − numero nei 16 F=0)/(16×24). Una replica generativa per query. Supporto [-3/16,+3/16]. Stimatore: media dei contrasti, inclusi tutti gli slot pianificati. Intervallo bilaterale Hoeffding a N fisso con ampiezza L=3/8 e α=0,025. Rifiutare H0 solo se l'intervallo esclude zero. Il codice proposto è in bounded_inference.py, separato dalle campagne.

Questa scelta conservativa evita di basare la decisione primaria sulla normalità dei pochi contrasti pilota. Non è efficiente quanto metodi che sfruttano varianza e struttura; le t non centrali nel report di potenza sono alternative di pianificazione, non il test della proposta robusta. Non scegliere a posteriori l'intervallo più stretto. Fonte: [Maurer e Pontil, limiti di concentrazione](https://www.cs.mcgill.ca/~colt2009/papers/012.pdf); la formula di potenza sufficiente è derivata nel report.

Per retrieval marginale il supporto è [-5/16,+5/16], ampiezza 5/8. Si possono raccogliere più assegnazioni offline senza generatore, con seed congelati. Per τC usare intervalli simultanei di quattro medie (numeratore congiunto YZ e denominatore Z per i due livelli), allocando α/4 a ciascuna media, poi propagare ai rapporti e alla differenza. Se il limite inferiore del denominatore è zero, l'intervallo del rapporto può essere [0,1]; non inventare precisione. Per le celle individuali quasi mai recuperate, riportare il problema di supporto.

## 7. Controlli

Negativi offline: sitemap on/off a contenuto indicizzato identico deve lasciare ranking invariato; rietichettare metadati non indicizzati non deve cambiare i punteggi; una condizione tecnica disattivata nell'estrattore non deve aggiungere token. Il controllo verifica la singola identità e l'intero indice, non uguaglianza casuale fra medie di gruppi diversi.

Positivi offline: query con termine univoco presente in un solo documento deve recuperarlo; JSON-LD/llms attivi devono comparire in chunk e manifest; pagine e nomi effettivamente esposti devono essere verificabili. Questi test di meccanismo non impongono un vantaggio complessivo di un bundle.

Controlli generativi proposti prima della raccolta: 12 contesti con un vendor esplicitamente pertinente e 12 con sole fonti editoriali, in set separato dai dati inferenziali. Gate tecnico: output formalmente valido e fonti/identità coerenti in tutti i 24; una deviazione arresta il lancio e richiede revisione, non retry selettivi. Sono test ingegneristici, non stime di accuratezza o effetto commerciale. Budget aggiuntivo 24 chiamate, da approvare.

## 8. Missing, esclusioni e arresto

Prima della raccolta: escludere solo fixture corrotte, fatti non equivalenti o controlli di integrità falliti, con motivazione documentata e rigenerazione del manifest prima del freeze. Dopo il freeze non escludere vendor/query/assegnazioni per scarsa esposizione, astensione, effetto estremo, segno o score poco favorevole.

Risposte API errate e parsing invalido sono missing. Un'astensione valida è Y=0, non missing. Nomi sconosciuti e raccomandazioni prive di supporto restano nel record; i vendor riconosciuti contano secondo l'esito prespecificato e il leakage è separato. Non ripetere tentativi pending senza riconciliazione; nessun retry automatico nel budget proposto.

Per un missing generativo, Z è noto se il retrieval è integro; assegnare al contributo Y l'intervallo compatibile con massimo tre raccomandazioni, propagando prima sul cluster e poi all'intervallo della media. È conservativo usare [-3/16,+3/16] per lo slot incerto. Per numeratori condizionati usare limiti compatibili con i vendor recuperati, senza impostare Y=0. N pianificato non cambia. Nessuna analisi primaria sulle sole assegnazioni complete.

Nessuna stopping rule di efficacia, futility o significatività. Arresto tecnico alla prima anomalia di integrità, cambio di versione, errore API o esaurimento budget: checkpoint, nessuna sostituzione dei dati, revisione esplicita prima di riprendere gli slot non ancora tentati. Se lo studio termina incompleto, riportare intervalli con missing e dichiarare perdita di potenza; non chiamarlo studio conclusivo. La potenza garantita nel calcolo vale a esiti completi.

## 9. Come attribuire gli esiti agli stadi

- Effetto su τR: evidenza sul recupero sotto quella pipeline e randomizzazione.
- Effetto su τY: evidenza totale sulla raccomandazione nella pipeline con discovery fissata.
- Differenza τC: evidenza condizionata nella popolazione selezionata; non prova da sola una preferenza causale del generatore.
- τR significativo e τC non significativo non dimostrano assenza di effetto a valle. Un pattern opposto non elimina meccanismi di composizione, ordine o contesto.
- Per un effetto causale a valle aggiungere un esperimento distinto a esposizione imposta. Non sostituire questo requisito con regressioni sul solo sottoinsieme recuperato.
- Discovery: conclusioni limitate al benchmark locale; il totale sul web rimane fuori ambito.

## 10. Sensibilità e riproducibilità

Report prespecificati: Δ2/5/10; SD proxy ×1/1,5/2; 80% e 90% di potenza; blocchi temporali; esiti per intento/template descrittivi; no-schema, no-llms e testo canonico come ablation globali offline; controllo di copertura del parser su campione casuale fissato e tutti i casi ambigui. Le risposte LLM originali non possono essere riusate per contesti cambiati.

Pilot usato solo per baseline, varianze, struttura e costi. Nessuna soglia scelta dal segno degli effetti. Registrare protocollo, hash, code/config e schedule prima dei nuovi dati; pubblicare deviazioni e risultati anche nulli. Fonte per la distinzione esplorativo/confermativo: [COS preregistration](https://www.cos.io/initiatives/prereg). La pubblicabilità richiede anche valutazione della novità e revisione esterna; non è garantita dal solo protocollo.
