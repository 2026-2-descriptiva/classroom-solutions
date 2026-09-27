import pandas as pd
from pathlib import Path


def pregunta_06():
    """Retorne valores únicos de `c4` en mayúsculas y ordenados alfabéticamente."""
    path = Path(__file__).resolve().parents[1] / "data" / "tbl1.tsv"
    table = pd.read_csv(path, sep="\t")
    return sorted(table["c4"].str.upper().unique().tolist())
    # raise NotImplementedError
