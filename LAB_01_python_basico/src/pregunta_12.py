import csv
from pathlib import Path


def pregunta_12():
    """Retorna la suma de los valores codificados en la quinta columna por letra."""
    totals = {}
    path = Path(__file__).resolve().parents[1] / "data" / "data.csv"
    with path.open(encoding="utf-8", newline="") as file:
        for row in csv.reader(file, delimiter="\t"):
            metric_total = sum(int(item.split(":")[1]) for item in row[4].split(","))
            totals[row[0]] = totals.get(row[0], 0) + metric_total
    return dict(sorted(totals.items()))
    # raise NotImplementedError
