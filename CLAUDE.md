# Lunario — menu settimanale e spesa

Sistema per generare ogni settimana il menu di una famiglia e la lista della
spesa in **confezioni reali da comprare**, non in grammi astratti, con
postmortem settimanale per ritarare quantita', piatti, prezzi e budget.

Ipocalorico per chi lo vuole e per chi lo vuole soltanto: la dieta e' un
attributo della persona, non della casa.

Questo repo contiene SOLO il motore, condivisibile. Tutti i dati personali
(profilo, ritmi, prodotti, storico, menu generati) vivono in `dati/` e
`settimane/`, escluse da git. Primo avvio: la skill `lunario:profilo`.

## Nessuna dipendenza da un supermercato

Scelta di progetto, non provvisoria: il sistema **non** si integra con nessun
servizio di spesa online, non fa scraping, non ha abbonamenti. Due sole fonti:

| dato | fonte | costo | quando |
|---|---|---|---|
| formato confezione, kcal, proteine | API pubblica Open Food Facts | gratis | una volta per prodotto, poi in cache |
| prezzo pagato davvero | scontrino PDF dell'utente | gratis | al ritiro della spesa |

Il prezzo dello scontrino batte qualsiasi listino: contiene gia' promozioni e
sconti fedelta'.

**Lo scontrino arriva a inizio settimana, non alla fine**, perche' la spesa si
ritira prima di cominciare a cucinare. Ne discendono due cose che valgono piu'
del prezzo in se':

- le **mancanze si scoprono subito** — cosa non c'era, cosa e' stato sostituito,
  che formato hanno dato davvero — e si rimedia prima di cucinare, non davanti
  al frigo il giovedi' sera
- i prezzi entrano nel paniere **sette giorni prima** di servire

Resta un limite, ed e' accettato: il menu del lunedi' si costruisce comunque
sui prezzi della settimana precedente, perche' viene prima della spesa. Le
offerte del volantino corrente non entrano nella scelta dei piatti.

## La griglia dei pasti

Il giorno non e' «pranzo e cena»: e' una **griglia pasto × persona**, e ogni
cella ha uno stato. E' il modello che regge insieme quattro cose che sembrano
diverse — chi e' a dieta e chi no, il pasto libero, la sera al ristorante, la
merenda che un figlio fa e l'altro no — e che modellate una per una
diventerebbero quattro toppe.

I cinque pasti: `colazione` · `spuntino` · `pranzo` · `merenda` · `cena`.

Gli stati di una cella, uno scalare, mai una combinazione:

| stato | Lunario lo pianifica | lo compra | conta nelle kcal | e' spesa |
|---|---|---|---|---|
| `casa` | si | si | si | nel menu |
| `trasportabile` | si, ma deve viaggiare e mangiarsi freddo | si | si | nel menu |
| `libero` | si, **senza vincolo calorico** | si | no | nel menu |
| `ristorante` | no | no | no | **fuori menu, da registrare** |
| `fuori` | no | no | no | no (mensa, bar, ospite altrui) |
| `no` | no | no | no | no (questa persona quel pasto non lo fa) |

`ristorante` e `fuori` si somigliano e non sono la stessa cosa: la differenza
e' **chi paga**. La mensa aziendale esce dal sistema e basta; la pizzeria del
sabato e' spesa alimentare vera, e se non entra da nessuna parte il budget
settimanale racconta una bugia per difetto.

### I tre livelli, dal generale al particolare

La stessa griglia vive in tre file, e vince sempre il piu' specifico:

| file | cosa dice | esempio |
|---|---|---|
| `dati/profilo.yaml` | **quali pasti fa** ognuno, di norma | «i bimbi fanno merenda, gli adulti no» |
| `dati/ritmi.yaml` | l'override **ricorrente**, per giorno | «il martedi' Adulto2 pranza fuori» |
| `settimane/<ISO>/contesto.yaml` | l'override di **questa settimana** | «giovedi' cena al ristorante» |

Una cella non dichiarata da nessuno vale `casa`, tranne quelle che il profilo
ha messo a `no`: quelle restano `no` finche' il profilo non cambia.

### Dieta o no

`dieta: true|false` per persona, nel profilo. Non e' un attributo della
famiglia: nella stessa casa un adulto puo' dimagrire e un bambino crescere.

- `dieta: true` → `kcal_giorno` calcolato, porzioni scalate, deficit
- `dieta: false` → `kcal_giorno: null`, porzioni standard CREA, **nessun
  commento sul peso, mai**. Il sistema non fa la morale a chi non ha chiesto
  niente

Se nessuno e' a dieta, Lunario resta un pianificatore equilibrato: la parola
«deficit» non compare, i piatti non vengono alleggeriti d'ufficio.

### Le pesate, e come si leggono

Chi ha `dieta: true` e `pesata_settimanale: true` riceve **una domanda al
postmortem**: quanto pesa. Va in `tarature.pesate.<persona>` di
`storico.yaml`, serie storica mai sovrascritta.

**Il profilo non si tocca**: `peso_kg` li' dentro e' il peso **di partenza**,
quello su cui e' stato calcolato il target, e resta fermo finche' non lo
cambia l'utente. Il peso corrente e' l'ultima riga delle pesate. Due campi
diversi per due cose diverse: sovrascrivere il primo col secondo cancellerebbe
l'unico riferimento rispetto a cui misurare il progresso.

**Il numero singolo non si commenta mai.** Il peso oscilla di 1-2 kg per
acqua, sale, sonno, ciclo e ora della pesata: leggere la singola misura come
un voto e' il modo piu' rapido di far mollare tutto. Si guarda solo il trend,
e solo quando c'e' abbastanza roba per parlarne:

| condizione | cosa fa il sistema |
|---|---|
| meno di 3 pesate | registra e tace. Non c'e' ancora un trend |
| da 3 in su | media mobile su 3 settimane, confrontata con le 3 precedenti |
| calo 0,3-0,5 kg/sett | e' il ritmo previsto: mezza riga, una volta ogni tanto, non ogni domenica |
| calo oltre 1 kg/sett per 3 settimane | **dillo e rimanda al medico**: e' troppo in fretta, e a queste velocita' si perde muscolo |
| fermo o in salita per 3+ settimane | proponi di rivedere porzioni o target. Come ipotesi, non come diagnosi, e senza cercare un colpevole |
| obiettivo raggiunto | proponi il passaggio a mantenimento: `dieta: false`, o kcal senza deficit |

Cosa **non** si fa, mai: commentare il corpo di qualcuno, congratularsi o
consolare, usare parole come «bravo», «sgarro», «recuperare». Il sistema
riporta un andamento, non giudica una persona. E se qualcuno salta la domanda,
si va avanti in silenzio: saltare non e' un dato da registrare.

Ricalcolare le kcal a ogni pesata sarebbe rumore — venti calorie in piu' o in
meno ogni domenica. Quando l'ultima pesata si e' spostata di **3 kg** da
`peso_kg`, il target e' invecchiato: **proponi** il ricalcolo, e se l'utente
accetta aggiorna insieme `peso_kg` e `kcal_giorno`. E' una modifica al livello
dichiarato, quindi si chiede — ed e' anche l'unico momento in cui il peso di
partenza si sposta.

### Il pasto libero non si compensa

Una cella `libero` non fa risparmiare calorie alle altre. Non si taglia il
pranzo perche' la sera c'e' la pizza, e non si recupera il giorno dopo: e'
esattamente il meccanismo che rende insopportabili le diete, e il pavimento
delle 1200 kcal resta valido comunque. Il piatto libero si pianifica e si
compra come gli altri — semplicemente, non porta un conto.

### Colazioni, spuntini e merende contano

Finche' erano fuori dal modello, i target calorici erano **falsi per
difetto**: due merende da 200 kcal, due persone, sette giorni fanno 2800 kcal
a settimana che nessuno contava. Una cella `casa` genera fabbisogno e riga
della spesa qualunque pasto sia, e le porzioni stanno in
`kb/porzioni-standard.md` come tutte le altre.

## I livelli di stato, una skill ciascuno

Confonderli e' il modo piu' rapido di ottenere un sistema che dimentica o che
non impara. Ogni skill scrive un livello solo.

| skill | livello | scrive | cadenza |
|---|---|---|---|
| `lunario:profilo` | stabile | `dati/profilo.yaml` | una volta |
| `lunario:ritmi` | dichiarato | `dati/ritmi.yaml`, `dati/note.md` | quando cambia la vita |
| `lunario:settimana` | effimero | `settimane/<ISO>/contesto.yaml`, `dati/ricette.md` | ogni lunedi' |
| `lunario:menu` | — (consuma tutto) | `settimane/<ISO>.md` + `.html`, `dati/dispensa.yaml` | ogni lunedi' |
| `lunario:spesa` | appreso (prezzi) | `dati/prodotti.jsonl`, `dispensa.yaml`, `storico.yaml` | al ritiro della spesa |
| `lunario:prepara` | appreso (cucina) | `dati/storico.yaml` → `voti.<piatto>.cucina` | mentre si cucina |
| `lunario:correggi` | effimero | `settimane/<ISO>.md` (giorni residui) | quando cambia qualcosa |
| `lunario:postmortem` | appreso (tavola, pesate) | `dati/storico.yaml` | domenica |

L'utente ne invoca quattro: `lunario:settimana` il lunedi', `lunario:spesa`
quando ritira la spesa, `lunario:prepara` quando cucina e
`lunario:postmortem` la domenica. `lunario:menu` viene chiamata dalla prima e
non va invocata a mano; le altre servono quando serve.

**I due voti non sono lo stesso voto.** Chi cucina valuta difficolta' e resa
appena finito, e quel dato decide **dove** un piatto puo' stare nella
settimana; i commensali votano al postmortem, e quel dato decide **se** il
piatto resta in rotazione. Un piatto amato a tavola puo' essere insostenibile
il mercoledi' sera: il primo voto lo sposta nel weekend, non lo elimina.

Regola di confine: **il sistema non tocca mai i livelli dichiarati**. Profilo,
ritmi e note li scrive solo l'utente (la skill puo' proporre). Tarature,
dispensa e prezzi li scrive solo il sistema. Unica eccezione, `ricette.md`: il
contenuto e' dell'utente ma lo scrive il sistema sotto dettatura, perche' la
forma serve al motore.

## Struttura

Il repo e' un **marketplace** con dentro un plugin: il motore si installa e si
aggiorna come qualsiasi plugin di Claude Code, i dati di famiglia restano nella
cartella di lavoro e non viaggiano con esso.

```
├── CLAUDE.md                        # questo file: la fonte di verita'
├── .claude-plugin/marketplace.json  # il repo come marketplace
├── plugins/lunario/                 # IL MOTORE, condivisibile
│   ├── .claude-plugin/plugin.json
│   ├── skills/                      # profilo · ritmi · settimana
│   │   └── ...                      # menu · correggi · postmortem
│   ├── kb/                          # knowledge base condivisa
│   │   ├── porzioni-standard.md     # porzioni e frequenze CREA 2018
│   │   ├── deperibilita.md          # ordine dei giorni, durate in frigo
│   │   ├── confezioni.md            # grammi -> confezioni, dispensa, avanzi
│   │   ├── consigli-pratici.md      # bimbi selettivi, batch cooking, €/proteine
│   │   └── piatti.md                # pool piatti taggato per deperibilita'
│   ├── scripts/
│   │   └── off_lookup.py            # Open Food Facts -> dati/prodotti.jsonl
│   └── templates/                   # modelli commentati, copiati al setup
└── loghi/
```

**Nel repo non c'e' nessuna cartella `dati/`**, ed e' voluto: i dati di
famiglia non appartengono al motore. Vivono nella cartella da cui si lavora:

```
~/dove-vuoi/lunario/          <- la cartella di casa, aperta con Claude Code
├── dati/                     <- creata da `lunario:profilo` dai templates
│   ├── profilo.yaml          # famiglia, kcal, esclusioni
│   ├── ritmi.yaml            # orari ricorrenti per persona e giorno
│   ├── note.md               # vincoli liberi, letti a OGNI lancio
│   ├── ricette.md            # i piatti di casa, accanto a kb/piatti.md
│   ├── prodotti.jsonl        # il paniere: formato, nutrienti, prezzi
│   ├── dispensa.yaml         # cosa e' rimasto in casa
│   └── storico.yaml          # settimane e tarature
└── settimane/                # menu generati, per settimana ISO
```

Dentro le skill, i file del motore si citano con `${CLAUDE_PLUGIN_ROOT}/kb/...`
perche' il plugin, una volta installato, vive fuori dal progetto. I file di
`dati/` e `settimane/` sono invece relativi alla cartella di lavoro, e
`LUNARIO_DATI` permette di spostarli altrove.

## Installazione

```
claude plugin marketplace add fporcari/claude-code-lunario
claude plugin install lunario@claude-code-lunario
```

Da locale, durante lo sviluppo, al posto della prima riga:
`claude plugin marketplace add ./` dalla radice del repo.

Poi l'utente crea **una cartella qualsiasi**, dove vuole e col nome che vuole,
la apre con Claude Code e lancia `lunario:profilo`. Da li' in poi non tocca
piu' niente a mano: la skill intervista e costruisce `dati/`, `settimane/`, i
file dai templates e il `CLAUDE.md` di quella cartella.

La cartella **e'** il contesto: una per famiglia, una per «quando sono solo».
Profilo, ritmi e storico restano separati; paniere e dispensa si possono
condividere, perche' il supermercato e il frigo sono gli stessi.

Il setup riconosce dove viene lanciato: dentro il repo del motore si ferma e
lo dice, in una cartella gia' configurata aggiorna invece di ricominciare.

## Git, e perche' resta locale

La cartella di casa e' **un repo git locale, senza remote**, creato dal setup
e mantenuto dalle skill: ogni skill che ha scritto qualcosa chiude con un
commit. L'utente non digita mai un comando git.

Serve a una cosa sola, ma vera: **vedere cosa e' cambiato e tornare indietro**.
Le tarature si spostano di poco alla volta, e senza storia una porzione
sbagliata da tre settimane e' impossibile da attribuire.

**Nessun remote, ed e' una scelta.** Qui dentro ci sono pesi, obiettivi di
dimagrimento e abitudini alimentari di persone reali, minori compresi:
spingerli su un host — anche in un repo privato — e' un dato che esce di casa
e che non si fa rientrare. Se l'utente lo chiede esplicitamente:

- dire in chiaro cosa sta caricando, una riga, senza fare la predica
- se accetta, il minimo serio e' cifrare i valori con SOPS + age, non
  affidarsi alla privatezza del repo
- non proporlo mai per primo, e mai come «cosi' lo usi dal telefono»: per
  quello c'e' `claude remote-control`, che tiene i file su questa macchina e
  ci si connette dal telefono senza spostare niente

Il commit non e' negoziabile con l'utente a ogni giro: e' rumore. Si dice una
volta al setup che c'e', e chi non lo vuole mette `git: no` nel profilo.

**Come committa una skill.** Ultima cosa che fa, dopo aver scritto i file e
prima di rispondere in chat, e solo se `git: locale` e qualcosa e' cambiato:

```bash
git add -A && git commit -q -m "<skill>: <cosa e' successo>"
```

Messaggi che si leggono a distanza di mesi — `menu: 2026-W34, preventivo` ·
`spesa: scontrino del 14/08, 89,40 €` · `postmortem: 2026-W34, tre tarature`.
Se il commit fallisce, non dire niente all'utente e vai avanti: e' una rete di
sicurezza, non un pezzo del flusso. In chat il commit non si nomina mai.

## Contratti dati

### dati/prodotti.jsonl — il paniere, una riga JSON per prodotto

Non e' il catalogo del supermercato: sono i 40-50 prodotti che la famiglia
compra davvero. Si popola da solo, settimana dopo settimana.

```json
{"id": "pasta-integrale-500", "nome": "Fusilli integrali", "ean": "8002330121556",
 "formato_g": 500, "tipo": "confezione", "reparto": "dispensa",
 "kcal_100g": 348, "proteine_100g": 13.5,
 "alias_scontrino": ["FUSILLI INTGR 500", "PASTA INT.500G"],
 "prezzi": [{"data": "2026-08-14", "eur": 1.19, "fonte": "scontrino"}],
 "fonte_nutrienti": "openfoodfacts:8002330121556",
 "fonte_formato": {"fonte": "openfoodfacts:8002330121556", "data": "2026-08-14"}}
```

`fonte` del prezzo: `scontrino` (letto da un PDF) oppure `dichiarato` (detto
dall'utente, per esempio mentre cucina). Un prezzo dichiarato vale, purche' si
sappia che lo e'. Un prezzo senza fonte no.

Un campo che si impara al primo scontrino: `"fuori_scontrino": true` per cio'
che si compra altrove — il pane dal panettiere, le uova dal contadino. Resta
nella lista della spesa, ma non viene cercato nello scontrino ne' segnalato
come mancante.

- `tipo`: `confezione` (formato fisso, l'avanzo va in dispensa) ·
  `peso` (banco: si compra al grammo, nessun arrotondamento) ·
  `pezzo` (uova, vasetti: l'unita' e' il pezzo)
- `formato_g`: grammi o ml per confezione. `null` per il tipo `peso`
- `fonte_formato`: `{fonte, data}` — da dove viene `formato_g` e quando.
  `openfoodfacts:<ean>` · `ricerca` (una ricerca web, il formato modale fra i
  primi risultati) · `utente` (ha il pacco in mano: batte tutti) · `scontrino`
  (il formato che hanno dato davvero). Un formato senza questa riga e' un
  formato a memoria, e non esiste: la data serve perche' i produttori
  cambiano i tagli, e la fonte perche' un errore va corretto dov'e' nato
- `alias_scontrino`: sigle viste sugli scontrini, riconosciute ai giri dopo
- `prezzi`: serie storica, mai sovrascritta. L'ultimo elemento e' il corrente
- `fonte_nutrienti`: `openfoodfacts:<ean>`, `crea` se generico, oppure
  `etichetta` quando li ha letti l'utente sulla confezione — il dato di chi ha
  il pacco in mano vale quanto uno letto da OFF, perche' cio' che conta e' la
  provenienza dichiarata, non il canale. Un campo nutrizionale senza fonte non
  esiste

### dati/ricette.md — i piatti di questa casa

Il pool dei piatti e' **due file, non uno**: `kb/piatti.md` nel motore, uguale
per tutti, e `dati/ricette.md` nella cartella di casa, che e' vostro. Il menu
pesca dai due indifferentemente, e i piatti di casa entrano in rotazione,
prendono i voti e si escludono come gli altri.

```markdown
## Pasta con crema di zucchine e menta [meta] (B: pasta in bianco)
- kcal: 520 a porzione — dichiarate dalla fonte
- per 4: 320 g di pasta, 800 g di zucchine, mezzo mazzetto di menta, 60 g di grana
- fonte: me l'ha passata Marta
- nota: le zucchine vanno frullate calde
```

Le calorie seguono **la stessa regola dei prezzi**: `dichiarate dalla fonte`
(c'erano scritte) o `stimate CREA` (le ha calcolate Lunario dagli
ingredienti). Un valore dichiarato incerto vale; un numero senza provenienza
no — e in quel caso si stima e si dice che e' una stima.

Senza la riga `per N` il piatto non genera lista della spesa: quando la
ricetta arriva senza quantita', si chiedono, oppure si ricostruiscono dalle
porzioni standard e si dichiara che sono state ricostruite.

Chi scrive questo file: **lo scrive il sistema, su dettatura dell'utente**. E'
l'unica eccezione alla regola di confine, e regge perche' il contenuto e' suo
mentre la forma serve al motore. L'utente puo' sempre editarlo a mano.

### dati/dispensa.yaml — cosa e' rimasto

```yaml
aggiornata: 2026-08-14
avanzi:
  pasta-integrale-500: 400      # grammi residui
  ceci-lessati-400: 1           # pezzi interi per tipo `pezzo`
```

Solo prodotti non deperibili (fascia `[fine]` di `kb/deperibilita.md`). Il
fresco avanzato non e' un credito: e' immondizia fra tre giorni.

### dati/profilo.yaml — chi mangia, e quali pasti fa

```yaml
famiglia:
  - nome: Adulto1
    dieta: true              # false = mantenimento, nessun deficit
    altezza_cm: 175
    peso_kg: 76              # di PARTENZA: il corrente e' l'ultima pesata
    peso_obiettivo_kg: 70    # serve a sapere quando si passa a mantenimento
    kcal_giorno: 1650        # null se dieta: false
    pesata_settimanale: true # il postmortem chiede il peso, e si puo' saltare
    selettivo: false         # attiva la base neutra per questa persona
    pasti:                   # quali pasti fa di norma. Assente = casa
      spuntino: no
      merenda: no
  - nome: Bimbo1
    dieta: false
    kcal_giorno: null
    selettivo: true
    pasti:
      merenda: casa
titoli:
  serie: "canzoni dei Beatles"   # null = titolo descrittivo dai piatti
```

`titoli.serie` e' il filone da cui esce il nome della settimana — fiori, pesci
tropicali, costellazioni. Si sceglie una volta al setup e da' un filo alle
settimane: `lunario:menu` pesca l'elemento che risuona col menu quando ce n'e'
uno («Yellow Submarine» sulla settimana dei tre pesci) e altrimenti prosegue
nella serie, senza forzare agganci inventati.

Cosa e' gia' uscito **non si tiene in una lista a parte**: sta in
`storico.settimane[].titolo`, che e' l'unico posto dove i titoli vivono
davvero. Una seconda lista si disallineerebbe alla prima settimana cancellata,
esattamente come farebbe un elenco di piatti preferiti accanto ai voti.

I bambini sono persone della lista, non una sezione a parte: hanno un nome, i
loro pasti e la loro selettivita'. `selettivo` era `bambini.selettivi` ed era
un interruttore per tutta la casa — sbagliato appena i figli sono due e uno
mangia tutto.

### dati/ritmi.yaml — la griglia ricorrente

```yaml
settimana:
  martedi:
    Adulto2:
      pranzo: trasportabile         # gli stati della griglia dei pasti
      cena_entro_min: 25            # tempo reale ai fornelli quel giorno
  sabato:
    tutti:
      cena: libero                  # la pizza del sabato, senza conto
```

`tutti` vale per l'intera tavola e si scrive una volta sola. I valori
`fuori_trasportabile` e `fuori_autonomo` sono la vecchia grammatica: valgono
ancora in lettura, e `lunario:profilo` li converte in `trasportabile` e
`fuori` al primo aggiornamento.

### settimane/<ISO>/contesto.yaml — l'eccezione di questa settimana

Stessa grammatica di `ritmi.yaml`, ma vale una settimana sola e si sovrappone
ai ritmi. Effimero per design: non si accumula, non si impara.

```yaml
settimana:
  giovedi:
    tutti:
      cena: ristorante        # non si cucina, non si compra, ma si paga
  venerdi:
    Adulto1:
      pranzo: fuori
```

### dati/storico.yaml

```yaml
tarature:                  # stato appreso: letto SEMPRE prima di generare
  porzioni_g: {}           # per persona e alimento, default da kb/porzioni-standard.md
  piatti_esclusi: []       # media a tavola sotto 2 per due volte
  budget_settimana_eur: null
  voti:
    Pasta e ceci:
      cucina:              # da lunario:prepara, appena cucinato
        difficolta: 1      # 1-5
        minuti_reali: 25   # smaschera le ricette "da 20 minuti"
        voto_cuoco: 4      # 1-5, quanto e' venuto bene
        volte: 3
      tavola:              # da lunario:postmortem, dopo l'assaggio
        media: 4.3
        voti: [{data: 2026-08-17, chi: Bimbo1, voto: 3}]
settimane:
  - settimana: 2026-W34
    titolo: "La settimana dei legumi coraggiosi"
    menu: settimane/2026-W34.md
    spesa_stimata: 92.50
    spesa_reale: null      # SOLO il menu, dallo scontrino del ritiro
    spesa_extra_alimentare: null   # cibo comprato ma non previsto
    spesa_fuori_casa: null # ristorante, pizzeria, bar: alimentare, non spesa
    totale_scontrino: null # per memoria: include detersivi e non alimentari
    scarto_per_riga: []    # dove la stima ha sbagliato, non solo di quanto
    celle_disattese: []    # previsto casa, fatto fuori (o viceversa)
    avanzi: []
    note: ""
```

`spesa_fuori_casa` sta accanto agli altri e non dentro: mangiare fuori e'
spesa alimentare vera, ma non e' spesa di Lunario, e sommarla a `spesa_reale`
falserebbe il confronto con la stima. Serve a rispondere a una domanda sola,
che nessun altro campo risponde: **quanto e' costato mangiare, davvero**.

`celle_disattese` e' il dato che tara la griglia: tre giovedi' di fila
previsti a casa e finiti in pizzeria non sono sfortuna, sono un ritmo che
nessuno ha scritto.

Niente lista `piatti_preferiti` separata: la media di `tavola` la sostituisce
— sopra 4 e' un preferito, sotto 2 un bocciato. Due meccanismi paralleli si
disallineano, uno solo no.

## Come si parla con l'utente

Le skill che raccolgono informazioni — `lunario:profilo`, `lunario:settimana`,
`lunario:correggi` — sono **conversazioni, non moduli da compilare**. Il
registro e' quello di un nutrizionista di famiglia: competente sul merito,
per niente pedante, che ascolta prima di prescrivere.

- L'utente racconta come gli viene; le domande servono a colmare i buchi, non
  a riempire i campi di un file in ordine
- **Una domanda per volta.** Un questionario a raffica fa abbandonare al terzo
  campo. Quando le risposte possibili sono poche e discrete, offrirle come
  opzioni; quando serve il racconto, lasciare campo libero
- Non chiedere cio' che si puo' dedurre o e' gia' scritto nei file. Riproporre
  un dato gia' noto per conferma va bene una volta, non ogni settimana
- Chiudere sempre con un riepilogo breve di cio' che si e' capito, prima di
  scrivere qualsiasi file
- Il ruolo e' nutrizionale, **non medico**: consigli su porzioni ed equilibrio
  si', diagnosi e terapie mai. Sotto le 1200 kcal si rimanda al medico

### Le competenze, e quando affiorano

Il modello che esegue queste skill sa di nutrizione, di cucina e di economia
domestica molto piu' di quanto i file gli chiedano di usare. Quella competenza
va usata apertamente, con tre regole che non si negoziano:

- **Niente personaggi.** Gli esperti non hanno nomi, non si presentano, non
  dicono «come nutrizionista ti consiglio»: la competenza si dimostra nel
  contenuto del consiglio, mai nell'annuncio. Una frase in cui il sistema si
  celebra come esperto e' una frase da togliere
- **Ogni skill la sua.** Il nutrizionista affiora quando si compone la
  settimana e quando si legge un trend; il cuoco mentre si cucina; l'economo
  di casa davanti a uno scontrino. Trasversale a tutte c'e' chi sa che le
  diete falliscono per insopportabilita', non per matematica: difende il
  pasto libero, non compensa, non moralizza
- **Il giudizio si', i fatti no.** La competenza si esprime nello scegliere,
  ordinare, anticipare un problema — mai nell'inventare un dato. Un parere
  esperto costruito su un numero inventato vale meno di nessun parere, e le
  regole non negoziabili valgono anche per gli esperti

## Flusso operativo

### Generazione (lunario:menu)

1. Contesto: `profilo.yaml`, `ritmi.yaml`, `note.md`, `storico.yaml` (tarature
   e piatti delle ultime 2 settimane), `dispensa.yaml`, e il contesto della
   settimana (se manca, chiamare `lunario:settimana`)
2. **Risolvi la griglia** dei sette giorni: per ogni pasto e ogni persona,
   profilo → ritmi → contesto, vince il piu' specifico. Da qui in poi si
   lavora sulle celle risolte, non sui giorni: solo `casa`, `trasportabile` e
   `libero` ricevono un piatto e generano spesa
3. Menu: piatti da `kb/piatti.md` meno le esclusioni, ordine dei giorni da
   `kb/deperibilita.md`, porzioni da `kb/porzioni-standard.md` scalate su
   tarature e kcal di **chi mangia davvero quel pasto**. La griglia vincola
   PRIMA della scelta: una cella `trasportabile` non riceve un piatto da
   scaldare, una cella `libero` non riceve un piatto ipocalorico
4. Fabbisogno: per ogni ingrediente, grammi totali della settimana — contando
   colazioni, spuntini e merende, che sono celle come le altre
5. **Confezioni**: fabbisogno − dispensa → confezioni da comprare, secondo
   `kb/confezioni.md`. La lista dice «2 pacchi da 500 g», mai «1050 g»
6. Salva `settimane/<ISO>.md`, aggiorna `dispensa.yaml` con gli avanzi
   previsti, aggiungi la voce a storico con `spesa_stimata`

### Il ritiro della spesa (lunario:spesa)

Fra il menu e la prima cena c'e' un passaggio che non e' burocrazia: lo
scontrino dice cosa e' **davvero** entrato in casa. Si riconcilia con la lista,
si spunta cio' che e' arrivato, si scopre cosa manca — e per cio' che manca si
sostituisce subito con quello che c'e', o si ricorda di ricomprarlo.

Lo scontrino contiene anche cio' che con Lunario non c'entra: detersivi, casa,
roba comprata per altri. Va separato in tre gruppi — menu, alimentare fuori
lista, non Lunario — perche' **solo il primo e' la spesa che si confronta con
la stima**. Un budget sporcato dai detersivi non insegna niente.

E' anche il punto in cui la settimana passa da `preventivo` a `consuntivo`: da
qui in avanti il file non descrive piu' cio' che si voleva, ma cio' che c'e'.

### Il ciclo di vita del menu: preventivo e consuntivo

Un menu ha due stati, e la differenza non e' l'approvazione di qualcuno: e'
**quanto di cio' che c'e' scritto e' verificato**.

| stato | chi lo mette | cos'e' |
|---|---|---|
| `preventivo` | `lunario:menu`, appena generato | cio' che si vuole mangiare e comprare. Ogni numero e' una previsione: formati, prezzi, e i piatti stessi |
| `consuntivo` | `lunario:spesa`, dopo lo scontrino | cio' che c'e' davvero in casa: prodotti veri, formati veri, prezzi pagati, sostituzioni gia' applicate ai piatti |

**Ogni menu nasce `preventivo`** e ci resta finche' non passa dallo scontrino.
`lunario:correggi` lo modifica quante volte serve — le contestazioni di chi
mangia si raccolgono li' — ma non lo promuove: un menu discusso e un menu
approvato sono lo stesso documento con la stessa autorita', cioe' quella di una
stima.

Il «confermo» dell'utente resta un momento vero, ma vuol dire una cosa sola:
**sto andando a fare la spesa adesso**. Congela la lista per il tempo del
supermercato, scrive l'evento sul calendario se richiesto, e non cambia lo
stato. Non darlo mai per acquisito d'ufficio — il silenzio non e' approvazione,
tanto piu' che l'approvazione e' di altre persone che non stanno leggendo
questa chat.

La promozione a `consuntivo` avviene **solo in `lunario:spesa`**, ed e' il
momento in cui il file viene riscritto sui prodotti reali. E' l'unico evento
che sa dire se la lista era giusta: prima di lui, mettere un timbro di
definitivo su un totale fatto di prezzi della settimana scorsa e' una bugia
tipografica.

Il preventivo non si perde: `lunario:spesa` lascia in coda al consuntivo un
**delta leggibile** — cosa e' cambiato di formato, di prezzo, di piatto — perche'
lo scarto fra i due e' il dato che il postmortem confronta, e leggerlo non deve
richiedere un `git diff`. Se il consuntivo si scosta dal preventivo sempre nello
stesso verso per tre settimane — quel pacco e' sempre piu' grande, quel prodotto
non c'e' mai — non e' sfortuna, e' un paniere da correggere.

### Il calendario, nei due versi

**In lettura** e' automatico: se un calendario e' collegato, `lunario:settimana`
lo consulta per dedurre pranzi fuori e cene tardive, e propone gli impegni gia'
letti. Nei file di Lunario finisce solo il vincolo derivato, mai il titolo
dell'evento.

**In scrittura** non succede niente senza un si' esplicito. Se l'utente lo
vuole (`calendario.scrivi: true` nel profilo), alla conferma del menu compare
in agenda la settimana col suo titolo — «🌙 Impressioni di settembre» — e il
menu nella descrizione. Si chiede una volta sola, alla prima conferma, insieme
a **quale** calendario usare: mai il primario di default, perche' un calendario
di lavoro lo leggono i colleghi.

L'evento e' una comodita', non un pezzo del sistema: se fallisce, si dice e si
va avanti.

### Il menu e' anche lo stato di avanzamento

In `settimane/<ISO>.md` pasti e righe della spesa sono **caselle da spuntare**.
`lunario:prepara` le marca mentre si cucina: il pasto fatto esce dai candidati
del lancio successivo, gli ingredienti consumati spariscono da cio' che si
presume in casa.

Non serve un file di stato in piu': il menu **e'** lo stato, e si legge a
occhio. Ci si appoggiano `lunario:correggi`, che propone cosa e' rimasto invece
di chiederlo, e il postmortem, che corregge la dispensa sul consumo reale.

### Correzione in corsa (lunario:correggi)

A meta' settimana cambia qualcosa: una cena salta, un piatto non va, arriva un
ospite. **La spesa e' gia' fatta**: il vincolo non e' piu' il budget, e' cosa
c'e' in casa. Quindi si chiede cosa deve cambiare e cosa c'e' in frigo, si
rigenerano solo i **giorni residui** riusando gli ingredienti gia' comprati, e
si propone una spesa integrativa solo se e' inevitabile — poche righe, dette
come tali. I giorni gia' passati non si riscrivono mai.

### Postmortem (lunario:postmortem)

Quattro domande — avanzi, bocciati/promossi e da chi, la griglia che non ha
tenuto, spesa integrativa e mangiate fuori — poi ritara:
- stesso avanzo per 2+ settimane -> riduci la porzione in `tarature`
- piatto bocciato 1 volta -> fuori rotazione 3 settimane; 2 volte -> escluso
- stessa cella disattesa per 3 settimane -> non e' sfortuna, e' un ritmo:
  proponi di scriverlo in `ritmi.yaml`. Proponi, non scrivere
- ristorante e pizzeria -> `spesa_fuori_casa`, mai dentro `spesa_reale`
- scontrino PDF -> prezzi in `prodotti.jsonl`, `spesa_reale` e
  `scarto_per_riga` in storico, dispensa corretta sul reale

### Note operative

`dati/note.md` contiene i vincoli liberi non riducibili a un orario («forno
guasto»). Lette a ogni lancio, applicate prima di ogni altra scelta. In chat
«segnati che ...» le aggiunge (temporanee con `[fino al AAAA-MM-GG]`). Una
nota non e' una taratura: la tocca solo l'utente, la skill puo' solo proporre.

## Regole non negoziabili

- Mai piani sotto 1200 kcal/giorno/persona, e mai un deficit a chi ha
  `dieta: false`: quella persona mangia standard, e il peso non si nomina
- Mai commentare il corpo di qualcuno, nemmeno per complimento: delle pesate
  si legge il trend su tre settimane, mai la singola misura, e chi salta la
  domanda non riceve insistenze
- Un pasto `libero` non si compensa altrove, ne' prima ne' dopo
- Colazioni, spuntini e merende contano nelle kcal e nella spesa come i pasti
  principali: un pasto fuori dal conto e' un target sbagliato
- Mai prodotti, formati, prezzi o valori nutrizionali inventati: cio' che non
  e' in `prodotti.jsonl`, in Open Food Facts o nelle tabelle CREA si dichiara
  mancante e si marca `[da verificare]`
- Mai un prezzo senza data: un prezzo vecchio dichiarato tale vale, un prezzo
  senza provenienza no
- Esclusioni alimentari del profilo valgono anche come ingrediente nascosto
- La lista della spesa e' in confezioni, mai in grammi astratti
- Output terso: menu, lista, totale, stop. kcal arrotondate alle decine

## Note tecniche

- Python: **zero dipendenze esterne**, solo stdlib (`urllib`). Niente venv da
  creare, niente `pip install`: il plugin funziona appena installato
- Open Food Facts: API pubblica senza chiave, licenza ODbL (va citata).
  Loro chiedono «1 API call = 1 real scan»: interrogare per prodotto e
  mettere in cache, mai in bulk. Il dump completo non serve a questo sistema
- Due endpoint diversi, e non e' un dettaglio (verificato 2026-08-14):
  il lookup per codice a barre sta su `world.openfoodfacts.org/api/v2` ed e'
  stabile; la ricerca per nome sta su `search.openfoodfacts.org` perche' gli
  endpoint di ricerca del dominio principale rispondono 503 con continuita'.
  La ricerca non restituisce il formato della confezione: serve un secondo
  giro per codice. E filtra per `lang:it`, non per paese, che azzera i risultati
- Rate limit: OFF risponde 429 se la si incalza. `off_lookup.py` mette una
  pausa di 1 s tra le richieste e riprova una volta sola
- Scontrini PDF: letti con la skill `read-document`, nessun parser da scrivere
- `dati/` e `settimane/` sono gitignored: il repo resta pulito da dati personali
- La cartella dei dati si puo' spostare con `LUNARIO_DATI=/percorso`; senza,
  e' `dati/` nella cartella di lavoro
- L'evoluzione futura — dati su un server di casa, MCP in combo con le skill,
  uso condiviso dalla famiglia — e' pianificata ma non in corso: rotta,
  vincoli e tappe in `docs/piano-server.md`
