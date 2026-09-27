import csv
from pathlib import Path


def pregunta_06():
    """Retorna mínimo y máximo de cada clave codificada en la quinta columna."""
    values = {}
    path = Path(__file__).resolve().parents[1] / "data" / "data.csv"
    with path.open(encoding="utf-8", newline="") as file:
        for row in csv.reader(file, delimiter="\t"):
            for item in row[4].split(","):
                key, value = item.split(":")
                values.setdefault(key, []).append(int(value))
    return [(key, min(group), max(group)) for key, group in sorted(values.items())]
    # raise NotImplementedError
