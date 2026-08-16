#!/usr/bin/env python3
"""Tier 2 — il giro completo, su una casa sintetica usa e getta.

Copia un fixture in una cartella temporanea, ci fa girare il motore headless
(`claude -p`, col plugin caricato da questo repo via `--plugin-dir`) nella
sequenza vera — settimana → spesa → prepara → correggi → postmortem — e dopo
ogni fase controlla le proprieta' di `asserzioni.py`.

    python3 tests/loop_runner.py --dry-run             # niente token: mostra cosa farebbe
    python3 tests/loop_runner.py --fixture famiglia
    python3 tests/loop_runner.py --fixture tutti --lavoro /tmp/lunario-test

**Costa token veri.** Non gira in CI: si lancia a mano prima di una release.
Il tier 1 (`lint_dati.py`) e' quello che gira sempre.

I prompt sono scritti per una conversazione a un colpo solo: headless nessuno
risponde alle domande, quindi il contesto che il lunedi' l'utente racconterebbe
a pezzi qui arriva tutto insieme. E' l'unica differenza rispetto all'uso vero,
ed e' dichiarata: cio' che si sta testando e' cosa il motore **lascia sui
file**, non come conduce la conversazione.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Il lint dei contratti e' del motore, non dei test: e' la stessa verifica che
# `lunario:tagliando` esegue dentro una cartella di casa.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "plugins", "lunario", "scripts"))
import asserzioni  # noqa: E402
from lint_dati import ERRORE, Lint  # noqa: E402

QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(QUI)
PLUGIN = os.path.join(REPO, "plugins", "lunario")
FIXTURES = os.path.join(QUI, "fixtures")
SCONTRINO = os.path.join(FIXTURES, "scontrino", "scontrino-famiglia.pdf")

FASI = ["settimana", "spesa", "prepara", "correggi", "postmortem"]


def prompt_settimana(fixture):
    comune = (
        "Lancia la skill lunario:settimana per la settimana che comincia lunedi' prossimo. "
        "Sono in modalita' non interattiva: NON farmi domande, ti do tutto adesso e tu "
        "generi il menu e la lista fino in fondo, salvando i file.\n\n"
    )
    per_fixture = {
        "famiglia": (
            "Impegni: giovedi' sera cena di lavoro per Adulto1, quindi giovedi' cena e' "
            "`ristorante` per lui e a casa siamo in tre. Nient'altro fuori dai ritmi soliti.\n"
            "Voglie: qualcosa con le melanzane. Stufi delle polpette.\n"
            "In casa, oltre a quello che sai: c'e' anche mezzo pacco di riso e due scatole "
            "di fagioli che non hai segnato. Il congelatore e' quello che risulta.\n"
        ),
        "single": (
            "Impegni: mercoledi' pranzo me lo porto al lavoro come sempre, venerdi' sera "
            "sono fuori a cena da amici — quindi `fuori`, non pago io.\n"
            "Voglie: niente di particolare. Sono stufo della zuppa di lenticchie.\n"
            "In casa non c'e' altro oltre a quello che risulta in dispensa.\n"
        ),
        "coppia-dispensa-profonda": (
            "Impegni: nessuno, settimana normale, si mangia sempre a casa.\n"
            "Voglie: niente di particolare.\n"
            "In casa c'e' molta roba: la dispensa e' piena, prima di comprare qualsiasi "
            "cosa guarda cosa risulta gia' esserci e dimmelo.\n"
        ),
    }
    return comune + per_fixture.get(fixture, per_fixture["famiglia"])


def prompt_spesa(fixture, casa):
    if fixture != "famiglia":
        return None  # lo scontrino sintetico e' tarato sul paniere di `famiglia`
    return (
        "Ho ritirato la spesa. Lancia lunario:spesa. Lo scontrino e' qui: "
        f"{SCONTRINO}\n\n"
        "Rispondo in anticipo a tutto, non farmi domande: le righe alimentari sono tutte "
        "nostre, non compriamo per nessun altro. Il pane lo prendo dal panettiere come "
        "sempre. Se manca qualcosa non cambiare il piatto: me lo procuro io prima del "
        "giorno in cui serve. Vai fino in fondo e salva i file."
    )


def prompt_prepara(fixture, casa):
    return (
        "Lancia lunario:prepara: sto cucinando adesso la cena di oggi, quella che risulta "
        "in menu — confermo che e' quella, non chiedermelo.\n\n"
        "Ti do subito tutto quello che chiederesti alla fine, cosi' non serve tornare: "
        "ho finito, difficolta' 2 su 5, voto del cuoco 4 su 5, ci ho messo 35 minuti veri. "
        "E' avanzata mezza porzione. A tavola c'erano tutti quelli previsti. "
        "Chiudi il pasto: spunta il menu e scrivi il diario."
    )


def prompt_correggi(fixture, casa):
    return (
        "Lancia lunario:correggi. Cambia una cosa: domani sera salta la cena prevista, "
        "ordiniamo la pizza — quindi quella cella diventa `ristorante`. "
        "Non farmi domande: quello che c'e' in frigo e' quello che risulta dal menu non "
        "ancora spuntato. Rigenera solo i giorni che restano riusando la spesa gia' fatta, "
        "aggiorna il contesto della settimana e scrivi il diario."
    )


def prompt_postmortem(fixture, casa):
    return (
        "Lancia lunario:postmortem, chiudiamo la settimana. Ti do tutto in un colpo, "
        "non farmi domande una per volta.\n\n"
        "Avanzi: e' avanzata pasta, come la settimana scorsa. Il resto e' finito.\n"
        "Voti: il piatto di lunedi' 4, quello di mercoledi' 2 e non e' piaciuto a nessuno.\n"
        "La settimana e' andata come previsto tranne la cena diventata pizza.\n"
        "Spesa extra: 12,00 euro al negozio sotto casa giovedi'. La pizza d'asporto "
        "e' costata 34,00 euro.\n"
        "La pesata la salto questa settimana.\n"
        "Applica le ritarature che ne conseguono e salva."
    )


# I test verificano **proprieta'**, non la finezza di una frase: girano su
# Sonnet perche' una suite che costa quanto una release non la lancia nessuno.
# Con `--modello` si passa qualunque altro, quando serve davvero.
MODELLO_PREDEFINITO = "sonnet"

PROMPT = {
    "settimana": lambda f, c: prompt_settimana(f),
    "spesa": prompt_spesa,
    "prepara": prompt_prepara,
    "correggi": prompt_correggi,
    "postmortem": prompt_postmortem,
}


class Corsa:
    def __init__(self, fixture, cartella_lavoro, opzioni):
        self.fixture = fixture
        self.opzioni = opzioni
        self.casa = os.path.join(cartella_lavoro, fixture)
        self.esiti = []
        self.registro = []

    # ------------------------------------------------------------------ preparazione

    def prepara(self, mutazione=None):
        origine = os.path.join(FIXTURES, self.fixture)
        if not os.path.isdir(origine):
            raise SystemExit(f"fixture sconosciuto: {self.fixture}")
        if os.path.exists(self.casa):
            shutil.rmtree(self.casa)
        shutil.copytree(origine, self.casa)
        if mutazione:
            mutazione(self.casa)
        self._git("init", "-q")
        self._git("add", "-A")
        self._git("-c", "user.email=test@lunario", "-c", "user.name=test",
                  "commit", "-q", "-m", "fixture: stato iniziale")
        return self.casa

    def _git(self, *argomenti):
        return subprocess.run(["git", *argomenti], cwd=self.casa,
                              capture_output=True, text=True)

    def istantanea(self):
        casa = asserzioni.Casa(self.casa)
        return {"dispensa": casa.dispensa(), "storico": casa.storico()}

    # ------------------------------------------------------------------- esecuzione

    def comando(self, prompt):
        argomenti = ["claude", "-p", prompt,
                     "--plugin-dir", PLUGIN,
                     "--permission-mode", "bypassPermissions",
                     "--output-format", "json"]
        if self.opzioni.modello:
            argomenti += ["--model", self.opzioni.modello]
        if self.opzioni.budget:
            argomenti += ["--max-budget-usd", str(self.opzioni.budget)]
        return argomenti

    def esegui_fase(self, fase, prima):
        prompt = PROMPT[fase](self.fixture, self.casa)
        if prompt is None:
            self.registro.append((fase, "saltata", "nessun prompt per questo fixture"))
            return []
        argomenti = self.comando(prompt)
        if self.opzioni.dry_run:
            print(f"\n--- {self.fixture} / {fase}")
            print("  $ " + " ".join(a if " " not in a else f"'{a[:60]}…'" for a in argomenti))
            print("  prompt:")
            for riga in prompt.splitlines():
                print("    " + riga)
            return []

        inizio = time.time()
        try:
            uscita = subprocess.run(argomenti, cwd=self.casa, capture_output=True,
                                    text=True, timeout=self.opzioni.timeout)
        except subprocess.TimeoutExpired:
            self.registro.append((fase, "timeout", f"oltre {self.opzioni.timeout}s"))
            return [asserzioni.Esito(f"{fase}: la skill termina", asserzioni.FALLITA, "timeout")]
        durata = time.time() - inizio
        self._salva_trascrizione(fase, uscita.stdout)
        # `claude -p` puo' fallire dicendolo **su stdout**, dentro il JSON, e
        # uscire lo stesso con 0: senza guardare `is_error` una sessione morta
        # sembrerebbe un giro andato bene con dei file che non ha scritto nessuno.
        motivo = self._perche_e_fallita(uscita)
        if motivo:
            self.registro.append((fase, "errore", motivo[:400]))
            return [asserzioni.Esito(f"{fase}: la skill termina", asserzioni.FALLITA, motivo[:300])]
        self.registro.append((fase, "ok", f"{durata:.0f}s"))

        casa = asserzioni.Casa(self.casa, prima=prima)
        return asserzioni.per_fase(fase, casa)

    @staticmethod
    def _perche_e_fallita(uscita):
        """None se e' andata bene, altrimenti il motivo in chiaro."""
        try:
            risposta = json.loads(uscita.stdout)
        except (json.JSONDecodeError, ValueError):
            risposta = None
        if isinstance(risposta, dict) and risposta.get("is_error"):
            return (f"{risposta.get('terminal_reason') or 'errore'}: "
                    f"{risposta.get('result') or 'nessun dettaglio'}")
        if uscita.returncode != 0:
            dettaglio = (uscita.stderr or "").strip() or (uscita.stdout or "").strip()
            return f"uscita {uscita.returncode}: {dettaglio}"
        return None

    def _salva_trascrizione(self, fase, testo):
        cartella = os.path.join(os.path.dirname(self.casa), "trascrizioni")
        os.makedirs(cartella, exist_ok=True)
        with open(os.path.join(cartella, f"{self.fixture}-{fase}.json"), "w",
                  encoding="utf-8") as f:
            f.write(testo)

    def gira(self, fasi, mutazione=None):
        self.prepara(mutazione)
        for fase in fasi:
            prima = self.istantanea()
            for esito in self.esegui_fase(fase, prima):
                self.esiti.append((fase, esito))
        if not self.opzioni.dry_run:
            violazioni = Lint(self.casa).esegui()
            for violazione in violazioni:
                if violazione.livello == ERRORE:
                    self.esiti.append(("lint", asserzioni.Esito(
                        f"contratto: {violazione.codice}", asserzioni.FALLITA,
                        f"{violazione.file}: {violazione.messaggio}")))
        return self.esiti


# ---------------------------------------------------------------------- rapporto

MARCATORE = {asserzioni.OK: "ok  ", asserzioni.FALLITA: "NO  ",
             asserzioni.NON_VERIFICABILE: "-   "}


def rapporto(corse):
    fallite = 0
    for corsa in corse:
        print(f"\n=== {corsa.fixture}  ({corsa.casa})")
        for fase, stato, dettaglio in corsa.registro:
            print(f"  · fase {fase}: {stato} {dettaglio}")
        for fase, esito in corsa.esiti:
            if esito.stato == asserzioni.FALLITA:
                fallite += 1
            riga = f"  {MARCATORE[esito.stato]} [{fase}] {esito.nome}"
            if esito.dettaglio:
                riga += f" — {esito.dettaglio}"
            print(riga)
            if esito.stato == asserzioni.FALLITA and esito.regola:
                print(f"        regola: {esito.regola}")
    print(f"\n{fallite} proprieta' violate.")
    return 1 if fallite else 0


def main(argomenti=None):
    parser = argparse.ArgumentParser(description="Tier 2: il giro completo su una casa sintetica")
    parser.add_argument("--fixture", default="famiglia",
                        help="famiglia | single | coppia-dispensa-profonda | tutti")
    parser.add_argument("--fasi", default=",".join(FASI), help="sottoinsieme delle fasi, separate da virgola")
    parser.add_argument("--lavoro", default=None, help="dove tenere la copia di lavoro")
    parser.add_argument("--modello", default=MODELLO_PREDEFINITO,
                        help=f"passa --model a claude (default: {MODELLO_PREDEFINITO})")
    parser.add_argument("--budget", type=float, default=None, help="tetto in dollari per fase")
    parser.add_argument("--timeout", type=int, default=900, help="secondi per fase")
    parser.add_argument("--dry-run", action="store_true", help="mostra i comandi, non spende niente")
    parser.add_argument("--json", action="store_true", help="uscita JSON")
    argomenti = parser.parse_args(argomenti)

    if not shutil.which("claude") and not argomenti.dry_run:
        print("claude non e' nel PATH: il tier 2 non puo' girare.", file=sys.stderr)
        return 2
    if not os.path.isdir(PLUGIN):
        print(f"plugin non trovato in {PLUGIN}", file=sys.stderr)
        return 2

    fixture = argomenti.fixture
    nomi = ([n for n in sorted(os.listdir(FIXTURES))
             if os.path.isdir(os.path.join(FIXTURES, n, "dati"))]
            if fixture == "tutti" else [fixture])
    fasi = [f.strip() for f in argomenti.fasi.split(",") if f.strip()]
    sconosciute = [f for f in fasi if f not in FASI]
    if sconosciute:
        print(f"fasi sconosciute: {sconosciute}", file=sys.stderr)
        return 2

    lavoro = argomenti.lavoro or tempfile.mkdtemp(prefix="lunario-test-")
    os.makedirs(lavoro, exist_ok=True)
    corse = []
    for nome in nomi:
        corsa = Corsa(nome, lavoro, argomenti)
        corsa.gira(fasi)
        corse.append(corsa)

    if argomenti.json:
        print(json.dumps([{
            "fixture": c.fixture,
            "casa": c.casa,
            "registro": c.registro,
            "esiti": [{"fase": f, **e.come_dizionario()} for f, e in c.esiti],
        } for c in corse], ensure_ascii=False, indent=1))
        return 1 if any(e.stato == asserzioni.FALLITA for c in corse for _f, e in c.esiti) else 0
    return rapporto(corse)


if __name__ == "__main__":
    sys.exit(main())
