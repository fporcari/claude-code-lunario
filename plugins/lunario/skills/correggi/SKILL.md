---
name: correggi
description: >-
  Cambia un menu gia' generato, sia mentre e' ancora in discussione — i figli
  contestano il giovedi', la moglie propone altro, si aggiusta prima di fare
  la spesa — sia a settimana iniziata, quando salta una cena, arrivano ospiti
  o non c'e' voglia di quel che era previsto. Gestisce anche la conferma del
  menu, che congela la lista della spesa. Da invocare quando l'utente dice
  "cambia il giovedi'", "non gli piace", "hanno protestato", "confermo il
  menu", "va bene cosi'", "vado a fare la spesa", "cambio idea", "ho ospiti",
  "cosa faccio con quello che ho in frigo". Raccoglie anche i pasti andati
  diversamente dal previsto, detti di passaggio — "stasera niente polpette,
  pizza d'asporto", "alla fine abbiamo mangiato fuori" — e li registra nel
  diario della settimana.
---

# Correggi — il menu cambia

Stessa skill per due situazioni molto diverse, e la differenza la fa lo
`stato` scritto in testa al markdown della settimana — che si trova con un
glob su `settimane/<ISO>*`. Sbagliarla significa proporre
un piatto per cui non e' stata comprata roba, o rifare la spesa per niente.

| stato | dove siamo | cosa vincola |
|---|---|---|
| `preventivo` | la spesa non e' ancora stata ritirata | **niente**: si cambia liberamente e la lista si rigenera |
| `consuntivo` | la spesa e' stata ritirata | **cosa c'e' in casa**: si riusa, non si ricompra |

Questa skill **non promuove niente**: il passaggio a `consuntivo` lo fa
`lunario:spesa` con lo scontrino in mano. Regole complete in `CLAUDE.md`.

## Se la spesa non e' ancora fatta

E' il caso piu' frequente e il piu' semplice: si sta ancora decidendo, spesso
riportando le obiezioni di chi non e' in questa chat.

- Chiedi cosa non va e **di chi e' l'obiezione**: «al piccolo non piace» e «a
  me non va» portano a soluzioni diverse — la prima si risolve con una base
  neutra piu' robusta, la seconda cambiando piatto
- Cambia quello che serve, ricontrolla i vincoli di sempre (deperibilita',
  frequenze, ritmi, esclusioni) e **rigenera la lista della spesa**
- Lo stato resta `preventivo`, prima e dopo: modificare una previsione la
  lascia una previsione
- Non riepilogare tutto il menu a ogni giro: mostra i giorni cambiati

Registra le obiezioni raccolte qui: se un piatto viene contestato prima ancora
di essere cucinato, e' un segnale buono quanto un voto basso.

## «Vado a fare la spesa»

Quando l'utente dice che va bene — «confermo», «ok cosi'», «vado a fare la
spesa» — non sta approvando dei numeri, che nessuno puo' ancora verificare:
sta dicendo che i **piatti** vanno bene e che esce di casa. Quindi:

1. **rigenera lista e HTML**, che sono quelli che andranno al supermercato
2. **scrivi la settimana sul calendario**, se l'utente lo vuole (sotto)
3. dillo in una riga, ricordando `lunario:spesa` al ritiro

Lo `stato` **non si tocca**: resta `preventivo` fino allo scontrino. Se dopo
questo momento arriva un'altra modifica, si fa senza cerimonie — avvisa in
mezza riga che la lista cambia, applicala e rigenera.

Segna in testa al file la data dell'ultima rigenerazione, cosi' si sa quale
versione e' finita in borsa.

### La settimana sul calendario

La decisione e' gia' stata presa al setup: leggi `calendario` in
`dati/profilo.yaml` e limitati a eseguire.

- `scrivi: false` o campo assente -> **non scrivere niente e non chiedere**.
  Chi ha detto di no al setup non va risollecitato ogni settimana. Un'eccezione
  sola: se il profilo e' `intervista: minima`, la domanda al setup non e' mai
  stata fatta — proponila **alla prima conferma**, una volta, e scrivi la
  risposta nel profilo, qualunque sia
- `scrivi: true` -> crea l'evento sul calendario indicato da `id`, nel modo
  indicato da `modo`: un evento di sette giorni col titolo della settimana —
  «🌙 Impressioni di settembre» — e il menu nella descrizione, oppure un
  evento per ogni cena

Se `scrivi: true` ma `id` e' vuoto o non esiste piu', allora chiedi: elenca i
calendari disponibili e fai scegliere, poi salva la scelta nel profilo.

Due cautele, perche' un'agenda la leggono anche altri:

- **mai scrivere senza che il profilo lo dica**, nemmeno «per comodita'»
- **se il menu cambia dopo la conferma**, aggiorna l'evento invece di crearne
  un altro: due settimane sovrapposte in agenda sono peggio di nessuna

L'evento e' una comodita', non un pezzo del sistema: se la scrittura fallisce,
dillo in mezza riga e vai avanti. Il menu e' gia' salvato dove conta.

Non dare mai per approvato il silenzio: qui l'approvazione e' di persone che
non stanno leggendo la chat.

## Se la spesa e' gia' stata ritirata

Qui la differenza con `lunario:settimana` e' tutta in una cosa: **la spesa e'
gia' fatta**. Il vincolo non e' piu' il gusto ne' il budget, e' cosa c'e' in
casa.

Leggi il markdown della settimana, `dati/dispensa.yaml`, il `contesto.yaml`
nella cartella della settimana, e il profilo con le sue esclusioni.
Stabilisci che giorno e' oggi: **i giorni passati non si toccano mai**, si
riscrivono solo quelli che restano.

## Le due domande

Una per volta, senza preamboli.

**1. Cosa deve cambiare?** Lascia raccontare. Puo' essere una sera che salta,
un piatto rifiutato, ospiti in piu', o solo mancanza di voglia. Se e' un
rifiuto, chiedi di chi — serve al postmortem, e un piatto bocciato dai
bambini non e' la stessa cosa di un piatto bocciato dall'adulto.

Se la modifica riguarda **dove** si mangia e non **cosa**, e' un cambio di
cella: «stasera ordiniamo» → `cena: ristorante`, «pranzo me lo porto» →
`pranzo: trasportabile`. Aggiornalo nel contesto della settimana, non solo nel
menu: e' quello che il postmortem confrontera' col reale.

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

Se salta una cena, **gli ingredienti di quel giorno non spariscono**: si
ricollocano. I deperibili si anticipano invece di sperare che tengano, il
resto scala in avanti. Una cena in meno non e' un problema di menu, e' un
problema di frigo — ed e' il motivo per cui vale la pena dirlo appena si sa,
non la domenica.

## Dopo

Riscrivi nel markdown della settimana solo i giorni cambiati, lasciando visibile
cosa c'era prima (una riga barrata o una nota). Aggiorna `dati/dispensa.yaml`
se la correzione cambia gli avanzi previsti.

**A settimana iniziata, scrivi anche il diario** — `diario.yaml` nella cartella
della settimana,
contratto in `CLAUDE.md`. Una modifica in corsa *e'* una voce di diario: una
cella spostata o saltata e' esattamente cio' per cui il diario esiste, e
saperlo il mercoledi' vale piu' che ricostruirlo la domenica.

```yaml
2026-08-21:
  cena:
    previsto: Polpette al sugo
    reale: pizza d'asporto
    stato: disattesa
```

Il vincolo, non il racconto: «cena fuori», non con chi. E niente domande in
piu' per riempirlo — ci va quello che l'utente ha gia' detto raccontando cosa
doveva cambiare.

Le correzioni fatte **prima** della spesa non sono voci di diario: li' non e'
successo ancora niente, si sta ancora decidendo.

**Il nome della settimana non si tocca**, nemmeno se il menu cambia da cima a
fondo: il titolo e' fissato alla generazione, e rinominare vorrebbe dire
muovere markdown, HTML, cartella e ogni link che ci puntava. Il documento
cambia contenuto, non identita'.

## Un'obiezione che vale piu' di un giovedi'

Alcune contestazioni non riguardano il piatto: riguardano **come si mangia in
questa casa**. «Carne a pranzo e a cena no», «a loro l'avanzo di mezzogiorno
la sera non glielo dai», «se il congelatore e' pieno il tetto del pesce
salta». Sono tolleranze, non capricci del giovedi': correggile qui, ma
**proponi anche di scriverle** in `tolleranze` del profilo, che e' l'unico
posto da cui torneranno utili la settimana prossima.

Il profilo e' un livello dichiarato: si scrive solo su un si' esplicito, mai
di iniziativa. Una riga per chiederlo, e se la risposta e' no si va avanti —
la correzione di oggi vale comunque.

I piatti rifiutati **non** finiscono subito nei bocciati: passali al
postmortem della domenica, che e' il posto dove si impara. Qui si registra il
fatto, non si tara il sistema.

Chiudi con i giorni nuovi e basta: l'utente sta cucinando, non sta leggendo.
