# Lunario — menu settimanale e spesa

Sistema per generare ogni settimana un menu ipocalorico di famiglia e la lista
della spesa in **confezioni reali da comprare**, non in grammi astratti, con
postmortem settimanale per ritarare quantita', piatti, prezzi e budget.

Questo repo contiene SOLO il motore, condivisibile. Tutti i dati personali
(profilo, ritmi, prodotti, storico, menu generati) vivono in `dati/` e
`settimane/`, escluse da git. Primo avvio: la skill `lunario:profilo`.

## Nessuna dipendenza da un supermercato

Scelta di progetto, non provvisoria: il sistema **non** si integra con nessun
servizio di spesa online, non fa scraping, non ha abbonamenti. Due sole fonti:

| dato | fonte | costo | quando |
|---|---|---|---|
| formato confezione, kcal, proteine | API pubblica Open Food Facts | gratis | una volta per prodotto, poi in cache |
| prezzo pagato davvero | scontrino PDF dell'utente | gratis | al postmortem |

Il prezzo dello scontrino batte qualsiasi listino: contiene gia' promozioni e
sconti fedelta'. Conseguenza accettata: il prezzo e' noto **il ciclo dopo**, e
il menu non puo' essere costruito sulle offerte della settimana corrente.

## I livelli di stato, una skill ciascuno

Confonderli e' il modo piu' rapido di ottenere un sistema che dimentica o che
non impara. Ogni skill scrive un livello solo.

| skill | livello | scrive | cadenza |
|---|---|---|---|
| `lunario:profilo` | stabile | `dati/profilo.yaml` | una volta |
| `lunario:ritmi` | dichiarato | `dati/ritmi.yaml`, `dati/note.md` | quando cambia la vita |
| `lunario:settimana` | effimero | `settimane/<ISO>/contesto.yaml` | ogni lunedi' |
| `lunario:menu` | — (consuma tutto) | `settimane/<ISO>.md`, `dati/dispensa.yaml` | ogni lunedi' |
| `lunario:correggi` | effimero | `settimane/<ISO>.md` (giorni residui) | quando cambia qualcosa |
| `lunario:postmortem` | appreso | `dati/storico.yaml`, `dati/prodotti.jsonl` | domenica |

L'utente ne invoca due: `lunario:settimana` il lunedi' e `lunario:postmortem`
la domenica. `lunario:menu` viene chiamata dalla prima e non va invocata a
mano; le altre servono quando serve.

Regola di confine: **il sistema non tocca mai i livelli dichiarati**. Profilo,
ritmi e note li scrive solo l'utente (la skill puo' proporre). Tarature,
dispensa e prezzi li scrive solo il sistema.

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

Poi, nella cartella dove si vuole tenere i propri dati, si lancia
`lunario:profilo` e il sistema guida il resto.

## Contratti dati

### dati/prodotti.jsonl — il paniere, una riga JSON per prodotto

Non e' il catalogo del supermercato: sono i 40-50 prodotti che la famiglia
compra davvero. Si popola da solo, settimana dopo settimana.

```json
{"id": "pasta-integrale-500", "nome": "Fusilli integrali", "ean": "8002330121556",
 "formato_g": 500, "tipo": "confezione", "reparto": "dispensa",
 "kcal_100g": 348, "proteine_100g": 13.5,
 "alias_scontrino": ["FUSILLI INTGR 500", "PASTA INT.500G"],
 "prezzi": [{"data": "2026-08-14", "eur": 1.19}],
 "fonte_nutrienti": "openfoodfacts:8002330121556"}
```

- `tipo`: `confezione` (formato fisso, l'avanzo va in dispensa) ·
  `peso` (banco: si compra al grammo, nessun arrotondamento) ·
  `pezzo` (uova, vasetti: l'unita' e' il pezzo)
- `formato_g`: grammi o ml per confezione. `null` per il tipo `peso`
- `alias_scontrino`: sigle viste sugli scontrini, riconosciute ai giri dopo
- `prezzi`: serie storica, mai sovrascritta. L'ultimo elemento e' il corrente
- `fonte_nutrienti`: `openfoodfacts:<ean>` oppure `crea` se generico. Un campo
  nutrizionale senza fonte non esiste

### dati/dispensa.yaml — cosa e' rimasto

```yaml
aggiornata: 2026-08-14
avanzi:
  pasta-integrale-500: 400      # grammi residui
  ceci-lessati-400: 1           # pezzi interi per tipo `pezzo`
```

Solo prodotti non deperibili (fascia `[fine]` di `kb/deperibilita.md`). Il
fresco avanzato non e' un credito: e' immondizia fra tre giorni.

### dati/ritmi.yaml — gli orari ricorrenti

```yaml
settimana:
  martedi:
    Adulto2:
      pranzo: fuori_trasportabile   # fuori_trasportabile | fuori_autonomo | casa
      cena_entro_min: 25            # tempo reale ai fornelli quel giorno
```

### settimane/<ISO>/contesto.yaml — l'eccezione di questa settimana

Stessa grammatica di `ritmi.yaml`, ma vale una settimana sola e si sovrappone
ai ritmi. Effimero per design: non si accumula, non si impara.

### dati/storico.yaml

```yaml
tarature:                  # stato appreso: letto SEMPRE prima di generare
  porzioni_g: {}           # per persona e alimento, default da kb/porzioni-standard.md
  piatti_esclusi: []       # bocciati definitivamente
  piatti_preferiti: []
  budget_settimana_eur: null
settimane:
  - settimana: 2026-W34
    menu: settimane/2026-W34.md
    spesa_stimata: 92.50
    spesa_reale: null      # dallo scontrino, al postmortem
    scarto_per_riga: []    # dove la stima ha sbagliato, non solo di quanto
    avanzi: []
    bocciati: []           # piatto + chi l'ha bocciato
    promossi: []
    note: ""
```

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

## Flusso operativo

### Generazione (lunario:menu)

1. Contesto: `profilo.yaml`, `ritmi.yaml`, `note.md`, `storico.yaml` (tarature
   e piatti delle ultime 2 settimane), `dispensa.yaml`, e il contesto della
   settimana (se manca, chiamare `lunario:settimana`)
2. Menu 7 giorni: piatti da `kb/piatti.md` meno le esclusioni, ordine dei
   giorni da `kb/deperibilita.md`, porzioni da `kb/porzioni-standard.md`
   scalate su tarature e kcal. Ritmi e contesto vincolano PRIMA della scelta:
   un giorno con pranzo fuori trasportabile non riceve un piatto da scaldare
3. Fabbisogno: per ogni ingrediente, grammi totali della settimana
4. **Confezioni**: fabbisogno − dispensa → confezioni da comprare, secondo
   `kb/confezioni.md`. La lista dice «2 pacchi da 500 g», mai «1050 g»
5. Salva `settimane/<ISO>.md`, aggiorna `dispensa.yaml` con gli avanzi
   previsti, aggiungi la voce a storico con `spesa_stimata`

### Correzione in corsa (lunario:correggi)

A meta' settimana cambia qualcosa: una cena salta, un piatto non va, arriva un
ospite. **La spesa e' gia' fatta**: il vincolo non e' piu' il budget, e' cosa
c'e' in casa. Quindi si chiede cosa deve cambiare e cosa c'e' in frigo, si
rigenerano solo i **giorni residui** riusando gli ingredienti gia' comprati, e
si propone una spesa integrativa solo se e' inevitabile — poche righe, dette
come tali. I giorni gia' passati non si riscrivono mai.

### Postmortem (lunario:postmortem)

Tre domande — avanzi, bocciati/promossi e da chi, scontrino — poi ritara:
- stesso avanzo per 2+ settimane -> riduci la porzione in `tarature`
- piatto bocciato 1 volta -> fuori rotazione 3 settimane; 2 volte -> escluso
- scontrino PDF -> prezzi in `prodotti.jsonl`, `spesa_reale` e
  `scarto_per_riga` in storico, dispensa corretta sul reale

### Note operative

`dati/note.md` contiene i vincoli liberi non riducibili a un orario («forno
guasto»). Lette a ogni lancio, applicate prima di ogni altra scelta. In chat
«segnati che ...» le aggiunge (temporanee con `[fino al AAAA-MM-GG]`). Una
nota non e' una taratura: la tocca solo l'utente, la skill puo' solo proporre.

## Regole non negoziabili

- Mai piani sotto 1200 kcal/giorno/persona
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
