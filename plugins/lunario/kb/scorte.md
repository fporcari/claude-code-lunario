# Le scorte: bande, fiducia, conteggio ciclico

Cio' che una casa **tiene in casa**, in contrapposizione a cio' che compra
questa settimana. Un pacco di sale non e' un avanzo di una spesa: e' una
scorta, e la differenza cambia dove va scritta e come si legge.

Questa pagina e' la regola condivisa fra `lunario:inventario` (che riempie),
`lunario:settimana` (che ne conta una fetta ogni lunedi') e `lunario:menu`
(che le consuma). Il contratto del file sta in `CLAUDE.md`.

## Perche' la precisione qui e' un difetto

Due errori opposti, e chiedono due precisioni diverse:

| errore | cosa costa | quanta precisione serve |
|---|---|---|
| **compro quello che ho gia'** | soldi fermi, roba che scade | una **quantita' approssimativa**, per scalare il fabbisogno |
| **il quinto pacco della stessa cosa** | cronico, e nessuno se ne accorge | solo una **soglia**: «ne hai gia' cinque, basta» |

Il secondo — quello che nessuno vede — si risolve col dato piu' grezzo
possibile. E' la licenza a non costruire un magazzino: **la parte che suona
sofisticata, cioe' lo scarico automatico dei consumi, e' quella che si rompe
per prima; la parte che suona stupida, cioe' una soglia per prodotto, e' quella
che sistema tutti e due gli errori.**

E c'e' una ragione in piu' per stare leggeri: l'inserimento a mano e' la causa
di morte documentata di ogni app di dispensa. Si riempie per una settimana, poi
una volta, poi mai — e un inventario aggiornato a meta' e' **peggio** di
nessuno, perche' si smette di crederci. Ogni scelta qui sotto e' una difesa
contro l'inserimento a mano.

## Le bande

Nessuno pesa la farina, e nessuno deve. `quantita` accetta due forme, e il
motore legge quella che trova senza convertirla di nascosto nell'altra:

| forma | quando | come si usa |
|---|---|---|
| un numero | confezioni intere: `4` pacchi di pasta | si sottrae dal fabbisogno |
| una banda | `pieno` · `medio` · `poco` · `finito` | non si sottrae in grammi: dice se la riga della spesa serve |

Come si legge una banda quando bisogna decidere se comprare:

| banda | vuol dire | la riga della spesa |
|---|---|---|
| `pieno` | ce n'e' piu' del fabbisogno di una settimana | sparisce |
| `medio` | ce n'e' abbastanza per questa settimana | sparisce, e si nomina uscendo |
| `poco` | ne resta meno di una settimana | resta, ed e' il candidato numero uno del conteggio ciclico |
| `finito` | non c'e' | resta, intera |

## La fiducia si calcola, non si scrive

Ogni riga porta `visto: <data>`: quando un essere umano l'ha confermata
l'ultima volta. La fiducia **non si memorizza** — si ricava da `visto`, dalla
`rotazione` e da quanto il menu di questa settimana ci si appoggia:

| rotazione | fresca fino a | invecchiata fino a | poi |
|---|---|---|---|
| `alta` (pasta, latte, pane) | 14 giorni | 30 giorni | stantia |
| `media` (scatolame, farine) | 30 giorni | 60 giorni | stantia |
| `bassa` (spezie, aceto, lievito) | 60 giorni | 120 giorni | stantia |

Se il menu della settimana **si appoggia molto** a quella riga — e' l'ingrediente
principale di due o piu' pasti — la si tratta di una tacca peggio: una scorta
su cui poggia il giovedi' sera vale meno di una che copre un condimento.

| fiducia | `lunario:menu` che fa |
|---|---|
| **fresca** | la sottrae in silenzio |
| **invecchiata** | la sottrae, e lo **dichiara nel menu**: «conto sui 2 pacchi di riso visti il 12 luglio» |
| **stantia** | **non se ne fida**: la mette nella fetta da contare del lunedi', prima di generare |

Il motore non ha bisogno di avere ragione. Ha bisogno di **sapere quanto e'
vecchia la sua convinzione** — perche' il consumo si osserva solo dove passa
`lunario:prepara`, e `prepara` non gira per ogni colazione, panino e caffe'.
La deriva ha quindi una direzione prevedibile: **il consumo e' sotto-registrato,
quindi il motore crede di avere piu' di quello che c'e'**. Oggi Lunario sbaglia
per difetto — non sa, e ricompra: costa soldi. Con uno scarico ingenuo
sbaglierebbe per eccesso — crede nel pollo che non c'e' e ci costruisce sopra
il giovedi': costa una cena e la fiducia. Il secondo errore e' il peggiore, ed
e' silenzioso.

## Il conteggio ciclico

Le cucine professionali non tengono un inventario perpetuo sulla dispensa
secca: fissano un livello e contano **a rotazione**, ognuno alla frequenza che
si merita. Un censimento completo, ogni lunedi', non lo fa nessuno due volte.

Quindi `lunario:settimana` tocca **al massimo sei righe**, scelte dove
l'incertezza incontra l'impatto:

1. **stantie**, e questa settimana servono
2. **vicine alla soglia** — `poco`, o quantita' ≤ `soglia`
3. **rotazione alta** e non viste da piu' di due settimane
4. a parita', le piu' vecchie

E si presentano come un **elenco da correggere**, mai come sei domande:

> Dovreste avere: 4 pacchi di pasta, la passata a `poco`, 2 scatole di tonno,
> il riso `pieno`, l'olio a `medio`, il caffe' non lo vedo da luglio.
> Cosa e' sbagliato?

Chi taglia corto non perde niente: la fetta si salta, invecchia ancora, e
torna la settimana dopo — con una priorita' piu' alta, perche' e' piu' stantia.

## Il movimento automatico non promuove niente a «contato»

`lunario:spesa` incrementa dallo scontrino, `lunario:menu` e `lunario:prepara`
decrementano, `lunario:postmortem` corregge sul consumo reale. Tutti muovono la
`quantita` come **stima**, e **nessuno tocca `visto`**.

E' la regola che tiene in piedi la fiducia: solo un conteggio umano — o una
foto confermata — azzera l'eta' del dato. Se il movimento automatico
aggiornasse anche `visto`, una dispensa piena di numeri derivati sembrerebbe
appena contata, e la fiducia diventerebbe una decorazione.

L'unica eccezione ragionevole e' lo **scontrino**: quello che e' entrato in
casa oggi e' un fatto, non una stima. Ma incrementa e basta: dice quanto e'
entrato, non quanto ce n'e' — perche' non sa quanto ce n'era.

## `massimo`: il campo che ferma il quinto pacco

Sopra `massimo`, un prodotto **non genera mai una riga della spesa**, e quando
sarebbe stato comprato lo si dice in mezza riga. E' l'unico posto del sistema
che agisce sull'errore che nessuno nota, e agisce anche su qualcosa che non e'
una dimenticanza: comprare in abbondanza e' un modo di **sentirsi previdenti**,
non un errore di memoria. Per questo la frase e' un dato — «ne hai gia' quattro»
— e mai un rimprovero.

## Cosa non entra, mai

- **Niente deperibili.** Solo la fascia `[fine]` di `deperibilita.md`: dispensa
  secca, scatolame, surgelati, uova, formaggi stagionati. Mezza busta di rucola
  fra tre giorni non esiste, e inventariarla vuol dire pianificare sul marcio
- **Niente date di scadenza per riga.** E' inserimento a mano puro, e la data
  che serve davvero — quella di congelamento — ce l'ha gia' il `freezer`
- **Niente posizioni, scaffali, zone.** La zona serve a fare le domande in un
  ordine sensato, non a essere memorizzata
- **Niente codici a barre come flusso principale.** Uno scanner in cucina e' un
  attrezzo che si usa per due settimane
