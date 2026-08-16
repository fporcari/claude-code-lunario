---
name: aggiorna
description: >-
  Porta la cartella di casa al contratto dati del motore installato: legge il
  timbro in dati/versione.yaml (o lo deduce dalla forma dei file, se la
  cartella e' nata prima che il timbro esistesse), applica i passi di
  migrazione mancanti e committa. Normalmente non la invoca nessuno: ogni
  skill la chiama da sola quando trova una cartella rimasta indietro, e poi
  prosegue col lavoro vero. Da invocare a mano quando l'utente dice "aggiorna
  la cartella", "ho aggiornato il plugin", "che versione ha questa cartella",
  "e' cambiato qualcosa nel motore", oppure quando una skill segnala che i
  file sono di un contratto precedente.
---

# Aggiorna — la cartella si allinea al motore

Il motore si aggiorna dal marketplace come qualsiasi plugin. La cartella di
casa no: `dati/` e `settimane/` restano esattamente come li ha lasciati la
versione precedente. Questa skill e' l'unico posto in cui vive la logica di
migrazione — se fosse copiata in otto skill, otto copie divergerebbero.

## 1. A che contratto e' questa cartella

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/versione.py --controlla
```

Tre risposte, e tre strade:

| risposta | cosa vuol dire | cosa fai |
|---|---|---|
| `ok: contratto N, allineata` | niente da fare | **dillo in una riga e fermati.** Se sei stata chiamata da un'altra skill, non dire niente: torna e basta |
| `migrazione necessaria: N -> M` | la cartella e' indietro | vai al punto 2 |
| `attenzione: la cartella e' al contratto N` | la cartella e' **avanti**: l'ha toccata un motore piu' nuovo | dillo e fermati. Non esiste un percorso all'indietro, e un motore vecchio ignora cio' che non conosce invece di romperlo |

Se la cartella non ha il timbro — e le cartelle nate prima che il timbro
esistesse non ce l'hanno — lo script **deduce il contratto dalla forma dei
file** e stampa come ha concluso. La deduzione e' di sola lettura e succede una
volta sola: da quando il timbro c'e', si legge quello e non si indovina piu'.

## 2. I tre tipi di cambiamento

E' la parte che impedisce a una migrazione di diventare un'intervista.

| tipo | esempio | comportamento |
|---|---|---|
| **additivo** | una sezione nuova, vuota | si applica **in silenzio**: non c'e' niente da chiedere |
| **riscrittura** | `fuori_trasportabile` → `trasportabile` | si applica da sola e si **riporta in una riga**. L'annullamento e' `git` |
| **serve l'utente** | il nome dei bambini, la serie dei titoli | **non si applica niente**: il campo resta assente, la cartella funziona lo stesso, e si **propone** al momento buono |

La terza riga porta la regola vera, ed e' un vincolo su tutto cio' che verra'
scritto da qui in poi, non una caratteristica di questa skill:

> **Ogni contratto nuovo deve degradare bene quando manca.**

Una cartella che non migra mai deve continuare a funzionare. La migrazione
**migliora** una cartella; non e' mai il prezzo del biglietto. Un campo nuovo
senza un default sensato non si inventa e non si chiede d'ufficio: si lascia
assente, e chi lo incontrera' lo proporra' quando serve.

## 3. I passi, in ordine

Sono dichiarativi e **idempotenti**: applicarli due volte non fa danni, perche'
ognuno controlla prima se c'e' gia' qualcosa da fare. Applica solo quelli fra
il contratto della cartella e quello del motore, in ordine crescente.

### Da 1 a 2 — la griglia dei pasti

Il contratto 1 e' tutto cio' che e' stato scritto prima che il giorno diventasse
una griglia pasto × persona.

| cosa trovi | tipo | cosa fai |
|---|---|---|
| `pranzo: fuori_trasportabile` | riscrittura | `pranzo: trasportabile` |
| `pranzo: fuori_autonomo` | riscrittura | `pranzo: fuori` |
| persona senza `dieta` | riscrittura | `dieta: true` se ha un `kcal_giorno`, `false` altrimenti — e se e' `false`, `kcal_giorno: null` |
| nessun `git` | additivo | `git: locale` |
| nessun `intervista` | additivo | `completa`: chi ha un profilo vecchio l'intervista l'ha gia' fatta |
| nessun `tolleranze` | additivo, e non scrive niente | i default conservativi valgono gia' senza il campo. Scriverli sarebbe far passare per scelte dei default |
| `max_pasti_*` come intero nudo | serve l'utente | resta com'e' e vale `vincolo`. La rigidita' si **propone** una volta, senza insistere |
| nessun `pesata_settimanale` | serve l'utente | vale `false`. **Non attivarlo in silenzio**: e' una domanda in piu' ogni domenica |
| persona a dieta senza `peso_obiettivo_kg` | serve l'utente | senza, non si sapra' mai quando passare a mantenimento. Proponi, non inventare |
| `bambini: {presenti, selettivi}` | serve l'utente | diventano voci di `famiglia`, ma **i nomi non li sai**. Proponi la conversione e chiedi solo i nomi: e' una domanda sola |
| nessun `titoli` | serve l'utente | resta assente, e i titoli nascono dai piatti. La serie si propone quando capita |

### Da 2 a 3 — le scorte

| cosa trovi | tipo | cosa fai |
|---|---|---|
| `dispensa.yaml` senza `scorte` | additivo | aggiungi `scorte: {}`. Vuota, e va bene che sia vuota: la riempie `lunario:inventario` quando l'utente vuole |

### Da 3 a 4 — la settimana e' una cartella

Dal contratto 4 i documenti della settimana stanno **dentro** la sua cartella,
uno per ruolo: `<nome>-preventivo.md` e `.html`, `<nome>-lista.md`,
`<nome>-consuntivo.md` e `.html`, `<nome>-postmortem.md`. Prima markdown e HTML
stavano accanto alla cartella, ed erano un file solo che si riscriveva da
preventivo a consuntivo.

| cosa trovi | tipo | cosa fai |
|---|---|---|
| settimane passate col markdown accanto alla cartella | additivo, e **non scrive niente** | restano dove sono, col nome che hanno. Le settimane nuove nascono nella cartella |
| **la settimana in corso** col markdown accanto alla cartella | serve l'utente | **proponi** di adattarla, in una riga. Se dice di si', la sposti; se non risponde, funziona lo stesso |

**Da sola questa migrazione non sposta un solo file**, ed e' deliberato: le
settimane passate sono un registro, e `settimana.py` le riconosce come
`layout: piatto` e le trova lo stesso. Spostarle vorrebbe dire muovere due file
per settimana, il `menu:` che ci punta in `storico.yaml` e qualsiasi link
mandato a qualcuno — per guadagnare un ordine che a nessuno serve su una
settimana gia' mangiata.

#### La settimana in corso, se l'utente vuole

C'e' un caso solo in cui l'ordine vecchio da' fastidio davvero, ed e' quando il
motore si aggiorna di mercoledi': quella settimana la si sta ancora vivendo,
e le manca **la lista** — cioe' la ragione per cui il contratto 4 esiste.
Lasciarla indietro e' legittimo, adattarla e' utile, e la differenza la sa solo
chi ci sta cucinando. Quindi si chiede, una riga, senza insistere:

> Questa settimana e' scritta col formato vecchio. La sposto nella sua cartella?
> Serve ad avere la lista della spesa come file a parte. Le settimane passate
> le lascio dove sono.

Su un si':

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/settimana.py --adatta
```

Sposta markdown e HTML nella cartella col nome del ruolo — che deduce dallo
`stato:` scritto in testa, vecchio vocabolario compreso — e sistema il `menu:`
in `storico.yaml`. **Rifiuta di toccare qualsiasi settimana che non sia quella
in corso o quella che sta per aprire**, ed e' la garanzia che rende sicuro
proporlo: il registro non e' raggiungibile da qui.

Le settimane sono due e non una perche' una settimana **si pianifica prima di
viverla**: il menu esce per i sette giorni che cominciano, e la spesa si ritira
prima di accendere i fornelli. Chi lavora di domenica ha su disco una settimana
che l'ISO di oggi non nomina ancora, ed e' proprio quella a cui manca la lista.

Due cose da dire dopo, in mezza riga ciascuna e solo se sono vere: che **la
lista non c'e' ancora** — non si inventa una spesa gia' fatta, la scrive il
prossimo giro di `menu` o `correggi` — e, se la settimana e' ancora un
preventivo, che basta un «rigenera la lista» per averla.

Su un no, o sul silenzio: si va avanti e non si torna sull'argomento. La
settimana funziona identica dov'e'.

## 4. Cosa non si tocca, mai

- **Il contenuto di `settimane/`.** Le settimane passate sono un registro, non
  dati vivi: si leggono come sono e non si riscrivono. Un vecchio `stato:
  bozza` o `confermato` si **legge** come `preventivo`, un `in corso` come
  `consuntivo` — nella testa di chi legge, non nel file
- **I nomi e la posizione delle settimane passate.** Quelle scritte come
  `2026-W34.md`, senza titolo, e quelle col markdown accanto alla cartella
  restano cosi': `settimana.py` le trova lo stesso, e rinominarle o spostarle
  vorrebbe dire muovere i file, il `menu:` in `storico.yaml` e ogni link che ci
  puntava. L'unica eccezione e' la settimana **in corso**, e solo se l'utente
  dice di si': lo script si rifiuta di toccare le altre
- **I livelli dichiarati**, oltre le riscritture di grammatica qui sopra.
  Profilo, ritmi e note sono dell'utente: una migrazione traduce il vocabolario
  del motore, non cambia cio' che l'utente ha deciso

Nessun meccanismo di backup: la cartella e' un repo git, e quello e' il backup.
Nessun percorso all'indietro: se serve, `git revert`.

## 5. Chiudere

1. **Scrivi il timbro**, sempre, anche quando non c'era niente da migrare e la
   forma diceva gia' il contratto giusto: e' il giro in cui si smette di
   indovinare.

   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/versione.py --scrivi <N> \
       --motore <versione del plugin> --data <oggi>
   ```

2. **Committa**, se `git: locale`:

   ```bash
   git add -A && git commit -q -m "aggiorna: contratto <vecchio> -> <nuovo>"
   ```

3. **Di' una riga per ogni riscrittura**, e niente per gli additivi. Le cose
   che servono all'utente non si chiedono adesso in fila: si segnano e le
   propone la skill giusta al momento giusto — la rigidita' dei tetti quando
   il congelatore spinge contro un tetto, la pesata la prima domenica, i nomi
   dei bambini quando serve un menu.

   > Ho allineato la cartella: due pasti usavano la vecchia grammatica
   > (`fuori_trasportabile` → `trasportabile`). Il resto era gia' a posto.

4. Se non c'era niente da fare e sei stata chiamata da un'altra skill, **taci**
   e restituisci il controllo. Un controllo di versione che si fa notare ogni
   lunedi' e' rumore, e il rumore si impara a saltare.

**Il contratto non e' tutta la salute della cartella.** Qui si guarda un
numero, e un numero allineato non dice niente su dove stiano i file: quello lo
guarda `lunario:tagliando`, che parte dai file e trova anche cio' che nessun
salto di contratto sistemerebbe. Se l'utente e' venuto qui perche' «qualcosa non
torna» e il contratto risulta allineato, la risposta e' il tagliando, non
questa skill.

Se il commit fallisce, non dirlo e vai avanti: e' una rete di sicurezza, non un
pezzo del flusso.
