# I test di Lunario

Il motore e' otto skill in markdown eseguite da un modello: **l'output non e'
deterministico e non lo sara' mai**. Un menu generato due volte sono due menu
diversi, correttamente. Quindi qui non si asserisce mai *il menu*: si
asserisce cio' che di qualunque menu deve essere vero.

La specifica esiste gia' ed e' la sezione **«Regole non negoziabili»** del
`CLAUDE.md` di radice: una suite di test scritta in prosa. Questi file la
trasformano in asserzioni.

## I tre tier, e quanto costano

| tier | cosa fa | costo | quando gira |
|---|---|---|---|
| **1 — lint dei contratti** | `lint_dati.py`: ogni YAML e' leggibile, gli id della dispensa esistono nel paniere, ogni prezzo ha data e fonte, nessun deperibile fra gli avanzi, nessuno stato di cella fuori vocabolario | zero token | sempre, CI compresa |
| **2 — il giro completo** | `loop_runner.py`: `claude -p` headless su una casa sintetica, settimana → spesa → prepara → correggi → postmortem, poi le proprieta' asserite sugli artefatti | token veri | a mano, prima di una release |
| **3 — il giudizio** | `giudizio.py`: il menu e' *buono*? equilibrato, vario, plausibile un mercoledi' sera | token veri | ogni tanto |

**Il tier 3 non puo' far fallire la suite**, ed e' la regola piu' importante
di questa pagina. Esce sempre 0. Una suite che diventa rossa a caso viene
ignorata entro due settimane, e una suite ignorata e' peggio di nessuna suite:
riporta verde su un motore rotto.

## Come si lanciano

```bash
python3 tests/test_lint.py            # tier 1 + i test del linter stesso
python3 tests/lint_dati.py            # tier 1 sui tre fixture
python3 tests/lint_dati.py ~/casa     # tier 1 su una casa vera
```

```bash
python3 tests/loop_runner.py --dry-run              # mostra cosa farebbe, non spende
python3 tests/loop_runner.py --fixture famiglia
python3 tests/loop_runner.py --fixture tutti --lavoro /tmp/lunario-test
python3 tests/loop_runner.py --fixture single --fasi settimana
```

```bash
python3 tests/scenari.py --dry-run                  # gli scenari avversi
python3 tests/scenari.py --scenario dispensa-vuota
python3 tests/scenari.py --scenario tutti
```

```bash
python3 tests/giudizio.py /tmp/lunario-test/famiglia/settimane/2026-W34-*.md
```

Il runner carica il motore da questo repo con `--plugin-dir`: **non serve
avere il plugin installato**, e si testa il codice che si ha davanti, non
quello dell'ultima release.

## Cosa vuol dire un fallimento

| tier | esito | cosa significa |
|---|---|---|
| 1 | errore | il contratto e' violato: un file scritto da una skill non ha la forma dichiarata in `CLAUDE.md`. E' sempre un bug |
| 1 | avviso | qualcosa e' sospetto ma potrebbe essere legittimo (un formaggio negli avanzi, un menu di storico che non esiste piu'). Non fa fallire |
| 2 | `NO` | una proprieta' del giro e' saltata. La riga dice quale regola, e in quale fase |
| 2 | `-` | non verificabile: il file non c'era, o la forma non si e' lasciata leggere. Non fa fallire, ma troppi `-` vogliono dire che il runner sta guardando il posto sbagliato |
| 3 | qualunque cosa | un'opinione. Non fa fallire, mai |

I codici delle violazioni del tier 1 sono **stabili**: i test asseriscono sui
codici, mai sul testo del messaggio, cosi' riformulare un messaggio non rompe
niente.

## Le tre case sintetiche

Vivono in `fixtures/`, e sono **l'unica eccezione alla regola «nessun dato
personale in git»**. Regge perche' sono dichiaratamente finte, e devono
restare finte a colpo d'occhio: nomi come `Adulto1` e `Solo1`, numeri tondi,
**nessun EAN** (un codice a barre inventato somiglierebbe a un prodotto vero),
nessuna fonte `openfoodfacts:`. Ogni `profilo.yaml` si apre con la riga che lo
dichiara, e `test_lint.py` verifica che sia ancora li'.

| fixture | cosa stressa |
|---|---|
| `single` | una persona, `dieta: true`, dispensa magra, `intervista: minima`. E' dove porzioni e pavimento delle 1200 kcal mordono, e dove meta' delle sezioni del profilo sono legittimamente assenti |
| `famiglia` | quattro persone, due bambini di cui uno `selettivo`, merende, pasto libero, ristorante fisso. **Tutti e sei gli stati di cella** in gioco |
| `coppia-dispensa-profonda` | due persone, nessuno a dieta, una cinquantina di prodotti fissi. E' la casa che ricompra cio' che ha gia' |

Piu' `fixtures/scontrino/`, uno scontrino sintetico in PDF (generato da un
`.txt` con `genera_pdf.py`, stdlib pura) che contiene apposta: righe che
corrispondono, una sostituzione di formato, una riga mai vista, un prodotto
della lista che manca, e del non alimentare da tenere fuori dai totali. Meta'
del valore di `lunario:spesa` sta in cosa fa con uno scontrino che non torna.

## Il sottoinsieme YAML, e perche' e' stretto

`minyaml.py` legge i file con la sola stdlib — regola del progetto: zero
dipendenze. Copre il sottoinsieme che il motore scrive davvero: mappe e liste
annidate, scalari, mappe e liste inline nelle forme dei template. Non copre
ancore, scalari multi-riga, documenti multipli.

Un file che non si lascia leggere e' segnalato come violazione invece di
essere interpretato a forza: **la semplicita' di questi file e' essa stessa
parte del contratto**, perche' a scriverli e rileggerli sono dei modelli.

Una divergenza deliberata da YAML 1.1, e vale la pena saperla: `no`, `yes`,
`on`, `off` restano **stringhe**. Nel contratto di Lunario `no` e' uno stato
di cella (`merenda: no`), non un booleano — un parser standard leggerebbe
quella riga come `False`, cioe' al contrario. Se un giorno qualcosa qui dentro
dovesse usare PyYAML, e' il primo punto in cui si romperebbe.

## Quello che questi test non prendono

Se il menu e' appetitoso. E' giudizio, non asserzione, e il tier 3 ammorbidisce
la distanza senza chiuderla. Il segnale vero per quello resta dov'era: i voti
in `storico.yaml`, dati da chi ha mangiato.
