# Changelog

Le versioni che contano sono quelle che cambiano il **contratto dei dati**: da
4.0.0 la cartella di casa porta un timbro (`dati/versione.yaml`) e si allinea da
sola, quindi aggiornare il motore non richiede piu' niente da parte tua.

## 4.1.0 — quello che manca e te lo prendi dopo

Al ritiro della spesa un ingrediente puo' non esserci, e gli esiti sono sempre
stati due: **si cambia il piatto**, oppure **te lo procuri tu** prima del giorno
in cui serve. Il primo era completo; il secondo viveva soltanto in chat, e una
chat non la rilegge nessuna skill. Il giovedi' `lunario:prepara` faceva cucinare
un piatto convinta che il branzino fosse in casa.

- **`sospesi`** nel `diario.yaml` della settimana: cosa manca, per quale pasto
  serve, e uno stato fra `da_procurare`, `procurato` e `rinunciato`. Effimero
  come la settimana — nasce allo scontrino, muore la domenica
- `lunario:spesa` offre i due esiti come due strade, non come una domanda
  aperta, e scrive il rimando invece di ricordarlo
- `lunario:prepara` lo nomina **il giorno in cui serve**, per primo e una volta
  sola: «il branzino era rimasto da prendere, l'hai preso?». Un no va dritto
  alla sostituzione, senza rimproveri
- `lunario:correggi` non ricolloca su un ingrediente che non e' in casa
- `lunario:postmortem` chiude quelli aperti, e conta i sospesi fra le mancanze:
  tre volte lo stesso prodotto non e' sfortuna, e' un paniere da correggere
- **un sospeso non e' una scorta**: finche' e' `da_procurare` non entra in
  dispensa, altrimenti il menu del lunedi' dopo scala un fabbisogno su roba che
  nessuno ha comprato
- il consuntivo porta in coda **«Da procurare»**, senza casella: lo stato vero
  sta nel diario, e due posti dove segnare la stessa cosa si contraddicono

Il **contratto dei dati non cambia** — la chiave e' nuova, opzionale e vive
dentro una settimana — quindi non c'e' niente da migrare: le cartelle esistenti
funzionano come sono.

Il tier 1 ora controlla il diario, che prima non guardava nessuno: date, pasti,
stati, e la forma dei sospesi. Due proprieta' nuove al tier 2 — il rimando
scritto in pagina deve stare anche nei file, e un sospeso non compare in
dispensa.

## 4.0.0 — la dispensa che sa cosa hai in casa

Tre issue in una release. Il contratto di `dati/dispensa.yaml` cambia, e da qui
in avanti la cartella sa migrare se stessa: e' la ragione per cui questa e' una
major.

### La dispensa profonda ([#12](https://github.com/fporcari/claude-code-lunario/issues/12))

Una casa non parte da zero, e sbaglia in due modi opposti: **compra quello che
ha gia'** (te ne accorgi svuotando la busta) e **accumula il quinto pacco della
stessa cosa** (non te ne accorgi mai). Il secondo si chiude col dato piu' grezzo
che esista, un tetto per prodotto — ed e' l'asimmetria che ha permesso di **non**
costruire un magazzino.

- `dati/dispensa.yaml` passa a **tre sezioni**: `scorte` (contate da un umano,
  grossolane, durano mesi), `avanzi` (calcolate dal motore), `freezer` (viste
  aprendo lo sportello)
- **bande invece di grammi**: `pieno | medio | poco | finito`, o un numero di
  confezioni. Nessuno pesa la farina
- **`soglia`** rimette in lista, **`massimo`** toglie dalla lista e lo dice
- la **fiducia non si memorizza, si calcola** da quando la riga e' stata vista
  l'ultima volta: fresca si sottrae in silenzio, invecchiata si sottrae
  dichiarandolo, stantia non si crede
- **`lunario:inventario`**, la skill nuova: il giro delle tre zone a voce o
  dalle foto degli scaffali, in blocco, con una tabella sola da correggere. Mai
  un modulo — l'inserimento a mano e' la causa di morte di ogni app di dispensa
- il lunedi' non e' piu' un censimento: `lunario:settimana` fa correggere **sei
  righe**, scelte dove l'incertezza incontra l'impatto. Chi taglia corto non
  perde niente
- il **valore della dispensa** in euro, dai tuoi scontrini, all'inventario e al
  postmortem
- `spesa` incrementa dallo scontrino, `menu` e `prepara` scalano come stima,
  `postmortem` corregge: **nessuno di questi tocca `visto`**

### La cartella si aggiorna da sola ([#13](https://github.com/fporcari/claude-code-lunario/issues/13))

- **`dati/versione.yaml`**: contratto, motore, data. Le cartelle nate prima non
  ce l'hanno, e il contratto si deduce dalla forma dei file, una volta sola
- **`lunario:aggiorna`**, la skill nuova: tutta la logica di migrazione in un
  posto solo, dichiarativa e idempotente. Non la invochi — la chiamano le altre
- tre comportamenti: additivo in silenzio, riscrittura applicata e riportata in
  una riga, e cio' che **serve a te** non viene inventato — resta assente e te
  lo si chiede al momento giusto
- da cui la regola che vincola tutto quello che verra': **ogni contratto nuovo
  deve degradare bene quando manca**. Una cartella che non migra mai continua a
  funzionare
- `lunario:profilo` torna a essere solo l'intervista

### Si sa cosa si rompe ([#14](https://github.com/fporcari/claude-code-lunario/issues/14))

- tre tier: il **lint dei contratti** (zero token, gira sempre), il **giro
  intero headless** su una casa sintetica, e un **parere** sul menu che non puo'
  far fallire niente
- tre case sintetiche in `tests/fixtures/`, piu' uno scontrino sintetico in PDF
- le «Regole non negoziabili» diventano asserzioni

### Rotture

Nessuna, per chi usa Lunario dalla chat. Il contratto di `dispensa.yaml` cambia,
ma in modo **additivo**: una cartella senza `scorte` continua a generare menu
esattamente come prima — ha solo la lista piu' lunga. La migrazione avviene da
sola alla prima skill che lanci, e l'annullamento e' `git revert` nella tua
cartella.

## 3.2.0

Template del menu mobile-first, il vestito della settimana, la sezione «Gia' in
casa».

## 3.1.0

README riscritto attorno al giro completo.

## 3.0.0

Preventivo e consuntivo: il menu ha due stati, e la promozione la fa solo
`lunario:spesa` con lo scontrino in mano.
