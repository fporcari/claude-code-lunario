# Porzioni standard e frequenze settimanali

Fonte: Linee Guida per una Sana Alimentazione, CREA rev. 2018 (porzioni
standard italiane, coerenti con i LARN/SINU). Valori per adulto; la porzione
personale si scala dal profilo (`dati/profilo.yaml`).

## Porzioni standard (peso a crudo salvo indicazione)

| Alimento | Porzione | Note |
|---|---|---|
| Pasta, riso, cereali | 80 g | in minestra: 40 g |
| Pane | 50 g | una fetta media/un panino piccolo |
| Patate | 200 g | conta come cereali, non come verdura |
| Verdura | 200 g | insalata a foglia: 80 g |
| Frutta | 150 g | un frutto medio |
| Carne | 100 g | rossa o bianca |
| Pesce | 150 g | |
| Legumi | 150 g cotti / 50 g secchi | |
| Uova | 50 g | un uovo |
| Latte | 125 ml | |
| Yogurt | 125 g | un vasetto |
| Formaggio fresco | 100 g | stagionato: 50 g |
| Olio extravergine | 10 g | un cucchiaio |
| Affettati | 50 g | |

## Frequenze settimanali raccomandate (a porzione)

| Gruppo | Frequenza |
|---|---|
| Verdura e frutta | 2-3 + 2-3 al giorno |
| Cereali (pasta/pane/riso) | a ogni pasto principale |
| Legumi | 2-4 volte |
| Pesce | 2-3 volte (preferire azzurro e pesci piccoli) |
| Carne totale | max 3 volte, di cui rossa max 1 |
| Salumi | max 1 volta |
| Uova | 2-4 |
| Formaggi | 2-3 volte |

## Colazione, spuntini e merende

Sono pasti, non contorno del sistema: se la cella e' `casa`, hanno una
porzione, entrano nel conto calorico e generano una riga di spesa. Ignorarli
e' il modo piu' rapido di scrivere un target che nessuno rispetta.

| pasto | quota della giornata | composizione tipica |
|---|---|---|
| Colazione | 20-25% | latte o yogurt + cereali/pane + frutta |
| Spuntino (mattina) | 5-10% | un frutto, oppure yogurt bianco |
| Merenda (pomeriggio) | 5-10% | frutta + 20-30 g pane, o yogurt, o 20 g frutta secca |

Porzioni degli spuntini, oltre a quelle della tabella sopra:

| Alimento | Porzione | Note |
|---|---|---|
| Frutta secca a guscio | 20 g | una manciata piccola |
| Fette biscottate | 20 g | due fette |
| Biscotti secchi | 30 g | |
| Cracker / gallette | 25 g | |
| Marmellata / miele | 15 g | un cucchiaino colmo |
| Cereali da colazione | 40 g | integrali, senza zuccheri aggiunti |
| Cioccolato fondente | 15 g | |

Regole d'uso:

- Bambini e adolescenti fanno **due** spuntini, gli adulti spesso nessuno: e'
  una scelta per persona, non per famiglia, e sta in `pasti` nel profilo.
- La merenda dei bambini si compra come tutto il resto: se e' `casa`, sta
  nella lista della spesa in confezioni, non «prendi qualcosa per merenda».
- Uno spuntino non e' un premio ne' una deroga: se c'e', e' dentro il conto
  della giornata fin dall'inizio.

## Chi e' a dieta e chi no

Nella stessa casa convivono i due casi, e vanno trattati diversamente **nella
stessa cena**: stesso piatto, porzioni diverse.

- `dieta: false` → porzioni standard di questa tabella, scalate solo su eta' e
  corporatura. Nessun deficit, nessun alleggerimento d'ufficio, e il peso non
  si nomina.
- `dieta: true` → porzioni scalate sul target kcal, col taglio fatto secondo
  la sezione qui sotto.
- Un pasto `libero` non entra nel conto e non si compensa altrove: ne' con un
  pranzo piu' magro lo stesso giorno, ne' col giorno dopo.

## Regole per diete ipocaloriche

- Il taglio calorico si fa su condimenti, porzioni di cereali e frequenza di
  formaggi/salumi. MAI su verdura, frutta e acqua.
- Sotto le 1200 kcal/giorno serve supervisione medica: il sistema non genera
  piani sotto questa soglia.
- Le kcal dei piatti sono stime da tabelle di composizione degli alimenti
  (CREA): indicative, arrotondare alle decine, mai spacciarle per misure.
