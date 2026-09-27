import pandas as pd
from pathlib import Path


def pregunta_09():
    """Retorne `tbl0` con una columna `year` extraída de `c3`."""
    path = Path(__file__).resolve().parents[1] / "data" / "tbl0.tsv"
    table = pd.read_csv(path, sep="\t")
    table["year"] = table["c3"].str[:4]
    return table
    # raise NotImplementedError
