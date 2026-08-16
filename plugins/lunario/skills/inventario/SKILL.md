---
name: inventario
description: >-
  Fa l'inventario delle scorte di casa — quello che si tiene sempre in
  dispensa, nel congelatore e in frigo fra i non deperibili — e ne ricava
  quantita' approssimative, soglie sotto cui ricomprare e tetti oltre cui non
  comprare piu'. Si racconta a voce o si mandano le foto degli scaffali: non
  c'e' niente da compilare. Da invocare la prima volta, al setup, e poi quando
  l'utente dice "rifacciamo l'inventario", "ho svuotato la dispensa", "quanta
  roba ho in casa", "ti mando le foto della credenza", "quanto vale la roba che
  ho in dispensa", "continuo a ricomprare le stesse cose". NON e' la domanda
  del lunedi' su cosa c'e' in casa: quella la fa lunario:settimana, su una
  fetta di sei righe.
---

# Inventario — cosa questa casa tiene in casa

Serve a chiudere due errori opposti: comprare cio' che c'e' gia', e accumulare
cinque pacchi della stessa cosa. Bande, fiducia e conteggio ciclico stanno in
`${CLAUDE_PLUGIN_ROOT}/kb/scorte.md`; il contratto di `dispensa.yaml` in
`CLAUDE.md`. Qui la procedura.

**Non e' un modulo da compilare, ed e' la cosa piu' importante di questa
pagina.** L'inserimento a mano e' la causa di morte di ogni app di dispensa: si
riempie per una settimana, poi mai piu'. Chi ha cinquanta prodotti in casa non
li digita, e non deve.

## Prima di tutto: la cartella e' allineata?

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tagliando.py --rapido
```

**Se non stampa niente, prosegui senza dire niente.** Se stampa righe `blocca`,
riparale prima: cio' che porta `[si ripara da solo]` con `tagliando.py
--ripara`, un `CONTRATTO_INDIETRO` passando da `lunario:aggiorna`, il resto da
`lunario:tagliando`. Poi torna qui — senza la sezione `scorte` non c'e' dove
scrivere quello che stai per contare.

## 0. Prima di cominciare, dillo

Una riga sola, prima di aprire il congelatore, perche' decide quanto l'utente
si impegna:

> Facciamo il giro: congelatore, dispensa, e del frigo solo le cose che durano.
> Non serve pesare niente — «tanto», «poco», «due pacchi» vanno benissimo. Puoi
> raccontarmelo o mandarmi le foto degli scaffali, come ti viene meglio.

E il perche', in mezza riga, **una volta sola**: serve a non ricomprare quello
che c'e' e a smettere di accumulare la stessa cosa. Non ripeterlo dopo.

## 1. Le tre zone, in quest'ordine

| zona | perche' li' | cosa entra |
|---|---|---|
| **1. congelatore** | e' quello che si dimentica sempre, e' gia' pagato, e spesso e' roba da smaltire | va in `freezer`, con la data di congelamento dove si sa |
| **2. dispensa secca** | e' dove vive l'accumulo, ed e' la zona che scala le quantita' della spesa | va in `scorte` |
| **3. frigo, ma solo i non deperibili** | burro, uova, formaggi stagionati, conserve aperte che durano | va in `scorte` |

**Un surgelato sta in una sezione sola.** Un pacco di filetti e' insieme un
prodotto del paniere e una cosa che si vede aprendo lo sportello: scritto in
tutte e due, verrebbe sottratto due volte e il menu ci costruirebbe sopra una
cena che non esiste. Va in `freezer` quando la data di congelamento conta — e
conta quasi sempre — e in `scorte` solo altrimenti. Mai in entrambe
(`${CLAUDE_PLUGIN_ROOT}/kb/scorte.md`).

**Il fresco non entra, mai.** Solo la fascia `[fine]` di
`${CLAUDE_PLUGIN_ROOT}/kb/deperibilita.md`. Se l'utente nomina la rucola,
prendine nota per il menu di questa settimana e non scriverla: fra tre giorni
non esiste, e pianificarci sopra vuol dire cucinare marcio.

Una zona per volta, e **non interrompere il racconto** per chiedere dettagli:
si annota tutto e si sistema dopo. Chi sta davanti a uno scaffale aperto elenca,
non risponde a domande.

## 2. Dettatura e foto valgono uguale

Non c'e' una strada principale e una di ripiego. In piedi davanti alla credenza,
**parlare e' piu' veloce che fotografare**, e il passaggio telefono → computer e'
attrito vero proprio per le case che ne hanno piu' bisogno.

- **A voce**: l'utente elenca come gli viene — «pasta ne ho tanta, quattro o
  cinque pacchi, poi due scatole di pelati, il riso quasi finito». Tu traduci in
  bande e numeri, non chiedere di essere piu' preciso
- **Con le foto**: vedi il punto 3, che e' un flusso a se'

## 3. Le foto, tutte insieme e una tabella sola

Il flusso giusto separa due momenti, e la separazione **e' il punto**: il
**telefono cattura** — davanti allo scaffale, senza decidere niente — e il
**computer riconcilia**, dove c'e' una tastiera. Un giro di foto, poi una
seduta sola.

1. **Prendi tutte le foto in un colpo.** Cinquanta prodotti confermati uno per
   uno sono esattamente la morte per inserimento a mano che questo disegno
   evita.
2. **La zona si dichiara, non si indovina.** Una foto di uno scaffale non dice
   se e' dispensa o congelatore, e il congelatore cambia tutto a valle
   (scongelamento, `da_smaltire`). Una riga al momento del caricamento basta:
   «le prime quattro sono la dispensa, le ultime due il congelatore». Se non
   l'ha detto, **chiedilo prima di leggere**, non dopo.
3. **Leggi e proponi una tabella unica**, con quello che hai riconosciuto:

   ```
   Dalla dispensa (4 foto):
    1. Fusilli integrali 500 g     ~4 pacchi    (fusilli-integrali-500)
    2. Passata di pomodoro 700 g   ~3 bottiglie (passata-700)
    3. Tonno all'olio 80 g         ~6 scatolette (tonno-olio-80)
    4. Riso arborio 1 kg           1 pacco aperto, ~mezzo
    5. «scatola blu, non si legge la marca»      [non riconosciuto]

   Non ho visto cosa c'e' dietro la prima fila del secondo scaffale.
   Correggi pure a parole: «la pasta sono 6», «la passata e' finita».
   ```

4. **Si corregge in prosa**, non riga per riga. «La pasta sono sei, il tonno
   lascialo stare» e' tutta l'interazione prevista.
5. **Di' cosa non hai visto.** La seconda fila dietro la prima, l'etichetta
   girata, lo scaffale in ombra: dichiararlo vale piu' che indovinare, ed e' la
   stessa regola dei formati.
6. **Non scrivere niente prima della conferma.** Nessuna scrittura nasce da
   un'immagine da sola.

Quello che non riconosci va proposto **come testo libero**, non buttato: una
riga «scatola blu» che l'utente rinomina in una parola vale piu' di una riga
persa. Cio' che riconosci, riconoscilo contro `alias_scontrino` e i nomi in
`dati/prodotti.jsonl`: la chiave di `scorte` e' l'id del prodotto quando esiste.

Questo flusso serve anche dopo, non solo al setup: svuotato uno scaffale, un
giro di foto lo riallinea. Ma resta uno strumento di **partenza e di
ricontrollo saltuario** — il viaggio telefono → computer vale la pena una
volta, non ogni lunedi'.

## 4. Le soglie si propongono alla fine, tutte insieme

**Mai chiedere una soglia per prodotto**: sono cinquanta domande, e nessuno
arriva alla decima. A giro finito, proponi tu — in un blocco solo, da
correggere:

| da cosa la ricavi | soglia | massimo |
|---|---|---|
| prodotti che il menu usa ogni settimana (pasta, passata, olio) | il consumo di ~2 settimane | ~4 settimane |
| scatolame e conserve | 2 pezzi | il doppio di quanto ce n'e' adesso, se e' ragionevole |
| roba che si usa di rado (spezie, lievito, aceto) | 1 | 2 |

E dove hai gia' dei dati veri, usali invece della tabella: `storico.yaml` sa
quante volte quel prodotto e' comparso nelle ultime settimane, e
`prodotti.jsonl` sa il formato. Una soglia ricavata dal consumo vero batte una
regola generica.

Il `massimo` merita una frase quando lo proponi, perche' e' il campo che fa il
lavoro che nessuno ha chiesto:

> Ti metto un tetto a 6 sulla passata: oltre quello non te la rimetto in lista,
> anche se il menu la userebbe. Ne hai gia' tre.

La `rotazione` (`alta`/`media`/`bassa`) la deduci tu dal tipo di prodotto: non
e' una domanda da fare, e serve solo a decidere ogni quanto riproporre quella
riga nella fetta del lunedi'.

## 5. Quanto vale la roba che avete in casa

A giro finito, e **solo a giro finito**, il numero che rende sensato aver fatto
tutto questo:

> In dispensa e in congelatore ci sono circa **340 €** di roba gia' pagata.

Si calcola dai prezzi in `dati/prodotti.jsonl` — ultimo prezzo noto × quantita'.
Valgono le regole di sempre: le righe senza prezzo restano fuori e il totale si
dichiara **parziale**, mai gonfiato per farlo sembrare completo. Le bande si
contano con una stima grossolana e dichiarata come tale (`pieno` ≈ il massimo,
`medio` ≈ la soglia, `poco` ≈ mezza soglia, `finito` = 0).

Dillo come un dato, non come un rimprovero. Un totale alto non e' una colpa: e'
la ragione per cui l'inventario ha senso tenerlo.

## 6. Scrivere, e chiudere

Scrivi `dati/dispensa.yaml`: `scorte` con `quantita`, `soglia`, `massimo`,
`visto` (oggi, perche' oggi qualcuno ha davvero guardato) e `rotazione`;
`freezer` per il congelatore, con le date dove si sanno. **`avanzi` non si
tocca**: e' cio' che il motore ha calcolato, ed e' un'altra cosa.

Poi, se `git: locale`:

```bash
git add -A && git commit -q -m "inventario: <n> scorte, <n> voci di congelatore"
```

Chiudi corto: quante righe sono entrate, il valore, e **una riga sola** su cosa
cambia — la lista della spesa si accorcia, e quello che e' sopra il tetto non
ci torna piu'. Non elencare quello che hai scritto: e' appena stato detto tutto
a voce.

Se l'inventario e' stato interrotto a meta', va benissimo: si scrive quello che
c'e', il resto resta assente, e le zone non fatte si riprendono quando l'utente
vuole. Una zona mancante non e' un errore da segnalare ogni volta.
