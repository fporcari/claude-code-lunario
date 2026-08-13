---
name: spesa
description: >-
  Riconcilia la spesa appena ritirata con la lista: dallo scontrino PDF ricava
  prodotti, quantita' e prezzi veri, spunta cio' che e' arrivato, segnala cosa
  manca o e' stato sostituito e — se un piatto e' compromesso — propone
  un'alternativa con quello che c'e' in casa. Aggiorna prezzi, paniere e
  dispensa sul reale. Da invocare quando l'utente dice "ho ritirato la spesa",
  "ho fatto la spesa", "ecco lo scontrino", "la spesa e' arrivata", "sono
  tornato dal supermercato", o passa un PDF di scontrino a inizio settimana.
---

# Spesa — quello che e' arrivato davvero

Si lancia **prima di cominciare a cucinare**, appena ritirata la spesa. E' il
momento in cui il sistema smette di lavorare su stime e passa ai fatti: la
lista diceva cosa serviva, lo scontrino dice cosa c'e'.

Regole e contratti in `CLAUDE.md`.

## 1. Leggi lo scontrino

Il PDF si legge con la skill `read-document` — nessun parser da scrivere. Da
ogni riga: descrizione, quantita', formato se c'e', prezzo pagato.

Se l'utente non ha il PDF, si puo' fare lo stesso a voce, ma dillo una volta:
col documento la riconciliazione e' esatta, a memoria e' approssimativa.

## 2. Separa cio' che riguarda Lunario

**Lo scontrino contiene molto piu' del menu**: detersivi, carta casa, prodotti
per l'igiene, cose comprate per qualcun altro. Quella roba non e' spesa
alimentare e non deve inquinare ne' il budget ne' il paniere.

**Il non alimentare lo scarti tu**, in silenzio: detersivi, carta casa,
igiene, animali, cartoleria si riconoscono dalla descrizione e non entrano
nemmeno nella lista che mostri. Se sei incerto su una riga, tienila: e' meno
fastidioso togliere una riga di troppo che scoprire dopo che ne mancava una.

Quello che **non** si puo' dedurre e' cosa di alimentare e' davvero di questa
casa: la spesa per la suocera sta sullo stesso scontrino, a volte sulla stessa
riga. Quindi presenta le righe alimentari come una **lista numerata con le
caselle gia' spuntate da te**, e falla correggere:

```
Alimentari sullo scontrino — ho spuntato quello che mi risulta vostro:

 1. [x] Fusilli integrali 500 g × 2      2,38 €   (era in lista)
 2. [x] Zucchine 600 g                   1,49 €   (era in lista)
 3. [x] Yogurt greco 125 g × 6           3,60 €   (gia' nel paniere)
 4. [ ] Biscotti frollini 700 g          2,90 €   (mai visto)

Togli, aggiungi o dimmi se di qualcosa e' vostra solo una parte.
```

Come pre-spuntare, in ordine di certezza:

| riga | casella |
|---|---|
| era nella lista della spesa di questa settimana | `[x]`, con «era in lista» |
| non era in lista ma e' gia' nel paniere | `[x]`, con «gia' nel paniere» |
| mai vista prima | `[ ]`, con «mai visto» |

Il motivo fra parentesi conta quanto la casella: dice all'utente **perche'** hai
deciso cosi', e gli permette di correggerti in una parola.

**Le quantita' parziali sono la regola, non l'eccezione.** «Degli yogurt tre
sono nostri» significa che la riga vale per meta': registra 3 pezzi e la meta'
del prezzo nella spesa di casa, e lascia fuori il resto. Non chiedere di
dividere ogni riga: chiedilo solo dove l'utente lo dice.

Le righe spuntate diventano `spesa_reale` (se erano in lista) o
`spesa_extra_alimentare` (se no). Solo la prima si confronta con
`spesa_stimata`: il budget riguarda il menu, non lo scontrino.

## 2a. Quello che non passa dallo scontrino

Alcune cose del menu si comprano altrove — il pane dal panettiere sotto casa,
le uova dal contadino, la frutta al mercato. Non sono **mancanti**: sono solo
comprate da un'altra parte.

La prima volta che un ingrediente del menu non compare sullo scontrino,
chiedilo insieme alle altre domande: «il pane non c'e' sullo scontrino — lo
prendi altrove o e' saltato?». Se la risposta e' «altrove», scrivi
`"fuori_scontrino": true` sul prodotto in `dati/prodotti.jsonl` e **non
chiederlo mai piu'**: da li' in poi resta in lista della spesa ma non viene
cercato nello scontrino ne' segnalato come mancante.

Il prezzo di quei prodotti resta quello che l'utente dichiara, quando gli va:
meglio un prezzo vecchio dichiarato tale che una riga vuota.

## 2b. Riconcilia con la lista

Per le righe del gruppo **menu**, confronta con la lista in
`settimane/<ISO>.md`. Quattro esiti, e solo due meritano di essere raccontati:

| esito | cosa fai |
|---|---|
| **arrivato come previsto** | spunta la riga, in silenzio |
| **formato diverso** (chiesto 500 g, dato 400 g) | il reale vince: ricalcola se il fabbisogno regge, e se non regge dillo |
| **manca** | vai al punto 3 |
| **in piu'**, fuori lista | gia' classificato sopra: nessun commento |

Il riconoscimento delle sigle segue le regole del paniere: se
`FUSILLI INTGR 500` e' gia' in `alias_scontrino`, si riconosce da solo; se e'
nuova, chiedi conferma una volta sola e poi salvala. Raggruppa le sconosciute
in una domanda unica invece di chiederle a una a una.

## 3. Cosa manca, e se e' un problema

Per ogni riga mancante, la domanda non e' «manca?» ma **«questo fa saltare un
piatto?»**. Rispondi tu, guardando il menu, e distingui:

- **Ininfluente** — mancano i pomodorini di guarnizione: annota e basta, non
  disturbare l'utente per questo
- **Sostituibile con quello che c'e'** — proponi la sostituzione gia' fatta:
  «non c'e' il branzino: giovedi' sposto sul merluzzo che hai nel
  congelatore». Una riga, non una domanda aperta
- **Compromette il piatto** — qui chiedi: cosa c'e' in casa che puo' sostituire,
  oppure se preferisce ricomprarlo. Se sceglie di ricomprare, tieni la riga in
  sospeso e ricordagliela; se sceglie di sostituire, aggiorna quel giorno nel
  menu

Non riscrivere l'intera settimana per un ingrediente: tocca i giorni colpiti e
lascia stare il resto. Se i giorni colpiti sono tanti, e' il caso di
`lunario:correggi`, e dillo.

## 4. Aggiorna i file

- **`dati/prodotti.jsonl`** — prezzo pagato con la data dello scontrino,
  aggiunto alla serie `prezzi` (mai sovrascrivere i vecchi); sigle nuove in
  `alias_scontrino`; formato reale se diverso da quello che si credeva. Per un
  prodotto mai visto, `${CLAUDE_PLUGIN_ROOT}/scripts/off_lookup.py` recupera
  formato e nutrienti
- **`dati/dispensa.yaml`** — quello che entra in casa e non si consuma questa
  settimana, solo non deperibili
- **`dati/storico.yaml`** — `spesa_reale` (solo il menu), accanto a
  `spesa_extra_alimentare` e `totale_scontrino` per memoria; e
  `scarto_per_riga`: dove la stima ha sbagliato, non solo di quanto. E' il dato
  che rende onesto il totale del lunedi' successivo
- **`settimane/<ISO>.md`** — righe spuntate, e i giorni corretti se ci sono
  state sostituzioni

## 5. Chiudi corto

L'utente ha le buste da svuotare. Due o tre righe:

- quanto ha speso davvero e di quanto si e' discostato dalla stima
- cosa manca e cosa hai fatto di conseguenza
- se resta qualcosa da ricomprare

Se e' andato tutto liscio, **una riga sola**: «Tutto arrivato, 89,40 € contro
i 92,50 stimati. Buona settimana.»

## Perche' questo momento conta

Lo scontrino a inizio settimana, invece che alla fine, cambia due cose:

1. **Le sostituzioni si fanno prima di cucinare**, non davanti al frigo vuoto
   il giovedi' sera
2. **I prezzi entrano nel paniere sette giorni prima**, quindi la stima del
   lunedi' successivo lavora su dati di una settimana fa invece che di due

Il postmortem della domenica, di conseguenza, non chiede piu' lo scontrino:
chiede avanzi e voti. Se c'e' stata una seconda spesa in settimana, quella si'
che si porta al postmortem.
