---
name: menu
description: >-
  Genera il menu dei 7 giorni e la lista della spesa in confezioni reali, a
  partire dal contesto gia' raccolto. Normalmente viene chiamata da
  lunario:settimana e non va invocata a mano: se l'utente chiede un menu
  partendo da zero, usare lunario:settimana. Da usare direttamente solo per
  rigenerare un menu con lo stesso contesto — "rifallo", "cambia i piatti ma
  tieni i vincoli", "riprova con meno carne".
---

# Menu — generazione

Motore vero e proprio. Non fa domande: consuma il contesto che le altre skill
hanno raccolto. Contratti e regole non negoziabili in `CLAUDE.md`.

## Input

`dati/profilo.yaml` · `dati/ritmi.yaml` · `dati/note.md` ·
`dati/storico.yaml` (tarature) · `dati/dispensa.yaml` ·
`settimane/<ISO>/contesto.yaml`. Se il contesto manca, chiama
`lunario:settimana` invece di indovinare.

## 1. I sette giorni

Ordine di applicazione dei vincoli — chi viene prima vince:

1. **Esclusioni del profilo** — anche come ingrediente nascosto
2. **Note e ritmi** — un giorno con `pranzo: fuori_trasportabile` riceve un
   piatto che viaggia e si mangia freddo, mai qualcosa da scaldare; un giorno
   con `cena_entro_min: 25` non riceve un piatto da 40 minuti
3. **Contesto della settimana** — le eccezioni si sovrappongono ai ritmi
4. **Deperibilita'** (`${CLAUDE_PLUGIN_ROOT}/kb/deperibilita.md`) — il fresco nei primi giorni, la
   dispensa in fondo. E' la regola che azzera lo spreco
5. **Rotazione** — mai i piatti delle ultime 2 settimane, mai i bocciati in
   quarantena, priorita' ai preferiti e alle voglie dichiarate
6. **Frequenze** (`${CLAUDE_PLUGIN_ROOT}/kb/porzioni-standard.md`) — pesce 2-3, carne max 3 di cui
   rossa max 1, legumi 2-4

Avanzi della settimana scorsa nei primi giorni. Se `bambini.selettivi`, ogni
cena porta la sua base neutra (`${CLAUDE_PLUGIN_ROOT}/kb/consigli-pratici.md`), segnalata in linea.

Porzioni da `${CLAUDE_PLUGIN_ROOT}/kb/porzioni-standard.md`, scalate sulle tarature e sul target
kcal di ogni persona. kcal indicative, arrotondate alle decine, mai spacciate
per misure.

## 2. Dai grammi alle confezioni

Il passo che rende la lista utile. Procedura completa in `${CLAUDE_PLUGIN_ROOT}/kb/confezioni.md`:

1. **fabbisogno** per ingrediente: porzione × persone × occorrenze
2. **meno la dispensa** (`dati/dispensa.yaml`)
3. **confezioni**: formato da `dati/prodotti.jsonl`; se il prodotto non c'e',
   `${CLAUDE_PLUGIN_ROOT}/scripts/off_lookup.py` lo cerca su Open Food Facts e lo aggiunge. Se non
   si trova nemmeno li', la riga resta in grammi e si marca
   `[formato da verificare]` — mai un formato a memoria
4. Applica la soglia del 10% (limare la porzione invece di comprare una
   confezione quasi inutile) e calcola l'avanzo previsto

Aggiorna `dati/dispensa.yaml` con gli avanzi previsti — **solo non
deperibili**, la fascia `[fine]` di `${CLAUDE_PLUGIN_ROOT}/kb/deperibilita.md`.

## 3. Il totale

Somma degli ultimi prezzi noti in `dati/prodotti.jsonl`. Ogni riga senza
prezzo si marca `[prezzo ignoto]` e resta fuori dal totale, che va dichiarato
come stima parziale — mai gonfiato con numeri inventati. Alla prima settimana
il totale puo' non esistere: e' normale, arriva col primo scontrino.

Se c'e' un `budget_settimana_eur` nelle tarature e la stima lo supera,
segnalalo in una riga e proponi la sostituzione a miglior €/100 g di proteine
(`${CLAUDE_PLUGIN_ROOT}/kb/consigli-pratici.md`).

## 4. Output

Salva `settimane/<anno>-W<settimana>.md`: i 7 giorni con pranzo, cena, kcal
per persona e base neutra dove serve; poi la lista per reparto in confezioni,
con il totale. Aggiungi la voce a `dati/storico.yaml` con `spesa_stimata`.

In chat: il menu, la lista, il totale. Stop. Le spiegazioni solo dove la
scelta non e' ovvia, una riga ciascuna.
