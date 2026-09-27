import csv
from pathlib import Path


def pregunta_09():
    """Retorna la frecuencia de cada clave de la quinta columna."""
    counts = {}
    path = Path(__file__).resolve().parents[1] / "data" / "data.csv"
    with path.open(encoding="utf-8", newline="") as file:
        for row in csv.reader(file, delimiter="\t"):
            for item in row[4].split(","):
                key, _ = item.split(":")
                counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))
    # raise NotImplementedError
