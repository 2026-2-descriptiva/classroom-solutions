import pandas as pd
from pathlib import Path


def pregunta_04():
    """Retorne el promedio de `c2` por cada categoría de `c1`."""
    path = Path(__file__).resolve().parents[1] / "data" / "tbl0.tsv"
    table = pd.read_csv(path, sep="\t")
    result = table.groupby("c1")["c2"].mean()
    result.name = None
    return result
    # raise NotImplementedError
