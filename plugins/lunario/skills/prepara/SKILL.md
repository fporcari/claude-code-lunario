---
name: prepara
description: >-
  Accompagna la preparazione del piatto di oggi: ingredienti nelle quantita'
  gia' scalate sulla famiglia, procedimento passo per passo, un video se se ne
  trova uno buono, e risposte alle domande mentre si cucina. A fine cottura
  chiede quanto e' stato difficile e che voto da' il cuoco alla propria opera —
  che e' un'altra cosa dal voto dei commensali. Da invocare quando l'utente
  dice "cosa cucino stasera", "come si fa", "prepariamo la cena", "aiutami a
  cucinare", "ci sono", "ho iniziato", "sto cucinando", "ho fatto", "e'
  pronto", o nomina un piatto del menu di oggi.
---

# Prepara — mentre si cucina

L'unica skill che si usa **in piedi, con le mani sporche**. Ne discende tutto
il resto: risposte corte, un passo per volta, niente preamboli.

## 1. Che piatto e'

Leggi `settimane/<ISO>.md`. I pasti gia' fatti sono spuntati (`- [x]`):
**escludili sempre**, anche se sono di oggi. Fra quelli che restano, il
candidato e' il pasto di oggi secondo l'ora — pranzo o cena — e secondo il
contesto della settimana.

**Chiedi conferma in una riga**, perche' la vita non seguo il menu:

> Stasera tocca **orata al forno con patate**. Confermi?

Se l'utente dice di no, **proponi la lista dei pasti rimasti** come opzioni da
scegliere — solo quelli non ancora spuntati, ognuno col giorno per cui era
previsto. Lui marca quello giusto e si procede con quello: il menu si e'
riordinato, non e' saltato.

Se il piatto scelto era previsto per un altro giorno, non riscrivere il menu
qui: se ne occupa `lunario:correggi` quando servira'. Qui si cucina.

Se il menu di oggi non esiste, o l'utente sta cucinando altro, chiedi cosa e
procedi lo stesso: questa skill serve anche fuori dal menu, e in quel caso non
spunta niente.

Recupera dal profilo il numero di commensali e le porzioni tarate, cosi' le
quantita' sono gia' quelle giuste per questa casa. Se il piatto ha una base
neutra per i bambini, il procedimento deve dire **dove** si biforca.

## 2. Cosa serve

Ingredienti in quantita' reali per stasera, non per una ricetta generica.
Segnala subito le due cose che fanno fallire una cena:

- cosa va tirato fuori **adesso** (carne da scongelare, burro da ammorbidire)
- cosa richiede attesa non comprimibile (lievitazione, ammollo, marinatura)

Se qualcosa manca in dispensa, dillo ora e proponi la sostituzione, non a
meta' cottura.

## 3. Il procedimento

Passi numerati, imperativi, uno per riga. Tempi e temperature dove contano.
Niente storia del piatto, niente aggettivi da rivista.

Poi **fermati e resta disponibile**. L'utente cucina e chiede: «quanto sale?»,
«e' troppo liquido», «posso usare il forno statico?». Rispondi corto e
concreto: sta aspettando con una padella accesa.

## 4. Il video

Cerca un video **solo se il piatto ha una tecnica che si capisce meglio
vedendola** — una piega, una consistenza, un taglio. Per una pasta e ceci non
serve, e proporlo e' rumore.

Regola ferrea: **il link va preso da una ricerca fatta adesso**, mai dalla
memoria. Un URL di YouTube inventato e' indistinguibile da uno vero finche'
l'utente non ci clicca, e a quel punto ha le mani sporche e nessuna voglia.
Se la ricerca non da' niente di buono, dillo in tre parole e vai avanti.

Proponi un link solo, dicendo che non l'hai guardato.

## 5. «Ho fatto»

Quando l'utente dice che ha finito, **due domande a bruciapelo**, senza
introduzioni e senza aspettare la cena:

1. **Quanto e' stato difficile, da 1 a 5?**
2. **Che voto dai a come ti e' venuto, da 1 a 5?**

Chiedile insieme, in due righe. E' il momento giusto: fra due ore si ricordera'
solo se e' piaciuto agli altri.

Chiedi anche i **minuti veri**, se lo sa: e' il dato che smaschera le ricette
«da 20 minuti» che ne prendono 45.

Scrivi in `tarature.voti[<piatto>].cucina` di `dati/storico.yaml`:
`difficolta`, `voto_cuoco`, `minuti_reali`, `volte`.

## 6. Segnare che e' fatto

In `settimane/<ISO>.md`, spunta due cose:

- **il pasto**: `- [ ]` diventa `- [x]`, cosi' al prossimo lancio e' fuori dai
  candidati
- **gli ingredienti che hai davvero usato**, nella lista della spesa

Il secondo punto e' quello che vale: una lista dove il consumato e' spuntato
dice a colpo d'occhio cosa e' rimasto in frigo. Ci si appoggiano
`lunario:correggi`, che smette di chiedere alla cieca cosa c'e' in casa, e il
postmortem, che corregge la dispensa sul reale invece che sul previsto.

Spunta solo cio' che e' stato consumato per intero. Mezza confezione aperta
non e' consumata: se serve, annotala accanto alla riga.

Fallo in silenzio: non elencare all'utente cosa hai spuntato.

## Cosa ci fa il sistema, e perche' non e' lo stesso voto del postmortem

| voto | chi | quando | cosa tara |
|---|---|---|---|
| **cucina** | chi ha cucinato | appena finito | **dove** il piatto puo' stare nella settimana |
| **tavola** | tutti | al postmortem | **se** il piatto resta in rotazione |

Un piatto puo' essere amatissimo a tavola e impossibile il mercoledi' sera.
Il primo voto non lo esclude: lo sposta nel weekend. Quindi:

- difficolta' 4-5, o minuti reali molto sopra i dichiarati -> il piatto va nei
  giorni con tempo, mai in una sera con `cena_entro_min` stretto
- voto del cuoco basso ma voto della tavola alto -> non e' il piatto, e' la
  ricetta: al prossimo giro proponi un procedimento diverso
- difficolta' 1 e voto alto -> e' un jolly, il candidato ideale per le sere
  storte

Chiudi con una riga sola. L'utente deve andare a tavola, non a leggere.
