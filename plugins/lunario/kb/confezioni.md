# Dai grammi alle confezioni

Il menu ragiona in grammi, la spesa si fa in confezioni. Questa e' la
conversione, ed e' il punto dove il sistema smette di essere un generatore di
diete e diventa una lista utile.

Regola d'oro: **la lista non dice mai «1050 g di pasta»**. Dice «2 pacchi da
500 g» e, se serve, «ne avanzano 400 g».

## I tre tipi di ingrediente

Il campo `tipo` in `dati/prodotti.jsonl` decide come si arrotonda.

| tipo | esempi | come si compra | avanzo |
|---|---|---|---|
| `confezione` | pasta, riso, legumi in scatola, latte, olio, farina | formato fisso: si arrotonda | va in dispensa |
| `peso` | verdura, frutta, carne e pesce al banco | al grammo: nessun arrotondamento | nessuno |
| `pezzo` | uova, mozzarelle, vasetti di yogurt | a unita' intere | vale il pezzo intero |

Per il tipo `peso` la lista riporta i grammi e basta: «600 g di zucchine» e'
gia' una riga della spesa, non serve tradurla.

## Il calcolo, tre passi

```
fabbisogno − dispensa = mancante → confezioni
```

1. **Fabbisogno**: somma dei grammi dell'ingrediente su tutti i pasti della
   settimana (porzione × celle che lo mangiano davvero), con le porzioni scalate
   sulle tarature.
2. **Meno la dispensa**: `dati/dispensa.yaml` dice cosa c'e' gia' in casa.
   Sottrarlo e' l'anello che evita di ricomprare ogni lunedi' la pasta di cui
   resta mezzo pacco.
3. **Confezioni**: `ceil(mancante / formato_g)`, con l'eccezione qui sotto.
   L'avanzo previsto — `confezioni × formato_g − mancante` — torna in dispensa.

Esempio: 3 pasti di pasta da 350 g totali fanno 1050 g; in dispensa ce ne sono
450; mancano 600 g; il formato e' 500 g; **2 pacchi**, avanzo 400 g.

## L'eccezione: limare invece di comprare

Comprare una confezione intera per coprire pochi grammi e' spreco travestito
da precisione. Se il mancante supera di poco un multiplo del formato:

- **scarto sotto il 10% del fabbisogno** -> compra le confezioni per difetto e
  riduci le porzioni della differenza, senza segnalarlo come rinuncia
- **scarto sopra il 10%** -> compra la confezione in piu'

Nell'esempio sopra: servirebbero 1050 g, due pacchi ne danno 1000 (con i 450
di dispensa si arriva a 1450, quindi abbondano). Quando invece mancano 1050 g
puliti, due pacchi coprono 1000 g: lo scarto e' 50 g su 1050, il 4,8%, sotto
soglia — si limano 17 g a pasto e nessuno se ne accorge.

La soglia del 10% e' un punto di partenza: si tara come le porzioni, dai
postmortem.

## Cosa entra in dispensa, cosa no

Solo i non deperibili, cioe' la fascia `[fine]` di `kb/deperibilita.md`:
dispensa secca, scatolame, surgelati, uova, formaggi stagionati.

**Il fresco avanzato non e' un credito.** Mezza busta di rucola avanzata non
va scritta da nessuna parte: fra tre giorni non esiste. Segnarla come dispensa
significherebbe pianificare la settimana dopo su un ingrediente marcio.

Una confezione aperta di un prodotto conservabile ha comunque una vita piu'
corta della confezione chiusa: passata di pomodoro aperta, latte aperto,
formaggio spalmabile. Se il postmortem li ritrova avanzati due volte di fila,
il problema e' il formato — vale la pena cercarne uno piu' piccolo.

## Da dove viene il formato

Da `dati/prodotti.jsonl` se il prodotto c'e' gia', altrimenti da Open Food
Facts (`scripts/off_lookup.py`), che restituisce `product_quantity` in grammi.

Mai a memoria. Se il formato non si trova ne' in un posto ne' nell'altro, la
riga della spesa resta in grammi e si marca `[formato da verificare]`: una
riga onesta vale piu' di una confezione inventata.
