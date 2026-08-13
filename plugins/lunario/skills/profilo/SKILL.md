---
name: profilo
description: >-
  Setup e aggiornamento di Lunario in una cartella. La prima volta intervista
  la famiglia — chi mangia, con quali obiettivi calorici, quali cibi sono
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

Nel caso normale non chiedere conferma sul percorso: l'utente ha gia' scelto
dove stare aprendo quella cartella. Chiedere «dove creo i file?» a chi si trova
gia' nella cartella giusta e' una domanda in piu' che non serve a niente.

## 1a. Se il profilo esiste gia': aggiornamento

Rilanciare questa skill su una casa configurata **non ricomincia da capo**.
Nessuno vuole rifare l'intervista perche' e' cambiato un peso.

Fai tre cose, in quest'ordine:

1. **Riepiloga in tre righe** cosa c'e' adesso: chi mangia, target calorici,
   esclusioni. Serve a far vedere all'utente cosa sta per cambiare
2. **Chiedi cosa cambia** e tocca solo quello. «E' cambiato il mio peso» si
   risolve con un numero e il ricalcolo delle calorie, non con un questionario
3. **Controlla se il profilo e' rimasto indietro**: confronta le sezioni
   presenti con `${CLAUDE_PLUGIN_ROOT}/templates/profilo.yaml`. Le versioni
   nuove del motore aggiungono campi, e un profilo scritto mesi fa non li ha

Sul punto 3: **proponi solo le novita' che cambiano qualcosa per l'utente**,
una riga ciascuna, e accetta un no senza insistere. Per esempio, a chi non ha
mai avuto la sezione `calendario`: «e' nuova la possibilita' di ritrovare il
menu in agenda — ti interessa?». Un campo aggiunto in silenzio con un default
va bene; una funzione che scrive da qualche parte va chiesta.

Controlla allo stesso modo che la casa sia completa: se mancano file che oggi
fanno parte del corredo — per esempio `dati/storico.yaml` o il `CLAUDE.md`
della cartella — copiali dai templates con `cp -n`, che non sovrascrive niente,
e dillo in mezza riga.

## 2. L'intervista

Una domanda per volta, tono da prima visita: si ascolta, non si compila. I
campi non essenziali hanno un default sensato e si correggono strada facendo.

**Chi mangia a questa tavola.** Nome (anche solo l'iniziale), eta' indicativa,
chi e' a dieta e chi no. Basta il racconto: «io e mia moglie a dieta, due
bambini che mangiano normale».

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

**Cosa non entra in casa.** Allergie, intolleranze, cose odiate, scelte
etiche. Non chiedere il perche'. Chiedi invece se valgono per tutti o per una
persona sola, e ricorda che varranno anche come ingrediente nascosto.

**I bambini, se ci sono.** Sono selettivi? Se si', si attiva la regola della
base neutra (`${CLAUDE_PLUGIN_ROOT}/kb/consigli-pratici.md`) e ogni cena avra'
una versione semplice estraibile.

**Come si cucina qui.** Minuti realistici per la cena nei feriali, cosa c'e' in
cucina che cambia le ricette (forno, friggitrice ad aria, pentola a pressione,
congelatore capiente), quante volte a settimana si mangia pesce o carne.

**Gusti e stanchezze.** Cucine che piacciono, piatti che in questa casa non si
vedranno mai, quanta voglia c'e' di provare cose nuove. Serve a filtrare
`${CLAUDE_PLUGIN_ROOT}/kb/piatti.md` dal primo menu invece che dopo tre
postmortem.

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

## 3. Costruire la casa

Riepiloga in poche righe cio' che hai capito e fatti confermare. **Poi** crea
tutto, nella cartella corrente, senza altre domande:

```bash
mkdir -p dati settimane
cp -n ${CLAUDE_PLUGIN_ROOT}/templates/profilo.yaml \
      ${CLAUDE_PLUGIN_ROOT}/templates/ritmi.yaml \
      ${CLAUDE_PLUGIN_ROOT}/templates/note.md \
      ${CLAUDE_PLUGIN_ROOT}/templates/prodotti.jsonl \
      ${CLAUDE_PLUGIN_ROOT}/templates/dispensa.yaml \
      ${CLAUDE_PLUGIN_ROOT}/templates/storico.yaml dati/
cp -n ${CLAUDE_PLUGIN_ROOT}/templates/CLAUDE.md ./CLAUDE.md
```

`cp -n` non sovrascrive mai: se la skill viene rilanciata, i dati restano.

Poi:

1. **Compila `dati/profilo.yaml`** con quello che ti ha detto, sostituendo i
   valori del modello e togliendo i commenti che non servono piu'
2. **Svuota `dati/prodotti.jsonl`** dalle righe di esempio: il paniere e' suo e
   si riempira' dai suoi scontrini
3. **Personalizza `./CLAUDE.md`**: nella prima riga il nome che l'utente da' a
   questa situazione («la famiglia Rossi», «quando sono solo»), cosi' chi apre
   la cartella fra sei mesi capisce subito dove si trova
4. Se dall'intervista sono emersi **orari ricorrenti**, scrivili in
   `dati/ritmi.yaml`; se sono emersi **vincoli liberi**, in `dati/note.md`.
   Quello che non e' emerso resta il modello commentato, e va bene cosi'

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

Di' cosa hai creato — la cartella, i file, dove sono — e cosa succede adesso:
`lunario:settimana` il lunedi'. Se l'intervista non ha coperto gli orari,
segnala che `lunario:ritmi` li raccoglie quando ha voglia: non e' obbligatorio
per il primo menu.
