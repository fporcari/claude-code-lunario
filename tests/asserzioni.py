#!/usr/bin/env python3
"""Tier 2 — le proprieta' che un giro del motore deve lasciare dietro di se'.

Non si asserisce **il menu**: il menu non e' deterministico, e non lo sara' mai.
Si asserisce cio' che di qualunque menu deve essere vero — le «Regole non
negoziabili» di `CLAUDE.md`, che sono gia' una suite di test scritta in prosa.

Ogni asserzione torna uno di tre esiti:

    ok                 la proprieta' regge
    fallita            la proprieta' e' violata: e' un bug del motore
    non_verificabile   il file non c'era, o la forma non si e' lasciata leggere

`non_verificabile` non fa fallire la suite ed e' deliberato: una suite che
diventa rossa per un dettaglio di formattazione viene ignorata entro due
settimane, e una suite ignorata e' peggio di nessuna suite. Ma non e' nemmeno
un verde: il rapporto lo stampa, e troppi `non_verificabile` sono un segnale.
"""

import glob
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from minyaml import ErroreYaml, carica_file  # noqa: E402

OK, FALLITA, NON_VERIFICABILE = "ok", "fallita", "non_verificabile"

PASTI = ("colazione", "spuntino", "pranzo", "merenda", "cena")
PAVIMENTO_KCAL = 1200


class Esito:
    def __init__(self, nome, stato, dettaglio="", regola=""):
        self.nome = nome
        self.stato = stato
        self.dettaglio = dettaglio
        self.regola = regola

    def __repr__(self):
        return f"<{self.stato} {self.nome}>"

    def come_dizionario(self):
        return {"nome": self.nome, "stato": self.stato,
                "dettaglio": self.dettaglio, "regola": self.regola}


# --------------------------------------------------------------------- lettura

class Casa:
    """Una cartella di casa dopo che una skill ci ha lavorato."""

    def __init__(self, radice, prima=None):
        self.radice = os.path.abspath(radice)
        self.dati = os.path.join(self.radice, "dati")
        self.prima = prima or {}

    def yaml(self, relativo):
        percorso = os.path.join(self.radice, relativo)
        if not os.path.isfile(percorso):
            return None
        try:
            return carica_file(percorso) or {}
        except ErroreYaml:
            return None

    def profilo(self):
        return self.yaml("dati/profilo.yaml") or {}

    def dispensa(self):
        return self.yaml("dati/dispensa.yaml") or {}

    def storico(self):
        return self.yaml("dati/storico.yaml") or {}

    def cartella_settimana(self):
        candidati = [p for p in glob.glob(os.path.join(self.radice, "settimane", "*"))
                     if os.path.isdir(p)]
        return sorted(candidati)[-1] if candidati else None

    def markdown_settimana(self):
        candidati = sorted(glob.glob(os.path.join(self.radice, "settimane", "*.md")))
        return candidati[-1] if candidati else None

    def testo_settimana(self):
        percorso = self.markdown_settimana()
        if not percorso:
            return None
        with open(percorso, encoding="utf-8") as f:
            return f.read()

    def diario(self):
        cartella = self.cartella_settimana()
        if not cartella:
            return None
        percorso = os.path.join(cartella, "diario.yaml")
        if not os.path.isfile(percorso):
            return None
        try:
            return carica_file(percorso) or {}
        except ErroreYaml:
            return None

    def paniere(self):
        percorso = os.path.join(self.dati, "prodotti.jsonl")
        prodotti = {}
        if not os.path.isfile(percorso):
            return prodotti
        with open(percorso, encoding="utf-8") as f:
            for riga in f:
                if riga.strip():
                    try:
                        prodotto = json.loads(riga)
                    except json.JSONDecodeError:
                        continue
                    prodotti[prodotto.get("id")] = prodotto
        return prodotti

    def commit(self):
        # Senza questo controllo `git log` risalirebbe al repo che contiene la
        # cartella, e risponderebbe con la storia di qualcun altro.
        if not os.path.isdir(os.path.join(self.radice, ".git")):
            return None
        try:
            uscita = subprocess.run(["git", "log", "--format=%s"], cwd=self.radice,
                                    capture_output=True, text=True, timeout=20)
        except (OSError, subprocess.SubprocessError):
            return None
        if uscita.returncode != 0:
            return None
        return [r for r in uscita.stdout.splitlines() if r.strip()]


def _stato_settimana(testo):
    trovato = re.search(r"^stato:\s*(\S+)\s*$", testo or "", re.MULTILINE)
    return trovato.group(1) if trovato else None


def _righe_spesa(testo):
    """Le righe della lista della spesa, saltando i giorni e le scorte."""
    righe, dentro = [], False
    for riga in (testo or "").splitlines():
        intestazione = riga.strip().lower()
        if intestazione.startswith("#"):
            dentro = "spesa" in intestazione
            continue
        if dentro and re.match(r"^\s*-\s*\[[ xX]\]", riga):
            righe.append(riga.strip())
    return righe


def _caselle(testo):
    fatte = len(re.findall(r"-\s*\[[xX]\]", testo or ""))
    aperte = len(re.findall(r"-\s*\[ \]", testo or ""))
    return fatte, aperte


# ------------------------------------------------------------------ asserzioni

def a_menu_scrive_quello_che_deve(casa):
    """La tabella delle skill dice cosa scrive `lunario:menu`."""
    mancanti = []
    if not casa.markdown_settimana():
        mancanti.append("settimane/<ISO>-<titolo>.md")
    if not glob.glob(os.path.join(casa.radice, "settimane", "*.html")):
        mancanti.append("settimane/<ISO>-<titolo>.html")
    if not casa.storico().get("settimane"):
        mancanti.append("voce in storico.settimane")
    if mancanti:
        return Esito("menu scrive i suoi file", FALLITA, "mancano: " + ", ".join(mancanti),
                     "tabella delle skill in CLAUDE.md")
    return Esito("menu scrive i suoi file", OK)


def a_settimana_nasce_preventivo(casa):
    """«Ogni menu nasce preventivo» — CLAUDE.md, ciclo di vita del menu."""
    testo = casa.testo_settimana()
    if testo is None:
        return Esito("il menu nasce preventivo", NON_VERIFICABILE, "nessun markdown di settimana")
    stato = _stato_settimana(testo)
    if stato is None:
        return Esito("il menu nasce preventivo", FALLITA, "nessuno `stato:` in testa")
    if stato != "preventivo":
        return Esito("il menu nasce preventivo", FALLITA, f"stato = {stato!r} prima dello scontrino",
                     "solo lunario:spesa promuove a consuntivo")
    return Esito("il menu nasce preventivo", OK)


def a_solo_spesa_promuove(casa):
    testo = casa.testo_settimana()
    if testo is None:
        return Esito("dopo lo scontrino e' consuntivo", NON_VERIFICABILE, "nessun markdown")
    stato = _stato_settimana(testo)
    if stato != "consuntivo":
        return Esito("dopo lo scontrino e' consuntivo", FALLITA, f"stato = {stato!r}",
                     "lunario:spesa promuove, e nessun altro")
    return Esito("dopo lo scontrino e' consuntivo", OK)


def a_consuntivo_senza_caselle(casa):
    """«Il consuntivo e' un registro, non un modulo»: niente input.spunta."""
    html = sorted(glob.glob(os.path.join(casa.radice, "settimane", "*.html")))
    if not html:
        return Esito("il consuntivo non si spunta", NON_VERIFICABILE, "nessun HTML")
    with open(html[-1], encoding="utf-8") as f:
        pagina = f.read()
    if 'class="spunta"' in pagina or "input.spunta" in pagina or "type=\"checkbox\"" in pagina:
        return Esito("il consuntivo non si spunta", FALLITA,
                     "l'HTML del consuntivo porta ancora delle caselle",
                     "lo stato in pagina e' invisibile alle skill")
    return Esito("il consuntivo non si spunta", OK)


def a_lista_in_confezioni(casa):
    """«La lista della spesa e' in confezioni, mai in grammi astratti»."""
    testo = casa.testo_settimana()
    if testo is None:
        return Esito("la lista e' in confezioni", NON_VERIFICABILE, "nessun markdown")
    righe = _righe_spesa(testo)
    if not righe:
        return Esito("la lista e' in confezioni", NON_VERIFICABILE, "nessuna riga di spesa riconosciuta")
    paniere = casa.paniere()
    confezioni = {p.get("nome", "").lower(): p for p in paniere.values()
                  if p.get("tipo") == "confezione"}
    if not confezioni:
        return Esito("la lista e' in confezioni", NON_VERIFICABILE, "paniere senza prodotti a confezione")
    colpevoli = []
    for riga in righe:
        minuscola = riga.lower()
        for nome, prodotto in confezioni.items():
            if nome and nome in minuscola:
                # una riga a confezioni dice «2 × 500 g», mai «1050 g» e basta
                if re.search(r"\d+\s*[x×]\s*\d+", minuscola) or "[formato da verificare]" in minuscola:
                    break
                if re.search(r"\d{3,}\s*(g|ml)\b", minuscola):
                    colpevoli.append(riga)
                break
    if colpevoli:
        return Esito("la lista e' in confezioni", FALLITA,
                     "righe in grammi per prodotti a confezione: " + " | ".join(colpevoli[:3]),
                     "regola non negoziabile: mai grammi astratti")
    return Esito("la lista e' in confezioni", OK)


def _parole_forti(testo):
    return {p for p in re.findall(r"[a-zàèéìòù]+", (testo or "").lower()) if len(p) > 3}


def _blocco(testo, intestazione):
    """Il testo sotto un'intestazione markdown, fino alla successiva dello stesso livello."""
    trovato = re.search(rf"^(#+)\s*{intestazione}\s*$", testo or "", re.MULTILINE | re.IGNORECASE)
    if not trovato:
        return None
    livello = len(trovato.group(1))
    resto = testo[trovato.end():]
    fine = re.search(rf"^#{{1,{livello}}}\s", resto, re.MULTILINE)
    return resto[:fine.start()] if fine else resto


def a_scorte_nominate_uscendo(casa):
    """Cio' che copre una scorta esce dalla lista **e viene nominato uscendo**.

    L'errore che si cerca e' quello caro: due filetti che invecchiano nel
    congelatore mentre il branzino si ricompra al banco. Si becca guardando se
    una voce di `freezer` ricompare fra le righe della spesa **senza** essere
    nominata in «Gia' in casa».

    Vale sul congelatore **com'era prima di generare** (`casa.prima`), che e'
    quello che il runner fotografa a ogni fase. Applicarla a una settimana
    passata di un fixture confronta il menu di allora col congelatore di oggi,
    e da' rossi che non vogliono dire niente.
    """
    testo = casa.testo_settimana()
    if testo is None:
        return Esito("le scorte usate sono nominate", NON_VERIFICABILE, "nessun markdown")
    freezer = (casa.prima.get("dispensa") or casa.dispensa()).get("freezer") or []
    if not freezer:
        return Esito("le scorte usate sono nominate", NON_VERIFICABILE, "congelatore vuoto")
    incasa = _blocco(testo, r"gi[aà]'? in casa") or ""
    ricomprate = []
    for voce in freezer:
        parole = _parole_forti(voce.get("cosa"))
        if not parole:
            continue
        comprata = any(len(parole & _parole_forti(riga)) >= min(2, len(parole))
                       for riga in _righe_spesa(testo))
        nominata = len(parole & _parole_forti(incasa)) >= min(2, len(parole))
        if comprata and not nominata:
            ricomprate.append(voce.get("cosa"))
    if ricomprate:
        return Esito("le scorte usate sono nominate", FALLITA,
                     f"in lista, e in congelatore, senza uscire da «Gia' in casa»: {ricomprate}",
                     "e' l'errore piu' caro che questo sistema possa fare")
    return Esito("le scorte usate sono nominate", OK)


def a_scongelamento_dichiarato(casa):
    """Ogni riga del congelatore che entra nel menu porta il suo scongelamento."""
    testo = casa.testo_settimana()
    if testo is None:
        return Esito("i surgelati portano lo scongelamento", NON_VERIFICABILE, "nessun markdown")
    blocco = _blocco(testo, "dal congelatore")
    if blocco is None:
        return Esito("i surgelati portano lo scongelamento", NON_VERIFICABILE,
                     "il menu non tira fuori niente dal congelatore")
    righe = [r for r in blocco.splitlines() if re.match(r"^\s*-\s*\[[ xX]\]", r)]
    if not righe:
        return Esito("i surgelati portano lo scongelamento", NON_VERIFICABILE,
                     "nessuna riga nel blocco del congelatore")
    if re.search(r"(scongel|in frigo)", blocco, re.IGNORECASE):
        return Esito("i surgelati portano lo scongelamento", OK, f"{len(righe)} righe")
    return Esito("i surgelati portano lo scongelamento", FALLITA,
                 "il congelatore entra nel menu senza nessuna riga di scongelamento",
                 "e' l'unico pezzo di settimana che il giorno stesso non si recupera")


def a_celle_non_cucinate_non_hanno_piatto(casa):
    """Una cella `fuori`/`ristorante`/`no` non riceve un piatto, e non resta bianca."""
    testo = casa.testo_settimana()
    if testo is None:
        return Esito("le celle non cucinate sono nominate", NON_VERIFICABILE, "nessun markdown")
    contesto = None
    cartella = casa.cartella_settimana()
    if cartella and os.path.isfile(os.path.join(cartella, "contesto.yaml")):
        try:
            contesto = carica_file(os.path.join(cartella, "contesto.yaml")) or {}
        except ErroreYaml:
            contesto = None
    if not contesto:
        return Esito("le celle non cucinate sono nominate", NON_VERIFICABILE, "nessun contesto.yaml")
    attese = []
    for giorno, persone in (contesto.get("settimana") or {}).items():
        for _chi, celle in (persone or {}).items():
            if not isinstance(celle, dict):
                continue
            for pasto, stato in celle.items():
                if stato in ("fuori", "ristorante"):
                    attese.append((giorno, pasto, stato))
    if not attese:
        return Esito("le celle non cucinate sono nominate", NON_VERIFICABILE,
                     "il contesto non ha celle fuori casa")
    minuscolo = testo.lower()
    mancanti = [f"{g} {p}" for g, p, s in attese if s.lower() not in minuscolo]
    if mancanti:
        return Esito("le celle non cucinate sono nominate", FALLITA,
                     "stati mai nominati nel menu: " + ", ".join(sorted(set(mancanti))),
                     "una riga bianca sembra un errore, «cena — fuori» e' un'informazione")
    return Esito("le celle non cucinate sono nominate", OK)


def a_pavimento_calorico(casa):
    """Mai sotto 1200 kcal/giorno per chi e' a dieta."""
    testo = casa.testo_settimana()
    if testo is None:
        return Esito("nessuno sotto le 1200 kcal", NON_VERIFICABILE, "nessun markdown")
    a_dieta = [p for p in casa.profilo().get("famiglia", []) if p.get("dieta") is True]
    if not a_dieta:
        return Esito("nessuno sotto le 1200 kcal", NON_VERIFICABILE, "nessuno e' a dieta")
    totali = [int(t) for t in re.findall(r"totale[^\n]*?(\d{3,4})\s*kcal", testo, re.IGNORECASE)]
    if not totali and len(casa.profilo().get("famiglia", [])) == 1:
        # Una persona sola: le kcal per pasto si sommano senza ambiguita' su chi.
        # Con piu' commensali la riga «450 / 380 kcal» non dice a chi tocca cosa,
        # e sommarla a caso produrrebbe un rosso finto.
        giorni = re.split(r"^#+\s*(?=luned|marted|mercoled|gioved|venerd|sabato|domenica)",
                          testo, flags=re.MULTILINE | re.IGNORECASE)[1:]
        # Un giorno con un pasto fuori dal sistema ha legittimamente un totale
        # basso: Lunario quel pasto non lo pianifica, e il pavimento riguarda
        # cio' che pianifica.
        giorni = [g for g in giorni
                  if not re.search(r"\b(fuori|ristorante|libero)\b", g, re.IGNORECASE)]
        totali = [t for t in (sum(int(k) for k in re.findall(r"(\d{2,4})\s*kcal", g))
                              for g in giorni) if t > 0]
    if not totali:
        return Esito("nessuno sotto le 1200 kcal", NON_VERIFICABILE,
                     "il menu non stampa totali giornalieri leggibili")
    bassi = [t for t in totali if int(t) < PAVIMENTO_KCAL]
    if bassi:
        return Esito("nessuno sotto le 1200 kcal", FALLITA,
                     f"totali giornalieri sotto il pavimento: {sorted(set(bassi))}",
                     "regola non negoziabile")
    return Esito("nessuno sotto le 1200 kcal", OK, f"{len(totali)} totali letti")


def a_nessun_deficit_a_chi_non_e_a_dieta(casa):
    profilo = casa.profilo()
    liberi = [p.get("nome") for p in profilo.get("famiglia", [])
              if p.get("dieta") is False and p.get("kcal_giorno") is not None]
    if liberi:
        return Esito("nessun deficit a chi non e' a dieta", FALLITA,
                     f"hanno un target ma non sono a dieta: {liberi}",
                     "regola non negoziabile")
    testo = (casa.testo_settimana() or "").lower()
    nomi = [p.get("nome", "") for p in profilo.get("famiglia", []) if p.get("dieta") is False]
    for nome in nomi:
        if not nome:
            continue
        finestra = re.findall(rf"{re.escape(nome.lower())}[^\n]{{0,60}}", testo)
        if any("deficit" in f or "dimagr" in f for f in finestra):
            return Esito("nessun deficit a chi non e' a dieta", FALLITA,
                         f"il menu parla di deficit accanto a {nome}")
    return Esito("nessun deficit a chi non e' a dieta", OK)


def a_pasto_libero_non_compensato(casa):
    """Un pasto `libero` non fa risparmiare calorie alle altre celle."""
    testo = casa.testo_settimana()
    if testo is None:
        return Esito("il pasto libero non si compensa", NON_VERIFICABILE, "nessun markdown")
    if "libero" not in testo.lower():
        return Esito("il pasto libero non si compensa", NON_VERIFICABILE, "nessuna cella libera")
    sospette = re.findall(r"[^\n]*\b(compens|recuper[ai]|per bilanciare|si alleggerisce il piatto)[^\n]*",
                          testo, re.IGNORECASE)
    if sospette:
        return Esito("il pasto libero non si compensa", FALLITA,
                     "il menu compensa: " + " | ".join(s if isinstance(s, str) else s[0]
                                                       for s in sospette[:2]),
                     "regola non negoziabile")
    return Esito("il pasto libero non si compensa", OK)


def a_esclusioni_rispettate(casa):
    esclusioni = [str(e).lower() for e in (casa.profilo().get("esclusioni") or [])]
    testo = (casa.testo_settimana() or "").lower()
    if not esclusioni:
        return Esito("le esclusioni tengono", NON_VERIFICABILE, "nessuna esclusione nel profilo")
    if not testo:
        return Esito("le esclusioni tengono", NON_VERIFICABILE, "nessun markdown")
    trovate = [e for e in esclusioni if re.search(rf"\b{re.escape(e)}", testo)]
    if trovate:
        return Esito("le esclusioni tengono", FALLITA, f"nel menu compare: {trovate}",
                     "vale anche come ingrediente nascosto")
    return Esito("le esclusioni tengono", OK)


def a_prezzi_con_data_e_fonte(casa):
    senza = []
    for identificativo, prodotto in casa.paniere().items():
        for prezzo in (prodotto.get("prezzi") or []):
            if not isinstance(prezzo, dict) or not prezzo.get("data") or not prezzo.get("fonte"):
                senza.append(identificativo)
    if senza:
        return Esito("ogni prezzo ha data e fonte", FALLITA, f"prodotti: {sorted(set(senza))[:5]}",
                     "regola non negoziabile")
    return Esito("ogni prezzo ha data e fonte", OK)


def a_fuori_casa_non_entra_in_spesa_reale(casa):
    settimane = casa.storico().get("settimane") or []
    if not settimane:
        return Esito("il ristorante resta fuori da spesa_reale", NON_VERIFICABILE, "storico vuoto")
    ultima = settimane[-1]
    fuori = ultima.get("spesa_fuori_casa")
    reale = ultima.get("spesa_reale")
    stimata = ultima.get("spesa_stimata")
    if fuori is None or reale is None:
        return Esito("il ristorante resta fuori da spesa_reale", NON_VERIFICABILE,
                     "campi non ancora compilati")
    if stimata and reale >= stimata + fuori - 0.01 and fuori > 0:
        return Esito("il ristorante resta fuori da spesa_reale", FALLITA,
                     f"spesa_reale {reale} sembra includere spesa_fuori_casa {fuori}",
                     "sommarle rompe l'unica cosa che spesa_reale sa fare")
    return Esito("il ristorante resta fuori da spesa_reale", OK)


def a_diario_e_caselle_concordano(casa):
    testo = casa.testo_settimana()
    diario = casa.diario()
    if testo is None or diario is None:
        return Esito("diario e caselle concordano", NON_VERIFICABILE, "manca il diario o il menu")
    fatte, _aperte = _caselle(testo)
    voci = sum(len([p for p in (g or {}) if p in PASTI]) for g in diario.values() if isinstance(g, dict))
    if voci == 0:
        return Esito("diario e caselle concordano", NON_VERIFICABILE, "diario vuoto")
    if fatte == 0:
        return Esito("diario e caselle concordano", FALLITA,
                     f"{voci} pasti nel diario ma nessuna casella spuntata nel menu",
                     "le caselle dicono CHE, il diario dice COSA: devono raccontare la stessa settimana")
    return Esito("diario e caselle concordano", OK, f"{fatte} caselle, {voci} voci di diario")


def a_dispensa_si_e_mossa(casa):
    prima = casa.prima.get("dispensa")
    dopo = casa.dispensa()
    if prima is None:
        return Esito("la dispensa si e' mossa", NON_VERIFICABILE, "nessuno stato precedente")
    if prima == dopo:
        return Esito("la dispensa si e' mossa", FALLITA,
                     "dispensa.yaml identica dopo un giro completo",
                     "il menu scrive gli avanzi previsti, la spesa e il postmortem li correggono")
    return Esito("la dispensa si e' mossa", OK)


def a_un_commit_per_skill(casa, skill_attese):
    profilo = casa.profilo()
    if profilo.get("git") == "no":
        return Esito("un commit per skill che ha scritto", NON_VERIFICABILE, "`git: no` nel profilo")
    messaggi = casa.commit()
    if messaggi is None:
        return Esito("un commit per skill che ha scritto", NON_VERIFICABILE,
                     "la cartella non e' un repo git a se'")
    mancanti = [s for s in skill_attese if not any(m.lower().startswith(s) for m in messaggi)]
    if mancanti:
        return Esito("un commit per skill che ha scritto", FALLITA,
                     f"nessun commit per: {mancanti} (visti: {messaggi[:6]})",
                     "ogni skill che ha scritto chiude con un commit")
    return Esito("un commit per skill che ha scritto", OK, f"{len(messaggi)} commit")


def a_nome_settimana_stabile(casa):
    """Il nome si fissa alla generazione: markdown, HTML e cartella allineati."""
    md = casa.markdown_settimana()
    cartella = casa.cartella_settimana()
    if not md or not cartella:
        return Esito("il nome della settimana e' allineato", NON_VERIFICABILE, "settimana incompleta")
    radice_md = os.path.basename(md)[:-3]
    if radice_md != os.path.basename(cartella):
        return Esito("il nome della settimana e' allineato", FALLITA,
                     f"markdown `{radice_md}` contro cartella `{os.path.basename(cartella)}`")
    html = os.path.join(os.path.dirname(md), radice_md + ".html")
    if not os.path.isfile(html):
        return Esito("il nome della settimana e' allineato", FALLITA, f"manca {radice_md}.html")
    return Esito("il nome della settimana e' allineato", OK, radice_md)


# ------------------------------------------------------------- insiemi per fase

def dopo_settimana(casa):
    return [
        a_menu_scrive_quello_che_deve(casa),
        a_settimana_nasce_preventivo(casa),
        a_nome_settimana_stabile(casa),
        a_lista_in_confezioni(casa),
        a_scorte_nominate_uscendo(casa),
        a_scongelamento_dichiarato(casa),
        a_celle_non_cucinate_non_hanno_piatto(casa),
        a_pavimento_calorico(casa),
        a_nessun_deficit_a_chi_non_e_a_dieta(casa),
        a_pasto_libero_non_compensato(casa),
        a_esclusioni_rispettate(casa),
        a_prezzi_con_data_e_fonte(casa),
        a_un_commit_per_skill(casa, ["settimana", "menu"]),
    ]


def dopo_spesa(casa):
    return [
        a_solo_spesa_promuove(casa),
        a_consuntivo_senza_caselle(casa),
        a_prezzi_con_data_e_fonte(casa),
        a_nome_settimana_stabile(casa),
        a_un_commit_per_skill(casa, ["spesa"]),
    ]


def dopo_prepara(casa):
    return [
        a_diario_e_caselle_concordano(casa),
        a_nome_settimana_stabile(casa),
        a_un_commit_per_skill(casa, ["prepara"]),
    ]


def dopo_correggi(casa):
    return [
        a_nome_settimana_stabile(casa),
        a_esclusioni_rispettate(casa),
        a_un_commit_per_skill(casa, ["correggi"]),
    ]


def dopo_postmortem(casa):
    return [
        a_fuori_casa_non_entra_in_spesa_reale(casa),
        a_dispensa_si_e_mossa(casa),
        a_prezzi_con_data_e_fonte(casa),
        a_un_commit_per_skill(casa, ["postmortem"]),
    ]


PER_FASE = {
    "settimana": dopo_settimana,
    "spesa": dopo_spesa,
    "prepara": dopo_prepara,
    "correggi": dopo_correggi,
    "postmortem": dopo_postmortem,
}


def per_fase(fase, casa):
    funzione = PER_FASE.get(fase)
    return funzione(casa) if funzione else []
