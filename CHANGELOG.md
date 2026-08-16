# Changelog

Le versioni che contano sono quelle che cambiano il **contratto dei dati**: da
4.0.0 la cartella di casa porta un timbro (`dati/versione.yaml`) e si allinea da
sola, quindi aggiornare il motore non richiede piu' niente da parte tua.

## 5.0.0 — la settimana e' una cartella, e la lista torna indietro

Nasce da una spesa vera all'Esselunga, col telefono in mano: la pagina HTML si
impallava, le spunte si perdevano, e ritrovare il punto costava piu' del fare la
spesa a memoria. Sotto l'inciampo c'erano tre difetti diversi, e il piu' grave
non era la pagina.

**La lista della spesa e' un file, ed e' un ingresso di dati.** Le spunte
dell'HTML vivevano in `localStorage`: restavano nel browser di quel telefono, e
`lunario:spesa` non le vedeva mai. Chi le faceva credeva di aver detto qualcosa
al sistema — che e' esattamente la regola gia' scritta per il consuntivo, uno
stato dentro una pagina e' invisibile alle skill **e lo e' in silenzio**. Adesso
la spesa e' `<nome>-lista.md`: reparti nell'ordine del negozio, una casella per
riga che vuol dire «preso», la riga d'uso sotto, e «Fuori Lunario» in coda.
Si apre col telefono da una cartella sincronizzata, si annota a mano — «non
c'erano, prese 2 da 70 g» — e al ritorno `lunario:spesa` **riapre lo stesso
file**. Nessuna esportazione, nessuna seconda copia da riconciliare, nessuna
dipendenza da Apple o da nessun altro: il markdown e' testo, e la
sincronizzazione e' una proprieta' della cartella. Una cartella non
sincronizzata funziona identica.

Le annotazioni hanno una gerarchia di fiducia, ed e' la meta' che conta:
**l'annotazione vince su quale prodotto e' entrato in casa** — l'utente era li'
— **lo scontrino vince su quanto e' costato**, che e' stampato. Una frase che
non si classifica non si interpreta: si chiede una volta.

**La settimana e' una cartella, e ci sta tutto dentro** — preventivo, lista,
consuntivo, postmortem, contesto, diario — ognuno col nome intero, perche' un
file scaricato sul telefono perde la cartella e `preventivo.md` nudo non dice
piu' di che settimana sia.

- **preventivo e consuntivo sono due file**, non uno stato che si sovrascrive:
  lo scarto fra i due e' la cosa che insegna qualcosa, e non deve richiedere un
  `git diff`
- **il documento vivo e' l'ultimo ruolo che esiste su disco**: il consuntivo se
  c'e', altrimenti il preventivo. E' li' che `prepara` spunta e `correggi`
  riscrive — anche a consuntivo scritto, perche' un fatto che scombina il piano
  e' esattamente cio' che un registro deve dire
- **il postmortem lascia un file**: com'e' andata, cosa e' cambiato, cosa resta
  aperto. Prima finiva fra `storico.yaml` e la chat, e la chat a febbraio non la
  rilegge nessuno
- lo risolve `scripts/settimana.py`, in un posto solo: cinque skill che
  compongono a mano gli stessi percorsi, dopo tre release sono cinque idee
  diverse di dove stiano i file

**Il consuntivo chiude sul cibo di casa, non sul totale della cassa.** Su uno
scontrino vero da 233,26 € c'erano uno zaino da 45,90 €, la carta igienica e la
spesa della suocera: la skill scorporava tutto correttamente e poi rimetteva il
totale di cassa nell'ultima riga, facendo sembrare la settimana costata il
doppio. Adesso l'etichetta e' «Totale cibo di casa» e il numero e' `spesa_reale`
+ `spesa_extra_alimentare`; il totale dello scontrino resta accanto, dichiarato
per quello che e'. E la spesa fatta per un'altra casa **resta in pagina**, voce
per voce e col suo subtotale: e' fuori dai conti, non cancellata dal documento —
quanto si deve a qualcuno e' il numero che si sta cercando.

Altro, piu' piccolo:

- **una casella, un significato.** «Preso» sulla lista, «fatto» sui pasti. Il
  consumo non e' una casella: sta in `dispensa.yaml` e nel diario. Prima la
  stessa casella voleva dire comprato, arrivato e consumato a seconda di chi la
  guardava
- **lo scontrino fotografato** si legge a due colonne separate, appaiando per
  indice e verificando la somma contro il totale stampato: su una foto storta le
  due colonne scivolano di una riga intera, e i prezzi finiscono sul prodotto
  sbagliato
- l'HTML resta e cambia mestiere: si stampa, si attacca al frigo, si mostra a
  chi la settimana la deve mangiare. Niente piu' caselle cliccabili

**Il contratto dei dati sale a 4**, e la migrazione **non sposta un solo file**.
Le settimane gia' scritte restano dove sono, col nome che hanno: lo script le
riconosce come `layout: piatto` e le trova comunque. Vale anche per la settimana
in corso, che e' il caso a cui viene voglia di fare un'eccezione — migrare un
documento mentre qualcuno ci sta cucinando sopra e' la sorpresa che questo
meccanismo esiste per non fare. Le settimane nuove nascono nella cartella.

## 4.1.1 — tre regole che il motore non poteva eseguire

Trovate facendo girare il tier 2 su `famiglia`: il giro passa, ma tre cose
scritte nelle skill non avevano modo di funzionare. Tutte e tre nate con la
4.0.0.

- **«Fuori rotazione per 3 settimane» non aveva dove atterrare.** `settimana` e
  `postmortem` lo ordinavano entrambe, ma `storico.yaml` aveva solo
  `piatti_esclusi`, che e' permanente: il piatto rientrava il lunedi' dopo come
  se niente fosse. Ora c'e' `tarature.piatti_in_quarantena`, con `fino_al`,
  `volte` e `perche` — le voci scadute si tolgono passando, e alla seconda volta
  si propone l'esclusione definitiva, che e' la regola che gia' c'era e che ora
  ha come contarla
- **`scorte` e `freezer` potevano descrivere lo stesso pacco**, e la formula lo
  sottraeva due volte: il motore credeva di avere il doppio del pesce. Vale la
  precedenza `freezer` > `scorte` > `avanzi`, chi scrive non duplica, e il tier 1
  lo segnala come avviso — due scorte davvero distinte restano possibili
- **`menu` e `prepara` scaricavano entrambi le scorte.** Adesso il menu le
  **legge e basta**: un piano non consuma niente, e una settimana pianificata e
  mai cucinata lasciava la dispensa piu' vuota del vero. Scarica solo `prepara`,
  che vede cosa e' finito in pentola

Il contratto dei dati non si muove: `piatti_in_quarantena` e' una chiave nuova e
opzionale, e una cartella senza continua a funzionare.

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
