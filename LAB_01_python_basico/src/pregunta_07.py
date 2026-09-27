import csv
from pathlib import Path


def pregunta_07():
    """Asocia cada valor de la segunda columna con sus letras, preservando orden."""
    letters = {}
    path = Path(__file__).resolve().parents[1] / "data" / "data.csv"
    with path.open(encoding="utf-8", newline="") as file:
        for row in csv.reader(file, delimiter="\t"):
            letters.setdefault(int(row[1]), []).append(row[0])
    return sorted(letters.items())
    # raise NotImplementedError
