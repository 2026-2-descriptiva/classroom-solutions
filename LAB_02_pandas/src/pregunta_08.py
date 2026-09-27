import pandas as pd
from pathlib import Path


def pregunta_08():
    """Retorne `tbl0` con una columna `suma` igual a `c0 + c2`."""
    path = Path(__file__).resolve().parents[1] / "data" / "tbl0.tsv"
    table = pd.read_csv(path, sep="\t")
    table["suma"] = table["c0"] + table["c2"]
    return table
    # raise NotImplementedError
