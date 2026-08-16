#!/usr/bin/env python3
"""Le settimane storte: gli scenari in cui il motore non ha niente su cui appoggiarsi.

Girano sopra il runner del tier 2 (`loop_runner.py`): stesso meccanismo, ma la
copia del fixture viene **guastata apposta** prima di partire, e i controlli
sono quelli specifici dello scenario.

    python3 tests/scenari.py --dry-run
    python3 tests/scenari.py --scenario dispensa-vuota
    python3 tests/scenari.py --scenario tutti

In alcuni di questi scenari il comportamento giusto e' **rifiutare e dirlo**:
una riga marcata `[formato da verificare]` e' un successo, non un fallimento.
Le asserzioni sono scritte di conseguenza — quello che non deve mai succedere
e' che il motore riempia il buco con un numero verosimile.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)

import asserzioni  # noqa: E402
import loop_runner  # noqa: E402
from asserzioni import FALLITA, NON_VERIFICABILE, OK, Casa, Esito  # noqa: E402

FIXTURES = loop_runner.FIXTURES


# ------------------------------------------------------------------ guasti

def svuota_dispensa(casa):
    with open(os.path.join(casa, "dati", "dispensa.yaml"), "w", encoding="utf-8") as f:
        f.write("# FIXTURE SINTETICO — dispensa svuotata apposta\naggiornata: 2026-08-16\n"
                "avanzi: {}\nfreezer: []\n")


def tutte_le_cene_fuori(casa):
    percorso = os.path.join(casa, "dati", "ritmi.yaml")
    giorni = ["lunedi", "martedi", "mercoledi", "giovedi", "venerdi", "sabato", "domenica"]
    righe = ["# FIXTURE SINTETICO — settimana senza nemmeno una cena a casa", "settimana:"]
    for indice, giorno in enumerate(giorni):
        righe += [f"  {giorno}:", "    tutti:",
                  f"      cena: {'ristorante' if indice % 2 else 'fuori'}"]
    with open(percorso, "w", encoding="utf-8") as f:
        f.write("\n".join(righe) + "\n")


def scontrino_dimezzato(casa):
    """Meta' della lista non e' arrivata: e' il caso che vale meta' della skill."""
    origine = os.path.join(FIXTURES, "scontrino", "scontrino-famiglia.txt")
    with open(origine, encoding="utf-8") as f:
        righe = f.read().splitlines()
    tenute, saltate = [], 0
    for riga in righe:
        # una riga di prodotto ha un prezzo in fondo; l'intestazione e il totale no
        if re.search(r"\d+[.,]\d\d\s*$", riga) and "TOTALE" not in riga.upper():
            saltate += 1
            if saltate % 2 == 0:
                continue
        tenute.append(riga)
    destinazione = os.path.join(casa, "scontrino-monco.txt")
    with open(destinazione, "w", encoding="utf-8") as f:
        f.write("\n".join(tenute) + "\n")
    subprocess.run([sys.executable, os.path.join(FIXTURES, "scontrino", "genera_pdf.py"),
                    destinazione, "--out", os.path.join(casa, "scontrino-monco.pdf")],
                   capture_output=True, text=True)


def ingrediente_che_nessuno_conosce(casa):
    with open(os.path.join(casa, "dati", "ricette.md"), "a", encoding="utf-8") as f:
        f.write("\n## Sformato di quinoncia [fine]\n"
                "- kcal: 400 a porzione — stimate CREA\n"
                "- per 2: 200 g di quinoncia secca, 300 g di verdure miste\n"
                "- fonte: fixture sintetico, la quinoncia non esiste\n"
                "- nota: serve a vedere cosa fa il motore con un prodotto che nessun "
                "database conosce\n")


def esclusione_in_forma_nascosta(casa):
    percorso = os.path.join(casa, "dati", "profilo.yaml")
    with open(percorso, encoding="utf-8") as f:
        testo = f.read()
    testo = re.sub(r"^esclusioni:\s*$", "esclusioni:\n  - pomodoro", testo,
                   count=1, flags=re.MULTILINE)
    with open(percorso, "w", encoding="utf-8") as f:
        f.write(testo)


def senza_git(casa):
    percorso = os.path.join(casa, "dati", "profilo.yaml")
    with open(percorso, encoding="utf-8") as f:
        testo = f.read()
    with open(percorso, "w", encoding="utf-8") as f:
        f.write(re.sub(r"^git:\s*locale\s*$", "git: no", testo, count=1, flags=re.MULTILINE))


# ---------------------------------------------------------------- controlli

def trascrizione(casa, fase):
    cartella = os.path.join(os.path.dirname(casa), "trascrizioni")
    for nome in os.listdir(cartella) if os.path.isdir(cartella) else []:
        if nome.endswith(f"-{fase}.json"):
            with open(os.path.join(cartella, nome), encoding="utf-8") as f:
                try:
                    return json.load(f).get("result", "")
                except json.JSONDecodeError:
                    return f.read()
    return ""


def c_menu_esce_lo_stesso(casa):
    if Casa(casa).markdown_settimana():
        return Esito("il menu esce anche a dispensa vuota", OK)
    return Esito("il menu esce anche a dispensa vuota", FALLITA,
                 "nessun markdown di settimana: la prima settimana di una casa nuova e' questa")


def c_nessuna_scorta_inventata(casa):
    testo = Casa(casa).testo_settimana() or ""
    if re.search(r"^#+\s*.*gi[aà]'? in casa", testo, re.MULTILINE | re.IGNORECASE):
        return Esito("niente scorte inventate", FALLITA,
                     "la dispensa era vuota ma il menu ha una sezione «Gia' in casa»",
                     "mai inventare cio' che c'e' in casa")
    return Esito("niente scorte inventate", OK)


def c_nessuna_cena_cucinata(casa):
    testo = (Casa(casa).testo_settimana() or "").lower()
    if not testo:
        return Esito("nessuna cena cucinata", NON_VERIFICABILE, "nessun markdown")
    cene = re.findall(r"^.*\bcena\b.*$", testo, re.MULTILINE)
    if not cene:
        return Esito("nessuna cena cucinata", FALLITA, "il menu non nomina nemmeno le cene",
                     "una cella che non si cucina si scrive lo stesso, marcata")
    cucinate = [c for c in cene
                if not re.search(r"(fuori|ristorante|non si cucina|nessuno)", c)]
    if cucinate:
        return Esito("nessuna cena cucinata", FALLITA,
                     f"{len(cucinate)} cene con un piatto in una settimana tutta fuori: "
                     + cucinate[0][:90])
    return Esito("nessuna cena cucinata", OK, f"{len(cene)} cene, tutte marcate")


def c_mancanze_dichiarate(casa):
    testo = trascrizione(casa, "spesa").lower()
    if not testo:
        return Esito("le mancanze si dicono", NON_VERIFICABILE, "nessuna trascrizione")
    if re.search(r"(manca|non c'|non e' arrivat|sostitu)", testo):
        return Esito("le mancanze si dicono", OK)
    return Esito("le mancanze si dicono", FALLITA,
                 "meta' della lista non e' arrivata e la skill non l'ha nominato")


def c_niente_formati_inventati(casa):
    """Un prodotto che nessun database conosce non prende un formato dal nulla."""
    sospetti = []
    for identificativo, prodotto in Casa(casa).paniere().items():
        fonte = (prodotto.get("fonte_formato") or {})
        if not isinstance(fonte, dict):
            sospetti.append(identificativo)
            continue
        quale = str(fonte.get("fonte", ""))
        if prodotto.get("formato_g") and (not quale or not fonte.get("data")):
            sospetti.append(identificativo)
        if quale.startswith("openfoodfacts") and not prodotto.get("ean"):
            sospetti.append(f"{identificativo} (OFF senza EAN)")
    if sospetti:
        return Esito("nessun formato inventato", FALLITA, f"prodotti: {sorted(set(sospetti))[:4]}",
                     "ogni formato porta fonte e data, o la riga resta in grammi marcata")
    testo = (Casa(casa).testo_settimana() or "").lower()
    if "quinoncia" in testo and "da verificare" not in testo:
        # non e' di per se' un errore: puo' aver chiesto all'utente. Ma senza
        # nessuno che risponda, headless, il marcatore e' l'unica uscita onesta.
        return Esito("nessun formato inventato", FALLITA,
                     "l'ingrediente sconosciuto e' in lista senza marcatore «da verificare»")
    return Esito("nessun formato inventato", OK)


def c_esclusione_nascosta_rispettata(casa):
    testo = (Casa(casa).testo_settimana() or "").lower()
    if not testo:
        return Esito("l'esclusione vale anche nascosta", NON_VERIFICABILE, "nessun markdown")
    forme = ["pomodoro", "pomodorini", "passata", "pelati", "concentrato di pomodoro",
             "sugo", "ketchup", "pizzaiola", "arrabbiata", "napoletana"]
    trovate = [f for f in forme if re.search(rf"\b{re.escape(f)}", testo)]
    if trovate:
        return Esito("l'esclusione vale anche nascosta", FALLITA,
                     f"escluso il pomodoro, nel menu c'e': {trovate}",
                     "regola non negoziabile: vale come ingrediente nascosto")
    return Esito("l'esclusione vale anche nascosta", OK)


def c_nessun_commit(casa):
    messaggi = Casa(casa).commit()
    if messaggi is None:
        return Esito("con `git: no` non si committa", OK, "nessun repo")
    oltre = [m for m in messaggi if not m.startswith("fixture:")]
    if oltre:
        return Esito("con `git: no` non si committa", FALLITA, f"commit fatti lo stesso: {oltre}",
                     "chi mette `git: no` non vuole commit")
    return Esito("con `git: no` non si committa", OK)


def c_ha_scritto_lo_stesso(casa):
    if Casa(casa).markdown_settimana():
        return Esito("senza git il motore lavora uguale", OK)
    return Esito("senza git il motore lavora uguale", FALLITA, "nessun menu generato")


# ----------------------------------------------------------------- scenari

class Scenario:
    def __init__(self, nome, fixture, fasi, guasto, controlli, perche, prompt_extra=None):
        self.nome = nome
        self.fixture = fixture
        self.fasi = fasi
        self.guasto = guasto
        self.controlli = controlli
        self.perche = perche
        self.prompt_extra = prompt_extra


SCENARI = [
    Scenario("dispensa-vuota", "single", ["settimana"], svuota_dispensa,
             [c_menu_esce_lo_stesso, c_nessuna_scorta_inventata],
             "la prima settimana di una casa nuova: dispensa vuota per definizione"),
    Scenario("tutto-fuori", "famiglia", ["settimana"], tutte_le_cene_fuori,
             [c_menu_esce_lo_stesso, c_nessuna_cena_cucinata],
             "una settimana in cui non si cena mai a casa"),
    Scenario("scontrino-monco", "famiglia", ["settimana", "spesa"], scontrino_dimezzato,
             [c_mancanze_dichiarate],
             "meta' della lista non e' arrivata",
             prompt_extra="Lo scontrino di oggi e' scontrino-monco.pdf nella cartella."),
    Scenario("prodotto-ignoto", "single", ["settimana"], ingrediente_che_nessuno_conosce,
             [c_menu_esce_lo_stesso, c_niente_formati_inventati],
             "un ingrediente che nessun database conosce"),
    Scenario("esclusione-nascosta", "famiglia", ["settimana"], esclusione_in_forma_nascosta,
             [c_esclusione_nascosta_rispettata],
             "un'esclusione che si nasconde dentro altri ingredienti"),
    Scenario("senza-git", "coppia-dispensa-profonda", ["settimana"], senza_git,
             [c_nessun_commit, c_ha_scritto_lo_stesso],
             "una casa che il versionamento non lo vuole"),
]


def main(argomenti=None):
    parser = argparse.ArgumentParser(description="Scenari avversi sopra il runner del tier 2")
    parser.add_argument("--scenario", default="tutti", help="nome dello scenario, o `tutti`")
    parser.add_argument("--lavoro", default=None)
    parser.add_argument("--modello", default=None)
    parser.add_argument("--budget", type=float, default=None)
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    argomenti = parser.parse_args(argomenti)

    scelti = SCENARI if argomenti.scenario == "tutti" else \
        [s for s in SCENARI if s.nome == argomenti.scenario]
    if not scelti:
        print(f"scenario sconosciuto: {argomenti.scenario}", file=sys.stderr)
        print("disponibili: " + ", ".join(s.nome for s in SCENARI), file=sys.stderr)
        return 2
    if not shutil.which("claude") and not argomenti.dry_run:
        print("claude non e' nel PATH.", file=sys.stderr)
        return 2

    base = argomenti.lavoro or tempfile.mkdtemp(prefix="lunario-scenari-")
    fallite = 0
    for scenario in scelti:
        lavoro = os.path.join(base, scenario.nome)
        os.makedirs(lavoro, exist_ok=True)
        print(f"\n=== {scenario.nome} — {scenario.perche}")
        if scenario.prompt_extra:
            originale = loop_runner.PROMPT[scenario.fasi[-1]]
            loop_runner.PROMPT[scenario.fasi[-1]] = \
                lambda f, c, o=originale, e=scenario.prompt_extra: (o(f, c) or "") + "\n" + e
        corsa = loop_runner.Corsa(scenario.fixture, lavoro, argomenti)
        corsa.gira(scenario.fasi, mutazione=scenario.guasto)
        if scenario.prompt_extra:
            loop_runner.PROMPT[scenario.fasi[-1]] = originale
        if argomenti.dry_run:
            print(f"  (guasto: {scenario.guasto.__name__}, controlli: "
                  + ", ".join(c.__name__ for c in scenario.controlli) + ")")
            continue
        for controllo in scenario.controlli:
            esito = controllo(corsa.casa)
            if esito.stato == FALLITA:
                fallite += 1
            print(f"  {loop_runner.MARCATORE[esito.stato]} {esito.nome}"
                  + (f" — {esito.dettaglio}" if esito.dettaglio else ""))
            if esito.stato == FALLITA and esito.regola:
                print(f"        regola: {esito.regola}")
        for fase, esito in corsa.esiti:
            if esito.stato == asserzioni.FALLITA:
                fallite += 1
                print(f"  {loop_runner.MARCATORE[esito.stato]} [{fase}] {esito.nome} — {esito.dettaglio}")

    print(f"\n{fallite} controlli falliti.")
    return 1 if fallite else 0


if __name__ == "__main__":
    sys.exit(main())
