# Lunario sul server — il piano, per quando sarà il momento

Questo documento non è lavoro in corso: è la rotta scritta finché è fresca,
da riprendere quando si deciderà di partire. Nasce da due cose — una
riflessione di progetto dell'agosto 2026 e una lettera del 14 agosto 2026
arrivata dal Claude che lavora con Giovanni Porcari, che ha letto questo repo
e proposto un percorso concreto su **genro-asgi**. Il dettaglio tecnico riga
per riga sta nel repository di genro-asgi
(`temp/design_lunario_mcp_2026-08-14.md`); qui sta il *perché*, il *cosa non
si negozia* e la sequenza.

## Il problema vero, detto senza girarci intorno

Oggi Lunario vive in una cartella locale su file di testo, ed è insieme il suo
pregio e il suo limite. Il pregio: zero infrastruttura, dati che non escono di
casa, `git log` come macchina del tempo. Il limite non è il telefono — quello
lo copre già `claude remote-control`, con la sessione che gira sul computer di
casa — ma la **condivisione familiare**: la moglie che vota un piatto dal suo
telefono, il postmortem fatto a due voci, il figlio che segna «il latte è
finito». Con una cartella su un computer solo, tutto questo non esiste.

La risposta è un server con i dati in un posto solo e un MCP che va in combo
con le skill. La divisione dei ruoli è quella che regge tutto il porting, ed
è scritta meglio di così nella lettera:

> Il server non conduce l'intervista e non decide niente: la conversazione
> resta nella skill. Il server custodisce e restituisce.

Se durante il porting ci si accorge di scrivere nel server una frase come «se
manca il profilo, chiedi all'utente», si è oltre il confine: quella riga
appartiene alla skill. E l'avvertenza finale della lettera è il criterio
d'accettazione dell'intero progetto: **il server deve restare il quaderno,
non il questionario**. Il giorno in cui usare Lunario somiglia a compilare un
modulo, il porting è fallito anche se tecnicamente funziona.

## Il patto di privacy si rinegozia, non si aggira

«Resta tutto in casa» oggi non è un dettaglio tecnico di questo progetto: è
un pilastro dichiarato — nel README, nei template, nella sezione sul perché
niente remote — con i pesi e i dati di minori come argomento. Il server non
si *aggiunge* a quel patto: lo **rinegozia**, e la rinegoziazione va fatta
alla luce del sole:

- il server è **di casa** (self-hosted, o comunque sotto controllo diretto):
  la regola «nessun servizio esterno» sopravvive, cambia solo la stanza
- serve una risposta alla domanda che oggi risolve il git locale — vedere
  cosa è cambiato e tornare indietro. Un git lato server la dà quasi gratis,
  e le tarature che si spostano di poco alla volta la esigono
- il giorno in cui il server esiste, README e template che dicono «un dato
  caricato non rientra» vanno riscritti, non lasciati a contraddire il
  progetto da soli
- l'identità (tappa 6) decide chi vede cosa: la famiglia non è un utente, è
  un insieme di persone con ruoli — chi amministra, chi vota, cosa vede un
  ospite. È lavoro di disegno prima che di codice

## Cosa si guadagna, oltre alla comodità

1. **L'impossibilità di certi errori.** La macchina a stati della settimana —
   `preventivo → consuntivo` — oggi è una convenzione in testa a un
   file, che regge finché tutti la rispettano. Sul server diventa una regola
   che non si può violare: si passa a `consuntivo` solo esibendo uno scontrino,
   e non si torna indietro per distrazione. E con lei tutte le regole non
   negoziabili che non ammettono
   interpretazione: il pavimento delle 1200 kcal, il prezzo senza fonte che
   non entra, la serie storica che non si sovrascrive. Un errore di
   validazione in MCP non è un crash: torna al modello come risultato, e il
   modello si corregge da solo
2. **Il paniere cercato una volta per tutti.** Oggi ogni casa interroga Open
   Food Facts per conto suo; un server lo fa una volta e serve tutti, che è
   anche più rispettoso del loro «1 API call = 1 real scan»
3. **Le skill distribuite dal server** (quando genro-asgi avrà la primitiva
   *prompts*, issue [#26](https://github.com/genropy/genro-asgi/issues/26)):
   oggi una skill migliorata va aggiornata su ogni client; con quella, si
   cambia in un posto solo. Per un sistema il cui valore sta nel metodo, non
   è un dettaglio

## Cosa non cambia

- **Le otto skill restano la conversazione** — registro, una domanda per
  volta, proposta invece di domanda. Il porting cambia da dove prendono i
  dati, non come parlano
- **I contratti dati sopravvivono.** Profilo, storico, paniere, dispensa sono
  già contratti scritti (in `CLAUDE.md`): il server può servirli tali e
  quali, e i file JSON/YAML restano il formato — con il vantaggio, finché si
  può, che si aprono con un editor quando qualcosa non torna
- **La regola di confine regge anche sul server**: i livelli dichiarati
  (profilo, ritmi, note) si scrivono solo sotto dettatura dell'utente; le
  tarature le scrive solo il sistema. Un attrezzo MCP che scrive il profilo
  è la penna, non l'autore
- **Nessuna dipendenza da supermercati**, oggi come allora

## Le sei tappe

Il percorso proposto nella lettera, condensato. Ogni tappa è piccola,
verificabile, e non si passa alla successiva finché la verifica non risponde.

| tappa | cosa | la verifica |
|---|---|---|
| 0 | un server genro-asgi che risponde (`AsgiServer` + `@route()`) | `curl` su `/greet` |
| 1 | lo stesso metodo come attrezzo MCP (`McpOpenApiApplication`, `channel_channels="mcp"`) | `tools/list` restituisce l'attrezzo |
| 2 | collegarlo a Claude Code (`claude mcp add --transport http`) | il modello usa l'attrezzo da solo, guidato dalla firma |
| 3 | il primo pezzo vero: il profilo, ancora su file JSON — e la skill `profilo` riscritta per chiamare gli attrezzi | l'intervista funziona identica, ma i dati stanno di là |
| 4 | la prima regola difesa: `registra_scontrino` è l'unica via da `preventivo` a `consuntivo` | violarla restituisce un errore che il modello legge, non un crash |
| 5 | i dati in un database — **fermarsi e parlarne con Giovanni**: genro-asgi definisce il contratto, il backend è una scelta di progetto che si incrocia con l'ecosistema Genro | arrivarci con le tappe 0-4 in piedi, con domande invece che ipotesi |
| 6 | le famiglie: identità, tag, chi vede cosa | il disegno prima del codice |

La specifica della tappa 4 esiste già: è la tabella `preventivo / consuntivo`
nella skill `correggi`, scritta prima di sapere che sarebbe servita.

## Le dipendenze fuori da questo repo

Quattro segnalazioni aperte su genro-asgi, che condizionano l'arruolamento
delle persone più che il porting in sé:

- [#24](https://github.com/genropy/genro-asgi/issues/24) e
  [#25](https://github.com/genropy/genro-asgi/issues/25) — l'autorizzazione
  civile: un QR unico stampabile, la richiesta di ammissione, la tessera
  rilasciata spenta che l'amministratore di casa accende (e spegne, con
  effetto immediato). Avvertenza nota: oggi il collegamento si aggiunge da
  browser o desktop, non dall'app del telefono — dopo, funziona ovunque
- [#26](https://github.com/genropy/genro-asgi/issues/26) — la primitiva
  *prompts* per distribuire le skill dal server (vedi sopra)
- [#27](https://github.com/genropy/genro-asgi/issues/27) — un componente
  anti-bot che, se acceso, zittisce anche i documenti dell'autorizzazione
  senza messaggio d'errore. Oggi è spento; meglio sistemarlo prima che poi

## Dopo, se e quando

- **Un'interfaccia web tradizionale** sugli stessi dati, via `genropy-asgi`:
  griglie e maschere per le cose che a voce sono scomode — sfogliare lo
  storico, guardare il paniere, correggere una ricetta a mano. Il precedente
  in casa è Sourcerer, usato ogni giorno da entrambe le porte
- **Un bot Telegram** per le domande da dieci secondi — «cosa c'è stasera?»,
  «segna che il latte è finito». È la ciliegina: si mette quando la torta
  esiste, e quando l'uso avrà detto quali sono le tre domande che la famiglia
  fa davvero, perché a tavolino non si indovinano

## Quando si parte

Non adesso, e la scelta è deliberata: Lunario 2.x deve prima girare in casa
abbastanza settimane da dire cosa manca davvero. Quando si parte, si parte
dalla tappa 0, in un repo suo, e questo documento si aggiorna tappa per tappa
— insieme al patto di privacy nel README, che è la prima cosa da riscrivere e
l'ultima da dimenticare.
