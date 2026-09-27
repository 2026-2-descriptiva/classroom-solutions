import csv
from pathlib import Path


def pregunta_11():
    """Retorna la suma de la segunda columna por código de la cuarta columna."""
    totals = {}
    path = Path(__file__).resolve().parents[1] / "data" / "data.csv"
    with path.open(encoding="utf-8", newline="") as file:
        for row in csv.reader(file, delimiter="\t"):
            for code in row[3].split(","):
                totals[code] = totals.get(code, 0) + int(row[1])
    return dict(sorted(totals.items()))
    # raise NotImplementedError
