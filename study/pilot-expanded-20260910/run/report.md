# Audit Black Box V2

Esperimento con generatore API

| Bundle | P(recuperato) | P(nome nel contesto) | P(raccomandato), risposte valide |
|---|---:|---:|---:|
| A | 0.041 | 0.041 | 0.034505208333333336 |
| B | 0.047 | 0.047 | 0.03515625 |
| C | 0.001 | 0.001 | 0 |
| D | 0.047 | 0.047 | 0.045572916666666664 |

Stati risposte: {'valid': 192, 'not_run': 0}.

Il retrieval è realmente eseguito sul corpus artificiale. La sitemap non interviene nella scoperta: tutti i file sono caricati da manifest.
I punteggi Agentabile non sono ancora calibrati. I bundle non equivalgono a dosi 20/40/60/80.
Le probabilità condizionate sono descrittive; non quantificano mediazione causale.
