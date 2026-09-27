import pandas as pd
from pathlib import Path


def pregunta_03():
    """Retorne la frecuencia de cada categoría de `c1`, ordenada alfabéticamente."""
    path = Path(__file__).resolve().parents[1] / "data" / "tbl0.tsv"
    table = pd.read_csv(path, sep="\t")
    result = table["c1"].value_counts().sort_index()
    result.name = None
    return result
    # raise NotImplementedError
