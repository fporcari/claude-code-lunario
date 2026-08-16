#!/usr/bin/env python3
"""I controlli sul repo del motore, non sui dati di una casa.

    python3 tests/test_repo.py

Zero token, zero dipendenze.

Qui dentro sta cio' che nessuno guarda finche' non e' sbagliato: la versione
scritta in tre posti, i nomi delle skill, i percorsi che la documentazione
promette. Roba che non rompe nessun test funzionale e che un utente vede
subito.
"""

import json
import os
import re
import sys
import unittest

QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(QUI)
MARKETPLACE = os.path.join(REPO, ".claude-plugin", "marketplace.json")
PLUGIN = os.path.join(REPO, "plugins", "lunario", ".claude-plugin", "plugin.json")
SKILLS = os.path.join(REPO, "plugins", "lunario", "skills")


def carica(percorso):
    with open(percorso, encoding="utf-8") as f:
        return json.load(f)


class LaVersioneStaInTrePosti(unittest.TestCase):
    """E divergono al primo bump, se nessuno le confronta.

    E' successo: `plugin.json` e' passato a 5.1.2 e il marketplace ha
    continuato ad annunciare 5.0.0 — cioe' la pagina che la gente guarda per
    sapere che versione e' diceva il numero sbagliato, mentre l'aggiornamento
    funzionava benissimo. Nessun test funzionale poteva accorgersene.
    """

    def test_marketplace_e_plugin_dicono_la_stessa_versione(self):
        plugin = carica(PLUGIN)["version"]
        mercato = carica(MARKETPLACE)
        self.assertEqual(plugin, mercato["metadata"]["version"],
                         "metadata.version del marketplace non segue plugin.json")
        voce = next(p for p in mercato["plugins"] if p["name"] == "lunario")
        self.assertEqual(plugin, voce["version"],
                         "la voce del plugin nel marketplace non segue plugin.json")

    def test_la_versione_e_semver(self):
        self.assertRegex(carica(PLUGIN)["version"], r"^\d+\.\d+\.\d+$")

    def test_il_changelog_nomina_la_versione_corrente(self):
        """Una release senza una riga di changelog e' una release che fra sei
        mesi nessuno sa cosa conteneva."""
        versione = carica(PLUGIN)["version"]
        with open(os.path.join(REPO, "CHANGELOG.md"), encoding="utf-8") as f:
            testo = f.read()
        maggiore_minore = ".".join(versione.split(".")[:2])
        self.assertTrue(
            re.search(rf"^## {re.escape(versione)}\b", testo, re.M)
            or re.search(rf"^## {re.escape(maggiore_minore)}\.\d+\b", testo, re.M),
            f"nessuna voce di changelog per {versione}")


class LeSkillSonoQuelleDichiarate(unittest.TestCase):
    def test_ogni_cartella_di_skill_ha_il_suo_SKILL_md(self):
        for nome in sorted(os.listdir(SKILLS)):
            if nome.startswith("."):
                continue
            with self.subTest(skill=nome):
                self.assertTrue(os.path.isfile(os.path.join(SKILLS, nome, "SKILL.md")))

    def test_il_nome_nel_frontmatter_e_quello_della_cartella(self):
        """Le skill si invocano col nome del frontmatter: se non combacia con
        la cartella, la documentazione manda l'utente su un nome che non c'e'."""
        for nome in sorted(os.listdir(SKILLS)):
            if nome.startswith("."):
                continue
            percorso = os.path.join(SKILLS, nome, "SKILL.md")
            with self.subTest(skill=nome), open(percorso, encoding="utf-8") as f:
                testa = f.read(400)
            trovato = re.search(r"^name:\s*(\S+)\s*$", testa, re.M)
            self.assertIsNotNone(trovato, f"{nome}: nessun `name:` nel frontmatter")
            self.assertEqual(nome, trovato.group(1))

    def test_gli_script_citati_dalle_skill_esistono(self):
        """`${CLAUDE_PLUGIN_ROOT}/scripts/x.py` in una skill e' una promessa:
        se il file non c'e', la skill fallisce dentro la cartella di qualcuno."""
        scripts = os.path.join(REPO, "plugins", "lunario", "scripts")
        citati = set()
        for nome in sorted(os.listdir(SKILLS)):
            percorso = os.path.join(SKILLS, nome, "SKILL.md")
            if not os.path.isfile(percorso):
                continue
            with open(percorso, encoding="utf-8") as f:
                citati |= set(re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/scripts/(\S+?\.py)", f.read()))
        self.assertTrue(citati, "nessuna skill cita uno script: il glob e' sbagliato")
        for script in sorted(citati):
            with self.subTest(script=script):
                self.assertTrue(os.path.isfile(os.path.join(scripts, script)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
