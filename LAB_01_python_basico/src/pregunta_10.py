import csv
from pathlib import Path


def pregunta_10():
    """Retorna letra, cantidad de códigos y cantidad de métricas por registro."""
    path = Path(__file__).resolve().parents[1] / "data" / "data.csv"
    with path.open(encoding="utf-8", newline="") as file:
        return [
            (row[0], len(row[3].split(",")), len(row[4].split(",")))
            for row in csv.reader(file, delimiter="\t")
        ]
        # raise NotImplementedError
