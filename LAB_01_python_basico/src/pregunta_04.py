import csv
from pathlib import Path


def pregunta_04():
    """Retorna la cantidad de registros por mes."""
    counts = {}
    path = Path(__file__).resolve().parents[1] / "data" / "data.csv"
    with path.open(encoding="utf-8", newline="") as file:
        for row in csv.reader(file, delimiter="\t"):
            month = row[2][5:7]
            counts[month] = counts.get(month, 0) + 1
    return sorted(counts.items())
    # raise NotImplementedError
