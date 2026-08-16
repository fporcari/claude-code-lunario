# Fixture — coppia con dispensa profonda

Casa Lunario **sintetica**, esiste solo per i test del motore: persone
inventate (`Adulto1`, `Adulto2`), numeri tondi, nessun dato reale.

Due adulti, **nessuno a dieta**: qui il peso non si nomina mai. La casa ricompra
sempre gli stessi prodotti e ne tiene una cinquantina fissi in credenza: e' il
fixture di regressione per il «cinque pacchi della stessa cosa».

## Il muro che questo fixture mostra, invece di aggirarlo

`dispensa.yaml` ha due sezioni sole: `avanzi`, cio' che il motore ha
**calcolato** da una spesa, e `freezer`, cio' che l'utente **vede** aprendo lo
sportello. Le ~35 voci fisse di questa casa — sale, olio, aceto, farina, caffe',
lievito, scatolame di riserva — non stanno legittimamente in nessuna delle due:
oggi **non hanno un posto dove vivere**, e ogni lunedi' vanno ridichiarate a
memoria, o si ricomprano. Il paniere invece le conosce tutte
(`dati/prodotti.jsonl`, 54 righe): la dispensa no.
