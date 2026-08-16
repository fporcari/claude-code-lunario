---
name: postmortem
description: >-
  Chiusura della settimana, la domenica. Legge prima il diario di cio' che si
  e' mangiato davvero, poi chiede solo cio' che manca — cosa e' avanzato,
  che voto danno i commensali ai piatti e da chi viene, quali pasti non sono
  andati come previsto, che spesa c'e' stata fuori dalla lista (negozio o
  ristorante) e — per chi e' a dieta e lo vuole — il peso della domenica, per
  vederne il trend. Poi ritara porzioni, rotazione dei piatti, griglia dei
  pasti e budget per la settimana successiva. Da invocare quando l'utente dice "postmortem",
  "com'e' andata la settimana", "chiudiamo la settimana", "e' avanzato...",
  "ai bimbi non e' piaciuto...", o la domenica. NON e' la skill dello
  scontrino della spesa grande: quello si registra al ritiro, con
  lunario:spesa.
---

# Postmortem — cosa si e' imparato

E' il pezzo che distingue il sistema da un generatore di menu qualsiasi.
Scrive il livello **appreso**. Regole di ritaratura in `CLAUDE.md`.

## Prima di tutto: la cartella e' allineata?

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/versione.py --controlla
```

Se risponde `migrazione necessaria`, passa da `lunario:aggiorna` e **poi torna
qui**: allineare la cartella e' il presupposto, non il lavoro che l'utente ha
chiesto. Se risponde `ok`, non dire niente — un controllo di versione che si fa
notare ogni lunedi' e' rumore.

## 0. Prima di chiedere, leggi

La domenica si apre su **cio' che e' gia' scritto**, e sono due file che
insieme raccontano quasi tutta la settimana:

- il **consuntivo** (il markdown della settimana, `stato: consuntivo`) — cosa e'
  entrato in casa, a che prezzo, con quali sostituzioni, e in coda lo scarto
  dal preventivo
- il **diario** (`diario.yaml`, nella cartella della settimana) — cosa si e' mangiato davvero,
  chi c'era, cosa e' avanzato, quali celle sono saltate, **registrato nel
  giorno in cui e' successo** invece che ricordato adesso

Comprato e cucinato, gia' assemblati. Leggili per primi, insieme al menu
spuntato.

Quello che il diario copre **non si chiede**: si propone come verificato, in
una riga, e si passa oltre. Le domande qui sotto valgono solo per i buchi.

Con un diario pieno, la domenica e' una conferma e non un interrogatorio, e
resta una sola domanda vera: la pesata.

**Un diario vuoto, o mezzo vuoto, e' normale.** Nessuno lo compila tutti i
giorni. Un pasto senza voce si chiede come si e' sempre fatto — e non si
commenta mai il fatto che manchi: rimproverare i buchi e' il modo piu' rapido
di far smettere sia il diario sia il postmortem.

## Le cinque domande, e due si possono saltare

Una per volta, secche. L'utente e' a fine settimana, non ha voglia di
un'intervista. Salta senz'altro quelle a cui il diario ha gia' risposto.

**1. Cosa e' avanzato?** Sia il cibo cucinato non mangiato, sia le confezioni
non aperte. Distingui le due cose: la prima e' una porzione sbagliata, la
seconda e' un fabbisogno sbagliato.

Gli `avanzo` gia' nel diario non si ridomandano: quello che l'utente ha detto
martedi' vale piu' di quello che ricorda oggi. La domanda copre i pasti che il
diario non ha.

Con un'eccezione che viene dal mestiere: se ad avanzare e' sempre la verdura,
la porzione non si tocca — il taglio calorico non passa mai da li', e una
porzione di verdura ridotta perche' avanza e' una resa, non una taratura. Li'
si cambia la preparazione: al forno invece che lessa, dentro il piatto invece
che accanto.

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

**3. La settimana e' andata come previsto?** Non chiederlo cosi': guarda il
diario e il menu spuntato e **proponi tu lo scarto**. «Risulta che giovedi'
non avete cenato a casa e sabato la pizza e' saltata — torna?». Le voci del
diario con `stato: disattesa` sono gia' la risposta: si portano in
`celle_disattese` senza ridomandarle. Interessa solo dove la griglia ha
sbagliato:

- previsto a casa, finito fuori → un piatto cucinato per nessuno, o buttato
- previsto fuori, finito a casa → una cena improvvisata, spesso male

Registra in `celle_disattese` della settimana: pasto, giorno, cosa era
previsto, cosa e' successo. Un dato solo, che serve a una cosa sola: se la
**stessa** cella salta tre settimane di fila, non e' sfortuna, e' un ritmo che
nessuno ha scritto. In quel caso proponi di metterlo in `ritmi.yaml` —
proponi, non scrivere: i ritmi sono livello dichiarato.

**4. C'e' stata altra spesa in settimana?** Due cose diverse, e vanno tenute
separate:

- **spesa integrativa** — il salto al negozio del giovedi'. Non lo scontrino
  grande: quello e' gia' stato registrato da `lunario:spesa` il giorno del
  ritiro. Se ricorre, la lista del lunedi' sbaglia sistematicamente qualcosa
- **mangiate fuori** — ristorante, pizzeria, bar. Chiedile solo se la griglia
  aveva celle `ristorante`, e chiedi solo il totale, non il dettaglio: va in
  `spesa_fuori_casa`, **mai** dentro `spesa_reale`. Sommarle romperebbe
  l'unica cosa che `spesa_reale` sa fare, cioe' il confronto con la stima

Il senso di tenerle separate e' che rispondono a due domande diverse: quanto
costa la spesa, e quanto costa mangiare. La seconda non la sa nessun altro
campo del sistema.

**5. La pesata**, e solo per chi nel profilo ha `dieta: true` **e**
`pesata_settimanale: true`. Se il profilo e' `intervista: minima` e nessuno a
dieta ha ancora quel campo, questa e' la domenica in cui proporla, una volta:
«vuoi che la domenica ti chieda il peso? Serve a vedere il trend, e si puo'
sempre saltare». La risposta va messa in forma nel profilo, e un no vale per
sempre. Poi, per chi la vuole: ultima, breve, e senza cerimonie:

> Peso della domenica, se ti va: Adulto1?

Tre regole, tutte importanti quanto il dato:

- **si puo' saltare.** Se l'utente non risponde, cambia discorso o dice di no,
  vai avanti senza commentare e **non registrare niente** — nemmeno il fatto
  che ha saltato. Non richiederlo piu' in questa sessione
- **non commentare il numero**, mai. Ne' «bene» ne' «peccato». Registra e basta
- se in casa ci sono piu' persone che si pesano, chiedile **in una riga sola**,
  non una domanda a testa

Scrivi in `tarature.pesate.<persona>` di `dati/storico.yaml` — `{data, kg}`,
serie mai sovrascritta. **Il profilo non lo tocchi**: `peso_kg` li' e' il peso
di partenza, il riferimento rispetto a cui si misura tutto, e lo cambia solo
l'utente.

Il trend si legge secondo la tabella in `CLAUDE.md`, e **si dice solo se c'e'
qualcosa da dire**: sotto le tre pesate non c'e' trend, e con l'andamento
previsto basta nominarlo ogni tanto, non ogni domenica. Quello che va detto
sempre, invece, e' un calo troppo rapido — oltre 1 kg a settimana per tre
settimane — e li' si rimanda al medico, perche' qui il ruolo e' nutrizionale e
si ferma prima.

Due letture che vengono dal mestiere, e servono soprattutto a non sbagliare
tono. Un plateau dopo settimane di calo regolare non e' un fallimento e non
autorizza indagini su cosa sia andato storto: a un peso piu' basso corrisponde
un fabbisogno piu' basso, e' fisiologia — la risposta sta nella tabella delle
ritarature, non nelle domande. E una risalita secca dopo una settimana con
piu' pasti fuori e' quasi sempre acqua e sale, non grasso: si registra, si
aspetta la domenica dopo, e non la si nomina nemmeno.

Se l'obiettivo e' stato raggiunto, proponi il passaggio a mantenimento: e' una
modifica al profilo, quindi si chiede, non si applica.

Se c'e' uno scontrino della spesa integrativa, leggilo con `read-document` e
applica le stesse regole di `lunario:spesa`: prezzi nella serie con la data,
sigle nuove in `alias_scontrino`, totale sommato a `spesa_reale`. Lo scontrino
del ristorante no: quello e' un numero solo in `spesa_fuori_casa`, e non
insegna niente al paniere.

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
| voto basso dei soli bambini | non toccare il piatto: rinforza la base neutra — e se quel bambino non ha ancora `selettivo` nel profilo, proponi di attivarlo |
| confezione avanzata 2 volte di fila | il formato e' sbagliato: proponi di cercarne uno piu' piccolo |
| sforo del budget | privilegia i piatti a miglior €/100 g di proteine (`${CLAUDE_PLUGIN_ROOT}/kb/consigli-pratici.md`) |
| stessa cella disattesa 3 volte | **proponi** un ritmo nuovo in `ritmi.yaml`, non scriverlo |
| merenda comprata e mai consumata | la cella e' `casa` ma nessuno la fa: proponi di metterla a `no` |
| `spesa_fuori_casa` sopra la spesa del menu | dillo una volta, come dato. Nessun commento morale: non e' il ruolo di questo sistema |
| peso fermo o in salita per 3+ settimane | proponi di rivedere porzioni o target, come ipotesi. Mai cercare un colpevole |
| calo oltre 1 kg/settimana per 3 settimane | dillo e **rimanda al medico**: troppo in fretta |
| ultima pesata a 3 kg da `peso_kg` | **proponi** il ricalcolo di `kcal_giorno`: e' il profilo, quindi si chiede. Sotto i 3 kg no, sarebbe rumore |

Un'eccezione sola alla prima riga: la porzione di verdura e frutta **non si
riduce mai** — il taglio non passa da li'
(`${CLAUDE_PLUGIN_ROOT}/kb/porzioni-standard.md`). Se avanza, si cambia
preparazione o piatto, non grammatura.

Correggi anche `dati/dispensa.yaml` sul reale: gli avanzi previsti dal menu
sono una stima, quello che c'e' davvero lo sa solo l'utente. Vale anche per la
sezione `freezer`: una scorta cucinata questa settimana esce, una porzione
messa via ci entra. Non serve una domanda apposta — se il diario dice che
giovedi' e' finito nel congelatore meta' polpettone, quella riga si scrive da
sola, e lunedi' `lunario:settimana` avra' qualcosa di vero da far correggere
invece di una lista vuota.

## Lo scarto fra preventivo e consuntivo

Se la settimana e' passata da `lunario:spesa`, in coda al markdown della settimana
c'e' la sezione **Scarto dal preventivo**. Leggila e portala in
`storico.settimane[]`: `spesa_stimata` accanto a `spesa_reale`, e le righe
divergenti in `scarto_per_riga`. Scrivere solo il totale reale cancella l'unica
cosa che il confronto sa insegnare.

Non commentarla riga per riga in chat — l'utente l'ha gia' vista al ritiro. Si
guarda invece la **ripetizione**: stessa riga divergente nello stesso verso per
tre settimane e' un dato del paniere, non della settimana.

| osservazione sullo scarto | conseguenza |
|---|---|
| lo stesso formato arriva sempre diverso da quello atteso | correggi `formato_g` in `prodotti.jsonl`: il paniere ha il dato sbagliato, non il negozio |
| lo stesso prodotto manca 3 volte | proponi di sostituirlo stabilmente nel paniere: non lo tengono |
| il consuntivo supera il preventivo di piu' del 10% per 3 settimane | i prezzi del paniere sono vecchi, e il budget lo e' di conseguenza. Dillo una volta, come dato |

## Chiusura

**Una riga sola**: cosa cambia la settimana prossima. Non un riepilogo di
tutto quello che hai scritto nei file — l'utente ha appena chiuso la
settimana, non vuole rileggerla.
