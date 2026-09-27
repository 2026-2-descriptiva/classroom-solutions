import csv
from pathlib import Path


def pregunta_02():
    """Retorna la cantidad de registros por letra, en orden alfabético."""
    counts = {}
    path = Path(__file__).resolve().parents[1] / "data" / "data.csv"
    with path.open(encoding="utf-8", newline="") as file:
        for row in csv.reader(file, delimiter="\t"):
            counts[row[0]] = counts.get(row[0], 0) + 1
    return sorted(counts.items())
    # raise NotImplementedError
