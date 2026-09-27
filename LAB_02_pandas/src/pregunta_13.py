import pandas as pd
from pathlib import Path


def pregunta_13():
    """Una `tbl0` y `tbl2` por `c0` y retorne la suma de `c5b` por `c1`."""
    data_dir = Path(__file__).resolve().parents[1] / "data"
    left = pd.read_csv(data_dir / "tbl0.tsv", sep="\t")
    right = pd.read_csv(data_dir / "tbl2.tsv", sep="\t")
    result = left.merge(right, on="c0").groupby("c1")["c5b"].sum()
    result.name = None
    return result
    # raise NotImplementedError
