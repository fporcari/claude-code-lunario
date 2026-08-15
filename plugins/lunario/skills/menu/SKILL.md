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
`dati/ricette.md` · `dati/storico.yaml` (tarature) · `dati/dispensa.yaml` ·
`settimane/<ISO>/contesto.yaml`. Se il contesto manca, chiama
`lunario:settimana` invece di indovinare.

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
3. **Deperibilita'** (`${CLAUDE_PLUGIN_ROOT}/kb/deperibilita.md`) — il fresco nei primi giorni, la
   dispensa in fondo. E' la regola che azzera lo spreco
4. **Rotazione** — mai i piatti delle ultime 2 settimane, mai i bocciati in
   quarantena, priorita' ai preferiti e alle voglie dichiarate
5. **Frequenze** (`${CLAUDE_PLUGIN_ROOT}/kb/porzioni-standard.md`) — pesce 2-3, carne max 3 di cui
   rossa max 1, legumi 2-4

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

Avanzi della settimana scorsa nei primi giorni. Per ogni persona con
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
2. **meno la dispensa** (`dati/dispensa.yaml`)
3. **confezioni**: formato da `dati/prodotti.jsonl`. I prodotti che non ci sono
   si risolvono adesso, col procedimento qui sotto — non si rimandano alla
   lista
4. Applica la soglia del 10% (limare la porzione invece di comprare una
   confezione quasi inutile) e calcola l'avanzo previsto

### 3a. I formati che mancano si cercano, non si rimandano

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
ISO, e finisce nel markdown, nell'HTML e in `storico.yaml`.

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

## 6. Output

Tre cose, in quest'ordine:

1. **`settimane/<anno>-W<settimana>.md`** — la fonte: in testa
   `stato: preventivo`, poi titolo, i 7 giorni e la lista per reparto in
   confezioni col totale.

   Ogni giorno porta le celle che esistono davvero: colazione e merende in una
   riga sola in testa, poi pranzo e cena col piatto, le kcal per persona e la
   base neutra dove serve. Le celle che non si cucinano si scrivono lo stesso,
   marcate — «cena — fuori (ristorante)» — perche' il giorno si legga per
   intero. Una cella `libero` si marca **libero**, senza kcal.

   Ogni pasto e ogni riga della spesa si scrivono come **caselle da spuntare**
   (`- [ ]`): `lunario:prepara` le marca man mano che si cucina e si consuma,
   e da quel momento il file dice non solo cosa era previsto, ma **a che punto
   e' la settimana**. E' lo stato su cui si appoggiano `lunario:correggi` e il
   postmortem
2. **`settimane/<anno>-W<settimana>.html`** — da
   `${CLAUDE_PLUGIN_ROOT}/templates/menu.html`, sostituendo i segnaposto
   `{{...}}` e ripetendo i blocchi marcati `RIPETI`. Si stampa e si attacca al
   frigo, ma soprattutto **si apre sul telefono al supermercato**: la lista si
   spunta col dito e le spunte restano dov'erano se la pagina si ricarica. I
   reparti vanno nell'ordine in cui si gira il negozio, non in ordine
   alfabetico.

   Due cose da riempire bene, perche' non si vedono guardando la pagina:
   `{{ISO}}` compare anche nella chiave di salvataggio, quindi due settimane
   aperte insieme non si mescolano; e ogni `input.spunta` vuole un `data-riga`
   **unico nella pagina** — uno slug del prodotto, non l'indice della riga,
   altrimenti aggiungere una voce sposta tutte le spunte gia' fatte
3. **Voce in `dati/storico.yaml`** con `titolo` e `spesa_stimata`

### 6a. Ogni riga della spesa dice a cosa serve

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

In chat: il titolo, il menu, la lista, il totale, e dove hai salvato l'HTML.
Stop. Le spiegazioni solo dove la scelta non e' ovvia, una riga ciascuna.

**Il menu esce sempre in preventivo**, e va detto in chiaro: formati, prezzi e
piatti sono tutti previsioni finche' non passano dallo scontrino. Chiudi con una
riga sola che invita a portarlo in famiglia e a tornare per le contestazioni —
«fammi sapere cosa ne pensano» — non con un invito a fare la spesa.

L'HTML si genera lo stesso, perche' e' il formato con cui si mostra il menu
agli altri, e porta **PREVENTIVO** nell'intestazione: un foglio stampato senza
quella parola finisce sul frigo, e il suo totale viene letto come soldi spesi.

Il preventivo resta tale anche dopo che l'utente dice «va bene»: `lunario:correggi`
lo modifica, `lunario:spesa` lo promuove a consuntivo col primo scontrino.
Nessun'altra skill cambia lo stato.
