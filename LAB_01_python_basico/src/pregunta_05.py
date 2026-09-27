import csv
from pathlib import Path


def pregunta_05():
    """Retorna máximo y mínimo de la segunda columna por letra."""
    values = {}
    path = Path(__file__).resolve().parents[1] / "data" / "data.csv"
    with path.open(encoding="utf-8", newline="") as file:
        for row in csv.reader(file, delimiter="\t"):
            values.setdefault(row[0], []).append(int(row[1]))
    return [(letter, max(group), min(group)) for letter, group in sorted(values.items())]
    # raise NotImplementedError
