#!/usr/bin/env python3
"""Il test del tier 1: il lint passa sui fixture puliti e becca quelli guasti.

    python3 tests/test_lint.py

Zero token, zero dipendenze: si lancia sempre, anche in CI.

Un linter che non e' mai stato visto fallire e' un linter di cui non si sa se
funziona. Qui ogni codice di violazione ha una corruzione che lo produce, e la
corruzione e' scritta in modo generico — si applica a tutti e tre i fixture,
non a quello su cui e' stata provata.
"""

import os
import re
import shutil
import sys
import tempfile
import unittest

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(os.path.dirname(QUI), "plugins", "lunario", "scripts"))

import minyaml  # noqa: E402
import settimana as settimana_del_motore  # noqa: E402
from lint_dati import ERRORE, Lint, cartelle_predefinite  # noqa: E402

FIXTURES = cartelle_predefinite()


# --------------------------------------------------------------- corruzioni

def inserisci_sotto(testo, chiave, righe_nuove):
    """Infila delle righe sotto `chiave:`, con l'indentazione dei suoi figli."""
    righe = testo.splitlines()
    for i, riga in enumerate(righe):
        trovato = re.match(rf"^(\s*){re.escape(chiave)}:\s*$", riga)
        if not trovato:
            continue
        indent_padre = len(trovato.group(1))
        indent_figli = indent_padre + 2
        for successiva in righe[i + 1:]:
            if not successiva.strip() or successiva.lstrip().startswith("#"):
                continue
            candidato = len(successiva) - len(successiva.lstrip(" "))
            if candidato > indent_padre:
                indent_figli = candidato
            break
        blocco = [" " * indent_figli + r for r in righe_nuove]
        return "\n".join(righe[:i + 1] + blocco + righe[i + 1:]) + "\n"
    raise AssertionError(f"chiave `{chiave}` non trovata nel file")


def scrivi(radice, relativo, testo):
    percorso = os.path.join(radice, relativo)
    with open(percorso, "w", encoding="utf-8") as f:
        f.write(testo)


def leggi(radice, relativo):
    with open(os.path.join(radice, relativo), encoding="utf-8") as f:
        return f.read()


def accoda(radice, relativo, testo):
    with open(os.path.join(radice, relativo), "a", encoding="utf-8") as f:
        f.write(testo)


def persona_a_dieta_troppo_bassa(radice):
    testo = leggi(radice, "dati/profilo.yaml")
    scrivi(radice, "dati/profilo.yaml", inserisci_sotto(testo, "famiglia", [
        "- nome: Guasto1",
        "  dieta: true",
        "  kcal_giorno: 900",
        "  peso_obiettivo_kg: 50",
    ]))


def deficit_a_chi_non_e_a_dieta(radice):
    testo = leggi(radice, "dati/profilo.yaml")
    scrivi(radice, "dati/profilo.yaml", inserisci_sotto(testo, "famiglia", [
        "- nome: Guasto2",
        "  dieta: false",
        "  kcal_giorno: 1500",
    ]))


def stato_di_cella_inventato(radice):
    testo = leggi(radice, "dati/profilo.yaml")
    scrivi(radice, "dati/profilo.yaml", inserisci_sotto(testo, "famiglia", [
        "- nome: Guasto3",
        "  dieta: false",
        "  pasti: {cena: quandoCapita}",
    ]))


def grammatica_vecchia(radice):
    testo = leggi(radice, "dati/profilo.yaml")
    scrivi(radice, "dati/profilo.yaml", inserisci_sotto(testo, "famiglia", [
        "- nome: Guasto4",
        "  dieta: false",
        "  pasti: {pranzo: fuori_trasportabile}",
    ]))


def avanzo_fantasma(radice):
    testo = leggi(radice, "dati/dispensa.yaml")
    scrivi(radice, "dati/dispensa.yaml",
           inserisci_sotto(testo, "avanzi", ["prodotto-che-non-esiste-500: 300"]))


def prezzo_senza_data(radice):
    accoda(radice, "dati/prodotti.jsonl",
           '{"id": "guasto-prezzo", "nome": "Prodotto guasto", "tipo": "peso", '
           '"prezzi": [{"eur": 1.5, "fonte": "scontrino"}]}\n')


def prezzo_senza_fonte(radice):
    accoda(radice, "dati/prodotti.jsonl",
           '{"id": "guasto-fonte", "nome": "Prodotto guasto", "tipo": "peso", '
           '"prezzi": [{"eur": 1.5, "data": "2026-08-01"}]}\n')


def confezione_senza_formato(radice):
    accoda(radice, "dati/prodotti.jsonl",
           '{"id": "guasto-formato", "nome": "Pacco senza formato", "tipo": "confezione"}\n')


def formato_a_memoria(radice):
    accoda(radice, "dati/prodotti.jsonl",
           '{"id": "guasto-memoria", "nome": "Pacco a memoria", "tipo": "confezione", '
           '"formato_g": 500}\n')


def nutrienti_senza_fonte(radice):
    accoda(radice, "dati/prodotti.jsonl",
           '{"id": "guasto-nutrienti", "nome": "Prodotto opaco", "tipo": "peso", '
           '"kcal_100g": 120}\n')


def id_duplicato(radice):
    prima = leggi(radice, "dati/prodotti.jsonl").splitlines()[0]
    accoda(radice, "dati/prodotti.jsonl", prima + "\n")


def settimana_malformata(radice):
    testo = leggi(radice, "dati/storico.yaml")
    scrivi(radice, "dati/storico.yaml", inserisci_sotto(testo, "settimane", [
        "- settimana: settimana-scorsa",
        "  spesa_stimata: parecchio",
    ]))


def yaml_con_tabulazione(radice):
    accoda(radice, "dati/ritmi.yaml", "\tguasto: 1\n")


def timbro_illeggibile(radice):
    scrivi(radice, "dati/versione.yaml",
           "contratto: due\nmotore: 3.4.0\nmigrata: 2026-08-16\n")


def quarantena_senza_scadenza(radice):
    testo = leggi(radice, "dati/storico.yaml")
    scrivi(radice, "dati/storico.yaml", inserisci_sotto(testo, "tarature", [
        "piatti_in_quarantena:",
        "  Polpette al sugo: {volte: 1, perche: stufo}",
    ]))


def quarantena_con_motivo_inventato(radice):
    testo = leggi(radice, "dati/storico.yaml")
    scrivi(radice, "dati/storico.yaml", inserisci_sotto(testo, "tarature", [
        "piatti_in_quarantena:",
        "  Polpette al sugo: {fino_al: 2026-09-07, volte: 1, perche: cosiPerCapriccio}",
    ]))


def scorta_gia_nel_congelatore(radice):
    """Lo stesso pacco in due sezioni: sottratto due volte."""
    testo = leggi(radice, "dati/dispensa.yaml")
    testo = inserisci_sotto(testo, "scorte", [
        "filetti-di-merluzzo-doppioni:",
        "  quantita: 2",
        "  visto: 2026-08-01",
    ])
    scrivi(radice, "dati/dispensa.yaml", inserisci_sotto(testo, "freezer", [
        "- cosa: filetti di merluzzo doppioni",
        "  pezzi: 2",
    ]))


def stato_settimana_inventato(radice):
    cartella = os.path.join(radice, "settimane")
    os.makedirs(cartella, exist_ok=True)
    with open(os.path.join(cartella, "2026-W40-guasta.md"), "w", encoding="utf-8") as f:
        f.write("---\nstato: bozza\ntitolo: Guasta\n---\n\n## Lunedi'\n")


def scrivi_diario(radice, nome, contenuto):
    """Una cartella di settimana col solo diario: basta al lint, e non tocca i
    consuntivi dei fixture, che raccontano gia' una loro storia coerente."""
    cartella = os.path.join(radice, "settimane", nome)
    os.makedirs(cartella, exist_ok=True)
    with open(os.path.join(cartella, "diario.yaml"), "w", encoding="utf-8") as f:
        f.write(contenuto)


DIARIO_SANO = (
    "sospesi:\n"
    "  - cosa: filetti di branzino\n"
    "    serve:\n"
    "      - {giorno: 2026-10-08, pasto: cena}\n"
    "    stato: da_procurare\n"
    "\n"
    "2026-10-08:\n"
    "  cena:\n"
    "    previsto: Branzino al forno\n"
    "    reale: Pasta al pomodoro\n"
    "    stato: disattesa\n"
)


def sospeso_con_stato_inventato(radice):
    scrivi_diario(radice, "2026-W41-guasta", DIARIO_SANO.replace("da_procurare", "forseArriva"))


def sospeso_senza_uso(radice):
    scrivi_diario(radice, "2026-W42-guasta",
                  "sospesi:\n"
                  "  - cosa: filetti di branzino\n"
                  "    stato: da_procurare\n")


def sospeso_su_prodotto_fantasma(radice):
    scrivi_diario(radice, "2026-W43-guasta",
                  "sospesi:\n"
                  "  - cosa: filetti di branzino\n"
                  "    prodotto: prodotto-che-non-esiste-250\n"
                  "    serve:\n"
                  "      - {giorno: 2026-10-08, pasto: cena}\n")


def pasto_di_diario_con_stato_inventato(radice):
    scrivi_diario(radice, "2026-W44-guasta", DIARIO_SANO.replace("disattesa", "quasiFatta"))


def pasto_di_diario_inventato(radice):
    scrivi_diario(radice, "2026-W45-guasta",
                  "2026-10-08:\n"
                  "  merendina:\n"
                  "    previsto: Pane e marmellata\n"
                  "    reale: Pane e marmellata\n")


def scrivi_settimana(radice, nome, documenti):
    """Una cartella di settimana coi documenti che le si passano."""
    cartella = os.path.join(radice, "settimane", nome)
    os.makedirs(cartella, exist_ok=True)
    for voce, contenuto in documenti.items():
        with open(os.path.join(cartella, voce), "w", encoding="utf-8") as f:
            f.write(contenuto)
    return cartella


def testa(stato, titolo="Guasta"):
    return f"---\nstato: {stato}\ntitolo: {titolo}\n---\n\n## I sette giorni\n"


def documento_con_un_altro_nome(radice):
    """Il prefisso non e' quello della cartella: nessuna skill lo aprira'."""
    scrivi_settimana(radice, "2026-W47-guasta",
                     {"2026-W47-un-altro-nome-preventivo.md": testa("preventivo")})


def preventivo_che_dice_consuntivo(radice):
    scrivi_settimana(radice, "2026-W48-guasta",
                     {"2026-W48-guasta-preventivo.md": testa("consuntivo")})


def documento_senza_stato(radice):
    scrivi_settimana(radice, "2026-W49-guasta",
                     {"2026-W49-guasta-preventivo.md": "# Settimana senza stato\n"})


CORRUZIONI = [
    ("KCAL_SOTTO_PAVIMENTO", persona_a_dieta_troppo_bassa),
    ("KCAL_SU_CHI_NON_E_A_DIETA", deficit_a_chi_non_e_a_dieta),
    ("STATO_CELLA_SCONOSCIUTO", stato_di_cella_inventato),
    ("GRAMMATICA_VECCHIA", grammatica_vecchia),
    ("AVANZO_SENZA_PRODOTTO", avanzo_fantasma),
    ("PREZZO_SENZA_DATA", prezzo_senza_data),
    ("PREZZO_SENZA_FONTE", prezzo_senza_fonte),
    ("FORMATO_MANCANTE", confezione_senza_formato),
    ("FORMATO_SENZA_FONTE", formato_a_memoria),
    ("NUTRIENTI_SENZA_FONTE", nutrienti_senza_fonte),
    ("ID_DUPLICATO", id_duplicato),
    ("ISO_MALFORMATO", settimana_malformata),
    ("YAML_ILLEGGIBILE", yaml_con_tabulazione),
    ("STATO_SETTIMANA_SCONOSCIUTO", stato_settimana_inventato),
    ("TIMBRO_MALFORMATO", timbro_illeggibile),
    ("QUARANTENA_SENZA_SCADENZA", quarantena_senza_scadenza),
    ("QUARANTENA_MALFORMATA", quarantena_con_motivo_inventato),
    ("STATO_SOSPESO_SCONOSCIUTO", sospeso_con_stato_inventato),
    ("SOSPESO_SENZA_USO", sospeso_senza_uso),
    ("SOSPESO_SENZA_PRODOTTO", sospeso_su_prodotto_fantasma),
    ("STATO_PASTO_SCONOSCIUTO", pasto_di_diario_con_stato_inventato),
    ("PASTO_SCONOSCIUTO", pasto_di_diario_inventato),
    ("DOCUMENTO_DISALLINEATO", documento_con_un_altro_nome),
    ("STATO_SETTIMANA_INCOERENTE", preventivo_che_dice_consuntivo),
    ("SETTIMANA_SENZA_STATO", documento_senza_stato),
]


# ------------------------------------------------------------------- i test

class TestFixturePuliti(unittest.TestCase):
    def test_ci_sono_tre_fixture(self):
        self.assertGreaterEqual(len(FIXTURES), 3, "servono almeno i tre fixture del contratto")

    def test_nessun_errore(self):
        for radice in FIXTURES:
            with self.subTest(fixture=os.path.basename(radice)):
                errori = [v for v in Lint(radice).esegui() if v.livello == ERRORE]
                self.assertEqual([], [f"{v.codice}: {v.messaggio}" for v in errori])

    def test_sono_dichiaratamente_finti(self):
        """Un fixture che non si vede a colpo d'occhio che e' finto e' un rischio."""
        for radice in FIXTURES:
            with self.subTest(fixture=os.path.basename(radice)):
                testa = leggi(radice, "dati/profilo.yaml").splitlines()[0].lower()
                self.assertIn("fixture sintetico", testa)

    def test_nessun_ean_nei_fixture(self):
        """Un EAN inventato somiglierebbe a un prodotto vero: nei fixture non ce ne sono."""
        for radice in FIXTURES:
            with self.subTest(fixture=os.path.basename(radice)):
                testo = leggi(radice, "dati/prodotti.jsonl")
                self.assertNotIn("openfoodfacts:", testo)
                for riga in testo.splitlines():
                    if riga.strip():
                        self.assertRegex(riga, r'"ean":\s*null')


class TestCorruzioni(unittest.TestCase):
    """Ogni codice ha una corruzione che lo produce, su ognuno dei tre fixture."""

    def esegui(self, radice, corruzione):
        with tempfile.TemporaryDirectory(prefix="lunario-lint-") as tmp:
            copia = os.path.join(tmp, os.path.basename(radice))
            shutil.copytree(radice, copia)
            corruzione(copia)
            return {v.codice for v in Lint(copia).esegui() if v.livello == ERRORE}

    def test_ogni_corruzione_viene_vista(self):
        for codice, corruzione in CORRUZIONI:
            for radice in FIXTURES:
                with self.subTest(codice=codice, fixture=os.path.basename(radice)):
                    self.assertIn(codice, self.esegui(radice, corruzione))

    def test_un_diario_sano_non_produce_niente(self):
        """L'altra meta' del lint: un contratto rispettato deve passare in
        silenzio. Un controllo troppo severo si scopre solo cosi'."""
        for radice in FIXTURES:
            with self.subTest(fixture=os.path.basename(radice)):
                codici = self.esegui(radice, lambda c: scrivi_diario(c, "2026-W46-sana", DIARIO_SANO))
                self.assertEqual(set(), codici)


class TestAvvisi(unittest.TestCase):
    """Alcune cose sono sospette senza essere sbagliate, e restano avvisi."""

    def test_scorta_e_freezer_che_si_somigliano(self):
        for radice in FIXTURES:
            with self.subTest(fixture=os.path.basename(radice)):
                with tempfile.TemporaryDirectory(prefix="lunario-lint-") as tmp:
                    copia = os.path.join(tmp, os.path.basename(radice))
                    shutil.copytree(radice, copia)
                    scorta_gia_nel_congelatore(copia)
                    violazioni = Lint(copia).esegui()
                    codici = {v.codice for v in violazioni}
                    self.assertIn("SCORTA_E_FREEZER_DUPLICATI", codici)
                    # avviso, non errore: due scorte distinte sono possibili
                    self.assertNotIn("SCORTA_E_FREEZER_DUPLICATI",
                                     {v.codice for v in violazioni if v.livello == ERRORE})


class TestCartellaSettimana(unittest.TestCase):
    """Il contratto della cartella: quali file ci stanno, e cosa e' solo sospetto."""

    def violazioni(self, radice, guasto):
        with tempfile.TemporaryDirectory(prefix="lunario-lint-") as tmp:
            copia = os.path.join(tmp, os.path.basename(radice))
            shutil.copytree(radice, copia)
            guasto(copia)
            return Lint(copia).esegui()

    def codici(self, radice, guasto, livello=None):
        # `single` non ha il timbro, ed e' voluto: e' il fixture che esercita la
        # deduzione dalla forma. L'avviso non riguarda la cartella settimana.
        return {v.codice for v in self.violazioni(radice, guasto)
                if v.codice != "TIMBRO_ASSENTE"
                and (livello is None or v.livello == livello)}

    def test_una_settimana_completa_passa_in_silenzio(self):
        """L'altra meta' del lint: il contratto rispettato non produce niente."""
        def sana(copia):
            nome = "2026-W50-sana"
            scrivi_settimana(copia, nome, {
                f"{nome}-preventivo.md": testa("preventivo", "Sana"),
                f"{nome}-preventivo.html": "<html><body>preventivo</body></html>",
                f"{nome}-lista.md": "# Spesa\n\n## Dispensa\n- [ ] Fusilli — 2 × 500 g\n",
                f"{nome}-consuntivo.md": testa("consuntivo", "Sana"),
                f"{nome}-consuntivo.html": "<html><body>consuntivo</body></html>",
                f"{nome}-postmortem.md": "# Postmortem\n",
                "contesto.yaml": "settimana: {}\n",
            })
        for radice in FIXTURES:
            with self.subTest(fixture=os.path.basename(radice)):
                self.assertEqual(set(), self.codici(radice, sana))

    def test_un_ruolo_inventato_e_solo_un_avviso(self):
        def guasto(copia):
            scrivi_settimana(copia, "2026-W51-guasta",
                             {"2026-W51-guasta-bozza.md": testa("preventivo")})
        for radice in FIXTURES:
            with self.subTest(fixture=os.path.basename(radice)):
                self.assertIn("RUOLO_SETTIMANA_SCONOSCIUTO", self.codici(radice, guasto))
                self.assertNotIn("RUOLO_SETTIMANA_SCONOSCIUTO", self.codici(radice, guasto, ERRORE))

    def test_un_file_estraneo_e_solo_un_avviso(self):
        """Uno scontrino lasciato li' non e' un errore: e' roba dell'utente."""
        def guasto(copia):
            scrivi_settimana(copia, "2026-W52-guasta", {"scontrino.txt": "TOTALE 12,00\n"})
        for radice in FIXTURES:
            with self.subTest(fixture=os.path.basename(radice)):
                self.assertIn("FILE_ESTRANEO_ALLA_SETTIMANA", self.codici(radice, guasto))
                self.assertNotIn("FILE_ESTRANEO_ALLA_SETTIMANA", self.codici(radice, guasto, ERRORE))

    def test_un_consuntivo_senza_preventivo_si_nota(self):
        def guasto(copia):
            nome = "2026-W53-guasta"
            scrivi_settimana(copia, nome, {f"{nome}-consuntivo.md": testa("consuntivo")})
        for radice in FIXTURES:
            with self.subTest(fixture=os.path.basename(radice)):
                self.assertIn("PREVENTIVO_SPARITO", self.codici(radice, guasto))


class TestRisoluzioneSettimana(unittest.TestCase):
    """Lo script che dice alle skill su quale file scrivere.

    Sbagliare il file vivo non da' nessun errore: da' una settimana raccontata
    in un documento che nessuno riaprira'. Quindi si verifica qui."""

    settimana = settimana_del_motore

    def casa(self, tmp, documenti, nome="2026-W34-commando"):
        os.makedirs(os.path.join(tmp, "settimane", nome), exist_ok=True)
        for relativo, contenuto in documenti.items():
            percorso = os.path.join(tmp, "settimane", relativo)
            os.makedirs(os.path.dirname(percorso), exist_ok=True)
            with open(percorso, "w", encoding="utf-8") as f:
                f.write(contenuto)
        return self.settimana.risolvi(tmp)

    def test_il_vivo_e_il_preventivo_finche_non_c_e_il_consuntivo(self):
        with tempfile.TemporaryDirectory() as tmp:
            esito = self.casa(tmp, {
                "2026-W34-commando/2026-W34-commando-preventivo.md": testa("preventivo"),
                "2026-W34-commando/2026-W34-commando-lista.md": "# Spesa\n",
            })
            self.assertEqual("cartella", esito["layout"])
            self.assertTrue(esito["vivo"].endswith("-preventivo.md"))

    def test_col_consuntivo_il_vivo_cambia(self):
        with tempfile.TemporaryDirectory() as tmp:
            esito = self.casa(tmp, {
                "2026-W34-commando/2026-W34-commando-preventivo.md": testa("preventivo"),
                "2026-W34-commando/2026-W34-commando-consuntivo.md": testa("consuntivo"),
            })
            self.assertTrue(esito["vivo"].endswith("-consuntivo.md"))

    def test_il_layout_vecchio_si_trova_lo_stesso(self):
        """Le settimane scritte prima del contratto 4 non si migrano: si leggono."""
        with tempfile.TemporaryDirectory() as tmp:
            esito = self.casa(tmp, {"2026-W34-commando.md": testa("consuntivo")})
            self.assertEqual("piatto", esito["layout"])
            self.assertTrue(esito["vivo"].endswith("2026-W34-commando.md"))

    def test_una_cartella_senza_documenti_non_ha_un_vivo(self):
        """`lunario:settimana` ha creato la cartella, il menu non e' ancora uscito."""
        with tempfile.TemporaryDirectory() as tmp:
            esito = self.casa(tmp, {"2026-W34-commando/contesto.yaml": "settimana: {}\n"})
            self.assertIsNone(esito["vivo"])

    def test_lo_slug_e_quello_del_contratto(self):
        self.assertEqual("yellow-submarine", self.settimana.slug("Yellow Submarine"))
        self.assertEqual("impressioni-di-settembre",
                         self.settimana.slug("Impressioni di settembre"))
        self.assertEqual("perche-no", self.settimana.slug("Perché no?!"))
        self.assertEqual("tre-pesci-e-un-forno", self.settimana.slug("  Tre pesci — e un forno  "))


class TestMiniYaml(unittest.TestCase):
    def test_no_resta_una_stringa(self):
        """`merenda: no` e' uno stato di cella, non un booleano."""
        letto = minyaml.carica("pasti:\n  merenda: no\n  colazione: casa\n")
        self.assertEqual({"pasti": {"merenda": "no", "colazione": "casa"}}, letto)

    def test_mappe_inline_e_liste(self):
        letto = minyaml.carica(
            "tetti: {valore: 3, rigidita: preferenza}\n"
            "vuoto: {}\n"
            "lista: []\n"
            "pesate:\n"
            "  - {data: 2026-08-09, kg: 70.5}\n"
        )
        self.assertEqual(3, letto["tetti"]["valore"])
        self.assertEqual({}, letto["vuoto"])
        self.assertEqual([], letto["lista"])
        self.assertEqual("2026-08-09", letto["pesate"][0]["data"])
        self.assertEqual(70.5, letto["pesate"][0]["kg"])

    def test_lista_di_mappe_a_blocchi(self):
        letto = minyaml.carica(
            "freezer:\n"
            "  - cosa: filetti\n"
            "    pezzi: 2\n"
            "    da_smaltire: true\n"
            "  - cosa: pollo\n"
        )
        self.assertEqual(2, len(letto["freezer"]))
        self.assertTrue(letto["freezer"][0]["da_smaltire"])
        self.assertEqual("pollo", letto["freezer"][1]["cosa"])

    def test_commenti_e_cancelletti_dentro_i_valori(self):
        letto = minyaml.carica("id: pasta#500   # questo e' un commento\n")
        self.assertEqual("pasta#500", letto["id"])

    def test_apostrofi_italiani_non_sono_virgolette(self):
        """`gia'` e `ce n'erano` sono ovunque: non aprono una stringa."""
        letto = minyaml.carica("causa: ricomprata mentre ce n'erano gia' tre   # nota\n")
        self.assertEqual("ricomprata mentre ce n'erano gia' tre", letto["causa"])

    def test_chiave_duplicata_e_un_errore(self):
        with self.assertRaises(minyaml.ErroreYaml):
            minyaml.carica("a: 1\na: 2\n")

    def test_tabulazione_e_un_errore(self):
        with self.assertRaises(minyaml.ErroreYaml):
            minyaml.carica("a:\n\tb: 1\n")

    def test_i_template_del_motore_si_leggono(self):
        templates = os.path.join(os.path.dirname(QUI), "plugins", "lunario", "templates")
        for nome in sorted(os.listdir(templates)):
            if nome.endswith(".yaml"):
                with self.subTest(template=nome):
                    self.assertIsInstance(minyaml.carica_file(os.path.join(templates, nome)), dict)


if __name__ == "__main__":
    unittest.main(verbosity=2)
