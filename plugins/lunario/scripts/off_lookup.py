#!/usr/bin/env python3
"""Open Food Facts -> dati/prodotti.jsonl

Cerca un prodotto e ne ricava cio' che serve al motore: formato della
confezione (per la conversione grammi -> pacchi) e nutrienti per 100 g.

Uso:
    python off_lookup.py --ean 8002330121556
    python off_lookup.py "fusilli integrali" --marca esselunga
    python off_lookup.py "ceci lessati" --salva ceci-lessati-400

Senza --salva stampa i candidati e non tocca niente: la scelta e' di chi
guarda, perche' il nome giusto lo riconosce solo chi ha comprato il prodotto.

Nessuna dipendenza esterna: solo stdlib. L'API di Open Food Facts e' pubblica
e non richiede chiave; i dati sono ODbL e la fonte va citata.

Loro chiedono "1 API call = 1 real scan": questo script e' fatto per essere
chiamato una volta per prodotto, non in ciclo su un listino.
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

PAUSA = 1.0  # secondi tra una richiesta e l'altra

API = "https://world.openfoodfacts.org/api/v2"
# La ricerca full-text vive su un servizio separato: gli endpoint di ricerca
# su world.openfoodfacts.org rispondono 503 con continuita' (verificato
# 2026-08-14). Il lookup per codice a barre invece e' stabile.
SEARCH = "https://search.openfoodfacts.org/search"
UA = "Lunario/1.0 (menu planner personale; https://github.com/fporcari)"
CAMPI = "code,product_name,product_name_it,brands,quantity,product_quantity,product_quantity_unit,nutriments,categories_tags"

# Il plugin vive fuori dal progetto una volta installato: i dati di famiglia
# stanno nella cartella da cui si lavora, non accanto a questo file.
DATI = Path(os.environ.get("LUNARIO_DATI") or Path.cwd() / "dati")
PRODOTTI = DATI / "prodotti.jsonl"


def _get(url, tentativi=2):
    """GET con ritmo gentile: Open Food Facts risponde 429 se la si incalza."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for n in range(tentativi):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429 and n + 1 < tentativi:
                time.sleep(PAUSA * 10)
                continue
            raise


def cerca(testo, marca=None, lingua="it", limite=5):
    """Ricerca per nome, in due passi.

    Il servizio di ricerca restituisce nome e codice ma NON il formato della
    confezione, che e' il dato per cui esiste questo script: i candidati
    vanno quindi ripresi uno per uno dal lookup per codice a barre.

    Si filtra per lingua e non per paese: su questo indice `countries_tags`
    azzera i risultati, `lang:` funziona (verificato 2026-08-14).
    """
    termini = [testo]
    if marca:
        termini.append(f"brands_tags:{marca.lower().replace(' ', '-')}")
    if lingua:
        termini.append(f"lang:{lingua}")
    q = {"q": " ".join(termini), "page_size": limite, "fields": "code,product_name,brands"}
    hits = _get(f"{SEARCH}?{urllib.parse.urlencode(q)}").get("hits", [])

    dettagliati = []
    for i, h in enumerate(hits):
        if not h.get("code"):
            continue
        if i:
            time.sleep(PAUSA)
        trovato = per_ean(h["code"])
        dettagliati.extend(trovato or [h])
    return dettagliati


def per_ean(ean):
    d = _get(f"{API}/product/{ean}?fields={CAMPI}")
    return [d["product"]] if d.get("status") == 1 else []


def normalizza(p, id_locale=None):
    """Prodotto OFF -> riga di dati/prodotti.jsonl (contratto in CLAUDE.md)."""
    n = p.get("nutriments") or {}
    peso = p.get("product_quantity")
    try:
        peso = round(float(peso)) if peso not in (None, "") else None
    except (TypeError, ValueError):
        peso = None
    nome = p.get("product_name_it") or p.get("product_name") or "?"

    def num(v):
        try:
            return round(float(v), 1)
        except (TypeError, ValueError):
            return None

    return {
        "id": id_locale or (p.get("code") or nome.lower().replace(" ", "-"))[:40],
        "nome": nome.strip(),
        "ean": p.get("code"),
        "formato_g": peso,
        # 'confezione' e' l'ipotesi giusta quando OFF dichiara un formato;
        # 'peso' e 'pezzo' li sa solo chi compra, quindi restano da confermare
        "tipo": "confezione" if peso else None,
        "reparto": None,
        "kcal_100g": num(n.get("energy-kcal_100g")),
        "proteine_100g": num(n.get("proteins_100g")),
        "alias_scontrino": [],
        "prezzi": [],
        "fonte_nutrienti": f"openfoodfacts:{p.get('code')}" if p.get("code") else None,
        # Da dove viene formato_g, e quando: i produttori cambiano i tagli, e
        # un formato sbagliato va corretto dove e' nato. Senza formato non c'e'
        # provenienza da dichiarare.
        "fonte_formato": {
            "fonte": f"openfoodfacts:{p.get('code')}" if p.get("code") else "openfoodfacts",
            "data": time.strftime("%Y-%m-%d"),
        } if peso else None,
    }


def salva(riga):
    """Aggiunge o aggiorna la riga in dati/prodotti.jsonl, per id."""
    PRODOTTI.parent.mkdir(parents=True, exist_ok=True)
    righe = {}
    if PRODOTTI.exists():
        for r in PRODOTTI.read_text(encoding="utf-8").splitlines():
            if r.strip():
                d = json.loads(r)
                righe[d["id"]] = d
    if riga["id"] in righe:
        # i campi appresi in casa (prezzi, alias, reparto, tipo) vincono
        # sempre su quelli di OFF: sono stati confermati da un umano
        vecchia = righe[riga["id"]]
        for k in ("alias_scontrino", "prezzi", "reparto", "tipo"):
            if vecchia.get(k):
                riga[k] = vecchia[k]
        # Un formato confermato da chi il pacco ce l'ha in mano, o letto su uno
        # scontrino, vale piu' di quello che OFF dichiara adesso: e' il formato
        # che questo negozio tiene davvero.
        conferma = (vecchia.get("fonte_formato") or {}).get("fonte", "")
        if conferma.startswith(("utente", "scontrino")) and vecchia.get("formato_g"):
            riga["formato_g"] = vecchia["formato_g"]
            riga["fonte_formato"] = vecchia["fonte_formato"]
    righe[riga["id"]] = riga
    with PRODOTTI.open("w", encoding="utf-8") as f:
        for d in righe.values():
            f.write(json.dumps(d, ensure_ascii=False) + "\n")
    return len(righe)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("testo", nargs="?", help="nome del prodotto da cercare")
    ap.add_argument("--ean", help="cerca per codice a barre (esatto)")
    ap.add_argument("--marca", help="filtra per marca, es. esselunga")
    ap.add_argument("--lingua", default="it", help="lingua dei prodotti (default: it)")
    ap.add_argument("--salva", metavar="ID", help="salva il primo risultato in dati/prodotti.jsonl con questo id")
    a = ap.parse_args()

    if not a.testo and not a.ean:
        ap.error("serve un nome da cercare oppure --ean")

    try:
        trovati = per_ean(a.ean) if a.ean else cerca(a.testo, a.marca, a.lingua)
    except urllib.error.HTTPError as e:
        if e.code == 429:
            sys.exit("Open Food Facts sta limitando le richieste: aspetta un minuto "
                     "e riprova. Se serve un solo prodotto, --ean costa una chiamata sola.")
        sys.exit(f"Open Food Facts ha risposto {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        sys.exit(f"Open Food Facts non raggiungibile: {e.reason}")

    if not trovati:
        sys.exit("nessun prodotto trovato: la riga della spesa resta in grammi, "
                 "marcata [formato da verificare]")

    for p in trovati:
        r = normalizza(p)
        formato = f"{r['formato_g']} g" if r["formato_g"] else "formato ignoto"
        kcal = f"{r['kcal_100g']} kcal" if r["kcal_100g"] is not None else "kcal ignote"
        prot = f"{r['proteine_100g']} g prot" if r["proteine_100g"] is not None else "proteine ignote"
        print(f"{r['ean'] or '-':<15} {r['nome'][:42]:<44} {formato:<16} {kcal}/100g  {prot}/100g")

    if a.salva:
        n = salva(normalizza(trovati[0], a.salva))
        print(f"\nsalvato come '{a.salva}' -> {PRODOTTI} ({n} prodotti nel paniere)")
        print("da completare a mano: reparto, e tipo se non e' 'confezione'")


if __name__ == "__main__":
    main()
