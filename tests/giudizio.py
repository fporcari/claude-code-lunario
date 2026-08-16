#!/usr/bin/env python3
"""Tier 3 — il menu e' *buono*? Un parere scritto, che non fa fallire niente.

    python3 tests/giudizio.py settimane/2026-W34-commando/2026-W34-commando-preventivo.md
    python3 tests/giudizio.py --casa /tmp/lunario-test/famiglia

Il tier 1 dice se i file rispettano il contratto, il tier 2 se il giro lascia
le proprieta' giuste. Nessuno dei due sa dire se quella settimana verrebbe
voglia di mangiarla, e quella e' la domanda che conta di piu'.

**Questo giro non puo' fallire, ed e' la sua regola piu' importante.** Esce
sempre 0. Un giudizio sfumato messo a fare da semaforo produce una suite che
diventa rossa a caso, e una suite rossa a caso viene ignorata entro due
settimane — a quel punto anche i tier 1 e 2 non li guarda piu' nessuno. Qui si
produce un testo per un essere umano, e la decisione resta sua.
"""

import argparse
import glob
import json
import os
import shutil
import subprocess
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(QUI)
sys.path.insert(0, os.path.join(REPO, "plugins", "lunario", "scripts"))
import settimana as settimana_del_motore  # noqa: E402

# I test verificano **proprieta'**, non la finezza di una frase: girano su
# Sonnet perche' una suite che costa quanto una release non la lancia nessuno.
# Con `--modello` si passa qualunque altro, quando serve davvero.
MODELLO_PREDEFINITO = "sonnet"

DOMANDA = """Leggi questo menu settimanale generato da Lunario e scrivi un parere per un essere
umano. Non devi correggerlo ne' rigenerarlo: devi dire cosa ne pensi.

Rispondi per punti, corto, su queste cinque cose:

1. **Equilibrio** — proteine, verdura, legumi, cereali nell'arco dei sette giorni. Qualcosa
   manca del tutto? Qualcosa torna troppo?
2. **Varieta'** — la settimana si legge anche in verticale: due piatti che si somigliano in
   due sere di fila, lo stesso sapore dominante a un giorno di distanza, la stessa tecnica
   di cottura sempre.
3. **Plausibilita' feriale** — il mercoledi' sera, dopo il lavoro, quel piatto lo fa
   qualcuno davvero? Guarda i tempi e il numero di pentole, non solo il nome.
4. **La lista sembra una spesa vera?** — e' roba che una persona porta a casa in due borse,
   o e' un elenco da ristorante? Ci sono righe che al supermercato uno salta perche' non
   capisce a cosa servono?
5. **La cosa che cambieresti**, una sola, e perche'.

Chiudi con un voto da 1 a 5 e una riga di motivazione. Sii schietto: un parere tiepido non
serve a nessuno. E non inventare: se un dato non c'e' nel file, dillo invece di dedurlo.

--- MENU ---

"""


def trova_menu(argomenti):
    """Il documento vivo dell'ultima settimana, con lo script del motore.

    Il glob nudo su `settimane/*.md` non basta piu': dal contratto 4 i
    documenti stanno dentro la cartella della settimana, e sono quattro."""
    if argomenti.menu:
        return argomenti.menu
    casa = argomenti.casa or os.getcwd()
    esito = settimana_del_motore.risolvi(casa)
    if esito and esito["vivo"]:
        return esito["vivo"]
    candidati = sorted(glob.glob(os.path.join(casa, "settimane", "*.md")))
    return candidati[-1] if candidati else None


def main(argomenti=None):
    parser = argparse.ArgumentParser(description="Tier 3: un parere sul menu. Non fa mai fallire.")
    parser.add_argument("menu", nargs="?", help="il markdown della settimana")
    parser.add_argument("--casa", help="una cartella di casa: prende la settimana piu' recente")
    parser.add_argument("--modello", default=MODELLO_PREDEFINITO,
                        help=f"default: {MODELLO_PREDEFINITO}")
    parser.add_argument("--out", default=None, help="dove scrivere il parere")
    argomenti = parser.parse_args(argomenti)

    percorso = trova_menu(argomenti)
    if not percorso or not os.path.isfile(percorso):
        print("Nessun menu da giudicare. (Non e' un fallimento.)")
        return 0
    if not shutil.which("claude"):
        print("claude non e' nel PATH: niente parere. (Non e' un fallimento.)")
        return 0

    with open(percorso, encoding="utf-8") as f:
        menu = f.read()

    comando = ["claude", "-p", DOMANDA + menu, "--output-format", "json"]
    if argomenti.modello:
        comando += ["--model", argomenti.modello]
    try:
        uscita = subprocess.run(comando, capture_output=True, text=True, timeout=600)
    except (OSError, subprocess.SubprocessError) as e:
        print(f"Il parere non e' arrivato: {e}. (Non e' un fallimento.)")
        return 0
    if uscita.returncode != 0:
        print(f"Il parere non e' arrivato (uscita {uscita.returncode}). (Non e' un fallimento.)")
        return 0

    try:
        parere = json.loads(uscita.stdout).get("result", uscita.stdout)
    except json.JSONDecodeError:
        parere = uscita.stdout

    destinazione = argomenti.out or os.path.splitext(percorso)[0] + ".giudizio.md"
    with open(destinazione, "w", encoding="utf-8") as f:
        f.write(f"# Parere su {os.path.basename(percorso)}\n\n"
                "Tier 3 di Lunario: un'opinione, non un test. Non fa fallire niente.\n\n"
                + parere + "\n")
    print(f"--- parere su {os.path.basename(percorso)} ---\n")
    print(parere)
    print(f"\nScritto in {destinazione}. Questo giro non fa fallire niente, per costruzione.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
