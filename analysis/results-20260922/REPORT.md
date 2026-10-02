# Audit Black Box V2 — analisi dei risultati

[Dichiarazione di conflitto d'interesse

L'autore di questo studio sviluppa e intende commercializzare Agentabile (agentabile.dev), uno strumento che assegna un punteggio di "agent-readiness" tecnica a siti web, valutando tra l'altro proprio le caratteristiche testate qui (llms.txt, dati strutturati schema.org/JSON-LD). L'autore ha quindi un interesse economico diretto nel dominio di questo studio.

Si segnala esplicitamente che i risultati di questo studio non favoriscono tale interesse commerciale: l'ipotesi primaria — che la presenza di llms.txt aumenti la probabilità di raccomandazione — non ha prodotto un effetto statisticamente rilevato, e l'unico effetto positivo osservato (duplicazione del corpo testuale) non sopravvive a un controllo che neutralizza il preprocessing della pipeline. Lo studio è pubblicato integralmente, dati grezzi inclusi, proprio perché il lettore possa verificare in autonomia ogni cifra.

Nota di framing e ambito

Questo non è uno studio osservazionale sul comportamento degli agenti d'acquisto reali. È un esperimento controllato in vitro su una pipeline sintetica: recupero lessicale BM25 su un corpus-giocattolo di 24 query in un singolo dominio (vini italiani), con un solo modello generativo (gemini-3.1-flash-lite) e 32 identità di negozio sintetiche. Nessuna conclusione qui riportata si trasferisce direttamente a sistemi di produzione (Google AI Overviews, ChatGPT, Perplexity, Gemini nella loro forma reale), che usano retrieval neurale/ibrido, ranking proprietari e discovery su web reale — nessuno dei quali è rappresentato in questo disegno.

Precisazioni sui risultati principali, per evitare sovra-interpretazione:

Ipotesi primaria (llms.txt) e JSON-LD: nessun effetto statisticamente rilevato. Questo non equivale a dimostrare l'assenza di un effetto: gli intervalli sono ampi (primaria: [−2,68; +3,12] punti percentuali) e lo studio non ha potenza per escludere un effetto piccolo. Il risultato è compatibile sia con l'assenza di effetto sia con un effetto piccolo non rilevabile a questa numerosità.
Duplicazione del corpo testuale (effetto T): +6,645 punti percentuali, statisticamente rilevato secondo il test pre-registrato. Tuttavia l'effetto non sopravvive alla variante di controllo canonica (una sola copia del body, senza schema né llms): il delta scende a circa −0,1 pp. Poiché la variante canonica rimuove più componenti contemporaneamente, questo risultato sostiene che l'effetto è sensibile al preprocessing e verosimilmente attribuibile alla meccanica del retrieval BM25 (frequenza dei termini, lunghezza del documento), ma non isola in modo definitivo che l'intero effetto sia un artefatto: il disegno confonde più fattori e non permette di escludere una componente residua. In ogni caso, l'effetto è specifico di questa pipeline e non è presentato come proprietà trasferibile ai sistemi reali.
Scostamento dal disegno pre-registrato

Il documento di disegno (DECISIONS.md) prevedeva 318 assegnazioni generative; ne sono state raccolte 367. Si tratta di un aumento della numerosità (maggiore potenza, non minore), congelato nel manifest sha256 il 2026-09-14, prima della raccolta dati — non è quindi una selezione a posteriori della numerosità. Lo si annota qui per piena trasparenza rispetto al numero indicato nel disegno.]

22 settembre 2026. Analisi offline della raccolta del 21 settembre. Protocollo
scientifico e addendum Batch sigillati; freeze operativo remoto
`f7606d529d0a4c44f628eb11286c8b6d1088747d`. Nessuna nuova generazione.

## Risultato principale

**La primaria su llms.txt non rifiuta l'ipotesi di effetto totale nullo.**
La probabilità di raccomandazione per slot vendor-query è 3,407% senza llms.txt
e 3,625% con llms.txt: differenza **+0,218 punti percentuali**, intervallo
Hoeffding al 97,5% **[−2,680; +3,115] pp**.
Non è una dimostrazione di effetto esattamente nullo o di equivalenza.
Sotto le assunzioni dell'intervallo, questo risultato non sostiene un effetto
totale di almeno +5 pp. La soglia di rilevanza resta quella prespecificata.

Fra le secondarie, **la duplicazione del body (T) aumenta retrieval e
raccomandazione totale nella pipeline BM25 studiata**. Non emerge una differenza
statisticamente rilevata per JSON-LD (S). I contrasti condizionati al retrieval
restano troppo imprecisi per rifiutare zero; non identificano effetti causali
diretti sul generatore.

## Tutti i nove contrasti prespecificati

Effetti e intervalli in punti percentuali, livello 1 meno livello 0. Primaria
L totale: alpha 0,025. Otto secondarie: alpha 0,003125 ciascuna (intervalli
individuali 99,6875%). Nessun test è stato selezionato in base al risultato.

| Fattore | Esito | Effetto pp | Intervallo pp | Zero escluso |
|---|---|---:|---:|---|
| L: llms.txt | Totale Y, primaria | +0,218 | [−2,680; +3,115] | No |
| L | Retrieval Z | +0,446 | [−5,418; +6,310] | No |
| L | Y condizionato a Z | −3,081 | [−78,610; +80,258] | No |
| S: JSON-LD | Totale Y | +0,018 | [−3,501; +3,536] | No |
| S | Retrieval Z | −0,277 | [−6,141; +5,587] | No |
| S | Y condizionato a Z | +5,370 | [−78,913; +79,889] | No |
| T: body duplicato | Totale Y | **+6,645** | **[+3,127; +10,164]** | **Sì** |
| T | Retrieval Z | **+7,695** | **[+1,831; +13,559]** | **Sì** |
| T | Y condizionato a Z | +49,350 | [−57,417; +100,000] | No |

I punti stimati di T superano 5 pp, ma i limiti inferiori non superano 5 pp:
non si può affermare che l'effetto minimo sostenuto sia almeno 5 pp.
Per T, Y passa da 0,193% a 6,838% e Z da 0,580% a 8,274%.
La differenza condizionata T ha un denominatore molto piccolo nel livello 0;
la cella S/L/T=100 non ha alcun vendor recuperato. I rapporti con denominatore
zero sono non identificati, non impostati a zero.

## Dati, integrità e metodo

- 367 assegnazioni indipendenti per disegno, 32 identità, 24 query fissate:
  8808 risposte principali, 281856 slot vendor-query. I 24 controlli sono esclusi
  da tutte le stime inferenziali e non sono stati ripetuti.
- 12 main SUCCEEDED, chiavi esatte e uniche, nessun missing o quarantena.
- Tutte le 8832 risposte, controlli inclusi, sono state rilette dagli archivi GET
  e riparsate con il parser frozen: corrispondenza completa con i rapporti.
- 5138 astensioni valide, conteggiate Y=0; 9909 raccomandazioni di vendor noti.
  Zero nomi sconosciuti, citazioni non supportate, raccomandazioni fuori Z/X,
  vendor recuperati ma non mostrati o chunk mostrati troncati.
- Sei manifest/sigilli originali verificati integralmente; hash del codice
  operativo verificati contro il freeze v2. Nessun artefatto frozen modificato.
- Unità inferenziale: assegnazione del pool, N=367, non 8808 richieste o 281856
  slot indipendenti. Ogni contrasto di cluster usa 16 vendor × 24 query/livello.
- Intervalli calcolati con `bounded_inference.py` sigillato, senza sostituire
  t-test/bootstrap più stretti. Supporti ±3/16 per Y e ±5/16 per Z. Per il
  condizionato: rapporto dei totali e propagazione degli intervalli simultanei
  sulle quattro medie, come da protocollo. Nessuna esclusione post-raccolta.
- Quattro test dell'adattatore analitico superati: denominatori, mantenimento
  dei vendor non esposti, rapporto dei totali, soglie/supporti e denominatore zero.

Il codice di collegamento ai risultati reali è stato scritto dopo la raccolta;
ipotesi, soglie, estimandi e funzioni di inferenza erano già nel pacchetto.
Non si presenta il repository privato come preregistrazione pubblica.

## Sensibilità descrittive e limiti delle assunzioni

La primaria L, escludendo a turno un Batch **solo come diagnostica**, varia
da −0,012 a +0,278 pp. Non è un'analisi sostitutiva: la stima primaria include
tutti gli slot. Per intento, L totale è +0,051 pp transazionale e +0,385 pp
valutativo. T totale è +7,292 e +5,999 pp rispettivamente; è positivo nei quattro
template (da +2,083 a +12,500 pp). Queste non sono ulteriori scoperte confermative.

Ogni job contiene due query per tutte le assegnazioni: tempo/job e coppia di query
sono confusi. Le differenze fra job non permettono di separare una deriva del
provider dalla diversa difficoltà delle query. Una sola replica generativa,
versione stabile e completezza dei dati **non provano indipendenza stocastica
fra cluster**. La validità degli intervalli e la garanzia di potenza restano
condizionate a tale assunzione; non si certifica potenza realizzata del 90%.
La potenza progettuale riguarda la primaria a Δ5 pp, non tutte le secondarie.
Le sensitivity di potenza Δ2/5/10 restano quelle nel pacchetto di pianificazione.

### Ablation globali del retrieval, solo offline

Ricostruite 8808 ricerche per variante; nessuna risposta LLM è riutilizzata
come se fosse generata con il contesto modificato. Risultati descrittivi:

| Pipeline | Insiemi di vendor recuperati cambiati / 8808 | Contrasto T retrieval, pp |
|---|---:|---:|
| Senza schema | 2681 | +7,292 |
| Senza llms.txt | 2512 | +9,115 |
| Testo canonico | 4352 | −0,101 |

Testo canonico: una copia del body, senza schema né llms, mantenendo markup,
identità e template. Le famiglie di ablation erano previste; questa precisa
implementazione diagnostica è definita dopo la raccolta e non aggiunge un test
confermativo. Il pattern è coerente con un meccanismo del preprocessing/BM25;
non dimostra una preferenza intrinseca di Gemini per testo duplicato.

### Discovery e controllo del parser

Il benchmark locale sigillato ha 16 esecuzioni: la sitemap rende raggiungibile
il target orfano nei due ordini; nei grafi diretto, catena e ciclo il target è
già raggiungibile. Nessuna inferenza su Google o sulla discovery del web.
Nel main W=1 per costruzione.
Il replay automatico del parser copre tutti gli output, e non ci sono casi
ambigui segnalati. Revisione umana della validità semantica del parser: ESEGUITA
su un campione stratificato di 70 casi (25 astensioni, 25 raccomandazioni, 20
risposte lunghe/atipiche; seed fisso 20260922), tratti dalle 8808 risposte
confermative. Zero discrepanze semantiche: tutte le astensioni esaminate sono
rifiuti genuini (nessuna raccomandazione occulta nel campo explanation con
recommendations vuoto); tutte le mappature nome→vendor del campione sono esatte.
Questo è coerente con i contatori aggregati unknown_names=0 e
unsupported_recommendations=0 su tutte le 8808 risposte. LIMITE: si tratta di
un campione (70/8808); l'assenza di discrepanze è compatibile con un tasso
d'errore reale basso ma non necessariamente nullo. Non si conclude che il
parser sia esente da errori, ma che non emergono errori sistematici di
classificazione o mappatura. Le explanation, sia di astensione sia di
raccomandazione, sono fortemente stereotipate — artefatto atteso del decoding
JSON vincolato e del corpus sintetico, non un difetto di parsing. Evidenza
della revisione: review/review-giudizi.csv.

## Conclusione sostenibile e prossimo passo

Nel pool sintetico e nelle query fissate, il test primario non rileva un effetto
totale di llms.txt. La ridondanza del body presenta differenze positive su
retrieval e raccomandazione totale con le soglie prespecificate, sotto le
assunzioni inferenziali dichiarate. Non si generalizza a siti reali, mercati,
query nuove o agenti di acquisto completi; non si sostiene una mediazione causale.

Raccolta e analisi principale sono concluse. Prima di una pubblicazione:
revisione metodologica indipendente delle assunzioni (la revisione semantica
del parsing è ESEGUITA, vedi sopra) e conservazione del runtime su un secondo
supporto. Nessuna nuova campagna necessaria per completare questo report.
Costo stimato complessivo già riportato: 1,24666525 USD; fattura finale non
verificata. Nessun commit o push eseguito per la generazione originale di
questa analisi (22 settembre 2026); i successivi interventi documentali del
2 ottobre 2026 sono stati committati e pubblicati su origin/main
(commit 31bcda1, d804f21).

I file JSON e observations.jsonl permettono di ricostruire stime, cluster,
sensibilità, tracciabilità e controlli; non contengono credenziali.
