---
name: ritmi
description: >-
  Registra gli orari e gli impegni RICORRENTI della famiglia — chi pranza
  fuori il martedi', quale sera c'e' poco tempo per cucinare, quando si mangia
  tardi — in dati/ritmi.yaml, e i vincoli liberi in dati/note.md. Da invocare
  quando l'utente dice "i nostri orari", "tutti i martedi'", "ogni settimana
  succede che", "e' cambiato il mio orario di lavoro", "segnati che" per un
  vincolo permanente. NON usarla per gli impegni di una singola settimana:
  quelli vanno a lunario:settimana.
---

# Ritmi — la settimana tipo

Scrive il livello **dichiarato**: vale finche' l'utente non lo cambia, e il
sistema non lo tocca mai da solo. Contratti in `CLAUDE.md`.

## Prima di tutto: la cartella e' allineata?

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/versione.py --controlla
```

Se risponde `migrazione necessaria`, passa da `lunario:aggiorna` e **poi torna
qui**: allineare la cartella e' il presupposto, non il lavoro che l'utente ha
chiesto. Se risponde `ok`, non dire niente — un controllo di versione che si fa
notare ogni lunedi' e' rumore.

## La distinzione che regge tutto

| | dove va |
|---|---|
| «il martedi' pranzo sempre fuori» | qui, `dati/ritmi.yaml` |
| «questo martedi' pranzo fuori» | `lunario:settimana` |

Nel dubbio chiedilo: «capita ogni settimana o solo questa?». Un ritmo
sbagliato inquina i menu per mesi; un contesto sbagliato dura sette giorni.

## Cosa raccogliere

La griglia **pasto × persona**, per giorno, solo dove c'e' qualcosa da dire —
un giorno senza vincoli non si scrive. Gli stati di una cella sono quelli di
`CLAUDE.md`:

| stato | quando |
|---|---|
| `casa` | il default: si cucina e si compra |
| `trasportabile` | deve viaggiare e mangiarsi freddo |
| `libero` | si cucina e si compra, ma non conta: la pizza del sabato |
| `ristorante` | fuori, e si paga: non si cucina ma la spesa esiste |
| `fuori` | mensa, bar, dai nonni: fuori dal sistema |
| `no` | quella persona quel pasto non lo fa |

Oltre alla griglia, per ogni giorno:

- **cena_entro_min**: i minuti veri ai fornelli quella sera, se sono meno del
  solito. La sera della piscina non e' la sera del risotto
- **note del giorno**: rientro tardi, cena presto per i bambini, chi manca

`tutti` al posto di un nome vale per l'intera tavola: «il sabato sera pizza
per tutti» si scrive una volta.

Chiedi in modo discorsivo — «raccontami una settimana tipo» — e ricostruisci
tu la griglia, invece di interrogare giorno per giorno. Poi rileggi quello che
hai capito e fatti correggere.

**I pasti fuori casa ricorrenti sono la meta' del valore di questo file.** Un
pranzo in mensa il mercoledi' e una pizzeria fissa il venerdi' sono due piatti
cucinati per nessuno ogni settimana, piu' la spesa relativa. Se l'utente
racconta la settimana senza nominarli, chiediglielo una volta: «c'e' qualche
pasto che di regola non si fa a casa?».

## I vincoli che non sono orari

«Il forno e' guasto», «niente piatti che puzzano di pesce in casa», «il sabato
si mangia dai nonni»: non sono griglia, sono testo. Vanno in `dati/note.md`,
permanenti oppure con `[fino al AAAA-MM-GG]` se hanno una scadenza.

Quando l'utente dice «segnati che ...», e' qui che finisce: aggiungi la riga,
conferma con una riga sola, non rigenerare niente se non te lo chiede.

## Manutenzione

A ogni lancio delle altre skill le note scadute vanno segnalate e ne va
proposta la rimozione — **proposta**, mai eseguita d'ufficio. Se un ritmo
viene contraddetto dal contesto settimanale per tre settimane di fila, dillo:
probabilmente il ritmo e' cambiato e nessuno l'ha aggiornato.
