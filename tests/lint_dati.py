#!/usr/bin/env python3
"""Tier 1 — il lint dei contratti. Zero token, zero dipendenze.

Prende una cartella di casa Lunario e riporta le violazioni del contratto
descritto in `CLAUDE.md`. Non giudica il menu e non sa niente di nutrizione:
controlla solo cio' che e' verificabile leggendo i file.

    python3 tests/lint_dati.py ~/lunario-casa
    python3 tests/lint_dati.py                 # tutti i fixture del repo
    python3 tests/lint_dati.py --json <casa>   # per il runner del tier 2

Uscita: 0 se non ci sono errori (gli avvisi non fanno fallire), 1 altrimenti.

Ogni violazione porta un **codice stabile**: i test asseriscono sui codici, mai
sul testo del messaggio, cosi' riformulare un messaggio non rompe una suite.
"""

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from minyaml import ErroreYaml, carica_file  # noqa: E402

ERRORE, AVVISO = "errore", "avviso"

PASTI = {"colazione", "spuntino", "pranzo", "merenda", "cena"}
STATI_CELLA = {"casa", "trasportabile", "libero", "ristorante", "fuori", "no"}
STATI_VECCHI = {"fuori_trasportabile": "trasportabile", "fuori_autonomo": "fuori"}
GIORNI = {"lunedi", "martedi", "mercoledi", "giovedi", "venerdi", "sabato", "domenica"}
CHIAVI_GIORNO_EXTRA = {"cena_entro_min", "pranzo_entro_min", "nota"}

TIPI_PRODOTTO = {"confezione", "peso", "pezzo"}
FONTI_PREZZO = {"scontrino", "dichiarato"}
FONTI_FORMATO = {"utente", "scontrino", "ricerca", "openfoodfacts"}
FONTI_NUTRIENTI = {"crea", "etichetta", "openfoodfacts"}
STATI_SETTIMANA = {"preventivo", "consuntivo"}

# Deperibilita': la fascia [fine] di kb/deperibilita.md e' l'unica ammessa in
# `avanzi`. Il reparto e' il segnale strutturato che abbiamo; dove non basta si
# declassa ad avviso invece di indovinare.
REPARTI_DEPERIBILI = {"ortofrutta", "pescheria", "macelleria", "panetteria"}
REPARTI_INCERTI = {"latticini-uova", "gastronomia", "banco", "salumi"}
# La fascia [fine] nomina esplicitamente uova e formaggi stagionati: stanno in
# un reparto deperibile ma deperibili non sono, e vanno riconosciuti dal nome.
NON_DEPERIBILE_NEL_NOME = ("surgelat", "congelat", "in scatola", "sott'olio", "essicc",
                           "uova", "grana", "parmigian", "pecorino", "stagionat")

PAVIMENTO_KCAL = 1200
DATA = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ISO_SETTIMANA = re.compile(r"^\d{4}-W\d{2}$")
NOME_SETTIMANA = re.compile(r"^\d{4}-W\d{2}(-[a-z0-9]+(-[a-z0-9]+)*)?$")


class Violazione:
    def __init__(self, codice, livello, file, messaggio):
        self.codice = codice
        self.livello = livello
        self.file = file
        self.messaggio = messaggio

    def __repr__(self):
        return f"<{self.livello} {self.codice} {self.file}>"

    def come_dizionario(self):
        return {
            "codice": self.codice,
            "livello": self.livello,
            "file": self.file,
            "messaggio": self.messaggio,
        }


class Lint:
    def __init__(self, radice):
        self.radice = os.path.abspath(radice)
        self.dati = self._cartella_dati()
        self.violazioni = []
        self.paniere = {}
        self.persone = set()

    # ------------------------------------------------------------- infrastruttura

    def _cartella_dati(self):
        if os.path.isdir(os.path.join(self.radice, "dati")):
            return os.path.join(self.radice, "dati")
        if os.path.isfile(os.path.join(self.radice, "profilo.yaml")):
            return self.radice
        return os.path.join(self.radice, "dati")

    def _relativo(self, percorso):
        return os.path.relpath(percorso, self.radice)

    def segnala(self, codice, livello, percorso, messaggio):
        self.violazioni.append(Violazione(codice, livello, self._relativo(percorso), messaggio))

    def _leggi_yaml(self, nome, obbligatorio):
        percorso = os.path.join(self.dati, nome)
        if not os.path.isfile(percorso):
            if obbligatorio:
                self.segnala("FILE_MANCANTE", ERRORE, percorso, f"manca {nome}")
            else:
                self.segnala("FILE_MANCANTE", AVVISO, percorso, f"manca {nome}, opzionale")
            return None
        try:
            contenuto = carica_file(percorso)
        except ErroreYaml as e:
            self.segnala("YAML_ILLEGGIBILE", ERRORE, percorso, str(e))
            return None
        if contenuto is None:
            return {}
        if not isinstance(contenuto, dict):
            self.segnala("YAML_ILLEGGIBILE", ERRORE, percorso, "la radice non e' una mappa")
            return None
        return contenuto

    # ------------------------------------------------------------------ esecuzione

    def esegui(self):
        if not os.path.isdir(self.dati):
            self.segnala("FILE_MANCANTE", ERRORE, self.dati, "nessuna cartella dati/")
            return self.violazioni
        self.controlla_versione()
        self.controlla_prodotti()
        self.controlla_profilo()
        self.controlla_ritmi()
        self.controlla_dispensa()
        self.controlla_storico()
        self.controlla_settimane()
        return self.violazioni

    # -------------------------------------------------------------- versione.yaml

    def controlla_versione(self):
        """Il timbro. Assente non e' un errore: le cartelle nate prima non ce
        l'hanno, e la prima skill che ci passa lo scrive."""
        percorso = os.path.join(self.dati, "versione.yaml")
        if not os.path.isfile(percorso):
            self.segnala("TIMBRO_ASSENTE", AVVISO, percorso,
                         "nessun timbro: il contratto verra' dedotto dalla forma dei file")
            return
        timbro = self._leggi_yaml("versione.yaml", obbligatorio=False)
        if timbro is None:
            return
        contratto = timbro.get("contratto")
        if not isinstance(contratto, int) or contratto < 1:
            self.segnala("TIMBRO_MALFORMATO", ERRORE, percorso, f"`contratto` = {contratto!r}")
        if not timbro.get("motore"):
            self.segnala("TIMBRO_MALFORMATO", ERRORE, percorso, "manca `motore`")
        if not DATA.match(str(timbro.get("migrata", ""))):
            self.segnala("DATA_MALFORMATA", ERRORE, percorso, f"`migrata` = {timbro.get('migrata')!r}")

    # -------------------------------------------------------------- prodotti.jsonl

    def controlla_prodotti(self):
        percorso = os.path.join(self.dati, "prodotti.jsonl")
        if not os.path.isfile(percorso):
            self.segnala("FILE_MANCANTE", AVVISO, percorso, "manca prodotti.jsonl: paniere vuoto")
            return
        with open(percorso, encoding="utf-8") as f:
            for numero, riga in enumerate(f, 1):
                if not riga.strip():
                    continue
                try:
                    prodotto = json.loads(riga)
                except json.JSONDecodeError as e:
                    self.segnala("JSON_ILLEGGIBILE", ERRORE, percorso, f"riga {numero}: {e}")
                    continue
                self._controlla_prodotto(prodotto, percorso, numero)

    def _controlla_prodotto(self, prodotto, percorso, numero:int):
        dove = f"riga {numero}"
        identificativo = prodotto.get("id")
        if not identificativo:
            self.segnala("CAMPO_OBBLIGATORIO_MANCANTE", ERRORE, percorso, f"{dove}: manca `id`")
            return
        dove = f"{identificativo}"
        if identificativo in self.paniere:
            self.segnala("ID_DUPLICATO", ERRORE, percorso, f"{dove}: id gia' usato")
        self.paniere[identificativo] = prodotto

        for campo in ("nome", "tipo"):
            if not prodotto.get(campo):
                self.segnala("CAMPO_OBBLIGATORIO_MANCANTE", ERRORE, percorso,
                             f"{dove}: manca `{campo}`")

        tipo = prodotto.get("tipo")
        if tipo and tipo not in TIPI_PRODOTTO:
            self.segnala("TIPO_SCONOSCIUTO", ERRORE, percorso,
                         f"{dove}: tipo `{tipo}` fuori da {sorted(TIPI_PRODOTTO)}")

        formato = prodotto.get("formato_g")
        if tipo == "confezione" and not isinstance(formato, (int, float)):
            self.segnala("FORMATO_MANCANTE", ERRORE, percorso,
                         f"{dove}: tipo confezione senza `formato_g`, la lista uscirebbe in grammi")
        if isinstance(formato, (int, float)) and formato <= 0:
            self.segnala("FORMATO_MANCANTE", ERRORE, percorso, f"{dove}: `formato_g` non positivo")
        if isinstance(formato, (int, float)):
            self._controlla_fonte_formato(prodotto.get("fonte_formato"), percorso, dove)

        if prodotto.get("kcal_100g") is not None or prodotto.get("proteine_100g") is not None:
            fonte = prodotto.get("fonte_nutrienti")
            if not fonte:
                self.segnala("NUTRIENTI_SENZA_FONTE", ERRORE, percorso,
                             f"{dove}: valori nutrizionali senza `fonte_nutrienti`")
            elif str(fonte).split(":")[0] not in FONTI_NUTRIENTI:
                self.segnala("FONTE_NUTRIENTI_SCONOSCIUTA", ERRORE, percorso,
                             f"{dove}: `fonte_nutrienti` = {fonte!r}")

        alias = prodotto.get("alias_scontrino", [])
        if alias is not None and not isinstance(alias, list):
            self.segnala("ALIAS_NON_LISTA", ERRORE, percorso, f"{dove}: `alias_scontrino` non e' una lista")

        self._controlla_prezzi(prodotto.get("prezzi"), percorso, dove)

    def _controlla_fonte_formato(self, fonte, percorso, dove):
        if not fonte:
            self.segnala("FORMATO_SENZA_FONTE", ERRORE, percorso,
                         f"{dove}: `formato_g` senza `fonte_formato`: e' un formato a memoria")
            return
        if not isinstance(fonte, dict):
            self.segnala("FORMATO_SENZA_FONTE", ERRORE, percorso,
                         f"{dove}: `fonte_formato` non e' {{fonte, data}}")
            return
        quale = str(fonte.get("fonte", "")).split(":")[0]
        if quale not in FONTI_FORMATO:
            self.segnala("FONTE_FORMATO_SCONOSCIUTA", ERRORE, percorso,
                         f"{dove}: fonte del formato = {fonte.get('fonte')!r}")
        if not DATA.match(str(fonte.get("data", ""))):
            self.segnala("DATA_MALFORMATA", ERRORE, percorso,
                         f"{dove}: `fonte_formato.data` = {fonte.get('data')!r}")

    def _controlla_prezzi(self, prezzi, percorso, dove):
        if prezzi is None:
            return
        if not isinstance(prezzi, list):
            self.segnala("PREZZO_NON_NUMERICO", ERRORE, percorso, f"{dove}: `prezzi` non e' una lista")
            return
        for prezzo in prezzi:
            if not isinstance(prezzo, dict):
                self.segnala("PREZZO_NON_NUMERICO", ERRORE, percorso, f"{dove}: prezzo non e' una mappa")
                continue
            if not DATA.match(str(prezzo.get("data", ""))):
                self.segnala("PREZZO_SENZA_DATA", ERRORE, percorso,
                             f"{dove}: prezzo senza data valida ({prezzo.get('data')!r})")
            fonte = prezzo.get("fonte")
            if not fonte:
                self.segnala("PREZZO_SENZA_FONTE", ERRORE, percorso, f"{dove}: prezzo senza `fonte`")
            elif fonte not in FONTI_PREZZO:
                self.segnala("FONTE_PREZZO_SCONOSCIUTA", ERRORE, percorso,
                             f"{dove}: fonte del prezzo = {fonte!r}")
            if not isinstance(prezzo.get("eur"), (int, float)):
                self.segnala("PREZZO_NON_NUMERICO", ERRORE, percorso,
                             f"{dove}: `eur` = {prezzo.get('eur')!r}")

    # ---------------------------------------------------------------- profilo.yaml

    def controlla_profilo(self):
        percorso = os.path.join(self.dati, "profilo.yaml")
        profilo = self._leggi_yaml("profilo.yaml", obbligatorio=True)
        if profilo is None:
            return

        intervista = profilo.get("intervista")
        if intervista is not None and intervista not in ("completa", "minima"):
            self.segnala("INTERVISTA_SCONOSCIUTA", ERRORE, percorso, f"`intervista` = {intervista!r}")

        famiglia = profilo.get("famiglia")
        if not isinstance(famiglia, list) or not famiglia:
            self.segnala("PROFILO_SENZA_FAMIGLIA", ERRORE, percorso, "nessuno mangia a questa tavola")
            famiglia = []
        for persona in famiglia:
            self._controlla_persona(persona, percorso)

        git = profilo.get("git")
        if git is not None and git not in ("locale", "no"):
            self.segnala("GIT_SCONOSCIUTO", ERRORE, percorso, f"`git` = {git!r}")

        for chiave, tetto in (profilo.get("preferenze") or {}).items():
            if not chiave.startswith("max_"):
                continue
            if isinstance(tetto, int):
                continue
            if isinstance(tetto, dict) and isinstance(tetto.get("valore"), int) \
                    and tetto.get("rigidita") in ("vincolo", "preferenza"):
                continue
            self.segnala("TETTO_MALFORMATO", ERRORE, percorso,
                         f"`{chiave}` = {tetto!r}: serve un intero o {{valore, rigidita}}")

        tolleranze = profilo.get("tolleranze") or {}
        for chi, valore in (tolleranze.get("avanzi") or {}).items():
            if valore not in ("come_sono", "trasformati", "mai"):
                self.segnala("TOLLERANZA_AVANZI_SCONOSCIUTA", ERRORE, percorso,
                             f"`tolleranze.avanzi.{chi}` = {valore!r}")

        calendario = profilo.get("calendario") or {}
        if calendario.get("scrivi") is True and not calendario.get("id"):
            self.segnala("CALENDARIO_SENZA_ID", AVVISO, percorso,
                         "`calendario.scrivi: true` ma nessun `id`: la skill dovra' chiederlo")

    def _controlla_persona(self, persona, percorso):
        if not isinstance(persona, dict):
            self.segnala("PERSONA_SENZA_NOME", ERRORE, percorso, "voce di `famiglia` non e' una mappa")
            return
        nome = persona.get("nome")
        if not nome:
            self.segnala("PERSONA_SENZA_NOME", ERRORE, percorso, "persona senza `nome`")
            return
        if nome in self.persone:
            self.segnala("NOME_DUPLICATO", ERRORE, percorso, f"{nome}: nome usato due volte")
        self.persone.add(nome)

        dieta = persona.get("dieta")
        kcal = persona.get("kcal_giorno")
        if dieta is None:
            self.segnala("DIETA_MANCANTE", AVVISO, percorso, f"{nome}: manca `dieta`")
        elif dieta is True:
            if kcal is None:
                self.segnala("KCAL_MANCANTE_A_DIETA", ERRORE, percorso,
                             f"{nome}: `dieta: true` senza `kcal_giorno`")
            elif not isinstance(kcal, (int, float)):
                self.segnala("KCAL_MANCANTE_A_DIETA", ERRORE, percorso,
                             f"{nome}: `kcal_giorno` = {kcal!r}")
            elif kcal < PAVIMENTO_KCAL:
                self.segnala("KCAL_SOTTO_PAVIMENTO", ERRORE, percorso,
                             f"{nome}: {kcal} kcal, sotto il pavimento di {PAVIMENTO_KCAL}")
            if persona.get("peso_obiettivo_kg") is None:
                self.segnala("OBIETTIVO_MANCANTE", AVVISO, percorso,
                             f"{nome}: a dieta senza `peso_obiettivo_kg`: non si sapra' quando smettere")
        elif dieta is False and kcal is not None:
            self.segnala("KCAL_SU_CHI_NON_E_A_DIETA", ERRORE, percorso,
                         f"{nome}: `dieta: false` ma `kcal_giorno` = {kcal!r}")

        for pasto, stato in (persona.get("pasti") or {}).items():
            self._controlla_cella(pasto, stato, percorso, f"{nome}")

    def _controlla_cella(self, pasto, stato, percorso, dove):
        if pasto in CHIAVI_GIORNO_EXTRA:
            if pasto != "nota" and not isinstance(stato, (int, float)):
                self.segnala("MINUTI_NON_NUMERO", ERRORE, percorso, f"{dove}: `{pasto}` = {stato!r}")
            return
        if pasto not in PASTI:
            self.segnala("PASTO_SCONOSCIUTO", ERRORE, percorso,
                         f"{dove}: pasto `{pasto}` fuori dai cinque della griglia")
            return
        if stato in STATI_VECCHI:
            self.segnala("GRAMMATICA_VECCHIA", ERRORE, percorso,
                         f"{dove}.{pasto}: `{stato}` e' la vecchia grammatica, oggi si scrive "
                         f"`{STATI_VECCHI[stato]}`")
            return
        if stato not in STATI_CELLA:
            self.segnala("STATO_CELLA_SCONOSCIUTO", ERRORE, percorso,
                         f"{dove}.{pasto}: stato `{stato}` fuori da {sorted(STATI_CELLA)}")

    # ------------------------------------------------------------------ ritmi.yaml

    def controlla_ritmi(self):
        percorso = os.path.join(self.dati, "ritmi.yaml")
        ritmi = self._leggi_yaml("ritmi.yaml", obbligatorio=False)
        if not ritmi:
            return
        self._controlla_griglia(ritmi.get("settimana") or {}, percorso)

    def _controlla_griglia(self, settimana, percorso):
        for giorno, persone in settimana.items():
            if giorno not in GIORNI:
                self.segnala("GIORNO_SCONOSCIUTO", ERRORE, percorso, f"giorno `{giorno}`")
            if not isinstance(persone, dict):
                self.segnala("YAML_ILLEGGIBILE", ERRORE, percorso, f"{giorno}: non e' una mappa di persone")
                continue
            for chi, celle in persone.items():
                if chi != "tutti" and self.persone and chi not in self.persone:
                    self.segnala("PERSONA_SCONOSCIUTA", AVVISO, percorso,
                                 f"{giorno}: `{chi}` non e' nel profilo")
                if not isinstance(celle, dict):
                    self.segnala("YAML_ILLEGGIBILE", ERRORE, percorso, f"{giorno}.{chi}: non e' una mappa")
                    continue
                for pasto, stato in celle.items():
                    self._controlla_cella(pasto, stato, percorso, f"{giorno}.{chi}")

    # --------------------------------------------------------------- dispensa.yaml

    def controlla_dispensa(self):
        percorso = os.path.join(self.dati, "dispensa.yaml")
        dispensa = self._leggi_yaml("dispensa.yaml", obbligatorio=False)
        if dispensa is None:
            return
        if not DATA.match(str(dispensa.get("aggiornata", ""))):
            self.segnala("DISPENSA_SENZA_DATA", AVVISO, percorso,
                         f"`aggiornata` = {dispensa.get('aggiornata')!r}")

        for identificativo, quantita in (dispensa.get("avanzi") or {}).items():
            if not isinstance(quantita, (int, float)):
                self.segnala("AVANZO_NON_NUMERICO", ERRORE, percorso,
                             f"{identificativo}: quantita' = {quantita!r}")
            if self.paniere and identificativo not in self.paniere:
                self.segnala("AVANZO_SENZA_PRODOTTO", ERRORE, percorso,
                             f"{identificativo}: non esiste in prodotti.jsonl")
                continue
            self._controlla_deperibilita(identificativo, percorso)

        freezer = dispensa.get("freezer") or []
        if not isinstance(freezer, list):
            self.segnala("YAML_ILLEGGIBILE", ERRORE, percorso, "`freezer` non e' una lista")
            return
        for voce in freezer:
            if not isinstance(voce, dict) or not voce.get("cosa"):
                self.segnala("FREEZER_SENZA_COSA", ERRORE, percorso, f"voce di freezer senza `cosa`: {voce!r}")
                continue
            if voce.get("dal") is not None and not DATA.match(str(voce["dal"])):
                self.segnala("DATA_MALFORMATA", ERRORE, percorso,
                             f"{voce['cosa']}: `dal` = {voce['dal']!r}")
            if voce.get("da_smaltire") is not None and not isinstance(voce["da_smaltire"], bool):
                self.segnala("FREEZER_SENZA_COSA", ERRORE, percorso,
                             f"{voce['cosa']}: `da_smaltire` non e' booleano")

    def _controlla_deperibilita(self, identificativo, percorso):
        prodotto = self.paniere.get(identificativo)
        if not prodotto:
            return
        nome = str(prodotto.get("nome", "")).lower()
        if any(marcatore in nome for marcatore in NON_DEPERIBILE_NEL_NOME):
            return
        reparto = prodotto.get("reparto")
        if reparto in REPARTI_DEPERIBILI:
            self.segnala("DEPERIBILE_IN_AVANZI", ERRORE, percorso,
                         f"{identificativo}: reparto `{reparto}`, fra tre giorni non esiste")
        elif reparto in REPARTI_INCERTI:
            self.segnala("DEPERIBILE_IN_AVANZI", AVVISO, percorso,
                         f"{identificativo}: reparto `{reparto}`, in avanzi solo se davvero non deperibile")

    # ---------------------------------------------------------------- storico.yaml

    def controlla_storico(self):
        percorso = os.path.join(self.dati, "storico.yaml")
        storico = self._leggi_yaml("storico.yaml", obbligatorio=False)
        if not storico:
            return
        tarature = storico.get("tarature") or {}

        for chi, alimenti in (tarature.get("porzioni_g") or {}).items():
            if not isinstance(alimenti, dict):
                self.segnala("PORZIONE_NON_NUMERICA", ERRORE, percorso, f"{chi}: porzioni non sono una mappa")
                continue
            for alimento, grammi in alimenti.items():
                if not isinstance(grammi, (int, float)) or grammi <= 0:
                    self.segnala("PORZIONE_NON_NUMERICA", ERRORE, percorso,
                                 f"{chi}.{alimento} = {grammi!r}")

        for chi, misure in (tarature.get("pesate") or {}).items():
            if self.persone and chi not in self.persone:
                self.segnala("PESATA_DI_CHI_NON_ESISTE", AVVISO, percorso, f"pesate di `{chi}`, non nel profilo")
            if not isinstance(misure, list):
                self.segnala("PESATA_MALFORMATA", ERRORE, percorso, f"{chi}: le pesate non sono una lista")
                continue
            for misura in misure:
                if not isinstance(misura, dict) or not DATA.match(str(misura.get("data", ""))) \
                        or not isinstance(misura.get("kg"), (int, float)):
                    self.segnala("PESATA_MALFORMATA", ERRORE, percorso, f"{chi}: pesata {misura!r}")

        for piatto, voti in (tarature.get("voti") or {}).items():
            self._controlla_voti(piatto, voti, percorso)

        viste = set()
        for settimana in (storico.get("settimane") or []):
            if not isinstance(settimana, dict):
                self.segnala("SETTIMANA_SENZA_ISO", ERRORE, percorso, f"voce di settimane: {settimana!r}")
                continue
            iso = settimana.get("settimana")
            if not iso or not ISO_SETTIMANA.match(str(iso)):
                self.segnala("ISO_MALFORMATO", ERRORE, percorso, f"chiave settimana = {iso!r}")
            elif iso in viste:
                self.segnala("SETTIMANA_DUPLICATA", ERRORE, percorso, f"{iso}: due voci con lo stesso ISO")
            viste.add(iso)
            for campo in ("spesa_stimata", "spesa_reale", "spesa_extra_alimentare",
                          "spesa_fuori_casa", "totale_scontrino"):
                valore = settimana.get(campo)
                if valore is not None and not isinstance(valore, (int, float)):
                    self.segnala("SPESA_NON_NUMERICA", ERRORE, percorso, f"{iso}.{campo} = {valore!r}")
            menu = settimana.get("menu")
            if menu and not os.path.exists(os.path.join(self.radice, str(menu))):
                self.segnala("MENU_INESISTENTE", AVVISO, percorso, f"{iso}: `{menu}` non esiste")

    def _controlla_voti(self, piatto, voti, percorso):
        if not isinstance(voti, dict):
            self.segnala("VOTO_FUORI_SCALA", ERRORE, percorso, f"{piatto}: voti non sono una mappa")
            return
        cucina = voti.get("cucina") or {}
        for campo in ("difficolta", "voto_cuoco"):
            valore = cucina.get(campo)
            if valore is not None and not (isinstance(valore, (int, float)) and 1 <= valore <= 5):
                self.segnala("VOTO_FUORI_SCALA", ERRORE, percorso, f"{piatto}.cucina.{campo} = {valore!r}")
        tavola = voti.get("tavola") or {}
        media = tavola.get("media")
        if media is not None and not (isinstance(media, (int, float)) and 1 <= media <= 5):
            self.segnala("VOTO_FUORI_SCALA", ERRORE, percorso, f"{piatto}.tavola.media = {media!r}")
        for voto in (tavola.get("voti") or []):
            if not isinstance(voto, dict):
                self.segnala("VOTO_FUORI_SCALA", ERRORE, percorso, f"{piatto}: voto {voto!r}")
                continue
            if not (isinstance(voto.get("voto"), (int, float)) and 1 <= voto["voto"] <= 5):
                self.segnala("VOTO_FUORI_SCALA", ERRORE, percorso, f"{piatto}: voto {voto.get('voto')!r}")
            if not DATA.match(str(voto.get("data", ""))):
                self.segnala("DATA_MALFORMATA", ERRORE, percorso, f"{piatto}: voto senza data valida")

    # -------------------------------------------------------------------- settimane

    def controlla_settimane(self):
        cartella = os.path.join(self.radice, "settimane")
        if not os.path.isdir(cartella):
            return
        for voce in sorted(os.listdir(cartella)):
            percorso = os.path.join(cartella, voce)
            radice_nome = voce[:-3] if voce.endswith(".md") else voce[:-5] if voce.endswith(".html") else voce
            if not NOME_SETTIMANA.match(radice_nome):
                self.segnala("NOME_SETTIMANA_FUORI_FORMATO", ERRORE, percorso,
                             f"`{voce}`: atteso <ISO>-<titolo>")
                continue
            if voce.endswith(".md"):
                self._controlla_markdown_settimana(percorso)
            elif os.path.isdir(percorso):
                contesto = os.path.join(percorso, "contesto.yaml")
                if os.path.isfile(contesto):
                    try:
                        dati = carica_file(contesto) or {}
                    except ErroreYaml as e:
                        self.segnala("YAML_ILLEGGIBILE", ERRORE, contesto, str(e))
                        continue
                    self._controlla_griglia(dati.get("settimana") or {}, contesto)

    def _controlla_markdown_settimana(self, percorso):
        with open(percorso, encoding="utf-8") as f:
            testa = f.read(2000)
        trovato = re.search(r"^stato:\s*(\S+)\s*$", testa, re.MULTILINE)
        if not trovato:
            self.segnala("SETTIMANA_SENZA_STATO", ERRORE, percorso, "manca `stato:` in testa")
        elif trovato.group(1) not in STATI_SETTIMANA:
            self.segnala("STATO_SETTIMANA_SCONOSCIUTO", ERRORE, percorso,
                         f"`stato: {trovato.group(1)}` fuori da {sorted(STATI_SETTIMANA)}")


# ------------------------------------------------------------------------ CLI

def cartelle_predefinite():
    qui = os.path.dirname(os.path.abspath(__file__))
    fixtures = os.path.join(qui, "fixtures")
    if not os.path.isdir(fixtures):
        return []
    return [os.path.join(fixtures, n) for n in sorted(os.listdir(fixtures))
            if os.path.isdir(os.path.join(fixtures, n, "dati"))]


def stampa(radice, violazioni, silenzio):
    errori = [v for v in violazioni if v.livello == ERRORE]
    avvisi = [v for v in violazioni if v.livello == AVVISO]
    nome = os.path.basename(os.path.normpath(radice))
    if not errori and not avvisi:
        if not silenzio:
            print(f"  {nome}: pulito")
        return
    print(f"  {nome}: {len(errori)} errori, {len(avvisi)} avvisi")
    for violazione in violazioni:
        if silenzio and violazione.livello == AVVISO:
            continue
        marcatore = "!" if violazione.livello == ERRORE else "·"
        print(f"    {marcatore} [{violazione.codice}] {violazione.file}: {violazione.messaggio}")


def main(argomenti=None):
    parser = argparse.ArgumentParser(description="Lint dei contratti dati di Lunario")
    parser.add_argument("cartelle", nargs="*", help="cartelle di casa; vuoto = i fixture del repo")
    parser.add_argument("--json", action="store_true", help="uscita JSON, per il runner del tier 2")
    parser.add_argument("--silenzio", action="store_true", help="solo gli errori")
    argomenti = parser.parse_args(argomenti)

    cartelle = argomenti.cartelle or cartelle_predefinite()
    if not cartelle:
        print("Nessuna cartella da controllare.", file=sys.stderr)
        return 2

    esito, rapporto = 0, {}
    if not argomenti.json:
        print(f"Lint dei contratti — {len(cartelle)} cartelle")
    for radice in cartelle:
        violazioni = Lint(radice).esegui()
        rapporto[radice] = [v.come_dizionario() for v in violazioni]
        if any(v.livello == ERRORE for v in violazioni):
            esito = 1
        if not argomenti.json:
            stampa(radice, violazioni, argomenti.silenzio)
    if argomenti.json:
        print(json.dumps(rapporto, ensure_ascii=False, indent=1))
    return esito


if __name__ == "__main__":
    sys.exit(main())
