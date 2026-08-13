---
name: correggi
description: >-
  Corregge il menu a settimana gia' iniziata, quando cambia qualcosa in corsa
  — una cena salta, arrivano ospiti, un piatto non e' piaciuto, e' avanzato
  qualcosa da smaltire, non c'e' voglia di quello che era previsto. Chiede
  cosa deve cambiare e cosa c'e' in frigo, poi ripropone solo i giorni che
  restano riusando la spesa gia' fatta. Da invocare quando l'utente dice
  "cambio idea", "stasera non mi va", "ho ospiti giovedi'", "e' saltata la
  cena di ieri", "cosa faccio con quello che ho in frigo", "non ho voglia di
  cucinare stasera".
---

# Correggi — la settimana e' gia' in corso

La differenza con `lunario:settimana` e' tutta qui: **la spesa e' gia' fatta**.
Il vincolo non e' piu' il budget, e' cosa c'e' in casa. Regole in `CLAUDE.md`.

## Prima

Leggi `settimane/<ISO>.md` (il menu in corso), `dati/dispensa.yaml`,
`settimane/<ISO>/contesto.yaml`, e il profilo con le sue esclusioni.
Stabilisci che giorno e' oggi: **i giorni passati non si toccano mai**, si
riscrivono solo quelli che restano.

## Le due domande

Una per volta, senza preamboli.

**1. Cosa deve cambiare?** Lascia raccontare. Puo' essere una sera che salta,
un piatto rifiutato, ospiti in piu', o solo mancanza di voglia. Se e' un
rifiuto, chiedi di chi — serve al postmortem, e un piatto bocciato dai
bambini non e' la stessa cosa di un piatto bocciato dall'adulto.

**2. Cosa c'e' in frigo?** E' la domanda che decide la proposta — ma non
farla alla cieca. Nel menu, `lunario:prepara` ha spuntato i pasti fatti e gli
ingredienti consumati: quello che resta **non** spuntato e' quello che c'e'
ancora in casa.

Quindi non chiedere l'inventario: **proponi la lista che hai gia**, e fatti
solo correggere. «Dovrebbero esserti rimasti 400 g di straccetti, le zucchine
e mezza busta di rucola — torna?». Una domanda sola invece di dieci.

Se il menu non e' stato spuntato (capita: si cucina senza lanciare la skill),
allora chiedi, partendo dagli ingredienti dei giorni saltati e facendoli
confermare a gruppi.

## La proposta

Rigenera **solo i giorni residui**, con questo ordine di priorita':

1. **Smaltire il fresco che sta per andare** — quello che c'e' e scade prima
   comanda il giorno piu' vicino, secondo `${CLAUDE_PLUGIN_ROOT}/kb/deperibilita.md`
2. **Riusare la spesa gia' fatta** — gli ingredienti comprati per i giorni
   saltati si ricollocano, non si buttano
3. **Rispettare i vincoli di sempre** — esclusioni, note, ritmi, base neutra
   per i bambini, target calorici. Una correzione non e' una deroga
4. **Zero spesa aggiuntiva**, se possibile

Se la spesa integrativa e' inevitabile, tienila a poche righe, dille come tali
(«servono solo due cose») e in confezioni, come sempre.

Con ospiti in piu': scala le quantita' sui commensali reali, non le porzioni
individuali di chi e' a dieta.

## Dopo

Riscrivi in `settimane/<ISO>.md` solo i giorni cambiati, lasciando visibile
cosa c'era prima (una riga barrata o una nota). Aggiorna `dati/dispensa.yaml`
se la correzione cambia gli avanzi previsti.

I piatti rifiutati **non** finiscono subito nei bocciati: passali al
postmortem della domenica, che e' il posto dove si impara. Qui si registra il
fatto, non si tara il sistema.

Chiudi con i giorni nuovi e basta: l'utente sta cucinando, non sta leggendo.
