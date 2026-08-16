#!/usr/bin/env python3
"""Il test del tagliando: trova cio' che il controllo del contratto non vedeva.

    python3 tests/test_tagliando.py

Zero token, zero dipendenze.

Il difetto da cui nasce questo file si asserisce nel primo test: una cartella
**col timbro giusto** e i documenti nella forma vecchia passava il controllo a
ogni lancio, per sempre, perche' l'unica verifica automatica confrontava due
interi. Il caso non e' teorico — e' la settimana in corso senza la sua lista
della spesa, cioe' la ragione per cui quel contratto era stato scritto.
"""

import datetime
import os
import shutil
import sys
import tempfile
import unittest

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(os.path.dirname(QUI), "plugins", "lunario", "scripts"))

import tagliando as motore_tagliando  # noqa: E402
import versione as motore_versione  # noqa: E402
from lint_dati import cartelle_predefinite  # noqa: E402
from tagliando import BLOCCANTE, Tagliando  # noqa: E402

DOMENICA = datetime.date(2026, 8, 16)          # 2026-W33: la settimana che apre e' W34

PROFILO = """famiglia:
  - nome: Adulto1
    dieta: false
    kcal_giorno: null
"""


def casa(radice, contratto=None, oggi=DOMENICA):
    """Una casa minima ma valida, col timbro se lo si chiede."""
    dati = os.path.join(radice, "dati")
    os.makedirs(dati, exist_ok=True)
    os.makedirs(os.path.join(radice, "settimane"), exist_ok=True)
    with open(os.path.join(dati, "profilo.yaml"), "w", encoding="utf-8") as f:
        f.write(PROFILO)
    if contratto is not None:
        motore_versione.scrivi_timbro(dati, contratto, "0.0.0", oggi.isoformat())
    return radice


def settimana_vecchia(radice, iso, stato="consuntivo"):
    """Il layout di prima: markdown e HTML **accanto** alla cartella."""
    nome = f"{iso}-commando"
    for estensione, contenuto in (("md", f"---\nstato: {stato}\n---\n\n## I sette giorni\n"),
                                  ("html", "<html></html>\n")):
        with open(os.path.join(radice, "settimane", f"{nome}.{estensione}"),
                  "w", encoding="utf-8") as f:
            f.write(contenuto)
    return nome


def codici(guasti):
    return {g.codice for g in guasti}


class IlTimbroGiustoNonBasta(unittest.TestCase):
    """Il difetto che ha fatto nascere il tagliando."""

    def test_una_settimana_nella_forma_vecchia_si_vede_anche_col_timbro_allineato(self):
        with tempfile.TemporaryDirectory() as tmp:
            casa(tmp, contratto=motore_versione.CONTRATTO_CORRENTE)
            settimana_vecchia(tmp, "2026-W34")
            guasti = Tagliando(tmp, oggi=DOMENICA).esegui()
            self.assertIn("SETTIMANA_DA_ADATTARE", codici(guasti))
            guasto = next(g for g in guasti if g.codice == "SETTIMANA_DA_ADATTARE")
            self.assertEqual(BLOCCANTE, guasto.livello)
            self.assertTrue(guasto.riparabile)

    def test_il_contratto_allineato_non_produce_nessun_guasto_di_contratto(self):
        with tempfile.TemporaryDirectory() as tmp:
            casa(tmp, contratto=motore_versione.CONTRATTO_CORRENTE)
            guasti = Tagliando(tmp, oggi=DOMENICA).esegui()
            self.assertNotIn("CONTRATTO_INDIETRO", codici(guasti))
            self.assertNotIn("TIMBRO_ASSENTE", codici(guasti))


class LeSettimanePassateRestanoUnRegistro(unittest.TestCase):
    def test_una_settimana_vecchia_non_e_un_guasto(self):
        """Il confine del contratto: si legge dov'e', non si sposta."""
        with tempfile.TemporaryDirectory() as tmp:
            casa(tmp, contratto=motore_versione.CONTRATTO_CORRENTE)
            settimana_vecchia(tmp, "2020-W02")
            guasti = Tagliando(tmp, oggi=DOMENICA).esegui()
            self.assertNotIn("SETTIMANA_DA_ADATTARE", codici(guasti))

    def test_la_settimana_che_apre_invece_si(self):
        """W34 di domenica: l'ISO di oggi non la nomina, ed e' quella viva."""
        with tempfile.TemporaryDirectory() as tmp:
            casa(tmp, contratto=motore_versione.CONTRATTO_CORRENTE)
            settimana_vecchia(tmp, "2026-W34")
            guasti = Tagliando(tmp, oggi=DOMENICA).esegui()
            self.assertIn("SETTIMANA_DA_ADATTARE", codici(guasti))


class LaRiparazione(unittest.TestCase):
    def test_ripara_sposta_i_documenti_dentro_la_cartella(self):
        with tempfile.TemporaryDirectory() as tmp:
            casa(tmp, contratto=motore_versione.CONTRATTO_CORRENTE)
            nome = settimana_vecchia(tmp, "2026-W34")
            tagliando = Tagliando(tmp, oggi=DOMENICA)
            tagliando.esegui()
            fatte, _righe = tagliando.ripara()
            self.assertEqual(1, fatte)
            dentro = os.path.join(tmp, "settimane", nome)
            self.assertTrue(os.path.isfile(os.path.join(dentro, f"{nome}-consuntivo.md")))
            self.assertFalse(os.path.exists(os.path.join(tmp, "settimane", f"{nome}.md")))
            # Ridiagnostica da sola: cio' che resta e' cio' che resta davvero.
            self.assertNotIn("SETTIMANA_DA_ADATTARE", codici(tagliando.guasti))

    def test_il_timbro_mancante_si_scrive_da_solo(self):
        """La cartella nata prima che il timbro esistesse: la forma dice gia'
        il contratto giusto, e manca solo la riga che smette di farlo dedurre."""
        sorgente = next((c for c in cartelle_predefinite()
                         if os.path.basename(c) == "famiglia"), None)
        if sorgente is None:
            self.skipTest("i fixture non sono raggiungibili da qui")
        with tempfile.TemporaryDirectory() as tmp:
            radice = os.path.join(tmp, "casa")
            shutil.copytree(sorgente, radice)
            os.remove(os.path.join(radice, "dati", "versione.yaml"))

            tagliando = Tagliando(radice, oggi=DOMENICA)
            tagliando.esegui()
            self.assertIn("TIMBRO_ASSENTE", codici(tagliando.guasti))

            fatte, _righe = tagliando.ripara()
            self.assertEqual(1, fatte)
            timbro = motore_versione.leggi_timbro(os.path.join(radice, "dati"))
            self.assertIsNotNone(timbro)
            self.assertEqual(motore_versione.CONTRATTO_CORRENTE, timbro["contratto"])
            self.assertNotIn("TIMBRO_ASSENTE", codici(tagliando.guasti))

    def test_il_contratto_indietro_non_lo_ripara_lo_script(self):
        """La migrazione ha i suoi passi, e vivono in `lunario:aggiorna`."""
        with tempfile.TemporaryDirectory() as tmp:
            casa(tmp, contratto=motore_versione.CONTRATTO_CORRENTE - 1)
            tagliando = Tagliando(tmp, oggi=DOMENICA)
            guasti = tagliando.esegui()
            guasto = next(g for g in guasti if g.codice == "CONTRATTO_INDIETRO")
            self.assertFalse(guasto.riparabile)


class IlLintNonDeveMaiCrashare(unittest.TestCase):
    """Un lint che crasha porta giu' la skill che l'ha chiamato.

    Trovato su una cartella vera: `settimana:` nel contesto portava un ISO
    invece della griglia dei giorni, e il lint ci chiamava `.items()` sopra.
    Il file era stato scritto dal sistema stesso, quindi non e' un caso
    patologico da laboratorio — e il crash arrivava **prima** di qualsiasi
    violazione, cioe' proprio dove il controllo doveva proteggere.
    """

    FUORI_FORMA = (
        ("dati/ritmi.yaml", "settimana: 2026-W34\n"),
        ("dati/profilo.yaml", PROFILO + "preferenze: nessuna\n"),
        ("dati/profilo.yaml", PROFILO + "tolleranze: come viene\n"),
        ("dati/profilo.yaml", PROFILO + "calendario: quello di lavoro\n"),
    )

    def test_un_blocco_che_non_e_un_blocco_si_segnala_e_non_esplode(self):
        for relativo, contenuto in self.FUORI_FORMA:
            with self.subTest(file=relativo, contenuto=contenuto.splitlines()[-1]), \
                    tempfile.TemporaryDirectory() as tmp:
                casa(tmp, contratto=motore_versione.CONTRATTO_CORRENTE)
                with open(os.path.join(tmp, relativo), "w", encoding="utf-8") as f:
                    f.write(contenuto)
                guasti = Tagliando(tmp, oggi=DOMENICA).esegui()   # non deve sollevare
                self.assertTrue(
                    any(g.codice.startswith("DATI_") for g in guasti),
                    "una forma sbagliata deve produrre una violazione, non il silenzio")

    def test_una_griglia_che_porta_un_iso_si_segnala(self):
        with tempfile.TemporaryDirectory() as tmp:
            casa(tmp, contratto=motore_versione.CONTRATTO_CORRENTE)
            cartella = os.path.join(tmp, "settimane", "2026-W34-commando")
            os.makedirs(cartella, exist_ok=True)
            with open(os.path.join(cartella, "contesto.yaml"), "w", encoding="utf-8") as f:
                f.write("settimana: 2026-W34\ndal: 2026-08-16\n")
            guasti = Tagliando(tmp, oggi=DOMENICA).esegui()
            self.assertIn("DATI_GRIGLIA_MALFORMATA", codici(guasti))


class IlGateNonDeveFarRumore(unittest.TestCase):
    def test_una_casa_sana_non_produce_niente(self):
        with tempfile.TemporaryDirectory() as tmp:
            casa(tmp, contratto=motore_versione.CONTRATTO_CORRENTE)
            self.assertEqual([], Tagliando(tmp, oggi=DOMENICA).esegui(rapido=True))

    def test_una_cartella_che_non_e_una_casa_lo_dice_una_volta_sola(self):
        """Senza profilo manca tutto: elencarlo dieci volte non aiuta nessuno."""
        with tempfile.TemporaryDirectory() as tmp:
            guasti = Tagliando(tmp, oggi=DOMENICA).esegui()
            self.assertEqual(["NON_E_UNA_CASA"], [g.codice for g in guasti])

    def test_l_uscita_distingue_cio_che_blocca_da_cio_che_non_blocca(self):
        with tempfile.TemporaryDirectory() as tmp:
            casa(tmp, contratto=motore_versione.CONTRATTO_CORRENTE)
            self.assertEqual(0, motore_tagliando._codice_uscita([]))
            settimana_vecchia(tmp, "2026-W34")
            guasti = Tagliando(tmp, oggi=DOMENICA).esegui()
            self.assertEqual(3, motore_tagliando._codice_uscita(guasti))


if __name__ == "__main__":
    unittest.main(verbosity=2)
