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
| il `contesto.yaml` della settimana | l'override di **questa settimana** | «giovedi' cena al ristorante» |

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
| `lunario:settimana` | effimero | `settimane/<ISO>-<titolo>/contesto.yaml`, `dati/ricette.md`, `dispensa.yaml` (la fetta contata del lunedi'), `storico.yaml` → `piatti_in_quarantena` | ogni lunedi' |
| `lunario:menu` | — (consuma tutto) | nella cartella della settimana: `-preventivo.md` + `.html` e `-lista.md`; `dati/dispensa.yaml` | ogni lunedi' |
| `lunario:spesa` | appreso (prezzi) | `-consuntivo.md` + `.html` (**accanto** al preventivo, mai sopra), `dati/prodotti.jsonl`, `dispensa.yaml`, `storico.yaml` | al ritiro della spesa |
| `lunario:prepara` | appreso (cucina) | `dati/storico.yaml` → `voti.<piatto>.cucina`, il `diario.yaml` della settimana, le caselle dei pasti sul documento vivo | mentre si cucina |
| `lunario:correggi` | effimero | il documento vivo (giorni residui) e il diario della settimana | quando cambia qualcosa |
| `lunario:postmortem` | appreso (tavola, pesate) | `dati/storico.yaml`, e `-postmortem.md` nella cartella della settimana | domenica |
| `lunario:inventario` | contato | `dati/dispensa.yaml` → `scorte` e `freezer` | una volta, poi quando si rifa' il giro |
| `lunario:aggiorna` | — (allinea i livelli al contratto) | `dati/versione.yaml`, e i file che il salto di contratto tocca | quando il motore e la cartella non combaciano |
| `lunario:tagliando` | — (rimette a posto la forma) | i file spostati o rinominati, e cio' che l'utente approva di correggere nei dati | quando qualcosa non torna, e dopo un aggiornamento del motore |

L'utente ne invoca quattro tutte le settimane: `lunario:settimana` il lunedi',
`lunario:spesa` quando ritira la spesa, `lunario:prepara` quando cucina e
`lunario:postmortem` la domenica. `lunario:inventario` si invoca una volta e
poi quasi mai. `lunario:menu` viene chiamata dalla prima e non va invocata a
mano; le altre servono quando serve.

**`aggiorna` e `tagliando` non sono la stessa skill**, e confonderle rimette in
piedi il difetto che il tagliando esiste per togliere: la prima esegue **il
salto di contratto**, un passo per volta, e guarda un numero; la seconda parte
**dai file** e trova anche cio' che nessun salto sistemerebbe — una settimana
nella forma vecchia dentro una cartella col timbro giusto, un documento con un
nome che nessuna skill aprira', una scorta senza data. Un numero allineato non
dice niente su dove stiano i file.

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
│   ├── skills/                      # profilo · ritmi · inventario
│   │   └── ...                      # settimana · menu · spesa · prepara
│   │                                # correggi · postmortem · aggiorna · tagliando
│   ├── kb/                          # knowledge base condivisa
│   │   ├── porzioni-standard.md     # porzioni e frequenze CREA 2018
│   │   ├── deperibilita.md          # ordine dei giorni, durate in frigo
│   │   ├── confezioni.md            # grammi -> confezioni, dispensa, avanzi
│   │   ├── consigli-pratici.md      # bimbi selettivi, batch cooking, €/proteine
│   │   ├── scorte.md                # bande, fiducia, conteggio ciclico
│   │   └── piatti.md                # pool piatti taggato per deperibilita'
│   ├── scripts/
│   │   ├── off_lookup.py            # Open Food Facts -> dati/prodotti.jsonl
│   │   ├── settimana.py             # dove stanno i file di una settimana, e qual e' il vivo
│   │   ├── versione.py              # il timbro della cartella, e come si deduce
│   │   ├── lint_dati.py             # i contratti dati: la verifica, non i test
│   │   ├── minyaml.py               # il sottoinsieme YAML, con la sola stdlib
│   │   └── tagliando.py             # contratto + forma + dati, e cosa si ripara
│   └── templates/                   # modelli commentati, copiati al setup
├── tests/                           # i tre tier, e tre case sintetiche
│   ├── loop_runner.py               # tier 2: il giro intero headless
│   ├── giudizio.py                  # tier 3: un parere, non un semaforo
│   └── fixtures/                    # single · famiglia · coppia-dispensa-profonda
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
│   ├── dispensa.yaml         # scorte contate, avanzi calcolati, congelatore
│   └── storico.yaml          # settimane e tarature
└── settimane/                # una cartella per settimana: <ISO>-<titolo>
```

Dentro le skill, i file del motore si citano con `${CLAUDE_PLUGIN_ROOT}/kb/...`
perche' il plugin, una volta installato, vive fuori dal progetto. I file di
`dati/` e `settimane/` sono invece relativi alla cartella di lavoro, e
`LUNARIO_DATI` permette di spostarli altrove.

### La settimana e' una cartella

Ogni settimana ha un titolo, ed e' l'unico appiglio che un essere umano usa
davvero: in un'altra chat, al telefono, due mesi dopo, nessuno dice «apri
2026-W34», dice «Commando». Quindi il titolo sta nel nome della cartella,
dopo l'ISO — e **tutta la settimana sta li' dentro**:

```
settimane/2026-W34-commando/
├── 2026-W34-commando-preventivo.md      # i sette giorni, come si voleva
├── 2026-W34-commando-preventivo.html    # la copia leggibile, da frigo
├── 2026-W34-commando-lista.md           # la spesa, sola: si annota e torna
├── 2026-W34-commando-consuntivo.md      # cosa c'e' davvero in casa
├── 2026-W34-commando-consuntivo.html
├── 2026-W34-commando-postmortem.md      # com'e' andata, cosa si e' cambiato
├── contesto.yaml
└── diario.yaml
```

**Nomi interi, non `preventivo.md` nudo**: un file scaricato sul telefono o
allegato a un messaggio perde la cartella e resta col suo nome soltanto, e
`preventivo.md` a quel punto non dice di quale settimana sia.

L'ISO resta davanti, e vale la pena difenderlo: l'ordine alfabetico continua a
essere l'ordine cronologico, e il motore trova una settimana senza conoscerne
il titolo. La chiave in `storico.yaml` resta l'ISO nudo; lo slug e' una
comodita' per gli occhi aggiunta sopra l'identificatore, non al posto suo.

Lo slug: minuscolo, accenti tolti, tutto cio' che non e' lettera o cifra
diventa `-`, niente `-` doppi ne' in testa o in coda. I titoli sono corti per
costruzione — vengono da una serie — quindi non serve troncare niente.

Il titolo nasce in `lunario:menu`, e il contesto e' gia' su disco quando
arriva: `lunario:settimana` crea `settimane/<ISO>/`, e il menu **rinomina la
cartella** appena ha il titolo. E' l'unico rename previsto dal sistema, e
avviene prima che qualcuno abbia visto un nome.

**Da li' in poi il nome si fissa e non cambia piu'.** Rinominare vuol dire
spostare la cartella, sei documenti e qualsiasi link che ci puntava:
`lunario:correggi` non lo fa mai, nemmeno se cambia il menu.

#### Qual e' il documento vivo

Preventivo e consuntivo sono **due file, non uno stato che si sovrascrive** —
il perche' sta piu' sotto, in «Il ciclo di vita del menu». Ne discende una
domanda che va risolta una volta sola: a meta' settimana, **su quale si
scrive?**

> **Il vivo e' l'ultimo ruolo che esiste su disco**: se c'e' il consuntivo e'
> quello, altrimenti il preventivo.

Nessuna data da confrontare, nessuno `stato:` da interpretare. `prepara`
spunta li', `correggi` riscrive li', il postmortem legge li'. Spuntare il file
sbagliato non da' nessun errore: da' una settimana raccontata in un documento
che nessuno riaprira'.

Chi lo risolve non e' il modello a mente, e' uno script:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/settimana.py
```

Stampa la cartella, i documenti che ci sono e la riga `vivo:`. La stessa
funzione la usano i test, cosi' non esistono due idee di dove stiano i file.

#### Le settimane scritte prima

Fino al contratto 3 markdown e HTML stavano **accanto** alla cartella, in un
file solo che si riscriveva da preventivo a consuntivo, e le piu' vecchie si
chiamavano `2026-W34.md`, senza titolo. **Restano dove sono e come sono**: lo
script le riconosce (`layout: piatto`), il file vivo e' quell'unico markdown, e
non si rinominano d'ufficio. Una settimana passata e' un registro, e un
registro non si riorganizza per farlo somigliare al presente.

Un'eccezione sola, e si **chiede**: la settimana **ancora da vivere**. Se il
motore si aggiorna di mercoledi', quella settimana la si sta ancora vivendo e le
manca la lista, cioe' la ragione per cui questo contratto esiste — quindi
`lunario:aggiorna` e `lunario:tagliando` propongono di spostarla, e su un si':

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/settimana.py --adatta
```

Sposta markdown e HTML nella cartella col nome del ruolo, dedotto dallo
`stato:` in testa (vecchio vocabolario compreso), e sistema il `menu:` in
`storico.yaml`. **Si rifiuta di toccare qualunque settimana che non sia quella
in corso o quella che sta per aprire**, ed e' cio' che rende sicuro proporlo: da
li' il registro non e' raggiungibile. La lista non la inventa — una spesa gia'
fatta non si ricostruisce — la scrive il prossimo giro di `menu` o `correggi`.

Le settimane adattabili sono **due**, e la seconda non e' una concessione: una
settimana **si pianifica prima di viverla**. Il menu esce per i sette giorni che
cominciano, e la spesa si ritira prima di accendere i fornelli — quindi chi
lavora di sabato o di domenica ha su disco una settimana che l'ISO di oggi non
nomina ancora, ed e' proprio quella a cui manca la lista. Un confronto con la
sola ISO corrente rifiutava il caso normale del sistema.

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

## La cartella si aggiorna da sola

Il motore si installa e si aggiorna dal marketplace come qualsiasi plugin;
`dati/` e `settimane/` restano esattamente come li ha lasciati la versione
precedente. Finche' nessuna skill sapeva **contro quale contratto** erano stati
scritti i file che stava leggendo, nessuna poteva adattarli — e ogni modifica
al contratto era una rottura latente in ogni cartella gia' in uso.

### Il timbro

```yaml
# dati/versione.yaml — lo scrive il sistema, mai l'utente
contratto: 4
motore: 5.0.0        # la versione del plugin che l'ha toccata per ultima
migrata: 2026-08-16
```

`contratto` e' il numero che conta, e **si muove solo quando si muove il
contratto dei dati**, non a ogni release del plugin. `motore` serve a chi apre
una cartella fra sei mesi e vuole sapere chi l'ha scritta.

Le cartelle nate prima che il timbro esistesse non ce l'hanno: la prima
migrazione **deduce il contratto dalla forma dei file** — la grammatica della
griglia in uso, quali sezioni ha `dispensa.yaml`, come si chiamano le settimane
— e scrive il timbro. Da li' in poi il timbro si legge, e non si indovina piu'.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/versione.py --controlla
```

### Il controllo e' automatico, non una skill da ricordarsi

Ogni skill, appena parte, guarda com'e' messa la cartella. Se c'e' qualcosa che
blocca, lo ripara **prima** di fare qualsiasi altra cosa, e poi prosegue col
compito che l'utente ha chiesto davvero. Una skill di manutenzione che bisogna
invocare a mano e' una skill che non invoca nessuno.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tagliando.py --rapido
```

**Guarda i file, non solo il numero**, e questa e' la correzione di un difetto
che il timbro da solo aveva: il controllo del contratto confronta due interi, e
due interi uguali zittivano tutto il resto. Una cartella col timbro giusto e i
documenti nella forma vecchia passava a **ogni** lancio, per sempre — e il caso
piu' comune e' il piu' fastidioso: la settimana in corso senza la sua lista
della spesa, che nessuno guardera' mai piu' perche' il numero e' a posto.

Tre verifiche, in un posto solo:

| cosa guarda | da dove viene | esempio di cio' che trova |
|---|---|---|
| il **contratto** | `versione.py` | la cartella e' al 3, il motore vuole il 4 |
| la **forma** | `settimana.py` | W34 ha i documenti fuori dalla cartella, e le manca la lista |
| i **contratti dati** | `lint_dati.py` | un prezzo senza data, una scorta senza `visto`, uno YAML che il motore non sa rileggere |

Il rapido stampa **solo cio' che blocca**, e quando non c'e' niente non stampa
niente: e' il controllo che gira mentre l'utente aspetta di cucinare, e un
elenco di difetti li' non e' aiuto, e' una skill che non parte mai. Il resto si
conta in una riga e lo guarda `lunario:tagliando`, quando c'e' tempo.

**Cio' che si ripara da solo e' solo cio' che e' meccanico** — spostare un file,
scrivere un timbro, sistemare un percorso. Un file di dati e' pieno di commenti
scritti per un essere umano, e uno script che lo riscrive li perde: quelli li
sistema la skill, che legge prima di scrivere e mostra la riga prima di
cambiarla.

La logica di migrazione vive tutta in `lunario:aggiorna`, in un posto solo:
duplicata in dieci skill, divergerebbe. I passi sono **dichiarativi e
idempotenti** — uno per salto di contratto, sicuri da applicare due volte. La
cartella e' un repo git, quindi ogni migrazione committa, e l'annullamento e'
`git`, non uno schema di backup.

### Tre tipi di cambiamento, tre comportamenti

E' la parte che impedisce a una migrazione di diventare un'intervista.

| tipo | esempio | comportamento |
|---|---|---|
| **additivo** | una sezione nuova e vuota (`scorte`) | si applica **in silenzio**: non c'e' niente da chiedere |
| **riscrittura** | `fuori_trasportabile` → `trasportabile` | si applica da sola e si **riporta in una riga**; l'annullamento e' `git` |
| **serve l'utente** | `titoli.serie`, i nomi dei bambini | **non si applica niente**: il campo resta assente, la cartella funziona lo stesso, e la skill giusta lo **propone** al momento buono |

La terza riga porta la regola vera, ed e' un vincolo di progetto su tutto cio'
che verra' scritto da qui in avanti:

> **Ogni contratto nuovo deve degradare bene quando manca.**

Una cartella che non migra mai deve continuare a funzionare. La migrazione
**migliora** una cartella; non e' mai il prezzo del biglietto.

### Cosa non si migra

- **Il contenuto di `settimane/`, e nemmeno la loro disposizione.** Le settimane
  passate sono un registro, non dati vivi: si leggono come sono, dove sono. Un
  vecchio `stato: bozza` o `confermato` si **legge** come `preventivo`, un `in
  corso` come `consuntivo` — nella testa di chi legge, non nel file. E quelle
  scritte quando markdown e HTML stavano accanto alla cartella restano li': lo
  script che risolve i percorsi le trova comunque, e spostarle vorrebbe dire
  muovere due file, il `menu:` che ci punta in `storico.yaml` e ogni link gia'
  mandato a qualcuno. Vale **anche per la settimana in corso**, che e' il caso
  a cui viene voglia di fare un'eccezione: migrare un documento mentre qualcuno
  ci sta cucinando sopra e' la sorpresa che questo meccanismo esiste per non fare
- **Niente percorso all'indietro.** Una cartella portata avanti e poi aperta da
  un motore piu' vecchio e' fuori perimetro: il motore vecchio ignora cio' che
  non conosce, che e' esattamente il comportamento giusto
- **Nessun backup proprio.** La cartella e' un repo git: quello e' il backup

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
- `prezzi`: serie storica, mai sovrascritta. L'ultimo elemento e' il corrente.
  `eur` e' il prezzo **della confezione** per i tipi `confezione` e `pezzo`, e
  il prezzo **al chilo** per il tipo `peso` — che al banco e' l'unica lettura
  che vuol dire qualcosa
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

### dati/dispensa.yaml — cosa c'e' in casa

```yaml
aggiornata: 2026-08-16

scorte:
  # Cio' che la casa TIENE in casa. Contato grossolanamente, rivisitato a
  # rotazione. Chiave = id in dati/prodotti.jsonl quando c'e', testo libero se no.
  pasta-integrale-500:
    quantita: 4              # confezioni intere, oppure una banda:
                             # pieno | medio | poco | finito
    soglia: 2                # sotto, torna in lista della spesa
    massimo: 6               # sopra, non si compra piu': e' il tetto
    visto: 2026-08-16        # quando un essere umano l'ha confermata
    rotazione: alta          # alta|media|bassa: ogni quanto rivisitarla
  passata-700:
    quantita: poco
    soglia: 3
    visto: 2026-07-04        # vecchia: la fetta del lunedi' la chiedera'

avanzi:
  pasta-integrale-500: 400      # grammi residui, per il tipo `confezione`
  uova-6: 4                     # pezzi interi, per il tipo `pezzo`

freezer:
  - cosa: filetti di branzino
    pezzi: 2
    grammi: 250                 # per pezzo, quando conta
    dal: 2026-06-12             # quando e' stato congelato, se si sa
    da_smaltire: true           # e' li' da troppo: il menu lo tira fuori
  - cosa: petto di pollo a fette
    grammi: 600
```

Tre sezioni, e sono tre cose diverse — confonderle e' il modo piu' rapido di
avere un inventario di cui non ci si fida piu':

| sezione | chi lo sa | precisione | quanto dura |
|---|---|---|---|
| `scorte` | l'ha **contato** un essere umano | grossolana, a bande | mesi: e' la dotazione di casa |
| `avanzi` | l'ha **calcolato** il motore: comprato meno consumato | precisa, in grammi | una settimana o due |
| `freezer` | l'ha **visto** l'utente aprendo lo sportello | pezzi e grammi, con la data | finche' non si cucina |

`freezer` non ha un `id` di prodotto perche' spesso non ce l'ha — «mezzo
scamone» non e' una riga del paniere — e porta invece la data di congelamento,
che e' il dato con cui si decide cosa esce per primo.

#### Le scorte, e perche' sono volutamente imprecise

Prima che `scorte` esistesse, una casa con cinquanta prodotti fissi non aveva
dove metterli, e li ridichiarava a memoria ogni lunedi': una prova di memoria
su cinquanta voci restituisce meta' risposta, tutte le volte.

Due errori opposti, e chiedono due precisioni diverse — l'asimmetria e' la
licenza a non costruire un magazzino:

- **compro quello che ho gia'** → serve una quantita' approssimativa, per
  scalare il fabbisogno
- **il quinto pacco della stessa cosa** → serve solo `massimo`. E' l'errore che
  nessuno nota, e si risolve col dato piu' grezzo che esista

`quantita` accetta un numero **oppure** una banda, e il motore legge quella che
trova senza convertirla di nascosto nell'altra.

**La fiducia non si scrive: si calcola** da `visto`, da `rotazione` e da quanto
il menu di quella settimana si appoggia a quella riga — fresca, invecchiata,
stantia. La tabella completa sta in `${CLAUDE_PLUGIN_ROOT}/kb/scorte.md`. Il
motore non deve avere ragione: deve **sapere quanto e' vecchia la sua
convinzione**, perche' il consumo si osserva solo dove passa `lunario:prepara`,
e la deriva ha una direzione prevedibile — il consumo e' sotto-registrato,
quindi il motore crede di avere piu' di quello che c'e'.

**Chi muove le scorte, e chi no.** `spesa` incrementa da cio' che e' entrato,
`prepara` decrementa cio' che ha davvero cucinato, `postmortem` corregge sul
consumo reale. **`menu` non le tocca**: le legge per calcolare la lista, ma un
piano non consuma niente — se scaricasse anche lui, una settimana mai cucinata
lascerebbe la dispensa piu' vuota del vero, e insieme a `prepara` scaricherebbe
due volte la stessa scatola.

E **il movimento automatico non promuove mai una riga a «contata»**: si muove
`quantita` come stima e **non si tocca `visto`**, perche' solo un conteggio
umano azzera l'eta' del dato. Altrimenti una dispensa piena di numeri derivati
sembrerebbe appena contata.

**Lo stesso oggetto sta in una sezione sola.** Un pacco di surgelati e' insieme
un prodotto del paniere e una cosa che si vede nel congelatore: scritto in
`scorte` **e** in `freezer` verrebbe sottratto due volte. Vale la precedenza
`freezer` > `scorte` > `avanzi`, e chi scrive non duplica
(`${CLAUDE_PLUGIN_ROOT}/kb/scorte.md`).

**Solo non deperibili**, in tutte e tre le sezioni: la fascia `[fine]` di
`kb/deperibilita.md`. Il fresco avanzato non e' un credito, e' immondizia fra
tre giorni.

Un piatto costruito su una riga di `freezer` **cancella la riga della spesa
corrispondente**, e la cancellazione va detta: un banco pesce quasi vuoto e'
sospetto finche' non si sa perche'. E porta un vincolo che il menu deve
stampare: **lo scongelamento**. Una bistecca vuole 12-24 ore in frigo, dei
filetti 8-12: un surgelato previsto per domenica sera e ricordato domenica
pomeriggio e' una cena che non avviene, ed e' l'unico pezzo di settimana che
il giorno stesso non si recupera.

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
preferenze:
  max_pasti_pesce_settimana: {valore: 2, rigidita: preferenza}
  max_pasti_carne_settimana: {valore: 3, rigidita: preferenza}
  max_carne_rossa_settimana: 1   # intero nudo = vincolo
tolleranze:
  ripetizioni:
    stessa_proteina_nel_giorno: false   # carne a pranzo E a cena
    stesso_piatto_nel_giorno: false     # l'avanzo di mezzogiorno la sera
    stesso_ingrediente_dopo_giorni: 2
  avanzi:
    tutti: come_sono             # come_sono | trasformati | mai
    bambini: trasformati         # la riga piu' stretta vince
  spesa_per_altri: false         # una seconda lista che viaggia con la spesa
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

#### I tetti, e quanto sono tetti

`max_pasti_pesce_settimana: 2` scritto come numero nudo si legge come una
regola, e il motore ci pianifica contro. Per molte case e' invece una
**preferenza**: in condizioni normali tiene, ma se nel congelatore c'e' roba
che invecchia, l'economia domestica vince, il tetto si supera apposta e lo si
dice in mezza riga. Sono due comportamenti opposti, e il file deve saperli
distinguere.

| forma | come si legge |
|---|---|
| `max_pasti_carne_settimana: 3` | **vincolo**: non si supera |
| `{valore: 3, rigidita: preferenza}` | si supera quando c'e' una ragione, e la ragione si dichiara |
| `{valore: 3, rigidita: vincolo}` | come l'intero nudo, ma detto apposta |

Il numero nudo resta valido e vale `vincolo`: e' il default conservativo, e un
profilo vecchio non cambia comportamento perche' e' uscita una versione nuova.

#### Le tolleranze

Sono le regole di tavola che nessuno dichiara e che si scoprono correggendo un
menu gia' scritto. Tutto cio' che non e' stato chiesto vale il **default
conservativo** — niente ripetizioni, avanzi solo trasformati per i bambini —
perche' un menu che ripete un ingrediente e' un menu che si fa correggere.

- `ripetizioni` — la stessa proteina a pranzo e a cena, lo stesso piatto due
  volte in un giorno, ogni quanti giorni un ingrediente puo' tornare
- `avanzi` — se tornano in tavola, e se ci tornano **come sono** o solo
  **trasformati** in un'altra forma un altro giorno. La riga dei bambini e'
  quasi sempre la piu' stretta, e vince su quella generale
- `spesa_per_altri` — se ogni settimana viaggia con la spesa una seconda
  lista per qualcun altro. Se `true`, quella roba resta **fuori da ogni
  totale**, dal paniere e dalla dispensa: non e' cibo di questa casa

#### Dove va scritta una risposta

Una casa impara cose su di se' a ogni menu, e il posto dove finiscono decide
se serviranno ancora fra sei mesi. Una domanda sola:

> **Il motore deve controllarlo da solo?**

| risposta | file | esempi |
|---|---|---|
| **si**, e' un campo che filtra o conta | `dati/profilo.yaml` | esclusioni, tetti e rigidita', ripetizioni vietate, spesa per altri |
| **no**, ma va letto prima di generare | `dati/note.md` | l'hummus si compra pronto, la merenda dei bimbi e' salata, niente integrale |
| **no**, e' per l'umano che apre la cartella | il `CLAUDE.md` di casa | come si lancia una skill, cos'e' la griglia dei pasti |

Il `CLAUDE.md` generato e' il posto **sbagliato** per una regola di casa, e la
seconda ragione conta piu' della prima: quel file lo scrive il plugin, quindi
una regola dell'utente ci sta a un aggiornamento dal trovarsi in un file che
non e' suo; e una regola scritta in prosa non si puo' chiedere al setup, ne'
riproporre quando la vita cambia, ne' ritarare al postmortem. Diventa un testo
che qualcuno deve ricordarsi di rileggere, che e' esattamente il fallimento da
cui nasce questa sezione.

C'e' un quarto caso, facile da mancare: quando cio' che sembra una stranezza
di casa e' invece un **difetto del motore** — «il menu esce disordinato»,
«non mi ha mai chiesto cosa avevo nel congelatore» — non va in nessuno dei tre
file. E' una issue sul plugin.

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

### <nome>-lista.md — la spesa, e l'unico file che torna indietro

Tutti gli altri documenti li scrive il sistema e li legge l'utente. Questo va
nel verso opposto: l'utente lo apre al supermercato, lo spunta, ci scrive
sopra, e al ritorno `lunario:spesa` rilegge **lo stesso file**. Non e' una
comodita' di formato: e' **un ingresso di dati**, e prima non c'era.

Un file solo, la sola spesa, niente menu dentro:

```markdown
# Spesa — 2026-W34 Commando
preventivo del 2026-08-17 · spunta col dito, annota accanto: rileggo tutto io

## Ortofrutta
- [ ] Zucchine — 1,5 kg
      → mer cena · gio cena
- [x] Rucola — 2 buste da 100 g      non c'erano, prese 2 da 70 g

## Fuori Lunario
- [ ] detersivo lavastoviglie
```

- **i reparti nell'ordine in cui si gira il negozio**, e sotto ogni riga i
  pasti che la usano: al banco e' cio' che dice cosa salta se manca
- **la casella vuol dire preso**, e niente altro. Non «consumato», non
  «arrivato in casa». Una casella con due significati e' una casella di cui non
  si fida piu' nessuno
- **«Fuori Lunario» in coda**, in una sezione sua: cio' che si compra comunque
  e che il motore non pianifica, compresa la spesa che viaggia per un'altra
  casa. In markdown il colore non esiste, e una sezione separata dice da sola
  cosa il motore deve ignorare — sopravvive a qualsiasi app la apra
- **le annotazioni sono testo libero**, in linea, dopo la riga. Nessuna sintassi
  da imparare, e non deve essercene una: chi scrive ha una mano sola e uno
  scaffale davanti

Come si legge un'annotazione sta in `lunario:spesa`, e la regola che conta e'
la gerarchia di fiducia: **l'annotazione vince su quale prodotto e' entrato in
casa** — l'utente era li' — **lo scontrino vince su quanto e' costato**, che e'
stampato. Una frase che non si classifica non si interpreta: si chiede una
volta.

Il file **non si riscrive**: e' il documento che l'utente ha annotato in piedi,
ed e' la prova di cosa e' successo quel giorno.

**Perche' non l'HTML.** C'e' stata una versione in cui la lista si spuntava sul
telefono e le spunte vivevano in `localStorage`. Funzionava, ed era inutile:
quelle spunte restavano nel browser di quel telefono, `lunario:spesa` non le
vedeva mai, e chi le faceva credeva di aver detto qualcosa al sistema. E' la
stessa regola gia' scritta per il consuntivo — uno stato dentro una pagina e'
invisibile alle skill, e lo e' **in silenzio**.

Che il file arrivi sul telefono e' una proprieta' della **cartella**, non del
formato: se `settimane/` sta in un servizio sincronizzato — iCloud, Dropbox,
Drive, Nextcloud, Syncthing si equivalgono — la lista si apre con un qualsiasi
editor markdown. Non c'e' niente da installare e niente da esportare, e **una
cartella non sincronizzata funziona identica**: la lista si legge dal computer.
Se qualcuno chiede cosa mettere in sincronizzazione, la risposta e' `settimane/`
e non tutta la cartella di casa: in `dati/` ci sono pesi e obiettivi.

### settimane/<ISO>-<titolo>/contesto.yaml — l'eccezione di questa settimana

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

### settimane/<ISO>-<titolo>/diario.yaml — cosa si e' mangiato davvero

Il contesto dice cosa **doveva** succedere; il diario dice cosa e' successo, e
si riempie **giorno per giorno**, non ricostruito la domenica.

```yaml
2026-08-19:
  pranzo:
    previsto: Piadina con hummus e verdure grigliate
    reale: la nonna ha portato le lasagne
    stato: disattesa
  cena:
    previsto: Cous cous con verdure e ceci
    reale: Cous cous con verdure e ceci
    chi: [Adulto1, Adulto2, Bimbo1, Bimbo2]
    avanzo: meta' teglia          # solo se c'e': e' un fatto di martedi'
```

`stato` si scrive **solo quando qualcosa e' andato storto** — `disattesa`
(previsto a casa, finito altrove, o viceversa), `saltata` (non si e' mangiato
quel pasto). Il silenzio vuol dire «come previsto», che e' il caso normale e
non merita una riga di conferma.

Scriverci non deve mai essere un modulo: una frase in chat — «stasera niente
polpette, pizza d'asporto», «Anna ha mangiato solo la pasta» — e' tutta
l'interazione, e `lunario:prepara` chiude il pasto da solo a fine cottura,
quando la conversazione c'e' gia'.

Vale la stessa regola di riservatezza del contesto: **il vincolo derivato, mai
il racconto**. «Cena fuori», non con chi.

**Un diario vuoto deve degradare bene.** Nessuno lo compilera' tutti i giorni,
e un postmortem che rimprovera i buchi e' un postmortem che si smette di fare:
un pasto senza voce si chiede la domenica, esattamente come oggi.

#### I sospesi — quello che manca e si prende dopo

Al ritiro della spesa un ingrediente puo' non esserci, e gli esiti sono due:
**si sostituisce** — e allora il piatto cambia, il consuntivo lo dice e non
resta niente in aria — oppure **si rimanda**, perche' l'utente se lo procura
prima del giorno in cui serve.

Solo il secondo ha bisogno di un posto dove stare. Detto in chat e basta, il
rimando muore con la chat: il giovedi' `lunario:prepara` fa cucinare un piatto
convinta che il branzino sia in casa.

```yaml
sospesi:
  - cosa: filetti di branzino
    prodotto: branzino-filetti-250     # l'id del paniere, quando c'e'
    serve:
      - {giorno: 2026-08-20, pasto: cena}
    stato: da_procurare                # da_procurare | procurato | rinunciato
```

Sta nel diario perche' e' **effimero come la settimana**: nasce allo
scontrino, muore la domenica, e le tre skill che devono saperlo — chi cucina,
chi corregge, chi chiude — quel file lo aprono gia'.

| stato | vuol dire | chi lo scrive |
|---|---|---|
| `da_procurare` | non e' in casa, e serve entro il primo giorno di `serve` | `lunario:spesa` |
| `procurato` | e' entrato in casa dopo | `lunario:prepara`, o `correggi` se l'utente lo dice |
| `rinunciato` | non e' arrivato: il piatto e' cambiato o saltato | chi ne prende atto |

Uno `stato` assente vale `da_procurare`, che e' lo stato in cui la voce nasce.

**Un sospeso non e' una scorta.** Finche' e' `da_procurare` non entra in
`dispensa.yaml` da nessuna parte: non c'e'. Una dispensa che conta cio' che
qualcuno ha promesso di comprare e' peggio di una dispensa vuota, perche' il
menu del lunedi' ci si appoggia. Ci entra quando diventa `procurato`, con le
regole di sempre.

E non e' nemmeno una lista della spesa: non si ripropone ogni volta e non si
insiste. Si nomina **il giorno in cui serve**, una volta, e la domenica se e'
rimasto aperto — perche' li' e' un dato: cio' che manca sempre non e' sfortuna,
e' un prodotto che quel negozio non tiene.

### dati/storico.yaml

```yaml
tarature:                  # stato appreso: letto SEMPRE prima di generare
  porzioni_g: {}           # per persona e alimento, default da kb/porzioni-standard.md
  piatti_esclusi: []       # media a tavola sotto 2 per due volte: definitivo
  piatti_in_quarantena:    # fuori rotazione, ma a scadenza: rientrano da soli
    Polpette al sugo: {fino_al: 2026-09-07, volte: 1, perche: stufo}
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
    menu: settimane/2026-W34-commando/2026-W34-commando-consuntivo.md
                           # la chiave resta l'ISO nudo; il percorso punta al documento
                           # piu' avanzato che c'e' — il consuntivo se e' arrivato
    spesa_stimata: 92.50
    spesa_reale: null      # SOLO il menu, dallo scontrino del ritiro
    spesa_extra_alimentare: null   # cibo comprato ma non previsto
    spesa_fuori_casa: null # ristorante, pizzeria, bar: alimentare, non spesa
    totale_scontrino: null # per memoria: include detersivi e non alimentari
    scarto_per_riga:       # dove la stima ha sbagliato, non solo di quanto
      - prodotto: passata-700
        stimato_eur: 2.40
        reale_eur: 3.60
        causa: ricomprata mentre in dispensa ce n'erano gia' tre
    celle_disattese:       # previsto casa, fatto fuori (o viceversa)
      - {giorno: 2026-08-22, pasto: cena, chi: tutti, previsto: casa, reale: ristorante}
    avanzi:
      - {cosa: pasta corta, quanto: mezzo pacco}
    note: ""
```

Le tre liste hanno una forma, e vale la pena averla scritta: la prima volta che
tre persone diverse hanno riempito questi campi ne sono uscite tre forme
incompatibili, e un campo che ognuno modella a modo suo non si puo' ne'
confrontare fra settimane ne' controllare. `causa` e' la meta' che conta di
`scarto_per_riga`: il quanto lo dicono i due numeri, il **perche'** no — ed e'
scritta a blocco, non in linea, perche' **una mappa inline non tollera una
virgola dentro un valore**: `{causa: ricomprata, ce n'erano tre}` non e' YAML
valido, e' una mappa con una voce rotta. Testo libero uguale a prosa: a blocco.

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

`piatti_in_quarantena` e `piatti_esclusi` non sono lo stesso elenco, e servivano
tutti e due: «fuori rotazione per 3 settimane» era scritto in due skill e non
aveva **nessun posto dove atterrare**, quindi il piatto rientrava il lunedi'
dopo come se niente fosse — una regola che il sistema non poteva eseguire.

| campo | quanto dura | chi ce lo mette |
|---|---|---|
| `piatti_in_quarantena` | fino a `fino_al`, poi rientra da solo | `settimana` (una stufaggine) e `postmortem` (media sotto 2) |
| `piatti_esclusi` | per sempre | solo `postmortem`, e **solo con un si'** dell'utente |

`perche` vale `stufo` o `bocciato`, e `volte` conta quante volte quel piatto ci
e' finito: alla **seconda** si propone l'esclusione definitiva, che e' la regola
che gia' c'era e che ora ha come contarla. Una voce con `fino_al` passato si
toglie quando la si incontra — nessuno deve ricordarsi di fare pulizia.

### dati/versione.yaml — il timbro

Tre scalari che dicono a che contratto sta questa cartella. Lo scrive il
sistema, mai l'utente; forma, deduzione dalla forma dei file e regole di
migrazione stanno in **«La cartella si aggiorna da sola»**, qui sopra.

```yaml
contratto: 4
motore: 5.0.0
migrata: 2026-08-16
```

Una cartella senza timbro non e' rotta: e' solo nata prima che il timbro
esistesse, e la prima skill che ci passa lo scrive.

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
5. **Confezioni**: fabbisogno − `avanzi` − `freezer` − `scorte` → confezioni da
   comprare, secondo `kb/confezioni.md` e con la fiducia di `kb/scorte.md`: una
   scorta fresca si sottrae in silenzio, una invecchiata si sottrae e si
   dichiara, una stantia non si crede. Sopra `massimo` non si compra, e lo si
   dice. La lista dice «2 pacchi da 500 g», mai «1050 g». Cio' che copre una
   scorta **esce dalla lista e viene nominato uscendo**
6. Salva, nella cartella della settimana: `-preventivo.md`, `-lista.md` e
   `-preventivo.html`. Poi aggiorna `dispensa.yaml` con gli avanzi previsti e
   aggiungi la voce a storico con `spesa_stimata`

### Le scorte si chiedono prima, non si scoprono dopo

`avanzi` dice cio' che il motore ha calcolato; non dice cio' che c'e'. Alla
prima settimana e' vuoto per definizione — ed e' esattamente la settimana in
cui il congelatore e' pieno di roba di prima —, poi deriva a ogni cena saltata.

Quindi `lunario:settimana` **guarda prima di generare**, e non fa un
censimento: il congelatore lo mostra per intero, perche' e' corto; delle
`scorte` rivisita **una fetta di al massimo sei righe**, scelte dove
l'incertezza incontra l'impatto (`kb/scorte.md`); del frigo chiede solo il
fresco di questa settimana, che non si inventaria. Sempre mostrando cio' che
crede di avere: correggere un elenco riesce a chiunque, ricordarlo a nessuno.

E' conteggio ciclico, non inventario perpetuo — le cucine professionali sulla
dispensa secca fanno cosi'. Chi taglia corto non perde niente: la fetta
invecchia e torna il lunedi' dopo, piu' in alto. Se `scorte` e' vuota, si
propone `lunario:inventario` **una volta sola** e si va avanti lo stesso: senza
inventario il sistema funziona identico, ha solo la lista piu' lunga.

Cio' che ne esce comanda **prima** della scelta dei piatti, non dopo: un
menu gia' scritto e una lista gia' chiusa a cui si tolgono quattro righe di
banco sono soldi spesi due volte, non un miglioramento del menu. Le scorte
sono anche la ragione tipica per cui un tetto `preferenza` si supera: se il
pesce e' li' da giugno, la seconda cena di pesce vince sul tetto, e si dice
perche'.

### Il ritiro della spesa (lunario:spesa)

Fra il menu e la prima cena c'e' un passaggio che non e' burocrazia: lo
scontrino dice cosa e' **davvero** entrato in casa. Si riconcilia con la lista,
si spunta cio' che e' arrivato, si scopre cosa manca — e per cio' che manca si
sostituisce subito con quello che c'e', oppure si rimanda, e allora il rimando
si scrive: e' un `sospeso` nel diario della settimana, non un promemoria in
chat.

Lo scontrino contiene anche cio' che con Lunario non c'entra: detersivi, casa,
roba comprata per altri. Va separato in tre gruppi — menu, alimentare fuori
lista, non Lunario — perche' **solo il primo e' la spesa che si confronta con
la stima**. Un budget sporcato dai detersivi non insegna niente.

Se il profilo ha `tolleranze.spesa_per_altri: true`, la lista che viaggia per
qualcun altro sta nel terzo gruppo e ci resta: fuori dai totali, fuori dal
paniere, fuori dalla dispensa. Non e' cibo di questa casa, e contarlo
falserebbe insieme il budget e le porzioni.

La lista non si riconcilia a memoria: **e' tornata indietro annotata**. Le
caselle dicono cosa e' stato preso, le frasi scritte accanto dicono cosa e'
cambiato — un formato, una sostituzione, un rimando. Come si leggono sta nel
contratto di `<nome>-lista.md`, qui sopra.

E' anche il punto in cui la settimana passa da preventivo a consuntivo: da qui
in avanti il documento vivo non descrive piu' cio' che si voleva, ma cio' che
c'e'.

### Il ciclo di vita del menu: preventivo e consuntivo

Un menu ha due stati, e la differenza non e' l'approvazione di qualcuno: e'
**quanto di cio' che c'e' scritto e' verificato**.

| documento | chi lo scrive | cos'e' |
|---|---|---|
| `-preventivo.md` | `lunario:menu`, appena generato | cio' che si vuole mangiare e comprare. Ogni numero e' una previsione: formati, prezzi, e i piatti stessi |
| `-consuntivo.md` | `lunario:spesa`, dopo lo scontrino | cio' che c'e' davvero in casa: prodotti veri, formati veri, prezzi pagati, sostituzioni gia' applicate ai piatti |

**Sono due file, non uno stato che si sovrascrive**, e il motivo e' che il
preventivo serve ancora: lo scarto fra quello che si voleva e quello che c'e'
e' l'unica cosa che insegna qualcosa al paniere, e leggerlo non deve richiedere
un `git diff`. Lo `stato:` in testa a ciascuno resta, e dice quale dei due si
sta leggendo quando il file viaggia da solo.

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

Il consuntivo lo scrive **solo `lunario:spesa`**, ed e' il momento in cui i
prodotti reali entrano nel documento. E' l'unico evento che sa dire se la lista
era giusta: prima di lui, mettere un timbro di definitivo su un totale fatto di
prezzi della settimana scorsa e' una bugia tipografica.

**Il consuntivo, di solito, non si tocca piu'.** Ma la settimana la scrivono
anche i fatti — una cena salta, arrivano ospiti, un ingrediente va a male — e
allora `lunario:correggi` lavora li' sopra, perche' quello e' il documento vivo.
Non e' ripianificare: e' registrare cosa e' successo davvero, che e' il mestiere
di un consuntivo. Si toccano **i giorni**, mai la parte che registra la spesa:
cosa e' entrato in casa e a che prezzo e' un fatto chiuso.

Nessuno dei due si spunta e nessuno dei due raccoglie note. Le caselle dei
pasti dicono **che** un pasto e' avvenuto e le marca `lunario:prepara`; le
annotazioni della settimana passano dal diario, pasto per pasto, mentre si
cucina. Uno stato scritto in una pagina HTML e' invisibile alle skill, ed e'
invisibile in silenzio: chi lo scrive crede di aver detto qualcosa al sistema,
e non l'ha ricevuta nessuno.

In coda al consuntivo c'e' comunque un **delta leggibile** — cosa e' cambiato
di formato, di prezzo, di piatto — perche' il confronto si fa a colpo d'occhio
e non file contro file. Se il consuntivo si scosta dal preventivo sempre nello
stesso verso per tre settimane — quel pacco e' sempre piu' grande, quel prodotto
non c'e' mai — non e' sfortuna, e' un paniere da correggere.

**Il totale del consuntivo e' il cibo di questa casa** — `spesa_reale` +
`spesa_extra_alimentare` — e non il totale della cassa. Il non alimentare e la
spesa di altre case sono gia' stati scorporati, e rimetterli dentro nell'ultima
riga disfa tutto lo scorporo: uno zaino da 45 € fa sembrare la settimana costata
il doppio, e quel numero non risponde a nessuna domanda. Se serve la
tracciabilita' col pezzo di carta, una riga «fuori da questo conto, per memoria»
dice il totale di cassa e cosa lo separa da questo. E cio' che si e' comprato
per un'altra casa **resta in pagina**, voce per voce e col suo subtotale: e'
fuori dai conti di Lunario, non cancellato dal documento — quanto si deve a
qualcuno e' esattamente il numero che si sta cercando.

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

### Il documento vivo e' anche lo stato di avanzamento

Nel documento vivo della settimana **i pasti sono caselle da spuntare**, e la
casella vuol dire una cosa sola: quel pasto e' stato fatto. Le marca
`lunario:prepara` mentre si cucina, e da li' in poi il pasto esce dai candidati
del lancio successivo.

**Una sola casella, un solo significato.** Le caselle della spesa vivono nella
lista e vogliono dire «preso»; il consumo non e' una casella affatto — sta in
`dispensa.yaml` e nel diario. Tre significati sulla stessa casella (comprato,
consumato, cucinato) sono una casella di cui non si fida piu' nessuno.

Le caselle dicono **che** un pasto e' avvenuto; il diario dice **cosa si e'
mangiato davvero**, ed e' la stessa informazione resa rispondibile. Ci si
appoggiano `lunario:correggi`, che propone cosa e' rimasto invece di
chiederlo, e il postmortem, che corregge la dispensa sul consumo reale.

Perche' non bastasse la memoria della domenica: il postmortem faceva quattro
domande su sette giorni, ed e' una prova di memoria che fallisce proprio dove
serve. Tre mercoledi' mangiati fuori sono un ritmo da scrivere in
`ritmi.yaml`, ma solo se sono stati registrati tutti e tre — ricostruito la
domenica, il terzo e' l'unico che qualcuno ricorda. «E' finita o e' rimasta
mezza teglia in frigo» e' una domanda a cui si sa rispondere il martedi', non
sei giorni dopo, ed e' la risposta che tara `porzioni_g`.

### Correzione in corsa (lunario:correggi)

A meta' settimana cambia qualcosa: una cena salta, un piatto non va, arriva un
ospite. **La spesa e' gia' fatta**: il vincolo non e' piu' il budget, e' cosa
c'e' in casa, e il documento su cui si scrive e' il consuntivo. Quindi si chiede cosa deve cambiare e cosa c'e' in frigo, si
rigenerano solo i **giorni residui** riusando gli ingredienti gia' comprati, e
si propone una spesa integrativa solo se e' inevitabile — poche righe, dette
come tali. I giorni gia' passati non si riscrivono mai.

### Postmortem (lunario:postmortem)

Si apre **leggendo il diario della settimana**, non chiedendo: cio' che e' gia'
registrato si propone come verificato e non si ridomanda. Restano le domande
sui buchi — avanzi, bocciati/promossi e da chi, la griglia che non ha tenuto,
spesa integrativa e mangiate fuori — poi ritara:
- stesso avanzo per 2+ settimane -> riduci la porzione in `tarature`
- piatto bocciato 1 volta -> fuori rotazione 3 settimane; 2 volte -> escluso
- stessa cella disattesa per 3 settimane -> non e' sfortuna, e' un ritmo:
  proponi di scriverlo in `ritmi.yaml`. Proponi, non scrivere
- ristorante e pizzeria -> `spesa_fuori_casa`, mai dentro `spesa_reale`
- scontrino PDF -> prezzi in `prodotti.jsonl`, `spesa_reale` e
  `scarto_per_riga` in storico, dispensa corretta sul reale

Poi **lascia un file**: `<nome>-postmortem.md` nella cartella della settimana —
com'e' andata, cosa ha cambiato, cosa resta aperto. Le tarature stanno in
`storico.yaml` perche' le rilegge una skill; il ragionamento che le ha prodotte
finiva in chat, e una chat a febbraio non la rilegge nessuno. Ne' voti uno per
uno ne' il peso di nessuno: quello sta in `storico.yaml`, e un numero sul corpo
di una persona non si scrive in un documento che qualcun altro puo' aprire.

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

## Come si sa cosa si e' rotto

Le skill sono markdown eseguito da un modello: **l'output non e' deterministico
e non lo sara' mai**. Un menu generato due volte sono due menu diversi, e va
bene cosi'. Quindi non si asserisce mai il menu: si asserisce cio' che di
qualunque menu deve essere vero — e quella specifica esiste gia', e' la sezione
«Regole non negoziabili» qui sopra. I test in `tests/` la trasformano in
asserzioni. Come si lanciano e cosa vuol dire un fallimento stanno in
`tests/README.md`; qui c'e' solo cio' che vincola chi tocca il motore.

| tier | cosa controlla | costo | quando |
|---|---|---|---|
| **1** `scripts/lint_dati.py` | i contratti dati: YAML leggibile, id che esistono, ogni prezzo con data e fonte, nessun deperibile fra gli avanzi, nessuno stato di cella fuori vocabolario, e i documenti della settimana col nome che le skill cercheranno | zero token | sempre |
| **2** `tests/loop_runner.py` | il giro intero headless su una casa sintetica, e le proprieta' che deve lasciare dietro | token veri | prima di una release |
| **3** `tests/giudizio.py` | il menu e' *buono*: equilibrio, varieta', plausibilita' di un mercoledi' sera | token veri | ogni tanto |

**Il tier 1 sta nel motore, non nei test**, ed e' la stessa verifica in
entrambi gli usi: il tier 1 la lancia sui fixture prima di una release,
`lunario:tagliando` la lancia dentro una cartella di casa mesi dopo, dove
`tests/` non e' mai stato copiato. Scritta due volte sarebbe divergente entro
due contratti — che e' esattamente il difetto da cui nasce la regola sotto.

**Il tier 3 non fa mai fallire la suite.** Esce sempre 0, per costruzione. Una
suite che diventa rossa a caso viene ignorata entro due settimane, e da li' in
poi riporta verde anche su un motore rotto.

Due vincoli che ricadono su chi cambia il motore:

- **Un contratto nuovo non e' finito finche' il tier 1 non lo controlla.** Un
  campo che nessuno verifica diverge in silenzio: e' successo la prima volta
  che tre persone hanno riempito `scarto_per_riga`, ed erano tre forme diverse
- **I file dei dati stanno in un sottoinsieme YAML semplice** — niente ancore,
  niente scalari multi-riga, niente documenti multipli. Non e' pigrizia del
  parser: quei file li scrivono e li rileggono dei modelli, e la semplicita' e'
  parte del contratto. `scripts/minyaml.py` li legge con la sola stdlib e
  segnala come violazione tutto cio' che ne esce

**I fixture sono l'unica eccezione alla regola «nessun dato personale in
git»**, e l'eccezione va dichiarata invece che lasciata implicita. In
`tests/fixtures/` vivono tre case sintetiche — `single`, `famiglia`,
`coppia-dispensa-profonda` — e reggono perche' sono **dichiaratamente finte, e
si vede a colpo d'occhio**: nomi come `Adulto1` e `Solo1`, numeri tondi,
nessun EAN (un codice a barre inventato somiglierebbe a un prodotto vero),
nessuna fonte `openfoodfacts:`. Un test verifica che la riga che lo dichiara
sia ancora in testa a ogni profilo.

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
- `dati/` e `settimane/` sono gitignored: il repo resta pulito da dati
  personali. L'unica negazione riguarda `tests/fixtures/*/`, le case sintetiche
- La cartella dei dati si puo' spostare con `LUNARIO_DATI=/percorso`; senza,
  e' `dati/` nella cartella di lavoro
- L'evoluzione futura — dati su un server di casa, MCP in combo con le skill,
  uso condiviso dalla famiglia — e' pianificata ma non in corso: rotta,
  vincoli e tappe in `docs/piano-server.md`
