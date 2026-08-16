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

## Prima di tutto: la cartella e' allineata?

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/versione.py --controlla
```

Se risponde `migrazione necessaria`, passa da `lunario:aggiorna` e **poi torna
qui**: allineare la cartella e' il presupposto, non il lavoro che l'utente ha
chiesto. Se risponde `ok`, non dire niente — un controllo di versione che si fa
notare ogni lunedi' e' rumore.

## 1. Leggi lo scontrino

Il PDF si legge con la skill `read-document` — nessun parser da scrivere. Da
ogni riga: descrizione, quantita', formato se c'e', prezzo pagato.

**Se lo scontrino e' una foto**, `read-document` esce con un errore e la strada
e' la skill `pdf` con l'OCR. Ma su uno scontrino lungo, arricciato e fotografato
di sbieco, leggere le due colonne appaiate non funziona: descrizioni e prezzi
scivolano fino a una riga intera di sfasamento, e il risultato e' un paniere con
i prezzi di un altro prodotto. Quello che funziona, in tre mosse:

1. **ritaglia le due colonne** e leggile come **due elenchi ordinati**,
   descrizioni da una parte e prezzi dall'altra
2. **appaia per indice**, non per posizione sull'immagine. I prodotti ripetuti
   sono la controprova che l'allineamento tiene — tre `1,99` uguali di fila,
   i `0,01` dei sacchetti
3. **somma le righe e confrontale col totale stampato.** Se non torna,
   l'allineamento e' saltato da qualche parte: si rilegge, non si aggiusta

**Se il PDF non si lascia leggere** — scansione illeggibile, file corrotto, un
formato che nemmeno l'OCR digerisce — dillo subito e senza giri, poi si
procede a voce: si chiede il totale, e i prezzi che l'utente ricorda dei
prodotti nuovi. Ogni prezzo raccolto cosi' entra nella serie con
`fonte: dichiarato` e la data di oggi. Quelli che nessuno ricorda restano
buchi dichiarati: **mai riempirli con un numero verosimile**, nemmeno per far
tornare il totale.

Se l'utente non ha il PDF, stessa strada, ma dillo una volta: col documento la
riconciliazione e' esatta, a memoria e' approssimativa.

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

Le righe **non** spuntate escono dai conti, ma non dal documento: cio' che e'
stato comprato per un'altra casa finisce nel consuntivo in una sezione sua,
voce per voce e col suo subtotale (4b). Quanto si deve a qualcuno e' un numero
che serve, e toglierlo dalla pagina obbliga a rifarlo a mano.

Nessuna delle due e' `spesa_fuori_casa`, che riguarda i pasti consumati al
ristorante e non passa mai da qui: la raccoglie il postmortem.

**Le merende non sono un extra.** Se in lista c'erano yogurt, frutta secca o
biscotti per gli spuntini, sono righe del menu come le altre e vanno spuntate
allo stesso modo. Un sistema che tratta la merenda dei bambini come «roba in
piu'» ricomincia a sbagliare i conti dopo due settimane.

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

## 2b. Riconcilia con la lista annotata

La lista non e' un ricordo di quello che si voleva comprare: e' un file, ed e'
**tornato indietro insieme allo scontrino**. Aprilo — e' `<nome>-lista.md`
dentro la cartella della settimana:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/settimana.py
```

Quattro esiti per ogni riga del gruppo **menu**, e solo due meritano di essere
raccontati:

| esito | cosa fai |
|---|---|
| **arrivato come previsto** | registralo, in silenzio |
| **formato diverso** (chiesto 500 g, dato 400 g) | il reale vince: ricalcola se il fabbisogno regge, e se non regge dillo |
| **manca** | vai al punto 3 |
| **in piu'**, fuori lista | gia' classificato sopra: nessun commento |

### Le caselle

Una casella spuntata nella lista vuol dire **preso**, e niente altro. Sono la
risposta onesta a «cosa avete comprato davvero», e le righe **non** spuntate
sono gia' i candidati alla sostituzione, senza chiedere a nessuno di
ricordarsele.

Con un'eccezione che va gestita e non ignorata: **una lista con zero caselle
spuntate e' indistinguibile da una lista mai aperta.** In quel caso le caselle
non dicono niente — non dicono «non ho comprato niente» — quindi si lavora sullo
scontrino e basta, e lo si nomina una volta sola, senza rimproveri: «la lista
non risulta spuntata, vado sullo scontrino». Se l'utente dice che invece l'ha
usata, si torna a crederci.

### Le annotazioni scritte a mano

Accanto a una riga puo' esserci una frase — «non c'erano, prese 2 da 70 g»,
«preso il branzino intero», «questo lo prendo giovedi'». E' testo libero per
costruzione: non c'e' una sintassi da imparare, e non deve essercene una.
Leggile, e portale in **uno** di questi esiti:

| l'annotazione dice | dove finisce |
|---|---|
| il formato era un altro | `formato_g` e `fonte_formato` in `prodotti.jsonl`, e il fabbisogno si ricalcola |
| ho preso un altro prodotto | sostituzione applicata al piatto (punto 3), e il prodotto nuovo entra nel paniere |
| ne ho preso di piu' o di meno | la quantita' reale, e l'avanzo che ne segue in `dispensa.yaml` |
| non c'era, me lo prendo dopo | un `sospeso` nel diario (punto 3) |
| non c'era, lascia perdere | il piatto cambia, e non resta niente in aria |
| l'ho preso altrove | `fuori_scontrino: true` sul prodotto (punto 2a) |
| quanto e' costato | prezzo con `fonte: dichiarato`, **solo** se non c'e' sullo scontrino |

Quando si crede a chi, perche' le due fonti sanno cose diverse:

| la domanda | chi vince | perche' |
|---|---|---|
| **quale** prodotto e' entrato in casa | l'annotazione | l'utente era li' e aveva il pacco in mano |
| **quanto** e' costato | lo scontrino | e' stampato, e contiene gia' sconti e promozioni |
| **che formato** hanno dato | lo scontrino se lo riporta, altrimenti l'annotazione, con `fonte_formato: {fonte: utente, data}` | |
| **cosa non e' arrivato** | la casella vuota, confermata dall'assenza sullo scontrino | due segnali concordi non si chiedono |

Un'annotazione che non entra in nessuna di queste caselle **non si interpreta**:
si chiede, una volta, insieme alle altre domande aperte. Indovinare cosa
volesse dire una frase e' esattamente il modo di scrivere nel paniere un dato
che nessuno ha detto.

La sezione **«Fuori Lunario»** in coda alla lista si legge e si salta: non
entra nei totali, non entra nel paniere, non entra in dispensa. E' li' apposta
per essere ignorata dal motore, e per non essere dimenticata dall'utente.

**Il file della lista non si riscrive.** E' il documento che l'utente ha
annotato in piedi davanti a uno scaffale: resta com'e', ed e' la prova di cosa
e' successo quel giorno. Cio' che si e' capito va nel consuntivo e nei file di
dati, non ricopiato li' sopra.

Il riconoscimento delle sigle segue le regole del paniere: se
`FUSILLI INTGR 500` e' gia' in `alias_scontrino`, si riconosce da solo; se e'
nuova, chiedi conferma una volta sola e poi salvala. Raggruppa le sconosciute
in una domanda unica invece di chiederle a una a una.

## 3. Cosa manca, e se e' un problema

Per ogni riga mancante, la domanda non e' «manca?» ma **«questo fa saltare un
piatto?»**. La risposta e' gia' scritta accanto alla riga: la lista dice a
quali pasti serve ogni ingrediente (`→ mer cena · gio cena`), quindi i piatti
colpiti non si cercano, si leggono. Se manca la riga d'uso — un menu vecchio —
allora si guarda il menu a mano.

Rispondi tu, e distingui:

- **Ininfluente** — mancano i pomodorini di guarnizione: annota e basta, non
  disturbare l'utente per questo
- **Sostituibile con quello che c'e'** — proponi la sostituzione gia' fatta:
  «non c'e' il branzino: giovedi' sposto sul merluzzo che hai nel
  congelatore». Una riga, non una domanda aperta
- **Compromette il piatto** — qui chiedi, e le risposte possibili sono due:
  **cambiamo il piatto** con quello che c'e' in casa, oppure **me lo procuro
  io** prima di quel giorno. Sono due strade diverse e vanno offerte come tali,
  non lasciate a una domanda aperta

| la risposta | cosa fai |
|---|---|
| **si sostituisce** | aggiorna quel giorno nel consuntivo, e finisce li': non resta niente in aria |
| **se lo procura dopo** | scrivi un `sospeso` nel diario della settimana, e non nominarlo piu' fino al giorno in cui serve |

Il rimando detto e basta e' un rimando perso: giovedi' `lunario:prepara` fa
cucinare quel piatto convinta che il branzino sia in casa. Quindi si scrive,
nel `diario.yaml` della cartella della settimana (contratto in `CLAUDE.md`):

```yaml
sospesi:
  - cosa: filetti di branzino
    prodotto: branzino-filetti-250
    serve:
      - {giorno: 2026-08-20, pasto: cena}
    stato: da_procurare
```

`serve` esce dalla riga d'uso della lista, che i pasti colpiti li dice gia'.
E **il sospeso non entra in dispensa**: non e' in casa, e una scorta promessa
falsa il menu del lunedi' successivo.

Non riscrivere l'intera settimana per un ingrediente: tocca i giorni colpiti e
lascia stare il resto. Se i giorni colpiti sono tanti, e' il caso di
`lunario:correggi`, e dillo.

## 4. Aggiorna i file

- **`dati/prodotti.jsonl`** — prezzo pagato con la data dello scontrino,
  aggiunto alla serie `prezzi` (mai sovrascrivere i vecchi); sigle nuove in
  `alias_scontrino`; formato reale se diverso da quello che si credeva, con
  `fonte_formato: {fonte: scontrino, data}` — il formato che hanno dato batte
  quello che il paniere sperava, e la prossima lista nasce giusta. Per un
  prodotto mai visto, `${CLAUDE_PLUGIN_ROOT}/scripts/off_lookup.py` recupera
  formato e nutrienti. Se Open Food Facts non lo conosce — coi prodotti a
  marchio del supermercato capita spesso — il dato si chiede a chi la
  confezione ce l'ha in mano: il formato sta scritto sul pacco, le kcal
  sull'etichetta. Entrano in `prodotti.jsonl` con `fonte_nutrienti: etichetta`
  e da li' valgono come un dato letto da OFF: cio' che conta e' la provenienza
  dichiarata, non il canale. E chiedi solo cio' che serve — il formato subito,
  i nutrienti solo se il prodotto entra nei conti di qualcuno a dieta
- **`dati/dispensa.yaml`** — quello che entra in casa e non si consuma questa
  settimana, solo non deperibili. E la sezione `freezer`: cio' che finisce
  nel congelatore invece che in pentola ci entra adesso, con la data di oggi,
  perche' fra due mesi sara' esattamente il pezzo che nessuno ricorda; cio'
  che il menu ha gia' tirato fuori ne esce.

  E le **`scorte`**: cio' che e' entrato oggi si somma alla quantita'. E'
  l'aggiornamento piu' affidabile di tutto il ciclo — viene da uno scontrino,
  non da una stima, e non costa una domanda. Ma **non tocca `visto`**: lo
  scontrino sa quanto e' **entrato**, non quanto ce n'e', perche' non sa
  quanto ce n'era. Solo un conteggio umano azzera l'eta' del dato
  (`${CLAUDE_PLUGIN_ROOT}/kb/scorte.md`)
- **`dati/storico.yaml`** — `spesa_reale` (solo il menu), accanto a
  `spesa_extra_alimentare` e `totale_scontrino` per memoria; e
  `scarto_per_riga`: dove la stima ha sbagliato, non solo di quanto. E' il dato
  che rende onesto il totale del lunedi' successivo
- **`diario.yaml` della settimana** — la lista `sospesi`, e **solo se qualcosa
  e' stato rimandato**. Se e' arrivato tutto, o e' stato tutto sostituito, il
  file non si tocca: una lista vuota non e' un dato
- **il consuntivo della settimana** — due file **nuovi**, accanto al
  preventivo: vedi il punto 4b. Il nome della cartella non cambia, e il
  preventivo non si tocca

## 4b. Il consuntivo si scrive accanto al preventivo

Questa skill e' **l'unica** che porta la settimana da preventivo a consuntivo.
Fino a un minuto fa il documento diceva cosa si voleva comprare; adesso ce n'e'
un secondo che dice cosa c'e' in casa, ed e' una differenza di autorita', non
di formattazione.

Due file nuovi nella cartella della settimana, gli stessi nomi con un ruolo
diverso:

```
settimane/2026-W34-commando/
├── 2026-W34-commando-preventivo.md      <- resta com'e', non si tocca
├── 2026-W34-commando-preventivo.html    <- idem
├── 2026-W34-commando-lista.md           <- annotata dall'utente, non si riscrive
├── 2026-W34-commando-consuntivo.md      <- nuovo
└── 2026-W34-commando-consuntivo.html    <- nuovo
```

**Il preventivo non si sovrascrive.** E' la ragione per cui i due sono due file:
lo scarto fra quello che si voleva e quello che c'e' e' il dato che il
postmortem confronta, e leggerlo non deve richiedere un `git diff`. Da qui in
poi il documento vivo della settimana e' il consuntivo — e' li' che
`lunario:prepara` spunta i pasti e `lunario:correggi` riscrive i giorni.

Cosa ci va dentro:

1. `stato: consuntivo` in testa, con la data del ritiro
2. **I sette giorni**, ripresi dal preventivo e **con le sostituzioni gia'
   applicate ai piatti**: se giovedi' il branzino e' diventato merluzzo,
   giovedi' dice merluzzo. Un consuntivo che nomina ancora un pesce che non e'
   entrato in casa non e' un registro. I pasti restano caselle: la settimana
   deve ancora essere cucinata
3. **Quello che e' entrato in casa**: nome, formato e prezzo dello scontrino,
   non quelli sperati. Una riga arrivata in 400 g resta 400 g anche se ne
   servivano 500. Non e' una lista della spesa e non ha caselle — la spesa e'
   fatta
4. **Il totale**, che e' il punto piu' facile da sbagliare: vedi qui sotto
5. **In coda, il delta**: poche righe, solo dove preventivo e consuntivo
   divergono — formato, prezzo, prodotto sostituito, riga mancante

```markdown
## Scarto dal preventivo
- Fusilli integrali: previsti 2 × 500 g, dati 2 × 400 g — 200 g in meno
- Branzino: non c'era → merluzzo surgelato (giovedi' cena)
- Olio EVO: 7,20 € contro i 5,90 dell'ultima volta

## Da procurare
- Filetti di branzino — servono giovedi' a cena
```

**«Da procurare» solo se ci sono sospesi**, e senza casella da spuntare: lo
stato vero sta nel diario, e due posti dove segnare la stessa cosa sono due
posti che si contraddicono. Qui la riga serve all'occhio di chi riapre il file.

### Il totale del consuntivo e' il cibo di casa

L'etichetta e' **«Totale cibo di casa»**, e il numero e' `spesa_reale` +
`spesa_extra_alimentare`: il menu piu' l'alimentare comprato fuori lista.

**Il totale dello scontrino non e' il totale del consuntivo.** Il non
alimentare e la spesa di altre case ne sono gia' fuori da mezz'ora, e
rimetterceli dentro nell'ultima riga disfa tutto lo scorporo appena fatto: uno
zaino da 45,90 € nel totale della settimana la fa sembrare costata il doppio, e
quel numero non risponde a nessuna domanda che qualcuno si sia posto.

Se serve la tracciabilita' col pezzo di carta, una riga **«fuori da questo
conto, per memoria»** dice il totale della cassa e cosa lo separa da questo. Ma
non e' il totale, e non sta al posto suo.

**La spesa per un'altra casa resta in pagina**, in una sezione sua, voce per
voce e con il suo subtotale: «scorporata» vuol dire fuori dai conti di Lunario,
non cancellata dal documento. Quanto si deve alla suocera e' esattamente il
numero che l'utente sta cercando, e sparire e' il modo piu' rapido di farglielo
rifare a mano.

```markdown
## Totale cibo di casa — 142,28 €
di cui menu 121,86 €, alimentare fuori lista 20,42 €

### Fuori da questo conto, per memoria
- alla cassa: 233,26 €
- non alimentare: 45,90 € di zaino, 12,80 € fra carta casa e detersivi
- spesa di un'altra casa: 32,28 € (dettaglio sotto)
```

### Il consuntivo e' un registro, non un modulo

Rigenera anche l'HTML, con `data-stato="consuntivo"` sul `body`.

Ne' il preventivo ne' il consuntivo hanno caselle cliccabili, e il motivo vale
la pena di scriverlo: **lo stato dentro la pagina e' invisibile alle skill, e lo
e' in silenzio.** Le skill leggono file. Una spunta o un commento messi nella
pagina sembrerebbero, a chi li scrive, esattamente come dire una cosa al
sistema — e non li avrebbe ricevuti nessuno. Al supermercato ci va il markdown
della lista, che invece torna indietro.

E per le annotazioni non servirebbe comunque: il momento in cui si annota
meglio non e' «guardando il menu la domenica», e' «davanti ai fornelli il
mercoledi'», dove `lunario:prepara` c'e' gia', sta gia' parlando e scrive gia'
sui file — nel diario della settimana. Un secondo canale produrrebbe solo due
registri mezzi pieni che si contraddicono.

## 4a. L'occhio sui prezzi

La serie storica in `prodotti.jsonl` non e' un archivio: e' il posto dove i
rincari si vedono. Confronta ogni prezzo con l'ultimo della serie, e se lo
scostamento e' netto dillo — una riga, come dato: «l'olio e' passato da 5,90 a
7,20». Niente commenti sul carovita: l'utente lo sa gia'.

Se un prodotto rincara stabilmente, due mosse da proporre — non insieme, e
solo quando i numeri le reggono:

- il **formato**: il prezzo al chilo della confezione grande di solito e'
  migliore, ma conviene solo se la casa la consuma davvero. Una confezione
  grande che il postmortem ritrova avanzata due volte non e' un risparmio: e'
  spreco comprato a prezzo scontato
- il **paniere**: a parita' di funzione nel piatto, il metro e' €/100 g di
  proteine (`${CLAUDE_PLUGIN_ROOT}/kb/consigli-pratici.md`) — ed e' il metro
  giusto anche quando non rincara niente

## 5. Chiudi corto

L'utente ha le buste da svuotare. Due o tre righe:

- **quanto e' costato il cibo di casa**, e di quanto si e' discostato dalla
  stima. Se alla cassa la cifra era un'altra, dillo nella stessa frase e di'
  cosa la separa: e' la domanda che si fa chiunque abbia in mano lo scontrino
- cosa manca e cosa hai fatto di conseguenza
- cosa resta da procurare, **e per quale giorno**: e' l'unica cosa di questa
  risposta che gli chiede di fare qualcosa

Su uno scontrino con dentro solo il menu, **una riga sola**: «Tutto arrivato,
89,40 € contro i 92,50 stimati. Buona settimana.»

Su uno scontrino vero, che il piu' delle volte contiene anche altro:

> Cibo di casa 142,28 €, di cui 121,86 € di menu. Alla cassa 233,26 €: la
> differenza e' lo zaino e la spesa di tua suocera (32,28 €, dettaglio nel
> consuntivo).

## Perche' questo momento conta

Lo scontrino a inizio settimana, invece che alla fine, cambia due cose:

1. **Le sostituzioni si fanno prima di cucinare**, non davanti al frigo vuoto
   il giovedi' sera
2. **I prezzi entrano nel paniere sette giorni prima**, quindi la stima del
   lunedi' successivo lavora su dati di una settimana fa invece che di due

Il postmortem della domenica, di conseguenza, non chiede piu' lo scontrino:
chiede avanzi e voti. Se c'e' stata una seconda spesa in settimana, quella si'
che si porta al postmortem.
