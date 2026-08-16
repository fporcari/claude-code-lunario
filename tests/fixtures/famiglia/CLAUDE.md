# Casa Lunario sintetica — fixture di test

Non e' una casa vera. E' il fixture che i test del motore usano per far girare
le skill su una cartella gia' configurata.

Ci abitano quattro persone inventate: Adulto1 (a dieta), Adulto2, Bimbo1
(selettivo) e Bimbo2. Nomi, pesi, prezzi e storico sono numeri tondi scelti a
tavolino: nessun dato qui dentro descrive una persona reale.

Stressa la **griglia dei pasti completa**: fra `dati/profilo.yaml` e
`dati/ritmi.yaml` compaiono tutti e sei gli stati di cella — `casa`,
`trasportabile`, `libero`, `ristorante`, `fuori`, `no` — piu' merende, spuntini
e un ristorante fisso il venerdi'.

Lo scontrino sintetico che gli fa da coppia sta in
`tests/fixtures/scontrino/`: contiene di proposito una sostituzione di formato,
una riga mai vista, un prodotto della lista che manca e quattro righe non
alimentari.
