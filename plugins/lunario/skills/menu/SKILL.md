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

## Prima di tutto: la cartella e' allineata?

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tagliando.py --rapido
```

**Se non stampa niente, prosegui senza dire niente**: e' il caso normale, e un
controllo che si fa notare a ogni lancio e' rumore.

Se stampa righe `blocca`, riparale **prima** — lavorare su file che non sono
quelli che credi non da' nessun errore, da' una settimana raccontata in un
documento che nessuno riaprira':

| cosa stampa | cosa fai |
|---|---|
| `[si ripara da solo]` | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tagliando.py --ripara`, poi una riga in chat su cosa si e' mosso |
| `CONTRATTO_INDIETRO` | passa da `lunario:aggiorna`, che esegue i passi di migrazione |
| qualsiasi altra cosa | passa da `lunario:tagliando` |

Poi torna qui: mettere a posto la cartella e' il presupposto, non il lavoro che
l'utente ha chiesto.

## Input

`dati/profilo.yaml` · `dati/ritmi.yaml` · `dati/note.md` ·
`dati/ricette.md` · `dati/storico.yaml` (tarature) · `dati/dispensa.yaml`
(`scorte`, `avanzi` **e** `freezer`) · il `contesto.yaml` della settimana. Dove
stanno i file della settimana lo dice lo script, e non si indovina:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/settimana.py
```

Se il contesto manca, chiama `lunario:settimana` invece di tirare a indovinare.

## 1. Risolvi la griglia, prima di scegliere qualsiasi piatto

Per ognuno dei sette giorni, per ognuno dei cinque pasti (`colazione`,
`spuntino`, `pranzo`, `merenda`, `cena`), per ogni persona: qual e' lo stato
della cella? Tre fonti, vince la piu' specifica.

```
profilo.pasti  <  ritmi.settimana.<giorno>  <  contesto.settimana.<giorno>
```

Una cella non dichiarata da nessuno vale `casa`; una messa a `no` dal profilo
resta `no`. `tutti` si espande su tutte le persone prima del confronto.

Il risultato e' la mappa su cui lavora tutto il resto:

| stato della cella | piatto | spesa | kcal |
|---|---|---|---|
| `casa` | si | si | contano |
| `trasportabile` | si, che viaggi e si mangi freddo | si | contano |
| `libero` | si, senza vincolo calorico | si | non contano |
| `ristorante` | no | no | no — ma la spesa esiste, la registra il postmortem |
| `fuori` | no | no | no |
| `no` | no | no | no |

**Non generare mai un piatto per una cella che non lo prevede**, e non
scriverla come vuota: nel menu si legge «giovedi' cena — fuori», che e'
un'informazione, mentre una riga bianca sembra un errore.

Se un giorno resta senza nessuna cella a `casa`, quel giorno non ha un menu, e
va bene: la settimana ne ha altri sei.

## 2. I sette giorni

Il pool da cui peschi e' **doppio**: `${CLAUDE_PLUGIN_ROOT}/kb/piatti.md` e
`dati/ricette.md`, i piatti di questa casa. Trattali allo stesso modo — stessa
rotazione, stessi voti, stesse esclusioni. Se in `ricette.md` c'e' qualcosa di
nuovo mai cucinato, **mettilo in un giorno con tempo** e dillo in mezza riga:
una ricetta mai provata il mercoledi' sera e' un rischio inutile.

Ordine di applicazione dei vincoli — chi viene prima vince:

1. **Esclusioni del profilo** — anche come ingrediente nascosto
2. **La griglia risolta** — una cella `trasportabile` riceve un piatto che
   viaggia e si mangia freddo, mai qualcosa da scaldare; un giorno con
   `cena_entro_min: 25` non riceve un piatto da 40 minuti; una cella `libero`
   pesca dai pasti liberi di `${CLAUDE_PLUGIN_ROOT}/kb/piatti.md` e non viene
   alleggerita
3. **Le scorte** (`dispensa.yaml`, sezione `freezer`) — cio' che e' gia' in
   casa entra nel menu **prima** che si scelga cosa comprare, e cio' che porta
   `da_smaltire: true` o una data vecchia entra per primo. E' roba pagata: un
   branzino comprato al banco mentre due filetti invecchiano nel congelatore
   e' l'errore piu' caro che questo sistema puo' fare
4. **Deperibilita'** (`${CLAUDE_PLUGIN_ROOT}/kb/deperibilita.md`) — il fresco nei primi giorni, la
   dispensa in fondo. E' la regola che azzera lo spreco
5. **Le tolleranze del profilo** (`tolleranze.ripetizioni`) — la stessa
   proteina a pranzo e a cena, lo stesso piatto due volte in un giorno, un
   ingrediente che torna troppo presto. Cio' che il profilo non dichiara vale
   il default conservativo: non si ripete
6. **Rotazione** — mai i piatti delle ultime 2 settimane; mai quelli in
   `tarature.piatti_in_quarantena` con `fino_al` **non ancora passato**, e mai
   quelli in `piatti_esclusi`, che non tornano piu'; priorita' ai preferiti e
   alle voglie dichiarate. Le voci di quarantena scadute toglile passando: e'
   il momento in cui le hai in mano, e nessuno deve ricordarsi di fare pulizia
7. **Frequenze** (`${CLAUDE_PLUGIN_ROOT}/kb/porzioni-standard.md`) — pesce 2-3, carne max 3 di cui
   rossa max 1, legumi 2-4, e i tetti del profilo

I tetti del profilo (`max_pasti_*`) hanno una **rigidita'**, ed e' il campo
che dice cosa fare quando le scorte spingono in senso contrario:

| forma nel profilo | cosa fai |
|---|---|
| numero nudo, o `rigidita: vincolo` | non lo superi. Se le scorte lo chiedono, lo dici e non lo fai |
| `rigidita: preferenza` | lo superi quando c'e' una ragione, **e la ragione la scrivi** — mezza riga: «due volte pesce, per smaltire i filetti di giugno» |

Un tetto superato in silenzio e' un tetto rotto; un tetto superato con la
ragione accanto e' una decisione che l'utente puo' ribaltare in una parola.

Le frequenze sono pensate su una settimana intera, ma **si applicano alle
celle che restano in casa**: se le cene cucinate sono quattro, quelle quattro
non possono essere due carni e due formaggi — pesce e legumi hanno la
precedenza, perche' altre occasioni non ci sono. E la settimana si legge
anche in verticale, come farebbe chi la deve mangiare: due piatti lunghi non
si affiancano in due sere di fila, lo stesso sapore dominante non torna a un
giorno di distanza, e la verdura c'e' ogni giorno senza che serva una regola
che lo imponga. Il giorno dopo un pasto libero e' un giorno normale: ne'
piu' leggero ne' piu' virtuoso, perche' la compensazione e' vietata anche
quando si traveste da buon senso.

Avanzi della settimana scorsa nei primi giorni, **nella forma che il profilo
tollera**: `tolleranze.avanzi` dice se tornano in tavola come sono, solo
trasformati in un'altra cosa, o mai — e la riga dei bambini, quasi sempre la
piu' stretta, vince su quella generale. Per ogni persona con
`selettivo: true`, i pasti a casa portano la loro base neutra
(`${CLAUDE_PLUGIN_ROOT}/kb/consigli-pratici.md`), segnalata in linea.

**Colazioni e merende non si sorteggiano ogni settimana**: sono abitudini. Si
sceglie una colazione e due o tre merende da
`${CLAUDE_PLUGIN_ROOT}/kb/piatti.md` e si ripetono, cambiando solo se qualcuno
se ne stufa. Nel menu stanno in testa al giorno, in una riga sola.

Porzioni da `${CLAUDE_PLUGIN_ROOT}/kb/porzioni-standard.md`, scalate sulle tarature e sul target
kcal di **chi mangia davvero quel pasto**: chi ha `dieta: false` prende la
porzione standard, senza deficit e senza commenti. kcal indicative,
arrotondate alle decine, mai spacciate per misure.

Il totale calorico del giorno somma **tutte** le celle a `casa` — colazione e
merende comprese — e ignora quelle `libero`. Un target che non conta le
merende e' un target falso.

## 3. Dai grammi alle confezioni

Il passo che rende la lista utile. Procedura completa in `${CLAUDE_PLUGIN_ROOT}/kb/confezioni.md`:

1. **fabbisogno** per ingrediente: porzione × **celle che lo mangiano** — non
   × persone. Un pranzo in mensa e una merenda che nessuno fa non comprano
   niente; la merenda dei due bambini compra per due, sette volte
2. **meno quello che c'e' gia' in casa** — `avanzi`, `freezer` e `scorte`, in
   quest'ordine e con la fiducia che ognuno si merita: vedi 3c
3. **confezioni**: formato da `dati/prodotti.jsonl`. I prodotti che non ci sono
   si risolvono adesso, col procedimento qui sotto — non si rimandano alla
   lista
4. Applica la soglia del 10% (limare la porzione invece di comprare una
   confezione quasi inutile) e calcola l'avanzo previsto

Se il profilo ha `tolleranze.spesa_per_altri: true`, la lista di casa resta
la lista di casa: la seconda spesa non entra nei fabbisogni, nel totale e
nella dispensa. Se ne parla `lunario:spesa` davanti allo scontrino.

### 3a. Cio' che copre una scorta esce dalla lista, e si dice uscendo

Quando un piatto e' costruito su una riga di `freezer` o su un avanzo di
dispensa, la riga della spesa corrispondente **non si compra**. Ma cancellarla
in silenzio rende sospetta tutta la lista: un banco pesce con una riga sola
sembra una dimenticanza finche' non si sa perche'. Quindi la cancellazione si
nomina nella sezione **«Gia' in casa»** (6c) del preventivo:

```markdown
### Dalla dispensa, non si compra
- Branzino al banco, 800 g → i due pacchi di filetti nel congelatore (lun cena)
- Straccetti di manzo, 350 g → il petto di pollo intero, tagliato (mar cena)
```

Il totale scende di conseguenza, e scende per una ragione leggibile.

### 3b. I formati che mancano si cercano, non si rimandano

Alla prima settimana di una casa nuova `prodotti.jsonl` e' vuoto, quindi
**tutti** i formati mancano. Se non li si cerca, l'intera lista esce in grammi
con `[formato da verificare]` su ogni riga, la dispensa resta vuota e la
settimana dopo si ricompra la pasta che e' gia' in casa. Il marcatore e'
onesto, ma deve restare l'eccezione che era: sono una decina di ricerche
meccaniche, ed e' esattamente il lavoro che fa la skill al posto dell'utente.

**Prima raccogli tutti i mancanti, poi cerca.** A fine passata del fabbisogno
hai la lista completa dei prodotti senza formato: sono ricerche indipendenti e
si fanno in blocco, non una per volta dentro il ciclo.

Per ognuno, in quest'ordine, e ci si ferma al primo che risponde:

1. **Codice a barre**, se lo si conosce da uno scontrino passato:
   `off_lookup.py --ean <ean> --salva <id>` — una chiamata, esatta
2. **Nome su Open Food Facts**: `off_lookup.py "<nome>" --marca <marca>`.
   Stampa i candidati col formato di ciascuno: **scegli il formato modale fra
   i primi risultati, non il primo hit**. Una ricerca di «fusilli barilla»
   restituisce buste artigianali da 200 g accanto allo standard da 500, e il
   primo posto non vuol dire niente. Poi salva il candidato scelto col suo EAN
3. **Ricerca web**, se OFF non conosce il prodotto: cerca il formato in cui
   quel prodotto si vende in Italia, e vale la stessa regola — il formato piu'
   ricorrente, non il primo trovato. Va in `prodotti.jsonl` con
   `fonte_formato: {fonte: ricerca, data: oggi}`
4. **L'utente**, che e' la fonte migliore di tutte perche' il pacco ce l'ha in
   dispensa. Quelli rimasti si chiedono **tutti in una volta**, in una domanda
   sola con l'elenco — mai un modulo, mai una domanda per prodotto. La risposta
   entra come `fonte_formato: {fonte: utente, data: oggi}` e da li' vale piu'
   di qualsiasi database
5. **Solo se non risponde nessuno**: riga in grammi e `[formato da verificare]`

Due regole che valgono per tutti i passaggi:

- **Scrivi in `prodotti.jsonl` subito**, appena trovato. Open Food Facts chiede
  «1 API call = 1 real scan»: la cache e' il modo di rispettarlo, e la seconda
  settimana costa zero chiamate
- **Mai un formato a memoria.** Ogni formato porta `fonte_formato` con la data:
  un errore si corregge dove e' nato, e il primo scontrino lo corregge da solo

Non raccontare all'utente le ricerche una per una: e' rumore. Se qualcosa e'
rimasto irrisolto, lo dice la riga marcata nella lista.

Aggiorna `dati/dispensa.yaml` con gli avanzi previsti — **solo non
deperibili**, la fascia `[fine]` di `${CLAUDE_PLUGIN_ROOT}/kb/deperibilita.md`.

### 3c. Quello che c'e' gia' in casa si sottrae per gradi

Il fabbisogno non si confronta con un magazzino: si confronta con tre cose che
il sistema conosce con tre gradi di certezza diversi, e l'ordine conta.

```
fabbisogno − avanzi − freezer − scorte = da comprare
```

1. **`avanzi`** — calcolati dal motore la settimana scorsa, in grammi. Si
   sottraggono per intero
2. **`freezer`** — visto dall'utente, con la data. Si sottrae per intero, e
   comanda anche **quali piatti** entrano in settimana (vedi il punto 3 dei
   vincoli)
3. **`scorte`** — contate una volta, e poi invecchiate. Qui la sottrazione
   **dipende da quanto e' vecchia la convinzione**

La fiducia si calcola da `visto`, `rotazione` e da quanto la settimana si
appoggia a quella riga — la tabella e' in `${CLAUDE_PLUGIN_ROOT}/kb/scorte.md`:

| fiducia | cosa fai |
|---|---|
| **fresca** | sottrai in silenzio |
| **invecchiata** | sottrai, e **dillo nel menu**: «conto sui 2 pacchi di riso visti il 12 luglio» |
| **stantia** | **non fidarti**: non sottrarre, e segnala che quella riga andava contata prima di generare |

Una banda non si sottrae in grammi, decide se la riga serve: `pieno` e `medio`
la fanno sparire, `poco` e `finito` la lasciano intera. Un numero si sottrae
come una quantita' vera.

**Sopra `massimo` non si compra, punto.** Se il fabbisogno chiederebbe una
confezione ma la scorta e' gia' al tetto, la riga non esce, e **lo si dice in
mezza riga** — perche' e' l'unico momento in cui l'errore che nessuno nota
diventa visibile:

```markdown
- Passata di pomodoro: ne servirebbe 1 bottiglia, ma ne avete gia' 6 (tetto: 6).
  Non la metto in lista.
```

Come dato, mai come rimprovero. Comprare in abbondanza non e' una
dimenticanza: e' un modo di sentirsi previdenti, e un sistema che ci mette
sopra un giudizio si fa spegnere.

**Il menu sottrae per calcolare, e non scrive la sottrazione.** Le `scorte`
servono a decidere cosa comprare: qui si leggono, non si toccano. A scaricarle
e' `lunario:prepara`, che vede cosa si e' cucinato davvero — se lo facesse anche
il menu, una settimana pianificata e mai cucinata lascerebbe la dispensa piu'
vuota di com'e', e le due skill insieme scaricherebbero due volte la stessa
scatola di ceci (`${CLAUDE_PLUGIN_ROOT}/kb/scorte.md`).

Quello che il menu scrive in `dispensa.yaml` resta solo `avanzi`: gli avanzi
**previsti** dalle confezioni comprate, dichiarati come previsione.

**Una cosa sola si sottrae una volta sola.** Se una riga di `scorte` e una di
`freezer` descrivono lo stesso pacco — capita coi surgelati, che sono insieme un
prodotto del paniere e una cosa vista nel congelatore — vale il `freezer`, che
e' datato e l'ha visto un umano. La scorta si ignora, e nel menu si nomina da
dove viene quello che stai contando.

## 4. Il totale

Somma degli ultimi prezzi noti in `dati/prodotti.jsonl`. Ogni riga senza
prezzo si marca `[prezzo ignoto]` e resta fuori dal totale, che va dichiarato
come stima parziale — mai gonfiato con numeri inventati. Alla prima settimana
il totale puo' non esistere: e' normale, arriva col primo scontrino.

Se c'e' un `budget_settimana_eur` nelle tarature e la stima lo supera,
segnalalo in una riga e proponi la sostituzione a miglior €/100 g di proteine
(`${CLAUDE_PLUGIN_ROOT}/kb/consigli-pratici.md`).

## 5. Il titolo della settimana

Ogni settimana ha un nome: serve a ricordarsela per nome invece che per numero
ISO, e finisce nel markdown, nell'HTML, in `storico.yaml` e **nel nome dei
file** (regola completa in `CLAUDE.md`).

**Se il profilo ha `titoli.serie`**, il nome si pesca da li' — «Norwegian
Wood», «Pesce pagliaccio», «Glicine» — e la serie da' un filo alle settimane
che un titolo descrittivo non ha. Come si sceglie l'elemento:

1. **Cerca la risonanza col menu.** «Yellow Submarine» sulla settimana dei tre
   pesci, «Fragola» su quella che apre col dolce di frutta. Quando c'e', e'
   la scelta migliore: il nome si ricorda perche' ha un aggancio
2. **Se non risuona niente, vai avanti nella serie** senza forzare. Un legame
   inventato e' peggio di nessun legame
3. **Mai ripetere** un titolo gia' uscito: l'elenco e' `titolo` delle voci in
   `storico.settimane`, non serve una lista a parte
4. Se la serie e' finita — capita dopo qualche mese — dillo in mezza riga e
   proponi di sceglierne un'altra. Non ricominciare da capo di tua iniziativa

**Se `serie` e' `null`**, il titolo nasce dai **piatti veri** di questi sette
giorni: «la settimana dei legumi coraggiosi», «tre pesci e un forno acceso»,
«la settimana che smaltisce il congelatore». Mai da una formula generica.

In entrambi i casi: una riga sola, ironico va bene e furbo no, e se non viene
niente di caratteristico un titolo piano e' meglio di uno forzato.

**Poi il titolo diventa il nome della cartella**, e da li' quello di ogni file
che ci finira' dentro. Lo slug lo calcola lo script, cosi' non lo si scrive a
mano due volte in modo diverso:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/settimana.py --slug "Commando"
mv settimane/2026-W34 settimane/2026-W34-commando
```

`lunario:settimana` ha creato `settimane/<ISO>/`: rinominala **adesso**, prima
di scrivere qualsiasi cosa, cosi' i documenti nascono gia' col nome giusto. E'
l'unico rename previsto dal sistema, e avviene prima che qualcuno abbia visto
un nome.

Da qui in poi il nome e' fissato: `lunario:correggi` non lo tocca nemmeno se
riscrive meta' settimana, perche' un rename dovrebbe muovere la cartella, sei
documenti e ogni link che ci puntava.

### 5a. Il vestito della settimana

Il template HTML porta in testa un blocco marcato **«IL VESTITO DELLA
SETTIMANA»**: undici colori, un glifo decorativo (il fregio) e il
`theme-color` del telefono. Non e' un tema fisso da lasciare com'e': si
ricompone **a ogni settimana**, ed e' il titolo a dettarlo — cosi' due menu
non si somigliano mai, e la settimana si riconosce dal colore prima ancora
che dal nome.

1. **Parti dal titolo.** «Yellow Submarine» veste di giallo su blu notte,
   «Glicine» di verdi e lilla slavati, «la settimana che apre il congelatore»
   di azzurro ghiaccio. Il fregio e' **un carattere solo** — ☾ ✿ ⚓ ❄ — che
   richiama la stessa immagine; se niente risuona, ☾ e' il default di casa
2. **Se il titolo non suggerisce niente**, la palette cambia lo stesso: leggi
   il `:root` dell'HTML della settimana precedente e cambia registro — dopo
   una chiara una scura, dopo un accento caldo uno freddo. La varieta' e' il
   punto, non un effetto collaterale
3. **Le regole del blocco vincono sull'estro**: gli undici colori si
   sostituiscono **tutti insieme**, i contrasti minimi scritti nel template
   non si scavalcano (la pagina si legge al supermercato, sotto luci forti:
   nel dubbio, chiara), `--su-accento` deve reggere la ✓ nella casella, e il
   `theme-color` nel `<head>` ripete l'esadecimale di `--fondo`
4. **La stampa non si veste**: il blocco `@media print` resta com'e', bianco
   e sobrio, qualunque cosa faccia lo schermo

Il vestito e' della settimana, non del menu: `lunario:correggi` che riscrive
tre giorni non lo cambia, e `lunario:spesa` che promuove a consuntivo cambia
lo stato, non i colori.

## 6. Output

**Tutto dentro la cartella della settimana**, e ogni file porta il nome intero:
un documento scaricato sul telefono o allegato a un messaggio perde la cartella
e resta col suo nome soltanto, e `preventivo.md` a quel punto non dice di quale
settimana sia.

```
settimane/2026-W34-commando/
├── 2026-W34-commando-preventivo.md      <- i sette giorni
├── 2026-W34-commando-preventivo.html    <- la copia da frigo
├── 2026-W34-commando-lista.md           <- la spesa, sola e da spuntare a mano
├── contesto.yaml
└── diario.yaml
```

Quattro cose, in quest'ordine:

1. **`<nome>-preventivo.md`** — la fonte: in testa `stato: preventivo`, poi
   titolo, i 7 giorni, «Gia' in casa» e il totale stimato. **La lista non ci
   sta dentro**: sta nel suo file, e il preventivo la nomina in una riga.

   Ogni giorno porta le celle che esistono davvero: colazione e merende in una
   riga sola in testa, poi pranzo e cena col piatto, le kcal per persona e la
   base neutra dove serve. Le celle che non si cucinano si scrivono lo stesso,
   marcate — «cena — fuori (ristorante)» — perche' il giorno si legga per
   intero. Una cella `libero` si marca **libero**, senza kcal.

   Ogni pasto e' una **casella da spuntare** (`- [ ]`), e vuol dire una cosa
   sola: quel pasto e' stato fatto. Le marca `lunario:prepara` man mano che si
   cucina, e da quel momento il file dice anche **a che punto e' la settimana**
2. **`<nome>-lista.md`** — la spesa, sola: vedi 6a. E' l'unico documento che
   l'utente modifica a mano, e l'unico che torna indietro
3. **`<nome>-preventivo.html`** — da
   `${CLAUDE_PLUGIN_ROOT}/templates/menu.html`, sostituendo i segnaposto
   `{{...}}` e ripetendo i blocchi marcati `RIPETI`. Si stampa e si attacca al
   frigo, e si mostra a chi la settimana la deve mangiare: e' la copia
   **leggibile**, non uno strumento. I reparti vanno nell'ordine in cui si gira
   il negozio, non in ordine alfabetico.

   Due cose da riempire bene, perche' non si vedono guardando la pagina: il
   salto «Già in casa» nella nav in testa si emette solo se la sezione esiste,
   e il vestito — palette, fregio, `theme-color` — segue la sezione 5a.
   **Nessuna casella cliccabile**: al supermercato ci va il markdown, e una
   pagina che raccoglie spunte che nessuna skill legge e' peggio di una pagina
   che non ne raccoglie
4. **Voce in `dati/storico.yaml`** con `titolo`, `spesa_stimata` e `menu` che
   punta al preventivo dentro la cartella

### 6a. La lista e' un file suo, ed e' l'unico che torna indietro

Al banco del pesce servono quaranta righe da spuntare, non un documento di
sette giorni. E soprattutto: **la lista e' un ingresso di dati**. L'utente la
apre sul telefono, spunta cio' che prende, annota accanto cio' che non c'era o
era diverso, e al ritorno `lunario:spesa` riapre **lo stesso file**. Non ci
sono due copie da riconciliare, e non c'e' niente da esportare.

Un file markdown, niente menu dentro:

```markdown
# Spesa — 2026-W34 Commando
preventivo del 2026-08-17 · spunta col dito, annota accanto: rileggo tutto io

## Banco pesce
- [ ] Filetti di branzino — 500 g
      → lun cena

## Ortofrutta
- [ ] Zucchine — 1,5 kg
      → mer cena · gio cena
- [ ] Rucola — 2 buste da 100 g
      → insalate, tutta la settimana

## Dispensa
- [ ] Fusilli integrali — 2 × 500 g
      → mar pranzo · ven cena

## Fuori Lunario
- [ ] detersivo lavastoviglie
- [ ] carta forno
```

Le regole della lista, tutte per la stessa ragione — che qualcuno la legge in
piedi, con una mano sola, e qualcun altro la rilegge tre giorni dopo:

- **i reparti nell'ordine in cui si gira il negozio**, come nell'HTML
- **una casella per riga**, con confezione e quantita' vere. La casella vuol
  dire **preso**, e niente altro: non «consumato», non «arrivato in casa»
- **la riga d'uso sotto**, come in 6b: e' quella che al banco dice cosa salta
  se manca
- **«Fuori Lunario» in coda, in una sezione sua**: cio' che si compra comunque
  e che il motore non pianifica. In markdown il colore non esiste, e una
  sezione separata dice da sola cosa il motore deve ignorare — sopravvive a
  qualsiasi app la apra. Se il profilo ha `tolleranze.spesa_per_altri: true`,
  anche la spesa che viaggia per un'altra casa sta qui
- **spazio per annotare**: si annota in linea, dopo la riga, a parole. Non c'e'
  una sintassi da imparare, e non deve essercene una

**La prima volta che scrivi una lista in questa casa** — nessuna settimana
precedente ha un `-lista.md` — dillo in mezza riga, una volta sola: la lista e'
un file, e se la cartella sta in un servizio sincronizzato la si apre col
telefono al supermercato con un qualsiasi editor markdown. Poi mai piu': non e'
una funzione da vendere, e' una comodita' che o si e' capita o non interessa.

### 6b. Ogni riga della spesa dice a cosa serve

Sotto ogni riga, in piccolo, **i pasti che usano quell'ingrediente**:

```markdown
- [ ] Carote — 700 g
      → mer cena · gio cena
- [ ] Fette biscottate — 2 × 300 g
      → colazione adulti, tutta la settimana
```

Il dato ce l'hai gia': la sezione 3 calcola il fabbisogno come porzione ×
celle che lo mangiano, quindi le celle sono in mano e basta portarle
all'output. Costa niente e risponde a tre domande che davanti allo scaffale
non hanno risposta:

- **cosa salta se manca.** «Niente finocchi al banco» diventa subito «e' il
  mercoledi' sera da ripensare» — che e' esattamente l'informazione con cui
  `lunario:spesa` propone una sostituzione
- **perche' questa roba e' in lista.** Uvetta e cannella in una lista italiana
  sembrano un errore finche' non si sa che sono il cous cous. Le righe senza
  spiegazione sono quelle che la gente salta in silenzio
- **se la quantita' e' giusta.** «Grana 300 g» non e' verificabile; «150 g per
  cucinare, 150 g a cubetti per la merenda dei bimbi» si controlla a colpo
  d'occhio, e una porzione sbagliata si becca prima dello scontrino invece che
  al postmortem

Come si scrivono:

- **Un pasto specifico**: giorno abbreviato e pasto — `mer cena`, `gio pranzo`
- **Un'abitudine**, non un giorno: a parole — `colazione adulti`, `merenda
  bimbi`, `tutta la settimana`. Elencare sette giorni per l'olio e' rumore
- Nell'HTML sono **collegamenti al blocco del giorno**, che ha il suo `id`

Falla anche come **verifica**: se una riga non ha nessun pasto che la usa, non
e' una riga della spesa, e' un residuo di una modifica precedente. Toglila
invece di comprarla.

### 6c. Gia' in casa: la seconda fonte del menu

Il menu ha **due fonti** — cio' che entra dal carrello e cio' che c'e' gia'
in casa — e la seconda ha una sezione sua, **nel preventivo, dopo i giorni**,
non nella lista: e' quello che **esce** di casa, non quello che entra nel
carrello, e al supermercato non ci si fa niente. Dentro, le due meta' si
trattano in modo opposto, perche' hanno nature opposte:

- **il congelatore e' una lista di azioni con un orario**: una riga per
  scorta, con il giorno in cui si mangia e l'ora in cui va spostata in
  frigo, e una casella che vuol dire **tirato fuori**
- **la dispensa e' una dichiarazione**: niente da fare, niente da spuntare —
  si nomina cio' che copre, cosi' la lista corta e il totale basso hanno una
  ragione leggibile

```markdown
## Gia' in casa

### Dal congelatore
- [ ] Filetti di branzino, 2 × 250 g → lun cena
      in frigo domenica sera (8-12 h)
- [ ] Scamone, 475 g → sab cena — e' li' da giugno, si smaltisce
      in frigo venerdi' mattina (12-24 h)

### Dalla dispensa, non si compra
- Branzino al banco, 800 g → i due pacchi di filetti nel congelatore (lun cena)
```

Lo scongelamento non e' un dettaglio da ricettario: e' **l'unico pezzo di
settimana che il giorno stesso non si recupera**. Un piatto rimandato si
sposta, un forno occupato si aspetta; una bistecca ancora dura alle otto di
sera e' una cena che non avviene. Quindi la riga dello scongelamento si
scrive sempre, anche quando sembra ovvia, e la casella la marca
`lunario:prepara` la sera prima.

Nell'HTML la sezione e' `#incasa`: il blocco `.scorte` per il congelatore
(casella, quantita', link al giorno che la usa) e il blocco `.dispensa` per
la riga della dispensa. La sezione — e il suo salto nella nav — c'e' solo se
la settimana usa delle scorte.

### 6d. Il piatto porta la sua ricetta, quando serve

Un menu si approva o si contesta sulla capacita' di **immaginarsi la
settimana**, e il nome nudo di un piatto non basta: «cous cous con verdure e
ceci» sono quattro cene diverse a seconda di cosa c'e' dentro.

- **Piatti di casa** (`dati/ricette.md`): il link e' al file, sull'ancora del
  piatto — `dati/ricette.md#pasta-con-crema-di-zucchine-e-menta`
- **Piatti del pool**: serve un URL, e vale la disciplina dei formati (3b) —
  **cercato adesso, mai scritto a memoria**. Un link inventato e' identico a
  uno vero finche' non ci si clicca. Se la ricerca non da' niente di buono,
  nessun link: e' un'assenza, non un problema
- **Piatti ovvi: niente link.** Se il nome determina il piatto — pasta al
  pomodoro, hamburger alla griglia, riso freddo — un link e' decorazione, e
  una lista dove tutto e' linkato smette di essere letta. La domanda da farsi
  e' se chi legge, senza aprire niente, sa gia' cosa arrivera' in tavola

Nel markdown il link sta accanto al piatto; nell'HTML e' il nome stesso a
essere cliccabile. **Sulla carta non deve comparire nessun URL**: la copia del
frigo non si riempie di indirizzi.

Le ricerche si fanno in blocco come quelle dei formati: sono pochi piatti a
settimana, e il link trovato resta scritto nel file della settimana, quindi
non si ricerca due volte.

### 6e. Vedere la cena prima di comprarla

Il link dice **cos'e'** un piatto; non dice cos'e' **qui** — scalato su questa
casa, con la base neutra tirata fuori per i bambini, dentro i trenta minuti di
un mercoledi'. Quella roba esiste gia', la sa `lunario:prepara`, e semplicemente
non e' raggiungibile prima di impegnarsi. Ed e' il momento in cui servirebbe:
vedere che giovedi' vuol dire grattugiare zucchine, sbattere otto uova e
quaranta minuti di forno e' cio' che fa dire «non il giovedi'» — prima che le
uova siano in frigo.

Quindi, chiudendo il preventivo, dillo in mezza riga: **si puo' chiedere
l'anteprima di un piatto** — «fammi vedere il giovedi'» — e risponde
`lunario:prepara` in modalita' anteprima, senza aprire niente e senza spuntare
niente.

Nell'HTML **non** si mette un link all'anteprima: una pagina statica non puo'
invocare una skill, e un link che non fa niente e' peggio di nessun link.
L'anteprima e' una cosa che si chiede parlando, ed e' giusto cosi' — a quel
punto la conversazione c'e' gia'.

In chat: il titolo, il menu, la lista, il totale, e dove hai salvato la
cartella. Stop. Le spiegazioni solo dove la scelta non e' ovvia, una riga
ciascuna.

**Il menu esce sempre in preventivo**, e va detto in chiaro: formati, prezzi e
piatti sono tutti previsioni finche' non passano dallo scontrino. Chiudi con una
riga sola che invita a portarlo in famiglia e a tornare per le contestazioni —
«fammi sapere cosa ne pensano» — non con un invito a fare la spesa.

L'HTML si genera lo stesso, perche' e' il formato con cui si mostra il menu
agli altri, e porta **PREVENTIVO** nell'intestazione: un foglio stampato senza
quella parola finisce sul frigo, e il suo totale viene letto come soldi spesi.

Il preventivo resta tale anche dopo che l'utente dice «va bene»: `lunario:correggi`
lo modifica, `lunario:spesa` scrive il consuntivo accanto ad esso col primo
scontrino. Nessun'altra skill lo fa, e **il preventivo non viene mai
sovrascritto**: resta li' com'era, ed e' cio' contro cui si misura tutto il
resto.
