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

Classifica ogni riga in tre gruppi, facendolo tu, senza interrogare l'utente
riga per riga:

| gruppo | cosa ci finisce | dove va |
|---|---|---|
| **menu** | quello che era in lista | `spesa_reale`, prezzi nel paniere |
| **alimentare fuori lista** | cibo comprato ma non previsto: frutta, snack, bevande | `spesa_extra_alimentare`, prezzi nel paniere |
| **non Lunario** | detersivi, casa, igiene, animali, regali, roba per altri | fuori da tutto: nessun prezzo, nessun totale |

Il non alimentare si riconosce dalla descrizione. Quello che **non** si puo'
dedurre e' il «comprato per altri»: un pane e' un pane anche se e' della
vicina. Per quello non tirare a indovinare.

Poi presenta il riepilogo **in una domanda sola**, non tre:

> Su 118,40 € di scontrino: **89,40 di spesa del menu**, 12,00 di alimentari
> fuori lista (frutta, yogurt), 17,00 non alimentari (detersivi, carta).
> Torna, o c'e' qualcosa che ho messo nel posto sbagliato?

Una correzione dell'utente basta a riclassificare. Solo `spesa_reale` si
confronta con `spesa_stimata`: il budget riguarda il menu, non lo scontrino.

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
