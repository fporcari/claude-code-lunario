"""Lettore YAML minimale, solo stdlib.

Lunario ha una regola: zero dipendenze esterne. Il linter dei contratti deve
pero' leggere i file YAML di una casa, e la stdlib non ha un parser YAML.
Questo modulo ne copre il **sottoinsieme che il motore scrive davvero**:
mappe e liste annidate, scalari, mappe e liste inline nelle forme usate dai
template.

Il sottoinsieme e' volutamente stretto. Un file che questo modulo non riesce a
leggere e' un file uscito dalla forma prevista, e il linter lo segnala come
violazione invece di arrangiarsi: la semplicita' di questi file e' essa stessa
parte del contratto, perche' li leggono e li riscrivono dei modelli.

Cosa NON si supporta, di proposito: ancore e alias, scalari multi-riga
(`|`, `>`), documenti multipli (`---`), chiavi complesse, tag espliciti.

Una divergenza deliberata da YAML 1.1: `no`, `yes`, `on`, `off` restano
**stringhe**. Nel contratto di Lunario `no` e' uno stato di cella della griglia
dei pasti (`merenda: no`), non un booleano — e un parser che lo convertisse in
`False` leggerebbe il file al contrario. Solo `true` e `false` sono booleani.
"""

import re

__all__ = ["carica", "carica_file", "ErroreYaml"]


class ErroreYaml(Exception):
    """Il file non sta nel sottoinsieme YAML previsto dal contratto."""

    def __init__(self, messaggio, riga=None):
        self.riga = riga
        super().__init__(f"riga {riga}: {messaggio}" if riga else messaggio)


# ---------------------------------------------------------------- pre-pulizia

def _senza_commento(riga):
    """Toglie il commento finale. `#` apre un commento solo se e' a inizio riga
    o preceduto da spazio: `id: pasta#500` non e' un commento.

    L'apostrofo in mezzo a una parola non apre una stringa: in italiano
    `ce n'erano` e `gia'` sono ovunque, e trattarli da virgolette farebbe
    sparire meta' riga.
    """
    virgoletta = None
    for i, c in enumerate(riga):
        if virgoletta:
            if c == virgoletta and (i == 0 or riga[i - 1] != "\\"):
                virgoletta = None
        elif c == "'" and i > 0 and (riga[i - 1].isalnum() or riga[i - 1] == "'"):
            continue
        elif c in "\"'":
            virgoletta = c
        elif c == "#" and (i == 0 or riga[i - 1] in " \t"):
            return riga[:i]
    return riga


def _righe_utili(testo):
    """(indentazione, contenuto, numero_riga) per le righe che portano dati."""
    fuori = []
    for numero, riga in enumerate(testo.splitlines(), 1):
        if riga.strip().startswith("---") or riga.strip() == "...":
            continue
        pulita = _senza_commento(riga).rstrip()
        if not pulita.strip():
            continue
        senza_indent = pulita.lstrip(" \t")
        indent = len(pulita) - len(senza_indent)
        if "\t" in pulita[:indent]:
            raise ErroreYaml("indentazione con tabulazione", numero)
        fuori.append((indent, senza_indent, numero))
    return fuori


# ------------------------------------------------------------------- scalari

_INTERO = re.compile(r"^[+-]?\d+$")
_DECIMALE = re.compile(r"^[+-]?(\d+\.\d*|\.\d+)([eE][+-]?\d+)?$")


def _scalare(testo, numero):
    testo = testo.strip()
    if testo == "":
        return None
    if testo[0] in "{[":
        return _flusso(testo, numero)
    if len(testo) >= 2 and testo[0] == testo[-1] and testo[0] in "\"'":
        return testo[1:-1].replace("\\\"", "\"").replace("\\'", "'")
    if testo in ("null", "~", "Null", "NULL"):
        return None
    if testo in ("true", "True", "TRUE"):
        return True
    if testo in ("false", "False", "FALSE"):
        return False
    if _INTERO.match(testo):
        return int(testo)
    if _DECIMALE.match(testo):
        return float(testo)
    # Le date restano stringhe: cosi' il linter le confronta come le legge
    # l'utente, e il comportamento non dipende dalla libreria di turno.
    return testo


def _taglia_di_primo_livello(corpo, numero):
    """Spezza il corpo di un flusso sulle virgole di primo livello."""
    pezzi, attuale, profondita, virgoletta = [], "", 0, None
    for c in corpo:
        if virgoletta:
            attuale += c
            if c == virgoletta:
                virgoletta = None
            continue
        if c in "\"'":
            virgoletta = c
            attuale += c
        elif c in "{[":
            profondita += 1
            attuale += c
        elif c in "}]":
            profondita -= 1
            attuale += c
        elif c == "," and profondita == 0:
            pezzi.append(attuale)
            attuale = ""
        else:
            attuale += c
    if virgoletta:
        raise ErroreYaml("virgoletta non chiusa", numero)
    if attuale.strip():
        pezzi.append(attuale)
    return pezzi


def _flusso(testo, numero):
    apre, chiude = testo[0], testo[-1]
    coppie = {"{": "}", "[": "]"}
    if chiude != coppie.get(apre):
        raise ErroreYaml(f"flusso non chiuso: {testo!r}", numero)
    corpo = testo[1:-1].strip()
    if apre == "[":
        return [_scalare(p, numero) for p in _taglia_di_primo_livello(corpo, numero)]
    mappa = {}
    for pezzo in _taglia_di_primo_livello(corpo, numero):
        chiave, separatore, valore = pezzo.partition(":")
        if not separatore:
            raise ErroreYaml(f"voce di mappa senza due punti: {pezzo!r}", numero)
        mappa[_scalare(chiave, numero)] = _scalare(valore, numero)
    return mappa


def _separa_chiave(testo, numero):
    """Divide `chiave: valore` sui primi due punti di primo livello."""
    profondita, virgoletta = 0, None
    for i, c in enumerate(testo):
        if virgoletta:
            if c == virgoletta:
                virgoletta = None
            continue
        if c in "\"'":
            virgoletta = c
        elif c in "{[":
            profondita += 1
        elif c in "}]":
            profondita -= 1
        elif c == ":" and profondita == 0:
            if i + 1 == len(testo) or testo[i + 1] in " \t":
                return testo[:i].strip(), testo[i + 1:].strip()
    return None, None


# ------------------------------------------------------------------- parsing

class _Lettore:
    def __init__(self, righe):
        self.righe = righe
        self.i = 0

    def cima(self):
        return self.righe[self.i] if self.i < len(self.righe) else None

    def indent_prossimo(self):
        return self.righe[self.i][0] if self.i < len(self.righe) else -1

    def blocco(self, indent):
        prima = self.cima()
        if prima is None or prima[0] < indent:
            return None
        if prima[1] == "-" or prima[1].startswith("- "):
            return self.sequenza(prima[0])
        return self.mappa(prima[0])

    def figlio(self, indent, numero):
        """Il blocco annidato sotto una chiave senza valore in linea."""
        if self.indent_prossimo() > indent:
            return self.blocco(self.indent_prossimo())
        return None

    def mappa(self, indent):
        risultato = {}
        while True:
            riga = self.cima()
            if riga is None or riga[0] != indent:
                break
            livello, testo, numero = riga
            if testo.startswith("- "):
                break
            chiave, valore = _separa_chiave(testo, numero)
            if chiave is None:
                if testo.endswith(":"):
                    chiave, valore = testo[:-1].strip(), ""
                else:
                    raise ErroreYaml(f"riga non interpretabile: {testo!r}", numero)
            chiave = _scalare(chiave, numero)
            if chiave in risultato:
                raise ErroreYaml(f"chiave duplicata: {chiave!r}", numero)
            self.i += 1
            if valore == "":
                risultato[chiave] = self.figlio(livello, numero)
            else:
                risultato[chiave] = _scalare(valore, numero)
        return risultato

    def sequenza(self, indent):
        risultato = []
        while True:
            riga = self.cima()
            if riga is None or riga[0] != indent:
                break
            livello, testo, numero = riga
            if not (testo == "-" or testo.startswith("- ")):
                break
            resto = testo[1:].strip()
            self.i += 1
            if resto == "":
                risultato.append(self.figlio(livello, numero))
                continue
            chiave, _valore = _separa_chiave(resto, numero)
            if chiave is not None and not resto.startswith(("{", "[")):
                # `- cosa: x` seguito da altre chiavi rientrate: e' una mappa.
                virtuale = self.indent_prossimo()
                if virtuale <= livello:
                    virtuale = livello + 2
                self.righe.insert(self.i, (virtuale, resto, numero))
                risultato.append(self.mappa(virtuale))
            else:
                risultato.append(_scalare(resto, numero))
        return risultato


def carica(testo):
    """Legge una stringa YAML del sottoinsieme previsto. Un file vuoto da' {}."""
    righe = _righe_utili(testo)
    if not righe:
        return {}
    lettore = _Lettore(righe)
    valore = lettore.blocco(righe[0][0])
    if lettore.i < len(lettore.righe):
        avanzo = lettore.righe[lettore.i]
        raise ErroreYaml(f"indentazione incoerente: {avanzo[1]!r}", avanzo[2])
    return valore


def carica_file(percorso):
    with open(percorso, encoding="utf-8") as f:
        return carica(f.read())
