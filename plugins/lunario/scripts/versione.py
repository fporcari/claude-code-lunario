#!/usr/bin/env python3
"""Il timbro di versione della cartella di casa, e come si indovina se non c'e'.

Il motore si aggiorna dal marketplace; la cartella di casa no. Senza un timbro
nessuna skill sa contro quale contratto sono stati scritti i file che sta
leggendo — e quindi nessuna puo' adattarli.

    python3 versione.py --controlla        # 0 = allineata, 3 = va migrata
    python3 versione.py --rileva           # indovina dalla forma, non scrive
    python3 versione.py --scrivi 3

Perche' qui non c'e' un parser YAML: **la rilevazione e' una domanda di testo**,
non di dati. «Questo profilo usa ancora la vecchia grammatica della griglia?»,
«la dispensa ha gia' la sezione delle scorte?» si rispondono guardando le
righe, e un parser in piu' sarebbe una dipendenza in piu' per niente. Le
migrazioni vere — quelle che cambiano il senso di un campo — non le fa questo
script: le fa `lunario:aggiorna`, che e' una skill, perche' vanno lette e non
sostituite a macchina.

Zero dipendenze esterne, come tutto il resto del motore.
"""

import argparse
import datetime
import json
import os
import re
import sys

# Il numero di contratto si muove SOLO quando si muove il contratto dei dati,
# non a ogni versione del plugin. La tabella completa, con cosa cambia a ogni
# passo, sta nella skill `lunario:aggiorna`.
CONTRATTO_CORRENTE = 4

DESCRIZIONE = {
    1: "prima della griglia dei pasti: `bambini:`, `fuori_trasportabile`, settimane senza titolo",
    2: "griglia dei pasti, preventivo/consuntivo, settimane <ISO>-<titolo>, diario",
    3: "dispensa a tre sezioni: le scorte contate accanto agli avanzi e al congelatore",
    4: "la settimana e' una cartella: preventivo, lista, consuntivo e postmortem, ognuno un file",
}


def versione_del_motore():
    """La versione del plugin, letta dal suo manifesto: un numero solo, in un
    posto solo. Scriverla a mano nel timbro vorrebbe dire tenerne allineate due."""
    manifesto = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             ".claude-plugin", "plugin.json")
    try:
        with open(manifesto, encoding="utf-8") as f:
            return json.load(f).get("version", "sconosciuta")
    except (OSError, json.JSONDecodeError):
        return "sconosciuta"


def cartella_dati(radice):
    esplicita = os.environ.get("LUNARIO_DATI")
    if esplicita:
        return esplicita
    return os.path.join(radice, "dati")


def leggi_timbro(dati):
    """Il timbro e' tre scalari: si legge a occhio, senza tirare dentro YAML."""
    percorso = os.path.join(dati, "versione.yaml")
    if not os.path.isfile(percorso):
        return None
    timbro = {}
    with open(percorso, encoding="utf-8") as f:
        for riga in f:
            trovato = re.match(r"^\s*(contratto|motore|migrata)\s*:\s*(\S+)\s*$", riga)
            if trovato:
                timbro[trovato.group(1)] = trovato.group(2)
    if "contratto" not in timbro:
        return None
    try:
        timbro["contratto"] = int(timbro["contratto"])
    except ValueError:
        return None
    return timbro


def scrivi_timbro(dati, contratto, motore, oggi):
    os.makedirs(dati, exist_ok=True)
    percorso = os.path.join(dati, "versione.yaml")
    with open(percorso, "w", encoding="utf-8") as f:
        f.write("# Il timbro della cartella. Lo scrive il sistema, mai l'utente.\n"
                "# `contratto` si muove solo quando si muove il contratto dei dati;\n"
                "# `motore` e' la versione del plugin che ha toccato questa cartella per ultima.\n"
                f"contratto: {contratto}\n"
                f"motore: {motore}\n"
                f"migrata: {oggi}\n")
    return percorso


def _testo(percorso):
    if not os.path.isfile(percorso):
        return ""
    with open(percorso, encoding="utf-8") as f:
        return f.read()


def rileva(dati, radice):
    """Indovina il contratto dalla forma dei file. Non scrive niente.

    Torna (contratto, motivi): i motivi si stampano, perche' una rilevazione
    che non dice come ha concluso non e' verificabile da nessuno.
    """
    profilo = _testo(os.path.join(dati, "profilo.yaml"))
    ritmi = _testo(os.path.join(dati, "ritmi.yaml"))
    motivi = []

    if not profilo:
        return None, ["nessun `dati/profilo.yaml`: qui non c'e' una casa Lunario"]

    vecchi = re.findall(r"\b(fuori_trasportabile|fuori_autonomo)\b", profilo + ritmi)
    if vecchi:
        motivi.append(f"vecchia grammatica della griglia: {sorted(set(vecchi))}")
    if re.search(r"^bambini:\s*$", profilo, re.MULTILINE):
        motivi.append("sezione `bambini:` invece di persone in `famiglia`")
    if re.search(r"^famiglia:\s*$", profilo, re.MULTILINE) and "pasti:" not in profilo \
            and "tolleranze:" not in profilo:
        motivi.append("nessuna griglia dei pasti e nessuna sezione `tolleranze`")

    if motivi:
        return 1, motivi

    settimane = os.path.join(radice, "settimane")
    if _settimana_a_cartella(settimane):
        return 4, ["c'e' gia' una settimana coi documenti dentro la cartella"]

    dispensa = _testo(os.path.join(dati, "dispensa.yaml"))
    if re.search(r"^scorte:\s*$", dispensa, re.MULTILINE):
        return 3, ["la dispensa ha gia' la sezione `scorte`",
                   "nessuna settimana coi documenti dentro la cartella"]

    motivi.append("griglia dei pasti presente")
    motivi.append("la dispensa non ha ancora la sezione `scorte`")
    if os.path.isdir(settimane):
        nomi = [n for n in os.listdir(settimane) if n.endswith(".md")]
        nudi = [n for n in nomi if re.match(r"^\d{4}-W\d{2}\.md$", n)]
        if nudi:
            motivi.append(f"{len(nudi)} settimane col nome ISO nudo, senza titolo "
                          "(restano valide: non si rinominano d'ufficio)")
    return 2, motivi


def _settimana_a_cartella(settimane):
    """Una settimana col preventivo (o la lista) dentro la propria cartella.

    E' il segno del contratto 4, e si vede da fuori: prima i documenti stavano
    **accanto** alla cartella, che conteneva solo contesto e diario.
    """
    if not os.path.isdir(settimane):
        return False
    for voce in os.listdir(settimane):
        cartella = os.path.join(settimane, voce)
        if not os.path.isdir(cartella):
            continue
        for dentro in os.listdir(cartella):
            if re.search(r"-(preventivo|lista|consuntivo|postmortem)\.(md|html)$", dentro):
                return True
    return False


def stato(radice):
    dati = cartella_dati(radice)
    timbro = leggi_timbro(dati)
    if timbro:
        return timbro["contratto"], "dal timbro", []
    contratto, motivi = rileva(dati, radice)
    return contratto, "dalla forma dei file", motivi


def main(argomenti=None):
    parser = argparse.ArgumentParser(description="Il timbro di versione di una cartella Lunario")
    parser.add_argument("--casa", default=".", help="la cartella di casa (default: quella corrente)")
    parser.add_argument("--controlla", action="store_true",
                        help="0 se allineata, 3 se va migrata, 2 se non e' una casa Lunario")
    parser.add_argument("--rileva", action="store_true", help="indovina dalla forma e spiega come")
    parser.add_argument("--scrivi", type=int, metavar="N", help="scrive il timbro a contratto N")
    parser.add_argument("--motore", default="", help="di default, la versione nel manifesto del plugin")
    parser.add_argument("--data", default="", help="di default, oggi")
    argomenti = parser.parse_args(argomenti)

    radice = os.path.abspath(argomenti.casa)
    dati = cartella_dati(radice)

    if argomenti.scrivi is not None:
        motore = argomenti.motore or versione_del_motore()
        oggi = argomenti.data or datetime.date.today().isoformat()
        percorso = scrivi_timbro(dati, argomenti.scrivi, motore, oggi)
        print(f"timbro scritto: contratto {argomenti.scrivi}, motore {motore} ({percorso})")
        return 0

    if argomenti.rileva:
        contratto, motivi = rileva(dati, radice)
        if contratto is None:
            print("non e' una cartella di casa Lunario: " + "; ".join(motivi))
            return 2
        print(f"contratto rilevato dalla forma: {contratto} — {DESCRIZIONE.get(contratto, '')}")
        for motivo in motivi:
            print(f"  · {motivo}")
        return 0

    contratto, come, motivi = stato(radice)
    if contratto is None:
        print("non e' una cartella di casa Lunario: " + "; ".join(motivi))
        return 2
    if contratto == CONTRATTO_CORRENTE:
        print(f"ok: contratto {contratto}, allineata (letto {come})")
        return 0
    if contratto > CONTRATTO_CORRENTE:
        print(f"attenzione: la cartella e' al contratto {contratto}, il motore si ferma a "
              f"{CONTRATTO_CORRENTE}. Aggiorna il plugin: questa versione ignora cio' che non conosce.")
        return 0
    print(f"migrazione necessaria: {contratto} -> {CONTRATTO_CORRENTE} (letto {come})")
    for motivo in motivi:
        print(f"  · {motivo}")
    return 3


if __name__ == "__main__":
    sys.exit(main())
