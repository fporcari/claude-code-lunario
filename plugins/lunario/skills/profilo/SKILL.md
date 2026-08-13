---
name: profilo
description: >-
  Prima configurazione di Lunario — intervista la famiglia per capire chi
  mangia, con quali obiettivi calorici, quali cibi sono esclusi e quanto tempo
  c'e' per cucinare, e scrive dati/profilo.yaml. Da invocare al primo avvio
  del sistema, quando l'utente dice "configuriamo", "setup", "primo avvio",
  "iniziamo da zero", "non ho ancora il profilo", oppure quando una skill
  scopre che dati/profilo.yaml manca. Usala anche per modificare il profilo
  esistente: "e' cambiato il mio peso", "aggiungi una persona", "non mangiamo
  piu' X", "cambio obiettivo".
---

# Profilo — chi siete

Scrive il livello **stabile**: il vincolo che cambia una volta l'anno.
Contratti e regole in `CLAUDE.md`, registro conversazionale incluso.

## Se il profilo esiste gia'

Non rifare l'intervista. Mostra un riepilogo di tre righe (chi, target kcal,
esclusioni), chiedi cosa cambia, tocca solo quello.

## L'intervista

Una domanda per volta, tono da prima visita: si ascolta, non si compila. Non
chiedere tutto — i campi non essenziali hanno un default sensato e si
correggono strada facendo.

**1. Chi mangia a questa tavola.** Nome (anche solo l'iniziale), eta'
indicativa, chi e' a dieta e chi no. Basta il racconto: «io e mia moglie a
dieta, due bambini che mangiano normale».

**2. L'obiettivo, per chi e' a dieta.** Non chiedere le kcal: chiedi il
peso di adesso, l'altezza e dove vorrebbero arrivare. Dai numeri calcola tu il
fabbisogno e proponilo, spiegando in una riga da dove viene.

Il calcolo: metabolismo basale con Mifflin-St Jeor, moltiplicato per un
fattore di attivita' (sedentario 1,2 · leggermente attivo 1,375 · attivo
1,55), meno un deficit ragionevole (300-500 kcal/giorno, cioe' circa 0,3-0,5
kg a settimana).

- **Mai proporre sotto 1200 kcal/giorno.** Se il calcolo ci va sotto, fermati:
  proponi 1200 e di' chiaramente che per scendere oltre serve un medico
- Se l'utente chiede un target piu' aggressivo di quello calcolato, dillo una
  volta e poi rispetta la sua scelta, sempre col pavimento delle 1200

**3. Cosa non entra in casa.** Esclusioni: allergie, intolleranze, cose
odiate, scelte etiche. Non chiedere il perche' — al motore non serve. Chiedi
invece se valgono per tutti o per una persona sola, e ricorda che varranno
anche come ingrediente nascosto.

**4. I bambini, se ci sono.** Domanda secca: sono selettivi? Se si', si
attiva la regola della base neutra (`${CLAUDE_PLUGIN_ROOT}/kb/consigli-pratici.md`) e ogni cena avra'
una versione semplice estraibile.

**5. Come si cucina qui.** Quanti minuti realistici per la cena nei giorni
feriali, cosa c'e' in cucina che cambia le ricette (forno, friggitrice ad
aria, pentola a pressione, congelatore capiente), quante volte a settimana si
mangia pesce o carne per abitudine.

**6. Gusti e stanchezze.** Cucine che piacciono, piatti che in questa casa non
si vedranno mai, quanta voglia c'e' di provare cose nuove. Serve a filtrare
`${CLAUDE_PLUGIN_ROOT}/kb/piatti.md` fin dal primo menu invece che dopo tre postmortem.

## Chiusura

Riepiloga in poche righe cio' che hai capito e fatti confermare. Poi crea la
cartella dei dati **nella cartella di lavoro corrente**, se non c'e' gia',
copiandoci i modelli commentati del plugin:

```
mkdir -p dati settimane
cp -n ${CLAUDE_PLUGIN_ROOT}/templates/*.yaml ${CLAUDE_PLUGIN_ROOT}/templates/*.md \
      ${CLAUDE_PLUGIN_ROOT}/templates/*.jsonl dati/
```

`cp -n` non sovrascrive mai: se l'utente rilancia questa skill, i suoi dati
restano intatti. Poi compila `dati/profilo.yaml` con quello che ti ha detto e
lascia gli altri file ai loro modelli, che si riempiranno da soli.

Se l'utente vuole tenere i dati altrove (per esempio in una cartella
sincronizzata), la variabile `LUNARIO_DATI` punta dove vuole lui: diglielo
solo se la cartella di lavoro sembra un posto di passaggio.

Chiudi indicando il passo successivo — `lunario:ritmi` per gli orari, oppure
direttamente `lunario:settimana` se l'utente ha fretta di vedere un menu: i
ritmi si possono aggiungere dopo.
