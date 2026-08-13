---
name: postmortem
description: >-
  Chiusura della settimana, la domenica. Tre domande — cosa e' avanzato, che
  voto danno i commensali ai piatti e da chi viene, se c'e' stata spesa
  integrativa — poi ritara porzioni, rotazione dei piatti e budget per la
  settimana successiva. Da invocare quando l'utente dice "postmortem",
  "com'e' andata la settimana", "chiudiamo la settimana", "e' avanzato...",
  "ai bimbi non e' piaciuto...", o la domenica. NON e' la skill dello
  scontrino della spesa grande: quello si registra al ritiro, con
  lunario:spesa.
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

**3. C'e' stata altra spesa in settimana?** Non lo scontrino grande: quello e'
gia' stato registrato da `lunario:spesa` il giorno del ritiro, e i prezzi sono
gia' nel paniere. Qui interessa solo la spesa **integrativa** — il salto al
negozio del giovedi' — perche' se ricorre significa che la lista del lunedi'
sbaglia sistematicamente qualcosa.

Se c'e' uno scontrino anche per quella, leggilo con `read-document` e applica
le stesse regole di `lunario:spesa`: prezzi nella serie con la data, sigle
nuove in `alias_scontrino`, totale sommato a `spesa_reale`.

Se invece il ritiro non e' mai passato da `lunario:spesa` — capita — allora
chiedi lo scontrino principale qui, e trattalo come farebbe quella skill.

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
