---
name: profilo
description: >-
  Setup di Lunario in una cartella nuova. Intervista la famiglia — chi mangia,
  con quali obiettivi calorici, quali cibi sono esclusi, quanto tempo c'e' per
  cucinare — e poi costruisce tutto da sola: sottocartelle, file dei dati e
  CLAUDE.md della cartella. Da invocare al primo avvio, quando l'utente dice
  "configuriamo", "setup", "primo avvio", "iniziamo da zero", "installo
  lunario qui", oppure quando un'altra skill scopre che dati/profilo.yaml
  manca. Usala anche per modificare un profilo esistente: "e' cambiato il mio
  peso", "aggiungi una persona", "non mangiamo piu' X", "cambio obiettivo".
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
| `dati/profilo.yaml` | in una casa **gia' configurata** | non rifare l'intervista: vai al punto 4 |
| niente di tutto questo | cartella **nuova** | e' il caso normale: procedi, e alla fine costruisci qui |

Nel caso normale non chiedere conferma sul percorso: l'utente ha gia' scelto
dove stare aprendo quella cartella. Chiedere «dove creo i file?» a chi si trova
gia' nella cartella giusta e' una domanda in piu' che non serve a niente.

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
