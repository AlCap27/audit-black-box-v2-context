from pathlib import Path
import json,math
P=Path(__file__).parent
r=json.loads((P/'power-results.json').read_text());m=r['metadata']
lines=['# Power e sensitivity analysis — 14 settembre 2026','',
'Analisi offline. Delta principale mantenuto a **5 punti percentuali assoluti**; scenari 2 e 10 pp. Target di pianificazione 80%, con scenario 90%. Nessuna nuova chiamata API. Tutte le numerosità escludono i 20 cluster pilota.','',
'## Baseline del pilot, non stime del nuovo fattoriale','',
'| Bundle storico | Retrieval | Raccomandazione totale | Raccomandazione fra recuperati | Recuperati |','|---|---:|---:|---:|---:|']
for b,x in m['baseline'].items():lines.append(f"| {b} | {x['p_retrieval']:.3%} | {x['p_total']:.3%} | {x['p_conditional']:.2%} | {x['retrieved']} |")
lines+=['','C ha solo due recuperi: la sua quota condizionata 0/2 è una descrizione, non una baseline precisa. La cella llms senza schema manca nel pilot. Le stime seguenti non sono una validazione della nuova cella.','',
'Un incremento totale di 5 pp rispetto a circa 3–4% corrisponde a circa 8–9%: grande in termini relativi, non impossibile. Non lo sostituiamo con il circa 1 pp osservato. A retrieval fissato al 4–5%, un aumento totale di 5 pp ottenuto solo migliorando la scelta a valle non è possibile; occorre cambiare anche esposizione/recupero oppure partire da un contesto controllato. Sulla probabilità condizionata la baseline D è 89,3%: +10 pp è vicino al soffitto. Questi vincoli non autorizzano una modifica automatica di Delta.','',
'## Dipendenze e varianze','',
f"SD dei contrasti pilota D–A per assegnazione: totale {m['proxy_sds']['total']:.6f}, retrieval {m['proxy_sds']['retrieval']:.6f}; SD della funzione di influenza della differenza di rapporti condizionati {m['proxy_sds']['conditional']:.6f}. Sono proxy per il futuro effetto principale, non effetti osservati nel nuovo disegno.",
'Ogni cluster contiene 32 venditori × 24 query. La varianza dei contrasti aggregati incorpora dipendenze interne e competizione; non si divide per 768 righe come se fossero indipendenti. Query e identità restano fisse. Non è identificabile una componente di varianza della ripetizione generativa dalle campagne con una sola replica per cella.','',
'Sensibilità SD ×1, ×1,5 e ×2 (varianza ×1, ×2,25, ×4): scenari dichiarati, non intervalli di confidenza della SD. Intenzione e template mostrano eterogeneità: risultati completi nel JSON. Non aggiungiamo un ICC inventato sopra una varianza già aggregata. Eventuale dipendenza temporale fra cluster è un rischio ulteriore.','',
'## Stime con approssimazione t, target 80%','',
'Le t non centrali assumono contrasti normali indipendenti; per i rapporti condizionati si aggiunge una linearizzazione. Il minimo operativo di 40 cluster è un limite prudenziale di pianificazione, non una soglia che garantisce validità. Questi numeri non sostituiscono il disegno conservativo proposto sotto.','',
'| Esito | Delta | Alpha | N teorico SD ×1 / ×2 | N operativo SD ×1 / ×2 | Chiamate se si genera, SD ×1 / ×2 |','|---|---:|---:|---:|---:|---:|']
for endpoint in ['total','retrieval','conditional']:
    for d in [.02,.05,.1]:
        rr=[x for x in r['planning'] if x['endpoint']==endpoint and x['delta']==d and x['target_power']==.8 and x['sd_multiplier'] in [1,2]]
        a,b=rr
        lines.append(f"| {endpoint} | {100*d:g} pp | {a['alpha']} | {a['n_normal_theory']} / {b['n_normal_theory']} | {a['n_with_minimum_40']} / {b['n_with_minimum_40']} | {a['calls_if_recommendation']} / {b['calls_if_recommendation']} |")
lines+=['','Ogni N è numero di assegnazioni indipendenti: 24 query, otto condizioni presenti simultaneamente (quattro vendor/cella), una replica generativa. Il terzo fattore è duplicazione della prosa nel body. Ogni effetto principale confronta 16 vendor contro 16. Non moltiplicare le chiamate per otto. Per retrieval puro il costo API è sempre zero; la colonna mostra il costo solo se si chiede anche una risposta per query. R=2 o R=3 costa rispettivamente 48N o 72N, senza una riduzione di N dimostrata. Tutte le potenze numeriche, i target 90% e SD ×1,5 sono in power-results.json.','',
'## Potenza conservativa basata sul supporto','',
'Il contrasto principale llms presente/assente confronta due gruppi di 16 vendor. Con massimo tre raccomandazioni il contrasto di ogni cluster è in [-3/16,+3/16], ampiezza L=0,375. Per retrieval top-5, L=0,625. Con cluster indipendenti, il test Hoeffding a numerosità fissa controlla alpha senza normalità.','',
'Soglia: r = L sqrt(log(2/alpha)/(2N)); rifiuto se |media| > r. Per una media vera di modulo almeno Delta, è sufficiente N ≥ L² [sqrt(log(2/alpha)) + sqrt(log(1/beta))]² / (2 Delta²). È un limite sufficiente conservativo, non un minimo necessario. Vale per dati completi e supporto rispettato; manca una garanzia analoga con dipendenze temporali non controllate.','',
'| Esito | Delta | Alpha | N per potenza ≥80% | N per ≥90% | API per 80% / 90% |','|---|---:|---:|---:|---:|---:|']
for endpoint in ['total','retrieval']:
    for d in [.02,.05,.1]:
        a,b=[x for x in r['bounded_guarantees'] if x['endpoint']==endpoint and x['delta']==d]
        lines.append(f"| {endpoint} | {100*d:g} pp | {a['alpha']} | {a['n']} | {b['n']} | {a['calls']} / {b['calls']} |")
lines+=['','Per l’esito condizionato non dichiariamo una numerosità garantita senza un limite inferiore credibile al recupero. Gli intervalli simultanei dei numeratori e denominatori danno intervalli conservativi per i rapporti; possono coprire tutto [-1,+1]. Le stime t sopra sono scenari informativi di costo, non garanzie. Se è obbligatoria potenza 80% anche per 5 pp condizionati, occorre approvare un disegno/budget distinto o validare ulteriormente il supporto.','',
'## Simulazioni diagnostiche, Delta 5 pp e SD ×2','',
'| Esito | N | Distribuzione dei contrasti | Rigetto sotto nullo | Potenza stimata | MCSE potenza |','|---|---:|---|---:|---:|---:|']
for x in r['simulations']:lines.append(f"| {x['endpoint']} | {x['n']} | {x['kind']} | {x['null_rejection']:.4%} | {x['power']:.2%} | {x['power_mcse']:.4f} |")
lines+=['','10000 simulazioni per cella, seed fisso. Nullo centrato: nessun effetto osservato usato come alternativa. Ricampionamento empirico dei contrasti preserva la variabilità aggregata del pilot, non genera il nuovo fattoriale completo. Normale e t5 possono generare contrasti fuori dal supporto: sono diagnostiche dell’approssimazione t, non simulatori realistici di liste top-3. La linearizzazione condizionata non simula denominatori nulli. Una frequenza 100% simulata non dimostra potenza esattamente uno; MCSE empirico nullo è solo l’esito finito. Non selezioniamo il metodo più favorevole.','',
'## Budget e assunzioni operative','',
f"Media storica: {m['mean_total_tokens_per_call']:.1f} token totali/chiamata; 7632 chiamate corrispondono orientativamente a {7632*m['mean_total_tokens_per_call']/1e6:.2f} milioni di token, prima dei controlli. Il nuovo contesto può cambiare consumo. Nessuna stima monetaria senza tariffa verificata.",
'Proposta principale: N=318, 7632 chiamate inferenziali +24 controlli generativi separati =7656 massime, nessun retry automatico. Se si desidera potenza conservativa 80% anche per retrieval a 5 pp, 1135 assegnazioni offline totali (le prime 318 condivise), 27240 recuperi di query e sempre 7656 API. Gli 817 snapshot aggiuntivi non generano risposte.','',
'Per dipendenza temporale residua, una sensitivity illustrativa con blocchi di dieci cluster e rho=0/0,05/0,10 usa DE=1+(10-1)rho, cioè 1/1,45/1,9: 318 diventa 318/462/605 cluster e 7632/11088/14520 chiamate inferenziali. È una correzione modellistica, non conserva automaticamente la garanzia Hoeffding; indipendenza o blocchi indipendenti richiedono giustificazione.','',
'Con il limite dichiarato di 500 chiamate/giorno, 7656 richiederebbero almeno 16 giornate a quota interamente disponibile. Non è una verifica del saldo né una promessa di disponibilità del servizio. Il periodo lungo aumenta il rischio di deriva: registrare e distribuire temporalmente le assegnazioni.','',
'Fonti metodologiche: [calcolo di potenza t, documentazione R](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/power.t.test.html); [t non centrale, SciPy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.nct.html); [disuguaglianze di concentrazione, Maurer–Pontil](https://www.cs.mcgill.ca/~colt2009/papers/012.pdf). La garanzia di potenza qui è derivata algebricamente dalla disuguaglianza, non riportata come risultato empirico.','',
'Riproduzione: python power_analysis.py, poi python render_power_report.py nella cartella. Sei test mirati in test_planning.py: nullo/tail t, numerosità minima, algebra del limite di potenza, copertura binomiale esatta selezionata, missing/overlap nullo, input invalidi. Non richiedono reti o credenziali.']
(P/'power-sensitivity.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('Written power-sensitivity.md')
