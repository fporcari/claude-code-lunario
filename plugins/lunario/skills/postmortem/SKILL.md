---
name: postmortem
description: >-
  Chiusura della settimana. Tre domande — cosa e' avanzato, cosa e' piaciuto o
  bocciato e da chi, e lo scontrino della spesa — poi ritara porzioni, piatti
  e prezzi per la settimana successiva. Dallo scontrino PDF ricava prodotti
  reali e prezzi pagati e aggiorna il paniere. Da invocare quando l'utente
  dice "postmortem", "com'e' andata la settimana", "chiudiamo la settimana",
  "ecco lo scontrino", "e' avanzato...", "ai bimbi non e' piaciuto...", o la
  domenica.
---

# Postmortem — cosa si e' imparato

E' il pezzo che distingue il sistema da un generatore di menu qualsiasi.
Scrive il livello **appreso**. Regole di ritaratura in `CLAUDE.md`.

## Le tre domande

Una per volta, secche. L'utente e' a fine settimana, non ha voglia di
un'intervista.

**1. Cosa e' avanzato?** Sia il cibo cucinato non mangiato, sia le confezioni
non aperte. Distingui le due cose: la prima e' una porzione sbagliata, la
seconda e' un fabbisogno sbagliato.

**2. I voti.** Per i piatti della settimana, un voto **da 1 a 5** e da chi
viene. Non chiederli uno per uno come un esame: proponi i piatti della
settimana e lascia che l'utente voti quelli che gli sono rimasti in mente —
il silenzio su un piatto vale «nella media», e va bene cosi'.

Il «chi» non e' un dettaglio: un 2 dei bambini su un piatto che gli adulti
hanno votato 4 si risolve con una base neutra piu' generosa, non togliendo il
piatto. Un 2 di tutti e' un piatto che esce.

Registra i voti in `tarature.voti` di `dati/storico.yaml`: media, numero di
voti e chi ha votato cosa. La media guida la rotazione — sopra 4 e' un
preferito, sotto 2 un bocciato — quindi non servono liste separate.

**3. Lo scontrino.** Se l'utente ha il PDF, chiedilo. Se non ce l'ha o non gli
va, basta il totale speso: il resto si fa lo stesso, con meno precisione.

## Lo scontrino

Il PDF si legge con la skill `read-document` — nessun parser da scrivere.
Da ogni riga ricava descrizione, quantita' e prezzo pagato, poi aggiorna
`dati/prodotti.jsonl`:

- **Riga riconosciuta** (la descrizione e' in `alias_scontrino` di un
  prodotto): aggiungi il prezzo alla serie `prezzi` con la data dello
  scontrino. Mai sovrascrivere i prezzi vecchi: la serie e' il valore
- **Riga nuova**: chiedi conferma all'utente una volta sola — «`PSTA INTGR
  500` e' la pasta integrale da 500 g?» — poi salva la sigla in
  `alias_scontrino` e non chiedere mai piu'. Se il prodotto non esiste ancora
  nel paniere, cercalo su Open Food Facts con
  `${CLAUDE_PLUGIN_ROOT}/scripts/off_lookup.py` per avere formato e nutrienti
- **Righe fuori lista**: quello che e' stato comprato senza essere a menu.
  Non e' un errore, e' informazione: segnalalo in una riga nelle note della
  settimana. Se ricorre, e' un consumo reale che il menu ignora

Non chiedere conferma per ogni riga: raggruppa le sconosciute e chiedile
insieme. Le righe che restano ambigue si lasciano fuori, dichiarandolo.

Poi registra `spesa_reale` e lo **scarto per riga** rispetto alla stima: dove
la previsione ha sbagliato, non solo di quanto. E' il dato che rende onesto il
totale del lunedi' successivo.

## La ritaratura

Applicala e dichiarala, senza chiedere permesso per le regole automatiche:

| osservazione | conseguenza |
|---|---|
| stesso avanzo per 2+ settimane | riduci la porzione in `tarature.porzioni_g` |
| media del piatto **sotto 2** | fuori rotazione 3 settimane |
| media sotto 2 per la seconda volta | in `piatti_esclusi` — questa **chiedila**, e' definitiva |
| media **sopra 4** | priorita' nella rotazione |
| voto basso dei soli bambini | non toccare il piatto: rinforza la base neutra |
| confezione avanzata 2 volte di fila | il formato e' sbagliato: proponi di cercarne uno piu' piccolo |
| sforo del budget | privilegia i piatti a miglior €/100 g di proteine (`${CLAUDE_PLUGIN_ROOT}/kb/consigli-pratici.md`) |

Correggi anche `dati/dispensa.yaml` sul reale: gli avanzi previsti dal menu
sono una stima, quello che c'e' davvero lo sa solo l'utente.

## Chiusura

**Una riga sola**: cosa cambia la settimana prossima. Non un riepilogo di
tutto quello che hai scritto nei file — l'utente ha appena chiuso la
settimana, non vuole rileggerla.
