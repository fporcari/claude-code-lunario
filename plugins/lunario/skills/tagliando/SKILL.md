---
name: tagliando
description: >-
  Il controllo completo della cartella di casa: verifica il contratto, la forma
  dei file, i documenti di ogni settimana e i contratti dati, ripara cio' che si
  ripara e riporta il resto in chiaro. Da invocare quando l'utente dice
  "controlla tutto", "tagliando", "e' tutto a posto?", "ho aggiornato il
  plugin", "qualcosa non torna", "sistemami la cartella", "il menu non trova i
  file", "manca la lista della spesa", oppure quando una skill riporta che
  c'e' qualcosa da riparare. E' anche il posto giusto dopo un aggiornamento
  del motore, per portare la cartella alla forma che le skill nuove si
  aspettano.
---

# Tagliando — cosa non torna, e cosa si ripara

Il motore si aggiorna dal marketplace; la cartella di casa resta com'era. Fino
a qui c'era **un solo controllo automatico** — il numero del contratto — e un
numero allineato zittiva tutto il resto: una cartella col timbro giusto e i
file nella forma vecchia passava a ogni lancio, per sempre.

Questa skill guarda **i file, non il numero**. E' il tagliando dell'auto: si
fa quando si vuole, trova cio' che si e' consumato, aggiusta cio' che si
aggiusta e ti dice il resto invece di lasciartelo scoprire in autostrada.

Non e' `lunario:aggiorna`: quella esegue **il salto di contratto**, un passo per
volta, e questa la chiama quando serve. Il tagliando e' piu' largo e piu' basso
— guarda anche una cartella perfettamente allineata, dove non c'e' nessun salto
da fare e i file sono lo stesso nel posto sbagliato.

## 1. La diagnosi

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tagliando.py
```

Stampa cosa non torna, diviso in tre:

| etichetta | cosa vuol dire | cosa ne fai |
|---|---|---|
| `blocca` | una skill che parte adesso lavorerebbe sui file sbagliati | si ripara **prima** di qualsiasi altra cosa |
| `da vedere` | un difetto vero nei dati, che non impedisce di lavorare | punto 3: si sistema con giudizio |
| `nota` | un dubbio, non un difetto | si dice una volta, non si insiste |

Cio' che porta `[si ripara da solo]` e' **meccanico**: spostare file, scrivere
un timbro, sistemare un percorso. Il resto no, ed e' voluto — un file di dati
e' pieno di commenti scritti per un essere umano, e uno script che lo riscrive
li perde.

**Se non c'e' niente, dillo in una riga e fermati.** Se sei stata chiamata da
un'altra skill, non dire niente: torna e basta.

## 2. Le riparazioni meccaniche

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tagliando.py --ripara
```

Le applica tutte e ridiagnostica da sola, cosi' quello che resta e' quello che
resta davvero. Riporta in **una riga per riparazione**, non un rapporto:

> W34 aveva i documenti fuori dalla cartella: spostati, e storico.yaml ora ci
> punta. La lista della spesa non c'era e non si inventa — la scrive il
> prossimo menu.

Se fra i guasti c'e' `CONTRATTO_INDIETRO`, quello **non** lo ripara lo script:
passa da `lunario:aggiorna`, che esegue i passi di migrazione uno per salto, e
poi rilancia la diagnosi.

### Cosa non si tocca, mai

Vale il confine gia' scritto nel contratto, e il tagliando non e' l'eccezione:

- **le settimane passate.** Sono un registro: si leggono dove sono, con il nome
  che hanno. Si adattano solo la settimana in corso e quella che sta per
  aprire — le uniche a cui manca ancora qualcosa da vivere
- **i livelli dichiarati.** Profilo, ritmi e note li scrive l'utente. Il
  tagliando puo' proporre, mai correggere d'ufficio
- **cio' che non capisce.** Un dato strano si riporta, non si normalizza:
  indovinare cosa intendeva chi ha scritto e' il modo piu' rapido di
  cancellare l'unica copia di un'informazione

## 3. I difetti dei dati, quelli che chiedono giudizio

Sono le righe `da vedere`. Non si riparano in blocco e non si elencano tutte:
**si raggruppano per causa**, si propone il rimedio e si chiede una volta.

| cosa trovi | cosa proponi |
|---|---|
| prodotti senza `formato_g` | cercarli con `off_lookup.py`, o chiedere il formato all'utente che ha il pacco in mano. Senza, la lista esce in grammi |
| `formato_g` senza `fonte_formato` | e' un formato a memoria: chiedere da dove viene, e datarlo |
| scorte senza `visto` | la fiducia non si calcola: proporre `lunario:inventario` sulla sola fetta che manca |
| YAML fuori dal sottoinsieme semplice | riscrivere **quella riga** nella forma piana, mostrando prima e dopo |
| uno stato di cella o un pasto fuori vocabolario | quasi sempre un refuso: mostrare la riga e chiedere cosa intendeva |
| una quarantena con `fino_al` passato | toglierla: il piatto e' rientrato da solo, come previsto |

Due regole che valgono su tutte:

- **una domanda per volta**, e solo dove la risposta cambia qualcosa. Venti
  prodotti senza formato sono **una** domanda, non venti
- **mostra la riga prima di cambiarla.** Un file di dati riscritto senza far
  vedere cosa c'era e' esattamente cio' che rende impossibile fidarsi di un
  sistema che si aggiusta da solo

## 4. Quando la cartella e' sana

Non inventarti lavoro. Una cartella pulita merita una riga sola — quante
settimane ci sono, a che contratto sta, e che non c'e' niente da fare. Un
tagliando che trova sempre qualcosa e' un tagliando che nessuno rifara'.

## 5. Chiudere

Se `git: locale` nel profilo e qualcosa e' cambiato, l'ultima cosa che fai:

```bash
git add -A && git commit -q -m "tagliando: <cosa e' stato riparato>"
```

Messaggi che si leggono fra sei mesi — `tagliando: W34 dentro la sua cartella`
· `tagliando: quattro formati dal paniere, due quarantene scadute`. Se il
commit fallisce, non dire niente e vai avanti.

In chat: cosa hai riparato, cosa resta e perche' resta. Niente elenchi lunghi,
niente rapporto. Se non resta niente, dillo e basta.
