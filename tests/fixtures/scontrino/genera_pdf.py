#!/usr/bin/env python3
"""Trasforma scontrino-famiglia.txt in un PDF di una pagina.

Fixture sintetico: serve a far girare `lunario:spesa` su un vero PDF senza
dipendere da uno scontrino reale. Zero dipendenze esterne, come tutto il
resto del motore: il PDF e' scritto a mano, una riga di testo per riga del
sorgente, font Helvetica.

    python3 genera_pdf.py [sorgente.txt] [--out percorso.pdf]

Senza argomenti impagina scontrino-famiglia.txt e scrive il PDF accanto. Con
un sorgente diverso serve anche agli scenari avversi, che si costruiscono uno
scontrino monco da dare in pasto a `lunario:spesa`.
"""

import argparse
from pathlib import Path

QUI = Path(__file__).resolve().parent
SORGENTE = QUI / "scontrino-famiglia.txt"

LARGHEZZA = 595          # A4 in punti
ALTEZZA = 842
MARGINE_SX = 60
PRIMA_RIGA_Y = 780
CORPO = 9                # punti
INTERLINEA = 11


def escape_pdf(testo):
    """Le tre sequenze che un literal string PDF non tollera nude."""
    return testo.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")


def stream_contenuto(righe):
    pezzi = ["BT", f"/F1 {CORPO} Tf", f"{INTERLINEA} TL",
             f"1 0 0 1 {MARGINE_SX} {PRIMA_RIGA_Y} Tm"]
    for riga in righe:
        pezzi.append(f"({escape_pdf(riga)}) Tj")
        pezzi.append("T*")
    pezzi.append("ET")
    return "\n".join(pezzi)


def costruisci_pdf(righe):
    contenuto = stream_contenuto(righe).encode("latin-1", "replace")

    oggetti = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {LARGHEZZA} {ALTEZZA}]"
         f" /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>"
         ).encode("ascii"),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica"
        b" /Encoding /WinAnsiEncoding >>",
        (b"<< /Length " + str(len(contenuto)).encode("ascii") + b" >>\nstream\n"
         + contenuto + b"\nendstream"),
    ]

    out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = []
    for numero, corpo in enumerate(oggetti, start=1):
        offsets.append(len(out))
        out += f"{numero} 0 obj\n".encode("ascii") + corpo + b"\nendobj\n"

    inizio_xref = len(out)
    out += f"xref\n0 {len(oggetti) + 1}\n".encode("ascii")
    out += b"0000000000 65535 f \n"
    for offset in offsets:
        out += f"{offset:010d} 00000 n \n".encode("ascii")
    out += (f"trailer\n<< /Size {len(oggetti) + 1} /Root 1 0 R >>\n"
            f"startxref\n{inizio_xref}\n%%EOF\n").encode("ascii")
    return bytes(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sorgente", nargs="?", default=str(SORGENTE),
                        help="il .txt da impaginare; senza, lo scontrino di famiglia")
    parser.add_argument("--out", default=str(QUI / "scontrino-famiglia.pdf"),
                        help="percorso del PDF da scrivere")
    args = parser.parse_args()

    righe = Path(args.sorgente).read_text(encoding="utf-8").splitlines()
    destinazione = Path(args.out)
    destinazione.write_bytes(costruisci_pdf(righe))
    print(f"{destinazione}: {len(righe)} righe, "
          f"{destinazione.stat().st_size} byte")


if __name__ == "__main__":
    main()
