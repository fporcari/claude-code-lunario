---
name: profilo
description: >-
  Setup e aggiornamento di Lunario in una cartella. La prima volta intervista
  la famiglia — chi mangia, chi e' a dieta e chi no, quali pasti fa ognuno
  (colazione, spuntini, merende, pasti liberi e fuori casa), quali cibi sono
  esclusi, quanto tempo c'e' per cucinare, se si vuole il menu in agenda — e
  costruisce tutto da sola: sottocartelle, file dei dati e CLAUDE.md della
  cartella. Rilanciata su una cartella gia' configurata NON ricomincia da
  capo: aggiorna solo cio' che e' cambiato e propone le novita' del motore che
  il profilo non ha ancora. Da invocare per "configuriamo", "setup", "primo
  avvio", "installo lunario qui", "aggiorna il setup", "e' cambiato il mio
  peso", "aggiungi una persona", "non mangiamo piu' X", "cambio obiettivo",
  oppure quando un'altra skill scopre che dati/profilo.yaml manca.
---

# Profilo — il setup della cartella

Scrive il livello **stabile** e, la prima volta, costruisce la casa attorno.
Contratti e registro conversazionale in `CLAUDE.md` del motore.

**L'utente crea solo la cartella e la apre.** Tutto il resto — sottocartelle,
file, CLAUDE.md — lo fai tu. Non chiedergli mai di lanciare `mkdir` o di
copiare template a mano.

## 1. Capire dove sei, prima di ogni altra cosa

Guarda la cartella di lavoro corrente:

| cosa trovi | dove sei | cosa fai |
|---|---|---|
| `plugins/lunario/` o `.claude-plugin/marketplace.json` | nel **repo del motore** | fermati: spiega che qui ci sta il codice, non la famiglia, e chiedi di aprire (o creare) una cartella personale |
| `dati/profilo.yaml` | in una casa **gia' configurata** | e' un **aggiornamento**: salta l'intervista e vai alla sezione qui sotto |
| niente di tutto questo | cartella **nuova** | e' il caso normale: procedi con l'intervista, e alla fine costruisci qui |

Su una cartella nuova `versione.py --controlla` risponde «non e' una cartella
di casa Lunario», ed e' giusto: qui il timbro non c'e' ancora perche' la casa
non c'e' ancora. Lo scrivi tu alla fine, al punto 3.

Nel caso normale non chiedere conferma sul percorso: l'utente ha gia' scelto
dove stare aprendo quella cartella. Chiedere «dove creo i file?» a chi si trova
gia' nella cartella giusta e' una domanda in piu' che non serve a niente.

## 1a. Se il profilo esiste gia': aggiornamento

Rilanciare questa skill su una casa configurata **non ricomincia da capo**.
Nessuno vuole rifare l'intervista perche' e' cambiato un peso.

**Una domanda sola, poi si scende in un ramo solo.** Se l'utente ha gia' detto
cosa vuole cambiare («e' cambiato il mio peso»), quella domanda non si fa
nemmeno: sei gia' nel ramo.

Riepiloga in due righe cosa c'e' adesso — chi mangia, target, esclusioni — e
chiedi **cosa vuole rivedere**, offrendo i rami come opzioni:

| ramo | cosa tocchi, e nient'altro |
|---|---|
| **chi mangia** | persone, pesi, obiettivi, chi e' a dieta e chi no |
| **i pasti** | la griglia: chi fa colazione, spuntino, merenda; pasti liberi fissi |
| **cosa non entra in casa** | esclusioni e intolleranze |
| **come si cucina** | minuti, attrezzatura, frequenze di carne e pesce |
| **cosa si tollera a tavola** | ripetizioni, avanzi, quanto sono rigidi i tetti, spesa per altri |
| **agenda e git** | calendario del menu, versionamento della cartella |
| **novita' del motore** | cio' che il profilo non ha ancora (sotto) |

Dentro il ramo scelto vale l'intervista normale: una domanda per volta, e si
chiude appena il ramo e' coperto. **Non passare al ramo successivo di tua
iniziativa** — se l'utente voleva rivedere due cose, lo dice lui.

Poi, in ogni caso, **controlla se il profilo e' rimasto indietro**: confronta
le sezioni presenti con `${CLAUDE_PLUGIN_ROOT}/templates/profilo.yaml`. Le
versioni nuove del motore aggiungono campi, e un profilo scritto mesi fa non
li ha.

Anche qui, **proponi solo le novita' che cambiano qualcosa per l'utente**, una
riga ciascuna, e accetta un no senza insistere. Per esempio, a chi non ha
mai avuto la sezione `calendario`: «e' nuova la possibilita' di ritrovare il
menu in agenda — ti interessa?». Un campo aggiunto in silenzio con un default
va bene; una funzione che scrive da qualche parte va chiesta.

### La migrazione non e' affare di questa skill

Le cartelle scritte da versioni precedenti del motore hanno una forma diversa —
la vecchia grammatica della griglia, la sezione `bambini`, sezioni che allora
non esistevano. **Non convertirle qui.** Quella logica vive tutta in
`lunario:aggiorna`, e ci vive per due ragioni: perche' duplicata in otto skill
divergerebbe, e perche' li' e' **versionata** — sa cosa e' gia' stato fatto,
invece di ricontrollare le stesse forme a ogni lancio.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/versione.py --controlla
```

Se dice che la cartella e' indietro, passa da `lunario:aggiorna` e torna qui:
quando riprendi, il profilo che leggi e' gia' nella forma corrente.

Quello che resta a questa skill sono le cose che `aggiorna` **non puo'**
decidere da sola, e che ti segnala: i nomi dei bambini, se qualcuno vuole la
pesata della domenica, quanto sono rigidi i tetti, dove vuole arrivare chi e' a
dieta. Sono domande, non conversioni — e si fanno una per volta, quando c'e'
occasione, non tutte in fila appena si apre la cartella.

Due cose vanno **chieste**, perche' cambiano il menu e non si deducono:

- se qualcuno fa spuntino o merenda, e chi
- se c'e' un pasto libero fisso in settimana

Il git invece si attiva e basta, con una riga di avviso: e' un `git init`
locale che non manda niente da nessuna parte.

Controlla allo stesso modo che la casa sia completa: se mancano file che oggi
fanno parte del corredo — per esempio `dati/storico.yaml` o il `CLAUDE.md`
della cartella — copiali dai templates con `cp -n`, che non sovrascrive niente,
e dillo in mezza riga.

## 2. L'intervista, e i suoi due passi

La prima visita da un nutrizionista vero non misura tutto: **fa partire**.
Quindi l'intervista ha un nucleo — le domande senza cui il primo menu non
puo' uscire — e un approfondimento che puo' aspettare. Offri la scelta in una
riga, all'inizio: «tre domande e partiamo col primo menu, il resto me lo
racconti strada facendo — oppure facciamo tutto adesso». Chi ha voglia di
raccontare racconti; chi vuole vedere il menu lo vede in cinque minuti.

### Il nucleo: senza queste non si parte

1. **Chi mangia a questa tavola** — nome e chi e' a dieta. Per chi e' a
   dieta, peso, altezza e obiettivo, col calcolo di cui sotto; se preferisce
   non dirlo adesso, `dieta: false` e porzioni standard, si cambia quando
   vuole
2. **Cosa non entra in casa** — allergie, intolleranze, esclusioni. Questa
   non si rimanda mai: un menu senza le esclusioni non e' incompleto, e'
   pericoloso
3. **Quali pasti si fanno** — non un interrogatorio, una proposta da
   correggere: «direi colazione a casa per tutti, merenda ai bimbi, pranzo
   feriale fuori per chi lavora — torna?»

Tutto il resto ha un default che regge: 30 minuti per cucinare nei feriali,
titoli descrittivi dai piatti, niente calendario, niente pesata. Scrivi nel
profilo `intervista: minima` e chiudi: e' il segnale, per te e per le skill a
valle, che i default sono default e non scelte.

### Il profilo minimo non e' un profilo dimezzato

Il primo menu esce identico — griglia, deperibilita', confezioni. Quello che
manca arriva **al momento in cui serve**, una domanda per volta, dalla skill
che ci sbatte contro:

| cosa manca | chi lo chiede, e quando |
|---|---|
| gusti e stanchezze | `lunario:settimana`, che gia' chiede voglie e stufaggini |
| selettivita' a tavola | `lunario:postmortem`, al primo piatto bocciato solo dai bambini |
| la pesata settimanale | `lunario:postmortem`, alla prima domenica con qualcuno a dieta |
| il menu in agenda | `lunario:correggi`, alla prima conferma del menu |
| il tempo vero per cucinare | `lunario:prepara`, quando i minuti reali smentiscono il default |
| le tolleranze a tavola | `lunario:correggi`, alla prima contestazione che le riguarda — «carne due volte in un giorno no» e' una tolleranza, non un capriccio del giovedi' |

La risposta e' dell'utente e tu la metti in forma nel profilo — lo stesso
patto di `ricette.md`. Quando i buchi sono finiti, togli `intervista: minima`.
E mai piu' di una di queste domande per volta: il percorso breve promette che
il resto non arriva tutto insieme.

### L'intervista completa

Chi la sceglie fa **la prima visita vera, una volta sola**: puo' durare, e va
bene che duri. Meglio venti minuti adesso che tre postmortem per scoprire che
il mercoledi' nessuno cena a casa. Dillo in una riga all'inizio — «ti faccio
un po' di domande, poi non te le faccio piu'» — e poi vai a fondo davvero.

Quello che rende sopportabile un'intervista lunga non e' farla corta: e'
**una domanda per volta**, e **arrivare con la proposta gia' pronta** da
correggere invece che con un campo vuoto da riempire. «Direi colazione a casa
per tutti, merenda solo per i bimbi — torna?» si risponde in una parola.

I campi non essenziali hanno un default sensato e si correggono strada
facendo. Se l'utente taglia corto («fai tu»), fermati: prendi i default,
dillo in mezza riga e va bene cosi' — e' il percorso breve, ci si arriva
anche da qui.

**Chi mangia a questa tavola.** Nome (anche solo l'iniziale), eta' indicativa,
chi e' a dieta e chi no. Basta il racconto: «noi due adulti a dieta, due
bambini che mangiano normale». **I bambini sono persone della lista**, con
nome e pasti loro: non una casella «ci sono i bambini».

**L'obiettivo, per chi e' a dieta.** Non chiedere le calorie: chiedi peso
attuale, altezza e dove vorrebbero arrivare, e calcola tu proponendo il
risultato con una riga di spiegazione.

Il calcolo: metabolismo basale con Mifflin-St Jeor, per un fattore di attivita'
(sedentario 1,2 · leggermente attivo 1,375 · attivo 1,55), meno un deficit di
300-500 kcal al giorno — circa 0,3-0,5 kg a settimana.

- **Mai proporre sotto 1200 kcal al giorno.** Se il calcolo ci va sotto,
  fermati: proponi 1200 e di' chiaramente che per scendere serve un medico
- Se l'utente vuole un target piu' aggressivo, dillo una volta sola e poi
  rispetta la sua scelta, sempre col pavimento delle 1200

Salva il peso di partenza in `peso_kg` e la meta' in `peso_obiettivo_kg`: il
secondo serve a sapere quando si e' arrivati, ed e' l'unico modo di proporre
il passaggio a mantenimento invece di tenere qualcuno a dieta per sempre.

**La pesata settimanale.** Chiedi, per ogni persona a dieta, se vuole che il
postmortem della domenica chieda il peso: serve a vedere il trend, che e'
l'unica cosa che dice se la taratura funziona. Dillo per quello che e' — «una
domanda la domenica, si puo' sempre saltare, e guardo l'andamento su tre
settimane, mai la singola pesata» — e accetta il no senza tornarci. Va in
`pesata_settimanale`.

**Chi non e' a dieta** ha `dieta: false` e `kcal_giorno: null`: porzioni
standard, nessun deficit. Non chiedergli il peso, non commentare il suo, non
proporgli di mettersi a dieta. Se **nessuno** e' a dieta va benissimo: Lunario
diventa un pianificatore equilibrato e la parola «deficit» non compare piu'.

> **Chi scrive non e' sempre chi mangia.** Al setup di solito c'e' una persona
> alla tastiera che risponde anche per gli altri, e peso e obiettivo sono la
> cosa piu' privata che questo sistema tocca. Quindi: chiedili una volta, in
> modo piano, e offri **subito** la via d'uscita — «se preferisce dirmelo
> dopo, o scriverlo lei nel file, il menu parte lo stesso con le porzioni
> standard». Se la risposta e' evasiva, non insistere e non tornarci: metti
> `dieta: false` e vai avanti. Un numero in meno costa una taratura; una
> domanda di troppo davanti a qualcuno costa il sistema intero.

**Quali pasti si fanno in questa casa.** E' la griglia, ed e' la parte che
cambia di piu' il menu. Chiedila per pasto, non per persona — «chi fa
colazione a casa?» si risponde meglio di «Luca cosa fa a colazione?»:

- **colazione** — chi la fa a casa, chi la salta, chi la fa al bar
- **spuntino di meta' mattina e merenda** — di solito i bambini si', gli
  adulti no. E' la domanda che nessun sistema fa e che sballa tutti i conti:
  una merenda da 200 kcal per due bambini e' 2800 kcal a settimana
- **pranzo** — a casa, da portarsi dietro, o mensa. Se la risposta cambia col
  giorno, non insistere qui: e' materia di `lunario:ritmi`
- **cena** — quasi sempre a casa; chiedi solo se c'e' una sera fissa che non
  lo e'

**Il pasto libero.** Chiedilo esplicitamente, perche' nessuno lo dichiara da
solo e tutti ce l'hanno: «c'e' un pasto in settimana in cui si mangia quel che
si vuole — la pizza del sabato, il pranzo della domenica?». Diventa una cella
`libero`: si cucina e si compra come gli altri, ma non si conta e **non si
compensa**. Dillo, perche' e' esattamente il contrario di quello che la gente
si aspetta da un sistema di diete — e' la ragione per cui questo si regge.

**Chi va assecondato a tavola.** Per ogni persona, se e' selettiva: bambini
che rifiutano il nuovo, ma anche adulti. Se si', per quella persona ogni cena
avra' una base neutra estraibile
(`${CLAUDE_PLUGIN_ROOT}/kb/consigli-pratici.md`). E' per persona, non per
casa: con due figli, uno che mangia tutto e uno no, un interruttore solo
sbaglia sempre.

**Cosa non entra in casa.** Allergie, intolleranze, cose odiate, scelte
etiche. Non chiedere il perche'. Chiedi invece se valgono per tutti o per una
persona sola, e ricorda che varranno anche come ingrediente nascosto.

**Come si cucina qui.** Minuti realistici per la cena nei feriali, cosa c'e' in
cucina che cambia le ricette (forno, friggitrice ad aria, pentola a pressione,
congelatore capiente), quante volte a settimana si mangia pesce o carne.

**Quanto sono tetti, i tetti.** Appena hai un numero — «carne due o tre volte»
— chiedi la cosa che nessuno dichiara da solo: **e se nel congelatore c'e'
roba che sta invecchiando e ti porterebbe a sforare?**. Le due risposte
scrivono due file diversi:

- «allora sforo, e' roba pagata» → `{valore: 3, rigidita: preferenza}`
- «no, la regola e' quella» → il numero nudo, che vale `vincolo`

E' una domanda sola per tutti i tetti insieme, non una per tetto. Un numero
scritto senza averla fatta e' un numero che il motore trattera' come una
regola, e la prima settimana con il congelatore pieno lo scoprirete correggendo
un menu gia' fatto.

**Cosa si tollera a tavola.** Sono le regole che nessuno pensa di dover dire
perche' in casa sono ovvie, e che si scoprono tutte allo stesso modo:
correggendo un menu gia' scritto. Chiedile qui, una per volta, e **lasciale
saltare**: chi non ci ha mai pensato non va interrogato, i default
conservativi reggono benissimo.

| domanda | dove va |
|---|---|
| carne (o pesce) a pranzo **e** a cena dello stesso giorno: si puo'? | `tolleranze.ripetizioni.stessa_proteina_nel_giorno` |
| lo stesso piatto due volte in un giorno — l'avanzo di mezzogiorno la sera? | `stesso_piatto_nel_giorno`, e chiedilo **a parte per i bambini**, che sono quasi sempre il caso stretto |
| gli avanzi tornano in tavola come sono, o solo trasformati in altro? | `tolleranze.avanzi` |
| ogni settimana parte una seconda spesa per qualcun altro? | `tolleranze.spesa_per_altri` |

L'ultima sembra fuori posto in un'intervista sul cibo, e non lo e': se ogni
settimana viaggia una lista per i suoceri, quella roba deve restare fuori da
ogni totale, dal paniere e dalla dispensa. Contata, falsa insieme il budget e
le porzioni — e nessuno capisce piu' perche'.

Quello che non viene chiesto, o a cui si risponde «boh», prende il **default
conservativo**: niente ripetizioni nel giorno, avanzi solo trasformati per i
bambini. Non e' timidezza, e' aritmetica: un menu che ripete un ingrediente
genera una correzione, un menu che non lo ripete al massimo genera un «potevi
anche rifarmelo».

**Quanto si mangia fuori.** Non per giudicare: per non cucinare per chi non
c'e'. Se e' una cosa fissa — «il venerdi' pizza fuori» — e' un ritmo; se
capita e basta, lo chiedera' `lunario:settimana` ogni lunedi'.

**Gusti e stanchezze.** Cucine che piacciono, piatti che in questa casa non si
vedranno mai, quanta voglia c'e' di provare cose nuove. Serve a filtrare
`${CLAUDE_PLUGIN_ROOT}/kb/piatti.md` dal primo menu invece che dopo tre
postmortem.

**Come si chiamano le settimane.** Ogni settimana prende un nome, per
ritrovarla senza contare i numeri ISO. Chiedi se vuole un **filone** da cui
pescarlo, e **proponi tre o quattro esempi concreti**, non la categoria
astratta: canzoni dei Beatles, fiori, pesci tropicali, costellazioni, cime
delle Alpi, film di Miyazaki, vini, isole greche. Meglio se e' una cosa che in
questa casa qualcuno ama gia': funziona come una playlist, non come
un'etichetta.

Va in `titoli.serie`. Se non gli interessa, `null`, e i titoli nascono dai
piatti della settimana come sempre — «la settimana dei legumi coraggiosi». Si
cambia quando si vuole, e quando la serie finisce se ne sceglie un'altra.

**Il menu in agenda.** Chiedi se vuole ritrovare la settimana sul calendario:
un evento col titolo del menu, che dal telefono dice cosa si mangia.

Se dice di si', **elenca i calendari che ha davvero** e fagli scegliere — non
dare per scontato nessun nome. Due cose da dire mentre sceglie, brevi:

- un **calendario dedicato** e' la sistemazione piu' comoda, col nome che
  preferisce: si accende e si spegne con un click e sparisce senza lasciare
  traccia se la cosa non piace. Va creato a mano (su calendar.google.com,
  accanto ad «Altri calendari», il + → «Crea nuovo calendario»), perche' il
  plugin gestisce eventi ma non crea calendari: se lo vuole, aspetta che lo
  abbia fatto e poi rileggi l'elenco
- se sceglie un calendario **condiviso o di lavoro**, dillo una volta: quello
  lo leggono altre persone

Chiedi anche se preferisce **un evento per tutta la settimana** o **uno per
ogni cena**, e salva tutto in `calendario` nel profilo. Se non gli interessa,
`scrivi: false` e non se ne parla piu'.

**Il git.** **Non e' una domanda.** Si attiva e basta, e se ne da' notizia in
mezza riga alla fine, mentre si dice cosa e' stato creato:

> «La cartella la tengo sotto git in locale, cosi' si puo' sempre tornare
> indietro. Resta tutto qui.»

`git: locale` e' il default e non si chiede: e' un repo locale senza remote,
non manda niente da nessuna parte e non ha controindicazioni — chiederlo
sarebbe solo una domanda in piu' in un'intervista gia' lunga. Chi non lo vuole
mette `git: no` nel profilo, e lo scopre da questa riga.

Non spiegare git a chi non ha chiesto, non elencare i vantaggi, non tornarci
sopra ai lanci successivi.

Se l'utente chiede un **remote** — GitHub, un server suo, «cosi' lo uso dal
telefono» — allora si', qui si parla, una volta e senza predica:

- di' cosa ci sarebbe dentro: pesi, obiettivi e abitudini alimentari di
  persone reali, minori compresi. Un repo privato riduce il rischio, non lo
  toglie: un dato caricato non rientra
- se il motivo e' il telefono, la risposta e' `claude remote-control` sul
  computer di casa: si guida la sessione dal telefono e i file non si spostano
- se dopo questo lo vuole lo stesso, e' una sua scelta legittima: aiutalo, e
  proponi SOPS + age per cifrare i valori. Non sabotare, non ripetere l'avviso

## 2a. Dove va scritta una risposta

Fare la domanda e' meta' del lavoro. L'altra meta' e' il file in cui la
risposta atterra, e sbagliarlo non si vede subito: si vede sei mesi dopo,
quando quella regola non ha piu' effetto su niente. Una domanda decide:

> **Il motore deve controllarlo da solo?**

| risposta | file | esempi |
|---|---|---|
| **si**, e' un campo che filtra o conta | `dati/profilo.yaml` | esclusioni, tetti e rigidita', ripetizioni vietate, spesa per altri |
| **no**, ma va letto prima di generare | `dati/note.md` | l'hummus si compra pronto, la merenda dei bimbi e' salata, niente integrale |
| **no**, e' per l'umano che apre la cartella | il `CLAUDE.md` di casa | come si lancia una skill, cos'e' la griglia dei pasti |

Il `CLAUDE.md` generato e' il posto sbagliato per una regola di casa, e la
seconda ragione conta piu' della prima: quel file lo scrive il plugin, quindi
una regola dell'utente ci sta a un aggiornamento dal trovarsi in un file che
non e' suo; e una regola in prosa non si puo' chiedere al setup, ne' riproporre
quando la vita cambia, ne' ritarare al postmortem. Diventa un testo che
qualcuno deve ricordarsi di rileggere.

C'e' un quarto caso, ed e' facile da mancare: quando cio' che sembra una
stranezza di casa e' un **difetto del motore** — «il menu esce disordinato»,
«non mi ha mai chiesto cosa avevo nel congelatore» — non va in nessuno dei
tre file. E' una issue sul plugin, e dirlo e' piu' utile che scriverlo da
qualche parte.

Quando scrivi una risposta, **di' in mezza riga dove l'hai messa** se non e'
il profilo: «l'ho segnata nelle note, cosi' la rileggo a ogni menu». Serve
all'utente per sapere dove tornare a cambiarla.

## 3. Costruire la casa

Riepiloga in poche righe cio' che hai capito e fatti confermare. **Poi** crea
tutto, nella cartella corrente, senza altre domande:

```bash
mkdir -p dati settimane
cp -n ${CLAUDE_PLUGIN_ROOT}/templates/profilo.yaml \
      ${CLAUDE_PLUGIN_ROOT}/templates/ritmi.yaml \
      ${CLAUDE_PLUGIN_ROOT}/templates/note.md \
      ${CLAUDE_PLUGIN_ROOT}/templates/ricette.md \
      ${CLAUDE_PLUGIN_ROOT}/templates/prodotti.jsonl \
      ${CLAUDE_PLUGIN_ROOT}/templates/dispensa.yaml \
      ${CLAUDE_PLUGIN_ROOT}/templates/storico.yaml dati/
cp -n ${CLAUDE_PLUGIN_ROOT}/templates/CLAUDE.md ./CLAUDE.md
```

`cp -n` non sovrascrive mai: se la skill viene rilanciata, i dati restano.

Poi, **prima di toccare git**, compila quello che hai raccolto:

1. **`dati/profilo.yaml`** con quello che ti ha detto, sostituendo i valori
   del modello e togliendo i commenti che non servono piu'
2. **Svuota `dati/prodotti.jsonl`** dalle righe di esempio: il paniere e' suo e
   si riempira' dai suoi scontrini
3. **Personalizza `./CLAUDE.md`**: nella prima riga il nome che l'utente da' a
   questa situazione («la famiglia Rossi», «quando sono solo»), cosi' chi apre
   la cartella fra sei mesi capisce subito dove si trova
4. Se dall'intervista sono emersi **orari ricorrenti**, scrivili in
   `dati/ritmi.yaml`; se sono emersi **vincoli liberi**, in `dati/note.md`.
   Quello che non e' emerso resta il modello commentato, e va bene cosi'
5. **Timbra la cartella**, cosi' nasce sapendo a che contratto sta e nessuno
   dovra' piu' indovinarlo dalla forma dei file:

   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/versione.py --scrivi <contratto corrente>
   ```

   Il numero del contratto corrente e' `CONTRATTO_CORRENTE` in quello script:
   non e' una cosa da chiedere all'utente e non si nomina in chat

**Solo adesso** il git locale, se `git: locale` (il default), cosi' il primo
commit contiene la casa vera e non i template vuoti:

```bash
git init -q 2>/dev/null
printf '.DS_Store\n*.pdf\n' > .gitignore
git add -A && git commit -q -m "Lunario: setup della casa"
```

Il `.gitignore` tiene fuori due sole cose: la robaccia di sistema e gli
scontrini PDF, che pesano e il cui contenuto utile e' gia' finito in
`prodotti.jsonl`. **Tutto il resto va versionato**: `dati/` e `settimane/`
sono esattamente cio' che ha senso avere sotto storia. Nessun `git remote`,
mai, se non lo chiede l'utente.

Se `git` non e' installato, se `git init` fallisce, o se la cartella sta gia'
dentro un altro repo, non e' un problema: dillo in mezza riga e vai avanti.
Lunario funziona identico senza.

## 4. Se accanto c'e' un'altra casa Lunario

Guarda le cartelle sorelle (`../*/dati/prodotti.jsonl`). Se ne trovi una, e'
la stessa persona in un'altra situazione — la famiglia, o la settimana da solo.

In quel caso **proponi di condividere paniere e dispensa**, spiegando perche'
in una riga: il supermercato e il frigo sono gli stessi, duplicarli significa
catalogare due volte gli stessi prodotti e credere di avere pasta che qualcun
altro ha gia' finito.

```bash
mkdir -p ../lunario-comune
mv ../<altra-casa>/dati/prodotti.jsonl ../lunario-comune/ 2>/dev/null
ln -sf ../../lunario-comune/prodotti.jsonl dati/prodotti.jsonl
ln -sf ../../lunario-comune/dispensa.yaml dati/dispensa.yaml
```

Profilo, ritmi e storico restano separati: sono legati a chi mangia, e mischiarli
falserebbe le tarature. Se l'utente preferisce due mondi del tutto separati,
va benissimo: non insistere.

## 5. Chiusura

**Chiudi con qualcosa da vedere, non con un elenco di file creati.** Chi ha
appena risposto a venti domande vuole sapere se ne e' valsa la pena, e a volte
non e' nemmeno solo: al setup c'e' spesso un'altra persona che guarda ed e'
quella da convincere.

Quindi, in quest'ordine e stretto:

1. **due righe** su cosa hai capito e dove vive adesso — la cartella, non
   l'elenco dei file uno per uno
2. **proponi di generare subito il primo menu**: «vuoi che proviamo con la
   settimana che viene?». Se dice di si', passa a `lunario:settimana` e vai:
   quello e' il momento in cui il sistema si spiega da solo
3. se dice di no, una riga su cosa succede il lunedi' e stop

Se l'intervista non ha coperto gli orari, non e' un problema e non va detto
come una mancanza: `lunario:ritmi` li raccoglie quando capita, e il primo menu
si fa lo stesso.

Il primo menu **non avra' i prezzi**, perche' il paniere e' vuoto: dillo prima
che lo scopra da solo, in mezza riga — «i prezzi arrivano col primo
scontrino» — cosi' un totale mancante e' una cosa attesa e non un difetto.
