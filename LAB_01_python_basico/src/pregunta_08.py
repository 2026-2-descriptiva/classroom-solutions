import csv
from pathlib import Path


def pregunta_08():
    """Asocia cada valor de la segunda columna con letras únicas y ordenadas."""
    letters = {}
    path = Path(__file__).resolve().parents[1] / "data" / "data.csv"
    with path.open(encoding="utf-8", newline="") as file:
        for row in csv.reader(file, delimiter="\t"):
            letters.setdefault(int(row[1]), set()).add(row[0])
    return [(value, sorted(group)) for value, group in sorted(letters.items())]
    # raise NotImplementedError
