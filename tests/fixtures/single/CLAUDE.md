# Lunario — casa sintetica «single» (fixture di test)

Questa **non** e' una cartella di casa vera: e' un fixture usato dai test del
motore. Persona, pesi, prezzi e settimane sono inventati, i numeri sono tondi
apposta e nessun prodotto ha un EAN.

Ci abita una persona sola: **Solo1**, adulta, `dieta: true`, nessun bambino,
nessuno spuntino e nessuna merenda.

Cosa stressa: porzioni per uno e pavimento delle 1200 kcal (target 1300),
dispensa quasi vuota, profilo da `intervista: minima` — senza `tolleranze` e
senza `titoli`, che il motore deve reggere assenti.

E' anche **l'unica cartella rimasta indietro, di proposito**: nessun
`versione.yaml`, quindi il contratto si deduce dalla forma dei file, e la sua
settimana ha il markdown **accanto** alla cartella invece che dentro, com'era
fino al contratto 3. Serve a verificare due cose che altrimenti nessuno
proverebbe: che il contratto si indovini bene, e che una settimana scritta dal
motore vecchio si trovi e si legga ancora. Non aggiornarla.

Non usarla come esempio di compilazione: per quello ci sono
`plugins/lunario/templates/`.
