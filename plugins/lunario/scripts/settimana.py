#!/usr/bin/env python3
"""Dove stanno i file di una settimana, e qual e' quello vivo.

La settimana e' una cartella, e dentro ci sono fino a sei documenti piu' due
file di dati. Cinque skill devono sapere gli stessi nomi e la stessa regola su
quale documento si scrive adesso: scritta cinque volte in prosa, dopo tre
release sarebbero cinque regole diverse.

    python3 settimana.py                      # la settimana di oggi, o l'ultima
    python3 settimana.py --iso 2026-W34
    python3 settimana.py --json
    python3 settimana.py --slug "Yellow Submarine"

**Il file vivo e' l'ultimo ruolo che esiste su disco**: se c'e' il consuntivo e'
quello, altrimenti il preventivo. Non si guardano date ne' lo `stato:` scritto
in testa — un solo posto da cui la risposta puo' venire, e nessun modo di
spuntare il file sbagliato in silenzio.

Il layout vecchio — markdown e HTML **accanto** alla cartella invece che dentro
— si legge come sempre: le settimane passate sono un registro e non si
rinominano. Li' il file vivo e' quell'unico markdown, che nasce preventivo e
diventa consuntivo riscrivendosi.

Zero dipendenze esterne, come tutto il resto del motore.
"""

import argparse
import datetime
import json
import os
import re
import sys
import unicodedata

# I ruoli, in ordine di vita: si nasce preventivo e si finisce postmortem. Il
# file vivo e' l'ultimo di questa fila che esiste davvero, `lista` esclusa —
# quella non e' un documento della settimana, e' lo strumento del supermercato.
RUOLI = ("preventivo", "lista", "consuntivo", "postmortem")
RUOLI_VIVI = ("consuntivo", "preventivo")
RUOLI_HTML = ("preventivo", "consuntivo")
DATI_SETTIMANA = ("contesto.yaml", "diario.yaml")

ISO = re.compile(r"^\d{4}-W\d{2}$")
NOME = re.compile(r"^(\d{4}-W\d{2})(-[a-z0-9]+(?:-[a-z0-9]+)*)?$")


def slug(titolo):
    """Minuscolo, accenti tolti, tutto cio' che non e' lettera o cifra a `-`."""
    piano = unicodedata.normalize("NFKD", str(titolo))
    piano = "".join(c for c in piano if not unicodedata.combining(c))
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", piano.lower())).strip("-")


def iso_di_oggi(oggi=None):
    anno, settimana, _giorno = (oggi or datetime.date.today()).isocalendar()
    return f"{anno}-W{settimana:02d}"


def _settimane(radice):
    cartella = os.path.join(radice, "settimane")
    if not os.path.isdir(cartella):
        return cartella, []
    nomi = set()
    for voce in os.listdir(cartella):
        radice_nome = re.sub(r"\.(md|html)$", "", voce)
        if NOME.match(radice_nome):
            nomi.add(radice_nome)
    return cartella, sorted(nomi)


def trova(radice, iso=None):
    """Il nome della settimana chiesta: quella dell'ISO, o l'ultima che c'e'.

    Torna (nome, come): `come` dice se e' quella chiesta o un ripiego, perche'
    una skill che lavora sulla settimana sbagliata deve poterlo dire.
    """
    _cartella, nomi = _settimane(radice)
    if not nomi:
        return None, "nessuna settimana"
    if iso:
        candidati = [n for n in nomi if n.startswith(iso)]
        if candidati:
            return sorted(candidati)[-1], "chiesta"
        return sorted(nomi)[-1], f"nessuna {iso}: l'ultima e' questa"
    corrente = [n for n in nomi if n.startswith(iso_di_oggi())]
    if corrente:
        return sorted(corrente)[-1], "settimana corrente"
    return sorted(nomi)[-1], "nessuna settimana corrente: l'ultima e' questa"


def percorsi(radice, nome):
    """Tutti i posti in cui quella settimana puo' avere qualcosa, esista o no."""
    settimane = os.path.join(radice, "settimane")
    cartella = os.path.join(settimane, nome)
    dentro = {}
    for ruolo in RUOLI:
        dentro[ruolo] = os.path.join(cartella, f"{nome}-{ruolo}.md")
    for ruolo in RUOLI_HTML:
        dentro[f"{ruolo}_html"] = os.path.join(cartella, f"{nome}-{ruolo}.html")
    for dato in DATI_SETTIMANA:
        dentro[dato[:-5]] = os.path.join(cartella, dato)
    dentro["cartella"] = cartella
    dentro["_piatto_md"] = os.path.join(settimane, f"{nome}.md")
    dentro["_piatto_html"] = os.path.join(settimane, f"{nome}.html")
    return dentro


def risolvi(radice, iso=None):
    nome, come = trova(radice, iso)
    if not nome:
        return None
    posti = percorsi(radice, nome)
    esistono = {chiave: p for chiave, p in posti.items()
                if not chiave.startswith("_") and os.path.exists(p)}
    nella_cartella = any(chiave in esistono for chiave in RUOLI)

    if nella_cartella:
        layout = "cartella"
    elif os.path.isfile(posti["_piatto_md"]):
        layout = "piatto"
    else:
        layout = "cartella"

    if layout == "piatto":
        # Un file solo che fa da preventivo e da consuntivo: e' il vivo per
        # definizione, e non c'e' niente da scegliere.
        esistono["preventivo"] = posti["_piatto_md"]
        if os.path.isfile(posti["_piatto_html"]):
            esistono["preventivo_html"] = posti["_piatto_html"]
        vivo = posti["_piatto_md"]
    else:
        vivo = next((esistono[r] for r in RUOLI_VIVI if r in esistono), None)

    return {
        "nome": nome,
        "iso": nome[:8],
        "come": come,
        "layout": layout,
        "cartella": posti["cartella"],
        "vivo": vivo,
        "esistono": esistono,
        "attesi": {c: p for c, p in posti.items() if not c.startswith("_")},
    }


def _relativi(radice, mappa):
    return {c: os.path.relpath(p, radice) for c, p in mappa.items()}


def stampa(radice, esito):
    print(f"settimana: {esito['nome']}  ({esito['come']})")
    print(f"layout: {esito['layout']}"
          + ("  — markdown e HTML accanto alla cartella, com'era prima: si legge, non si rinomina"
             if esito["layout"] == "piatto" else ""))
    vivo = esito["vivo"]
    dove = os.path.relpath(vivo, radice) if vivo else "— nessun documento: il menu non e' ancora uscito"
    print(f"vivo: {dove}")
    print("ci sono:")
    for chiave, percorso in sorted(_relativi(radice, esito["esistono"]).items()):
        if chiave == "cartella":
            continue
        print(f"  · {chiave}: {percorso}")
    mancanti = [c for c in RUOLI + tuple(f"{r}_html" for r in RUOLI_HTML)
                if c not in esito["esistono"]]
    if mancanti and esito["layout"] == "cartella":
        print("mancano: " + ", ".join(mancanti))


def main(argomenti=None):
    parser = argparse.ArgumentParser(description="I file di una settimana di Lunario")
    parser.add_argument("--casa", default=".", help="la cartella di casa (default: quella corrente)")
    parser.add_argument("--iso", default="", help="la settimana, in ISO (default: quella di oggi)")
    parser.add_argument("--json", action="store_true", help="uscita JSON")
    parser.add_argument("--slug", default="", metavar="TITOLO",
                        help="lo slug di un titolo, e basta: non guarda il disco")
    argomenti = parser.parse_args(argomenti)

    if argomenti.slug:
        print(slug(argomenti.slug))
        return 0

    radice = os.path.abspath(argomenti.casa)
    if argomenti.iso and not ISO.match(argomenti.iso):
        print(f"`--iso {argomenti.iso}` non e' un ISO di settimana (2026-W34)", file=sys.stderr)
        return 2

    esito = risolvi(radice, argomenti.iso or None)
    if esito is None:
        print("nessuna settimana in `settimane/`: la crea `lunario:settimana`")
        return 2

    if argomenti.json:
        print(json.dumps({
            "nome": esito["nome"],
            "iso": esito["iso"],
            "come": esito["come"],
            "layout": esito["layout"],
            "vivo": os.path.relpath(esito["vivo"], radice) if esito["vivo"] else None,
            "esistono": _relativi(radice, esito["esistono"]),
            "attesi": _relativi(radice, esito["attesi"]),
        }, ensure_ascii=False, indent=1))
        return 0

    stampa(radice, esito)
    return 0


if __name__ == "__main__":
    sys.exit(main())
