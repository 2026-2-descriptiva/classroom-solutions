import csv
from pathlib import Path


def pregunta_01():
    """Retorna la suma de la segunda columna."""
    path = Path(__file__).resolve().parents[1] / "data" / "data.csv"
    with path.open(encoding="utf-8", newline="") as file:
        return sum(int(row[1]) for row in csv.reader(file, delimiter="\t"))
        # raise NotImplementedError
