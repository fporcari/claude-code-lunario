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

## Il menu ha due stati

| stato | quando | cosa vuol dire |
|---|---|---|
| `preventivo` | dal lunedì fino alla spesa | quello che volete mangiare. Formati, prezzi e piatti sono stime: il totale **non** è una spesa |
| `consuntivo` | dopo lo scontrino | quello che c'è davvero in casa: prodotti veri, prezzi pagati, sostituzioni già applicate |

Il preventivo si cambia quante volte serve — è per questo che lo si fa girare
in casa prima di uscire. Il passaggio a consuntivo lo fa `lunario:spesa` quando
gli dai lo scontrino, e nessun'altra skill lo tocca.

La lista della spesa del preventivo **si spunta col dito**: aprila sul telefono
al supermercato, le spunte restano dov'erano anche se ricarichi la pagina.
Restano in quel browser e basta — al ritorno, quello che è entrato in casa lo
dice lo scontrino.

## La griglia dei pasti

Il giorno non e' «pranzo e cena»: e' una griglia **pasto × persona**, e ogni
cella dice cosa succede a quel pasto per quella persona.

| stato | vuol dire |
|---|---|
| `casa` | si cucina, si compra, conta nelle calorie |
| `trasportabile` | idem, ma deve viaggiare e mangiarsi freddo |
| `libero` | si cucina e si compra, ma non conta: la pizza del sabato |
| `ristorante` | non si cucina, non si compra — pero' si paga, e si registra |
| `fuori` | mensa, bar, ospite: fuori dal sistema |
| `no` | quel pasto quella persona non lo fa |

Tre file la scrivono, e vince sempre il piu' specifico: `profilo.yaml` dice
quali pasti fai di solito, `ritmi.yaml` cosa cambia ogni settimana,
`settimane/<ISO>/contesto.yaml` cosa cambia solo questa volta.

Colazione, spuntino e merenda sono pasti come gli altri: se sono `casa`,
finiscono nel conto delle calorie e nella lista della spesa. Un pasto fuori
dal conto e' un obiettivo calorico sbagliato.

## Git: c'e', ed e' solo tuo

Questa cartella e' un repo git **locale, senza remote**: le skill committano
da sole quando hanno finito, e tu non digiti mai un comando. Serve a vedere
cosa e' cambiato e a tornare indietro — `git log`, `git diff` — quando una
taratura ti sembra andata storta.

Non c'e' nessun remote e non te lo proporra' nessuno: qui dentro ci sono pesi
e abitudini di persone vere. Per lavorare dal telefono non serve — `claude
remote-control` sul computer di casa fa esattamente quello, lasciando i file
dove sono. Se il git non lo vuoi, `git: no` in `profilo.yaml`.

## Cosa c'e' dentro

```
dati/
├── profilo.yaml      chi siete, calorie, esclusioni       <- lo scrivi tu
├── ritmi.yaml        gli orari che si ripetono            <- lo scrivi tu
├── note.md           i vincoli che detti a voce           <- lo scrivi tu
├── ricette.md        i piatti vostri, non del motore       <- lo detti tu
├── prodotti.jsonl    il paniere: formati, valori, prezzi  <- lo scrive il sistema
├── dispensa.yaml     cosa e' rimasto in casa              <- lo scrive il sistema
└── storico.yaml      settimane passate e tarature         <- lo scrive il sistema
settimane/            i menu generati, uno per settimana
└── 2026-W34/
    ├── contesto.yaml  gli impegni di QUELLA settimana      <- lo racconti tu
    └── diario.yaml    cosa avete mangiato davvero          <- lo scrive il sistema
```

Il diario si riempie strada facendo, senza che tu compili niente: basta dirlo
mentre succede — «stasera niente polpette, pizza d'asporto» — e a fine cottura
ci pensa `lunario:prepara`. Serve la domenica: quello che è già scritto il
postmortem non te lo richiede. Se resta mezzo vuoto non è un problema, e
nessuno te lo farà notare.

`ricette.md` e' l'unico file misto: il contenuto e' tuo, la forma serve al
motore. Basta dire in chat «mi hanno dato questa ricetta» — anche con un link
o una foto — e ci finisce dentro, con ingredienti, quantita' e calorie. Da
quel momento e' un piatto come tutti gli altri: entra nel menu, prende i voti,
esce di rotazione se non piace.

**La regola di confine**: i file marcati «lo scrivi tu» il sistema non li
tocca mai — puo' proporre una modifica, ma li cambi tu. Quelli marcati «lo
scrive il sistema» sono suoi: puoi leggerli e correggerli, ma si riempiono da
soli. `ricette.md` sta in mezzo, ed e' l'unico: il contenuto e' tuo, lo detti
a voce, e il sistema lo mette in forma.

## Se tieni piu' di una cartella

Una per famiglia, una per quando sei solo: profilo, ritmi e storico restano
separati — ed e' giusto, sono legati a chi mangia. Ma **la dispensa e il
paniere andrebbero condivisi**, perche' il frigo e il supermercato sono gli
stessi. Chiedilo a `lunario:profilo`, che li collega senza duplicarli.

## Privacy

Qui dentro ci sono i pesi, gli obiettivi e le abitudini di persone reali,
minori compresi. **Questa cartella non va su GitHub**, nemmeno in un repo
privato: il git locale ti da' la storia senza far uscire niente di casa. Il
motore, quello si', e' pubblico e non contiene niente di tuo.
