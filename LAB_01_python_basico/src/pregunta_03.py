import csv
from pathlib import Path


def pregunta_03():
    """Retorna la suma de la segunda columna por letra."""
    totals = {}
    path = Path(__file__).resolve().parents[1] / "data" / "data.csv"
    with path.open(encoding="utf-8", newline="") as file:
        for row in csv.reader(file, delimiter="\t"):
            totals[row[0]] = totals.get(row[0], 0) + int(row[1])
    return sorted(totals.items())
    # raise NotImplementedError
