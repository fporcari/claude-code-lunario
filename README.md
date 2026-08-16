<p align="center">
  <img src="loghi/lunario-logo.png" alt="Lunario" width="420">
</p>

<p align="center">
  <em>Il menu della settimana e la spesa in confezioni vere, non in grammi astratti.</em>
</p>

---

Lunario è un plugin per [Claude Code](https://claude.com/claude-code): il lunedì
gli racconti la settimana che hai davanti, lui ti prepara il menu dei sette
giorni e la lista della spesa; la domenica gli dici com'è andata e lui impara.

Non è un'app di diete con le opzioni: è un motore di regole universali — la
deperibilità del frigo, le porzioni CREA, i divieti — più un profilo che
descrive **la tua** famiglia. Cambiare vita si fa cambiando un file.

Di fatto è un *workflow domestico*: fasi in sequenza, con lo stato su file di
testo invece che nella memoria della chat, e un passo di verifica che ritara
quello dopo.

## Il giro della settimana

Cinque momenti. Ognuno legge quello che ha lasciato il precedente e scrive per
il successivo — nessuno deve ricordarsi niente, perché niente vive nella chat.

```
   LUNEDÌ                RITIRO              MENTRE CUCINI        DOMENICA
   ──────                ──────              ─────────────        ────────
 lunario:settimana → lunario:spesa    →   lunario:prepara   →  lunario:postmortem
        │                  │                     │                    │
   racconti la        dai lo scontrino      cucini il piatto     dici com'è andata
   settimana +        in PDF                di oggi              (o non lo dici:
   sei righe di                                                  il diario c'è già)
   dispensa da
   correggere
        │                  │                     │                    │
        ▼                  ▼                     ▼                    ▼
   menu + spesa       prezzi veri,          spunte sul menu,     porzioni, rotazione
   in confezioni      sostituzioni,         voto del cuoco,      e budget ritarati
   → PREVENTIVO       → CONSUNTIVO          diario del giorno    → si riparte

    una volta sola:   ┌──────────────────────────────┐
    lunario:profilo   │  in qualsiasi momento:       │
    lunario:inventario│  lunario:correggi            │
                      │  salta una cena, arrivano    │
                      │  ospiti, i figli protestano  │
                      └──────────────────────────────┘
```

Non serve ricordare i nomi delle skill: «prepariamo la settimana», «ho fatto la
spesa», «cosa cucino stasera», «com'è andata» bastano a far partire quella
giusta.

## La differenza

Un generatore di menu ti dice «1050 g di pasta». Lunario ti dice:

```
- [ ] Fusilli integrali — 2 × 500 g · 2,38 €
      → mer cena · ven pranzo        (ne avanzano 400 g: sono in dispensa)
```

La settimana dopo quei 400 g li sottrae dalla spesa. È la conversione da grammi
a confezioni reali, con una dispensa che si ricorda cosa hai in casa.

E il menu segue l'orologio del frigo: il pesce lunedì, le foglie martedì, i
legumi il venerdì. Gli ingredienti si consumano nell'ordine in cui si rovinano,
che è la regola che azzera lo spreco prima ancora di parlare di budget.

## La dispensa profonda, e i due errori che chiude

Una casa non parte da zero. Ne fa due, di errori, e sono opposti:

| errore | cosa costa | quanto lo vedi |
|---|---|---|
| **compri quello che hai già** | soldi fermi, roba che scade | te ne accorgi svuotando la busta |
| **il quinto pacco della stessa cosa** | cronico | **mai**: nessuno conta le bottiglie di passata |

Il secondo si risolve col dato più grezzo che esista — un tetto per prodotto — e
questa asimmetria è la licenza a **non** costruire un magazzino. Perché il
magazzino, quello vero, muore sempre allo stesso modo: si riempie a mano per una
settimana, poi una volta, poi mai più — e un inventario aggiornato a metà è
*peggio* di nessun inventario, perché smetti di crederci.

Quindi: `lunario:inventario` una volta, raccontando o mandando le foto degli
scaffali. Niente da compilare.

```yaml
# dati/dispensa.yaml
scorte:
  pasta-integrale-500:
    quantita: 4          # confezioni intere, oppure: pieno | medio | poco | finito
    soglia: 2            # sotto, torna in lista
    massimo: 6           # sopra, non te la rimetto in lista. Mai
    visto: 2026-08-16    # quando qualcuno l'ha guardata davvero
    rotazione: alta      # ogni quanto te la richiedo
```

Nessuno pesa la farina, e non serve: «tanto», «poco», «due pacchi» bastano a
decidere se una riga della spesa serve o no.

**Poi la dispensa invecchia, e il sistema lo sa.** Il consumo si osserva solo
dove passi da `lunario:prepara`, e da lì non passano le colazioni, i panini e i
caffè: quindi il motore crede sempre di avere *più* di quello che c'è. Per
questo non memorizza una certezza, ma **quanto è vecchia la sua convinzione**:

| il dato è | cosa fa il menu |
|---|---|
| **fresco** | lo scala dalla spesa, in silenzio |
| **invecchiato** | lo scala, ma te lo dice: «conto sui 2 pacchi di riso visti il 12 luglio» |
| **stantio** | non ci si fida: te lo chiede lunedì, prima di generare |

E il lunedì non è un censimento. Sono **sei righe**, scelte dove l'incertezza
incontra l'impatto, presentate come un elenco da correggere:

> Dovreste avere: la pasta a 4 pacchi, la passata a `poco`, 2 scatole di tonno,
> il riso `pieno`, e il caffè non lo vedo da luglio. Cosa è sbagliato?

Se tagli corto non perdi niente: quella fetta invecchia e torna il lunedì dopo,
più in alto. È il conteggio a rotazione delle cucine professionali, che sulla
dispensa secca non tengono un inventario perpetuo — fissano un livello e contano
un pezzo per volta.

Infine il numero che rende sensato averlo fatto: **quanto vale la roba che avete
in casa**, dai prezzi dei vostri scontrini. Ed è anche la frase che ferma il
quinto pacco — detta come un dato, mai come un rimprovero:

```
Passata di pomodoro: ne servirebbe 1 bottiglia, ma ne avete già 6 (tetto: 6).
Non la metto in lista.
```

## Il giorno non è «pranzo e cena»

È una griglia **pasto × persona**, e ogni cella dice cosa succede davvero:

| stato | si pianifica | si compra | conta nelle kcal | è spesa |
|---|---|---|---|---|
| `casa` | sì | sì | sì | nel menu |
| `trasportabile` | sì, e deve viaggiare | sì | sì | nel menu |
| `libero` | sì, **senza vincolo calorico** | sì | no | nel menu |
| `ristorante` | no | no | no | fuori menu, **ma registrata** |
| `fuori` | no | no | no | no (mensa, bar, ospite) |
| `no` | no | no | no | no (quel pasto non lo fa) |

Tre file la scrivono, e vince sempre il più specifico:

```
profilo.yaml          «i bimbi fanno merenda, gli adulti no»        sempre
    ↓
ritmi.yaml            «il martedì pranzo fuori»                     ogni settimana
    ↓
contesto.yaml         «questo giovedì si cena al ristorante»        questa volta
```

Da qui vengono quattro cose che nessun generatore di menu fa. **Chi è a dieta
e chi no convivono nella stessa cena**, stesso piatto e porzioni diverse — e
se non è a dieta nessuno, la parola «deficit» non compare mai. **Il pasto
libero esiste e non si compensa**: non si taglia il pranzo perché la sera c'è
la pizza, che è il meccanismo per cui le diete diventano insopportabili.
**Colazione, spuntino e merenda contano** — due merende da 200 kcal per due
bambini fanno 2800 kcal a settimana, e un target che le ignora è un target
falso. E **il ristorante non sparisce dai conti**: non è spesa di Lunario, ma
è spesa alimentare, e finisce in un campo suo che risponde alla domanda che
nessun altro risponde — quanto costa mangiare, non quanto costa la spesa.

## Un lunedì qualunque

> **Tu:** prepariamo la settimana
>
> **Lunario:** Dal calendario: giovedì cena di lavoro tua, mercoledì nuoto dei
> bimbi fino alle 18.30 — quindi giovedì cucino solo per tre e mercoledì serve
> una cena pronta in 25 minuti. Torna? E ditemi se c'è una voglia, o qualcosa
> che non volete più vedere.
>
> **Tu:** torna. Siamo stufi del merluzzo, e venerdì viene a cena mia madre
>
> **Lunario:** Il merluzzo esce di rotazione per tre settimane. Venerdì
> aggiungo un posto a tavola, porzioni intere. Prima di scrivere il menu:
> dovrei avere in congelatore due confezioni di filetti di branzino e mezzo
> chilo di pollo a fette — cosa c'è che non ho segnato?
>
> **Tu:** c'è anche un pezzo di scamone di giugno che va smaltito
>
> **Lunario:** Allora lo metto sabato, ed è la ragione per cui questa settimana
> la carne è tre volte invece di due: te lo dico perché il tetto è una vostra
> preferenza, non una regola — se preferisci, lo sposto alla prossima. Il
> branzino copre il lunedì, quindi al banco pesce non compri niente.
>
> **Tu:** ok. E la passata? Ne prendo sempre
>
> **Lunario:** Ne avete già sei bottiglie, che è il tetto che avevate messo:
> non te la rimetto in lista. Non è un rimprovero, è che sono nove euro fermi
> in credenza.
>
> **Tu:** ok. Ai bimbi le lenticchie di martedì non vanno giù
>
> **Lunario:** Le tengo, ma martedì la base dei bimbi è pasta al pomodoro e
> le lenticchie restano in tavola senza trattative. Ecco la settimana — il
> pesce lunedì che è fresco, il minestrone venerdì che fa piazza pulita del
> frigo — e la lista: 2 pacchi di fusilli Barilla da 500 g, la passata Mutti
> da 700 g, il Grana Padano che avete già in casa non lo ricompro…

<!-- SEGNAPOSTO: screenshot del menu HTML di una settimana vera.
     Lo genera l'autore da settimane/<ISO>-<titolo>.html e lo committa a mano.
     Non generarlo in modo sintetico: un menu inventato violerebbe la
     regola «mai inventare» che regge il progetto. -->

## Cosa esce

Due file con lo stesso contenuto e due mestieri diversi. Il markdown è la
fonte, e porta lo stato di avanzamento della settimana:

```markdown
---
stato: preventivo
titolo: Commando
---

## Lunedì 18 agosto
colazione: yogurt greco, frutta, fette biscottate · merenda bimbi: pane e marmellata
- [ ] pranzo — Insalata di farro, pomodorini e mozzarella      450 / 380 kcal
- [ ] cena — Filetti di branzino al forno con patate           520 / 430 kcal

## Dal congelatore
- [ ] Filetti di branzino, 2 × 250 g → lun cena
      in frigo domenica sera (8-12 h)

## La spesa — ortofrutta
- [ ] Zucchine — 600 g · 1,49 €
      → lun cena · gio pranzo

### Non si compra, c'è già
- Branzino al banco, 800 g → i due pacchi nel congelatore (lun cena)
```

L'HTML è lo stesso menu da stampare e attaccare al frigo — ma soprattutto da
aprire sul telefono al supermercato, dove **la lista si spunta col dito** e le
spunte restano dov'erano anche se ricarichi la pagina.

Tre dettagli che sembrano piccoli e non lo sono:

- **ogni riga della spesa dice a cosa serve** (`→ lun cena · gio pranzo`), così
  «non c'erano le zucchine» diventa subito «è il lunedì da ripensare»
- **quello che è già in casa esce dalla lista, e l'uscita si dice**: un banco
  pesce vuoto sembra una dimenticanza finché non si sa perché
- **lo scongelamento ha una riga sua**, la sera prima. È l'unico pezzo di
  settimana che il giorno stesso non si recupera: un piatto si sposta, un forno
  si aspetta, una bistecca ancora dura alle otto di sera è una cena che salta

E ogni settimana ha un nome — il tuo filone: canzoni dei Beatles, pesci
tropicali, film. Il nome sta anche nel file, perché è così che la chiami:

```
settimane/
├── 2026-W34-commando.md
├── 2026-W34-commando.html
└── 2026-W34-commando/
    ├── contesto.yaml     gli impegni di quella settimana
    └── diario.yaml       cosa avete mangiato davvero
```

L'ISO davanti tiene l'ordine alfabetico uguale all'ordine cronologico; il
titolo dietro serve a te, che due mesi dopo non dirai mai «apri 2026-W34».

## Preventivo e consuntivo

Un menu ha due stati, e la differenza non è l'approvazione di qualcuno: è
**quanto di ciò che c'è scritto è verificato**.

| | `preventivo` | `consuntivo` |
|---|---|---|
| **quando** | dal lunedì fino alla spesa | dopo lo scontrino |
| **cosa dice** | quello che volete mangiare | quello che c'è davvero in casa |
| **i numeri** | stime: formati, prezzi, e i piatti stessi | prodotti veri, formati veri, prezzi pagati |
| **come si usa** | documento di lavoro: la lista si spunta al supermercato | registro: non c'è niente da spuntare |
| **chi lo scrive** | `lunario:menu` | `lunario:spesa`, e nessun altro |

Il «confermo» tuo non promuove niente, e vuol dire una cosa sola: *sto andando
a fare la spesa adesso*. Mettere il timbro di definitivo su un totale fatto di
prezzi della settimana scorsa sarebbe una bugia tipografica.

Il preventivo non si perde: in coda al consuntivo resta il **delta leggibile**
— cosa è cambiato di formato, di prezzo, di piatto — perché lo scarto fra i due
è il dato che la domenica insegna qualcosa, e leggerlo non deve richiedere un
`git diff`.

```markdown
## Scarto dal preventivo
- Fusilli integrali: previsti 2 × 500 g, dati 2 × 400 g — 200 g in meno
- Branzino: non c'era → merluzzo surgelato (giovedì cena)
- Olio EVO: 7,20 € contro i 5,90 dell'ultima volta
```

Se il consuntivo si scosta sempre nello stesso verso per tre settimane — quel
pacco è sempre più grande, quel prodotto non c'è mai — non è sfortuna, è un
paniere da correggere.

## Come impara, in concreto

Due domeniche di fila la stessa risposta al postmortem — «è avanzata pasta» —
e in `dati/storico.yaml` succede questo:

```yaml
# prima
tarature:
  porzioni_g: {}

# dopo
tarature:
  porzioni_g:
    Adulto1:
      pasta: 70      # era 80, avanzata due settimane su due
```

Dal lunedì successivo il fabbisogno si calcola sulla porzione nuova — e
siccome la lista ragiona in confezioni, prima o poi quei grammi in meno
diventano un pacco in meno. Nessuno ha aperto un file, nessuno ha «impostato»
niente: il sistema ha guardato la pentola.

Funziona allo stesso modo su tutto il resto:

| cosa succede, due o tre volte | cosa cambia da solo |
|---|---|
| un piatto avanza | la porzione scende in `tarature.porzioni_g` |
| un piatto viene bocciato a tavola | fuori rotazione 3 settimane, poi escluso |
| un piatto «da 20 minuti» ne prende 40 | il tempo reale entra nei voti del cuoco, e quel piatto smette di finire di mercoledì |
| il giovedì si mangia sempre fuori | te lo dice, e propone di scriverlo nei ritmi. Propone: non lo scrive |

## Le regole di casa, e dove vanno

Prima o poi salta fuori una regola che nessuno aveva detto — «l'hummus lo
compriamo pronto», «carne a pranzo *e* a cena no», «la merenda dei bimbi è
salata». Il posto in cui finisce decide se servirà ancora fra sei mesi:

| il sistema deve controllarlo da solo? | dove va | esempi |
|---|---|---|
| **sì**, è un campo che filtra o conta | `dati/profilo.yaml` | esclusioni, quante volte carne o pesce, ripetizioni vietate |
| **no**, ma va letto prima di ogni menu | `dati/note.md` | l'hummus si compra pronto, niente integrale, forno guasto |
| **no**, è per l'umano che apre la cartella | il `CLAUDE.md` di casa | come si lancia una skill, cos'è la griglia |

Non devi indovinare: lo dici in chat e la skill lo mette dove va, dicendoti
dove l'ha messo. Il setup chiede anche le **tolleranze** — le ripetizioni che
sopportate, se gli avanzi tornano in tavola come sono o solo trasformati,
quanto sono rigidi i tetti di carne e pesce — perché sono esattamente le regole
che, se non chieste, si scoprono correggendo un menu già scritto.

E un tetto sa dire quanto è un tetto:

```yaml
max_pasti_carne_settimana: {valore: 3, rigidita: preferenza}
# preferenza -> si supera quando c'è una ragione, e la ragione si dichiara
# vincolo    -> non si supera. È il default di un numero scritto da solo
```

## Il peso, se lo vuoi — e come non diventa un giudizio

Chi è a dieta può farsi chiedere il peso dal postmortem della domenica. È
opzionale, si sceglie al setup e **si può saltare ogni volta**, senza dover
spiegare niente: se non rispondi, Lunario va avanti e non registra nemmeno che
hai saltato.

Quello che ne fa è l'unica cosa che ha senso farne: **il trend su tre
settimane**, mai la singola misura.

| quante pesate | cosa fa |
|---|---|
| meno di 3 | registra e tace: non c'è ancora un trend |
| da 3 in su | media mobile su 3 settimane contro le 3 precedenti |
| calo 0,3-0,5 kg/sett | è il ritmo previsto: mezza riga ogni tanto, non ogni domenica |
| oltre 1 kg/sett per 3 settimane | te lo dice e ti manda dal medico: lì il ruolo di questo sistema finisce |
| fermo per 3+ settimane | propone di rivedere porzioni o target. Come ipotesi, non come diagnosi |
| obiettivo raggiunto | propone il mantenimento, invece di tenerti a dieta per sempre |

Il peso oscilla di 1-2 kg per acqua, sale e sonno, e leggere la pesata di
stamattina come un voto è il modo più rapido di mollare tutto a febbraio. Non
commenta mai il numero: niente «bravo», niente «sgarro», niente «recuperare».
Riporta un andamento, non giudica una persona.

## Le ricette che vi passano

Un piatto che vi ha segnalato qualcuno si aggiunge dicendolo — «me l'ha passata
Marta», anche con un link o una foto. Finisce in `dati/ricette.md`, e da lì è un
piatto come gli altri: entra nel menu, prende i voti, esce di rotazione se non
piace.

```markdown
## Pasta con crema di zucchine e menta [meta] (B: pasta in bianco)
- kcal: 520 a porzione — dichiarate dalla fonte
- per 4: 320 g di pasta, 800 g di zucchine, mezzo mazzetto di menta, 60 g di grana
- fonte: me l'ha passata Marta
- nota: le zucchine vanno frullate calde
```

Le calorie seguono la regola dei prezzi: se c'erano sulla fonte valgono così
come sono, altrimenti le stima Lunario dalle tabelle CREA e lo dice.

## Nessuna dipendenza da un supermercato

Scelta di progetto, non provvisoria: niente integrazioni con servizi di spesa
online, niente scraping, niente abbonamenti. Due sole fonti, entrambe gratuite:

| dato | da dove | quando |
|---|---|---|
| formato della confezione, kcal, proteine | [Open Food Facts](https://world.openfoodfacts.org) | una volta per prodotto, poi in cache |
| prezzo pagato davvero | il tuo scontrino in PDF | al ritiro della spesa |

Il prezzo dello scontrino batte qualsiasi listino, perché contiene già le
promozioni e gli sconti fedeltà che hai avuto davvero. E siccome la spesa si
ritira *prima* di cominciare a cucinare, lo scontrino serve a qualcosa di più
che ai prezzi: dice cosa non è arrivato, così l'alternativa si trova il lunedì
e non davanti al frigo il giovedì sera.

Su quello che manca decidi tu, e le strade sono due: **cambiamo il piatto** con
quello che avete in casa, oppure **te lo procuri tu** prima del giorno in cui
serve. Nel secondo caso il rimando non resta in chat — viene scritto, e mentre
cucini quel piatto te lo ricorda una volta sola.

Uno scontrino però non è la spesa di Lunario. Viene diviso in tre, e solo il
primo gruppo si confronta con la stima:

```
scontrino ──┬── quello che era nel menu        -> spesa_reale, si confronta
            ├── alimentare fuori lista         -> spesa_extra_alimentare
            └── detersivi, casa, roba di altri -> fuori da tutti i conti
```

Le righe te le presenta **con le caselle già spuntate** — «era in lista», «già
nel paniere», «mai visto» — e tu correggi in una parola. Anche a metà: sei
yogurt di cui tre della suocera valgono mezza riga. E ciò che compri altrove —
il pane dal panettiere, le uova dal contadino — dopo la prima volta smette di
risultare mancante.

### Quando il database non ti conosce

Open Food Facts è collaborativo, e sulla marca del supermercato la copertura
è reale ma parziale: interrogando la sua
[API di ricerca](https://world.openfoodfacts.org/api/v2/search?brands_tags=esselunga&fields=code&page_size=1)
(14 agosto 2026) i prodotti censiti sono circa 2.100 per Esselunga, 3.200 per
Coop, 2.900 per Conad e 3.000 per Carrefour in Italia, mentre Lidl ne ha 1.500
a proprio nome più quelli dei suoi marchi (la sola Italiamo supera il
migliaio). Sembrano numeri discreti, ma anche quando il prodotto c'è manca
spesso proprio il dato che serve a Lunario: dei prodotti Esselunga censiti,
meno della metà ha il formato della confezione compilato.

Per questo la degradazione è un percorso previsto, non un incidente — e a ogni
gradino si dichiara, mai si inventa:

```
codice a barre su OFF  ->  nome su OFF  ->  ricerca web  ->  lo chiedi a me
                                                                    │
                                        (nessuno lo sa) ────────────┴──> riga in
                                                                grammi, marcata
                                                            «formato da verificare»
```

Tu sei la fonte migliore, non l'ultima spiaggia: il pacco ce l'hai in dispensa,
il formato sta scritto sopra e le calorie sull'etichetta. Il dato che dichiari
entra nel paniere con la sua provenienza e vale quanto uno letto dal database.
Lo stesso vale per gli scontrini: se il PDF non si lascia leggere, si va a voce
— i prezzi che ricordi entrano come «dichiarati», quelli che nessuno ricorda
restano buchi. Una riga onesta vale più di una confezione inventata.

## Installazione

```bash
claude plugin marketplace add fporcari/claude-code-lunario
claude plugin install lunario@claude-code-lunario
```

Poi apri con Claude Code la cartella dove vuoi tenere i tuoi dati e lancia
`lunario:profilo`: l'intervista crea `dati/` e `settimane/` e ti guida. Puoi
scegliere il percorso breve — tre domande e il primo menu subito — o
l'intervista completa, che è più lunga ma poi non torna più.

Se in casa tieni sempre le stesse quaranta cose, un giro di `lunario:inventario`
ti ripaga alla prima spesa. Non è obbligatorio, e non si rifà: senza, il sistema
funziona identico e la lista è solo più lunga.

Per aggiornare il motore quando esce una versione nuova:

```bash
claude plugin marketplace update claude-code-lunario && claude plugin update lunario@claude-code-lunario
```

Poi **riavvia Claude Code**: le skill si caricano all'avvio, e una sessione già
aperta continuerebbe con quelle vecchie. La tua cartella non devi toccarla: si
allinea da sola alla prima skill che lanci, e cosa è cambiato lo trovi in
[CHANGELOG.md](CHANGELOG.md).

## La cartella si aggiorna da sola

Il motore esce in versioni nuove; la tua cartella si allinea da sé. La prima
skill che parte guarda il timbro in `dati/versione.yaml` e, se i file sono di una
versione precedente, li porta avanti **prima** di fare quello che le hai chiesto.
Non c'è niente da lanciare.

Tre comportamenti, e il terzo è quello che conta:

| il cambiamento è | cosa succede |
|---|---|
| **additivo** — una sezione nuova e vuota | si applica in silenzio |
| **una riscrittura** — `fuori_trasportabile` → `trasportabile` | si applica, e te lo dice in una riga. Per tornare indietro c'è `git` |
| **serve una tua risposta** — un nome, una preferenza | **non si applica niente**: il campo resta assente, la cartella funziona lo stesso, e te lo chiede quando serve |

Da cui la regola che vincola tutto quello che verrà scritto in futuro: **ogni
contratto nuovo deve degradare bene quando manca**. Una cartella che non si
aggiorna mai continua a funzionare — l'aggiornamento la migliora, non è il prezzo
del biglietto.

Le settimane passate non si toccano: sono un registro, e un registro non si
riscrive per farlo somigliare al vocabolario di oggi.

## Le dieci skill

Ne lanci quattro tutte le settimane; le altre partono da sole o quando servono.

| skill | quando | cosa fa |
|---|---|---|
| `lunario:profilo` | una volta | ti intervista: chi siete, obiettivi, esclusioni, cosa tollerate a tavola. Calcola le calorie da peso e altezza, e costruisce la cartella |
| `lunario:ritmi` | quando cambia la vita | la settimana tipo: chi pranza fuori il martedì, quale sera c'è poco tempo |
| `lunario:inventario` | una volta, poi quasi mai | l'inventario di quello che tenete sempre in casa, a voce o dalle foto degli scaffali. Ne ricava soglie e tetti, e ti dice quanto vale |
| `lunario:settimana` | **il lunedì** | legge il calendario, ti chiede impegni, voglie, di cosa sei stufo, e ti fa correggere sei righe di dispensa. Poi genera |
| `lunario:menu` | automatica | i 7 giorni e la lista in confezioni, in markdown e in HTML. Ogni riga dice a quali pasti serve |
| `lunario:spesa` | **al ritiro** | dallo scontrino: prezzi veri, cosa manca, alternative subito. Separa il menu dai detersivi, e da qui il menu non è più una previsione |
| `lunario:prepara` | **mentre cucini** | ingredienti scalati, procedimento, un video se serve, poi difficoltà e voto del cuoco. Prima di cucinare fa anche l'anteprima: com'è questo piatto, qui, per voi |
| `lunario:correggi` | a settimana in corso | cambi idea? Ti propone cosa è rimasto e rifà solo i giorni che restano |
| `lunario:postmortem` | **la domenica** | legge cos'è successo davvero e chiede solo il resto: voti dei commensali e — se vuoi — il peso → ritara porzioni, rotazione e budget |
| `lunario:aggiorna` | automatica | allinea la cartella quando il motore va avanti. Non la invochi: la chiamano le altre |

**I due voti non sono lo stesso voto.** Chi cucina valuta difficoltà e resa
appena finito, e quel dato decide *dove* un piatto può stare nella settimana; i
commensali votano la domenica, e quel dato decide *se* resta in rotazione. Un
piatto amato a tavola può essere insostenibile il mercoledì sera: il primo voto
lo sposta nel weekend, non lo elimina.

## Dove finiscono i tuoi dati

Nella tua cartella, mai in questo repo. Il motore è pubblico, la tua famiglia
no:

```
~/dove-vuoi/lunario/
├── dati/
│   ├── profilo.yaml       chi siete, calorie, esclusioni, tolleranze
│   ├── ritmi.yaml         gli orari che si ripetono
│   ├── note.md            i vincoli che detti a voce
│   ├── ricette.md         i piatti vostri: quelli che vi hanno passato
│   ├── prodotti.jsonl     il tuo paniere: formati, nutrienti, prezzi
│   ├── dispensa.yaml      scorte contate, avanzi calcolati, congelatore
│   ├── versione.yaml      a che versione di Lunario sta questa cartella
│   └── storico.yaml       settimane passate e tarature apprese
└── settimane/             i menu generati, uno per settimana
```

Per tenerli altrove: `LUNARIO_DATI=/percorso/che/preferisci`.

La cartella è anche un **repo git locale, senza remote**: le skill committano
da sole quando hanno finito, così `git log` e `git diff` ti dicono cosa è
cambiato e quando, e si può tornare indietro. Nessun remote viene creato né
proposto — qui dentro ci sono pesi, obiettivi e abitudini di persone reali,
minori compresi, e un repo privato riduce il rischio ma non lo toglie: un dato
caricato non rientra. Per lavorare dal telefono non serve comunque: con
[`claude remote-control`](https://code.claude.com/docs/en/remote-control) la
sessione gira sul computer di casa e la guidi dal telefono, senza spostare un
file. Se il git non lo vuoi, `git: no` nel profilo.

## Come si sa che non si è rotto niente

Le skill sono markdown eseguito da un modello: due menu generati due volte sono
due menu diversi, correttamente. Quindi la suite non asserisce mai *il menu* —
asserisce ciò che di qualunque menu deve essere vero, e quella specifica esiste
già: è la lista dei divieti qui sopra.

| tier | cosa controlla | costo |
|---|---|---|
| **1** | i contratti dei dati: ogni prezzo con data e fonte, nessun deperibile in dispensa, nessuno stato di cella inventato | zero token, gira sempre |
| **2** | il giro intero headless su una casa sintetica, e cosa lascia sui file | token veri, prima di una release |
| **3** | il menu è *buono*? equilibrio, varietà, plausibilità di un mercoledì sera | token veri, ogni tanto |

Il tier 3 **non può far fallire la suite**: esce sempre 0. Una suite che diventa
rossa a caso viene ignorata entro due settimane, e da lì in poi riporta verde
anche su un motore rotto.

```bash
python3 tests/test_lint.py              # zero token
python3 tests/loop_runner.py --dry-run  # mostra cosa farebbe, non spende
```

## Cosa gli è vietato

Un sistema AI affidabile si progetta prima di tutto per ciò che gli è vietato:

- mai inventare prodotti, formati, prezzi o valori nutrizionali — ciò che non
  si trova si dichiara mancante
- mai un prezzo senza data e provenienza: uno letto dallo scontrino e uno detto
  a voce valgono entrambi, purché si sappia quale è quale
- mai piani sotto le 1200 kcal al giorno a persona: sotto quella soglia serve
  un medico, non un modello
- mai un deficit a chi non è a dieta, e mai una parola sul suo peso
- mai compensare un pasto libero, né prima né dopo
- mai ignorare un'esclusione alimentare, nemmeno come ingrediente nascosto
- mai toccare le note e il profilo che hai scritto tu: il sistema può proporre,
  non decidere
- mai commentare il corpo di qualcuno: delle pesate si guarda il trend su tre
  settimane, e la domanda della domenica si può sempre saltare

## Crediti

Porzioni e frequenze dalle [Linee Guida per una Sana Alimentazione, CREA rev.
2018](https://www.crea.gov.it/web/alimenti-e-nutrizione/-/linee-guida-per-una-sana-alimentazione-2018).
Dati prodotto da [Open Food Facts](https://world.openfoodfacts.org), licenza
ODbL.

Le calorie stimate sono indicative, non misure. Lunario non è un dispositivo
medico e non sostituisce il parere di un professionista.
