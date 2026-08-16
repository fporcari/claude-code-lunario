#!/usr/bin/env python3
"""Il tagliando: cosa non torna in questa cartella, e cosa si ripara da solo.

    python3 tagliando.py                 # la diagnosi, non tocca niente
    python3 tagliando.py --rapido        # il controllo che ogni skill fa all'avvio
    python3 tagliando.py --ripara        # applica le riparazioni meccaniche
    python3 tagliando.py --json

Tre verifiche che prima stavano in tre posti e non si parlavano:

1. **il contratto** — il timbro contro quello del motore (`versione.py`)
2. **la forma** — le settimane scritte col layout vecchio, i documenti che
   nessuna skill troverebbe (`settimana.py`)
3. **i contratti dati** — il lint di tutti i file (`lint_dati.py`)

La seconda e' quella che mancava, ed e' la ragione per cui questo file esiste:
il controllo del contratto guarda **un numero**, e un numero allineato zittiva
tutto il resto. Una cartella col timbro giusto e i file nel layout vecchio
passava il controllo a ogni lancio, per sempre — e il difetto piu' fastidioso,
la settimana senza la sua lista, e' esattamente di quella forma.

**Lo script ripara solo cio' che e' meccanico**: spostare file, scrivere un
timbro, sistemare un percorso. Tutto cio' che richiede di leggere e capire —
una scorta incoerente, una quarantena scaduta dentro un file pieno di commenti
— lo riporta e basta, e lo sistema `lunario:tagliando`, che ha il giudizio per
farlo senza rovinare il file intorno.

Zero dipendenze esterne, come tutto il resto del motore.
"""

import argparse
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import settimana as motore_settimana  # noqa: E402
import versione as motore_versione  # noqa: E402
from lint_dati import AVVISO, ERRORE, Lint  # noqa: E402

# Un guasto bloccante ferma la skill che sta partendo: va riparato prima, o il
# lavoro si appoggia su file che non sono quelli che crede. Un guasto normale
# si riporta e si va avanti — una cartella imperfetta deve restare usabile.
BLOCCANTE, NORMALE, NOTA = "bloccante", "normale", "nota"

LIVELLO_DAL_LINT = {ERRORE: NORMALE, AVVISO: NOTA}


class Guasto:
    """Una cosa che non torna, e come si aggiusta se si aggiusta da sola."""

    def __init__(self, codice, livello, dove, cosa, ripara=None, come=None):
        self.codice = codice
        self.livello = livello
        self.dove = dove
        self.cosa = cosa
        self.ripara = ripara          # callable: applica la riparazione, torna righe
        self.come = come              # cosa succede se si ripara, detto all'utente

    @property
    def riparabile(self):
        return self.ripara is not None

    def come_dizionario(self):
        return {
            "codice": self.codice,
            "livello": self.livello,
            "dove": self.dove,
            "cosa": self.cosa,
            "riparabile": self.riparabile,
            "come": self.come,
        }

    def __repr__(self):
        return f"<{self.livello} {self.codice} {self.dove}>"


class Tagliando:
    def __init__(self, radice, oggi=None):
        self.radice = os.path.abspath(radice)
        self.oggi = oggi or datetime.date.today()
        self.guasti = []

    def segnala(self, codice, livello, dove, cosa, ripara=None, come=None):
        self.guasti.append(Guasto(codice, livello, dove, cosa, ripara, come))

    # ------------------------------------------------------------------ diagnosi

    def esegui(self, rapido=False):
        """Torna la lista dei guasti. `rapido` salta cio' che non blocca.

        Il rapido lo lancia ogni skill appena parte, e deve tacere quando non
        c'e' niente da dire: un controllo che stampa comunque qualcosa diventa
        rumore che si impara a saltare, e allora non controlla piu' niente.
        """
        self.guasti = []
        if not os.path.isdir(self.radice):
            self.segnala("CARTELLA_ASSENTE", BLOCCANTE, self.radice,
                         "questa cartella non esiste")
            return self.guasti
        self.controlla_contratto()
        # Se qui non c'e' una casa, tutto il resto direbbe la stessa cosa in
        # dieci modi diversi: mancano i file perche' non c'e' niente da mancare.
        if any(g.codice == "NON_E_UNA_CASA" for g in self.guasti):
            return self.guasti
        self.controlla_forma_settimane()
        self.controlla_dati(solo_errori=rapido)
        return self.guasti

    # ---------------------------------------------------------------- contratto

    def controlla_contratto(self):
        contratto, come, motivi = motore_versione.stato(self.radice)
        corrente = motore_versione.CONTRATTO_CORRENTE
        if contratto is None:
            self.segnala("NON_E_UNA_CASA", BLOCCANTE, "dati/profilo.yaml",
                         "qui non c'e' una cartella di casa Lunario: "
                         + "; ".join(motivi))
            return
        if contratto > corrente:
            self.segnala(
                "CONTRATTO_AVANTI", NOTA, "dati/versione.yaml",
                f"la cartella e' al contratto {contratto}, il motore si ferma a {corrente}: "
                "l'ha toccata una versione piu' nuova. Aggiorna il plugin — questa "
                "versione ignora cio' che non conosce invece di romperlo")
            return
        if contratto < corrente:
            self.segnala(
                "CONTRATTO_INDIETRO", BLOCCANTE, "dati/versione.yaml",
                f"contratto {contratto}, il motore vuole il {corrente} (letto {come})",
                come="la migrazione la esegue `lunario:aggiorna`, un passo per salto")
            return
        # Allineata, ma senza timbro: e' la cartella nata prima che il timbro
        # esistesse, e la forma dice gia' il contratto giusto. Timbrare costa
        # tre righe e toglie una deduzione a ogni lancio futuro.
        dati = motore_versione.cartella_dati(self.radice)
        if motore_versione.leggi_timbro(dati) is None:
            self.segnala(
                "TIMBRO_ASSENTE", NOTA, "dati/versione.yaml",
                f"nessun timbro, ma la forma dice contratto {contratto}: manca solo la riga",
                ripara=lambda: self._timbra(contratto),
                come="scrive dati/versione.yaml col contratto gia' in uso")

    def _timbra(self, contratto):
        dati = motore_versione.cartella_dati(self.radice)
        percorso = motore_versione.scrivi_timbro(
            dati, contratto, motore_versione.versione_del_motore(), self.oggi.isoformat())
        return [f"scritto {os.path.relpath(percorso, self.radice)}: contratto {contratto}"]

    # -------------------------------------------------------------------- forma

    def controlla_forma_settimane(self):
        """Le settimane che nessuna skill troverebbe dove le cerca.

        Le passate restano dove sono — sono un registro, e questo e' scritto nel
        contratto — quindi si guarda solo cio' che e' ancora vivo: la settimana
        in corso e quella che apre.
        """
        cartella = os.path.join(self.radice, "settimane")
        if not os.path.isdir(cartella):
            return
        adattabili = motore_settimana.iso_adattabili(self.oggi)
        _c, nomi = motore_settimana._settimane(self.radice)
        for nome in nomi:
            iso = nome[:8]
            if iso not in adattabili:
                continue
            esito = motore_settimana.risolvi(self.radice, iso)
            if esito is None or esito["layout"] != "piatto":
                continue
            self.segnala(
                "SETTIMANA_DA_ADATTARE", BLOCCANTE, f"settimane/{nome}.md",
                f"{nome} e' ancora nel layout vecchio: i documenti stanno accanto "
                "alla cartella invece che dentro, e le manca la lista della spesa",
                ripara=lambda iso=iso: self._adatta(iso),
                come="sposta markdown e HTML dentro la cartella col nome del ruolo, "
                     "e sistema il `menu:` in storico.yaml")

    def _adatta(self, iso):
        fatto, righe = motore_settimana.adatta(self.radice, iso, self.oggi)
        if not fatto:
            raise RuntimeError("; ".join(righe))
        return righe

    # --------------------------------------------------------------------- dati

    def controlla_dati(self, solo_errori=False):
        """Il lint dei contratti, tradotto in guasti.

        Nessuno di questi si ripara da qui: un file di dati e' pieno di
        commenti scritti per un essere umano, e uno script che lo riscrive li
        perde. Li sistema la skill, che sa leggere prima di scrivere.
        """
        violazioni = Lint(self.radice).esegui()
        for v in violazioni:
            if solo_errori and v.livello != ERRORE:
                continue
            # Il timbro assente lo tratta gia' controlla_contratto, che sa anche
            # ripararlo: qui sarebbe la stessa cosa detta due volte.
            if v.codice == "TIMBRO_ASSENTE":
                continue
            self.segnala(f"DATI_{v.codice}", LIVELLO_DAL_LINT[v.livello], v.file, v.messaggio)

    # ---------------------------------------------------------------- riparazione

    def ripara(self):
        """Applica le riparazioni meccaniche. Torna (fatte, righe)."""
        righe, fatte = [], 0
        for guasto in list(self.guasti):
            if not guasto.riparabile:
                continue
            try:
                righe += [f"· {r}" for r in guasto.ripara()]
                fatte += 1
            except Exception as e:  # una riparazione che fallisce non ferma le altre
                righe.append(f"· {guasto.codice}: non riparato — {e}")
        if fatte:
            # La forma e' cambiata sotto i piedi: si ridiagnostica, cosi' cio'
            # che resta e' quello che resta davvero e non la lista di prima.
            self.esegui()
        return fatte, righe


# ------------------------------------------------------------------------- CLI

def _codice_uscita(guasti):
    if any(g.livello == BLOCCANTE for g in guasti):
        return 3
    if any(g.livello == NORMALE for g in guasti):
        return 1
    return 0


SOGLIA_RAGGRUPPO = 3


def _righe(guasti, etichetta):
    """Le righe di un gruppo, con lo stesso guasto ripetuto contato invece che
    elencato.

    Ventidue prodotti senza formato sono **un** difetto visto ventidue volte, e
    stampati uno per uno seppelliscono i due guasti che bloccano davvero. Una
    diagnosi che non si legge fino in fondo non e' una diagnosi.
    """
    per_codice = {}
    for g in guasti:
        per_codice.setdefault(g.codice, []).append(g)
    righe = []
    for codice, gruppo in per_codice.items():
        if len(gruppo) >= SOGLIA_RAGGRUPPO:
            primo = gruppo[0]
            dove = sorted({g.dove for g in gruppo})
            in_quanti = dove[0] if len(dove) == 1 else f"{len(dove)} file"
            righe.append(f"  · [{etichetta}] {in_quanti}: {primo.cosa}")
            righe.append(f"      e altre {len(gruppo) - 1} volte lo stesso ({codice})")
            continue
        for g in gruppo:
            marchio = " [si ripara da solo]" if g.riparabile else ""
            righe.append(f"  · [{etichetta}] {g.dove}: {g.cosa}{marchio}")
            if g.come:
                righe.append(f"      -> {g.come}")
    return righe


def stampa(radice, guasti, rapido):
    nome = os.path.basename(os.path.normpath(radice))
    if not guasti:
        if not rapido:
            print(f"{nome}: tutto a posto")
        return
    bloccanti = [g for g in guasti if g.livello == BLOCCANTE]
    normali = [g for g in guasti if g.livello == NORMALE]
    note = [g for g in guasti if g.livello == NOTA]
    if rapido and not bloccanti and not normali:
        return
    riparabili = sum(1 for g in bloccanti if g.riparabile)
    if bloccanti:
        coda = f", di cui {riparabili} si riparano da soli" if riparabili else ""
        print(f"{nome}: {len(bloccanti)} da riparare prima di andare avanti{coda}")
    else:
        print(f"{nome}: niente di bloccante")
    for riga in _righe(bloccanti, "blocca"):
        print(riga)

    # Nel rapido il resto non si elenca: e' il controllo che una skill fa
    # mentre l'utente aspetta di cucinare, e un elenco di difetti dei dati li'
    # non e' aiuto, e' una skill che non parte mai. Si dice che ci sono.
    if rapido:
        if normali:
            print(f"  · altri {len(normali)} difetti nei dati, nessuno bloccante: "
                  "`lunario:tagliando` per vederli")
        return
    for gruppo, etichetta in ((normali, "da vedere"), (note, "nota")):
        for riga in _righe(gruppo, etichetta):
            print(riga)


def main(argomenti=None):
    parser = argparse.ArgumentParser(
        description="Il tagliando di una cartella di casa Lunario.")
    parser.add_argument("casa", nargs="?", default=".",
                        help="la cartella di casa (default: quella corrente)")
    parser.add_argument("--rapido", action="store_true",
                        help="solo cio' che blocca: il controllo che ogni skill fa all'avvio")
    parser.add_argument("--ripara", action="store_true",
                        help="applica le riparazioni meccaniche")
    parser.add_argument("--json", action="store_true")
    argomenti = parser.parse_args(argomenti)

    tagliando = Tagliando(argomenti.casa)
    tagliando.esegui(rapido=argomenti.rapido)

    righe_riparazione = []
    if argomenti.ripara:
        _fatte, righe_riparazione = tagliando.ripara()

    if argomenti.json:
        print(json.dumps({
            "casa": tagliando.radice,
            "guasti": [g.come_dizionario() for g in tagliando.guasti],
            "riparazioni": righe_riparazione,
        }, ensure_ascii=False, indent=2))
        return _codice_uscita(tagliando.guasti)

    if righe_riparazione:
        print("Riparato:")
        for riga in righe_riparazione:
            print(f"  {riga}")
    stampa(argomenti.casa, tagliando.guasti, argomenti.rapido)
    return _codice_uscita(tagliando.guasti)


if __name__ == "__main__":
    sys.exit(main())
