# Lunario — la cartella di casa

Questa cartella contiene i dati di **una** situazione: chi mangia, con che
ritmi, cosa si compra e cosa si e' imparato. Il motore non e' qui: e' il
plugin `lunario`, che si aggiorna per conto suo.

Se apri questa cartella con Claude Code, sei nel posto giusto per generare il
menu e chiudere la settimana.

## Come si usa

| quando | cosa lanciare |
|---|---|
| **lunedi'** | `lunario:settimana` — racconti la settimana, esce menu e spesa |
| **domenica** | `lunario:postmortem` — avanzi, bocciati, scontrino |
| a settimana in corso | `lunario:correggi` — se cambia qualcosa |
| quando cambia la vita | `lunario:ritmi` — orari nuovi, vincoli permanenti |
| quando cambia la famiglia | `lunario:profilo` — peso, obiettivi, esclusioni |

Non serve ricordarsi i nomi: basta dire «prepariamo la settimana» o «com'e'
andata», e la skill giusta parte da sola.

## Cosa c'e' dentro

```
dati/
├── profilo.yaml      chi siete, calorie, esclusioni       <- lo scrivi tu
├── ritmi.yaml        gli orari che si ripetono            <- lo scrivi tu
├── note.md           i vincoli che detti a voce           <- lo scrivi tu
├── prodotti.jsonl    il paniere: formati, valori, prezzi  <- lo scrive il sistema
├── dispensa.yaml     cosa e' rimasto in casa              <- lo scrive il sistema
└── storico.yaml      settimane passate e tarature         <- lo scrive il sistema
settimane/            i menu generati, uno per settimana
```

**La regola di confine**: il sistema non tocca mai i primi tre. Puo' proporre
una modifica, ma li scrivi tu. Gli ultimi tre sono suoi: puoi leggerli e
correggerli, ma si riempiono da soli.

## Se tieni piu' di una cartella

Una per famiglia, una per quando sei solo: profilo, ritmi e storico restano
separati — ed e' giusto, sono legati a chi mangia. Ma **la dispensa e il
paniere andrebbero condivisi**, perche' il frigo e il supermercato sono gli
stessi. Chiedilo a `lunario:profilo`, che li collega senza duplicarli.

## Privacy

Qui dentro ci sono i pesi, gli obiettivi e le abitudini di persone reali.
Questa cartella non va su GitHub: se la metti sotto git, tienila privata.
Il motore, quello si', e' pubblico e non contiene niente di tuo.
