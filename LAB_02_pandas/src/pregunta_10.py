import pandas as pd
from pathlib import Path


def pregunta_10():
    """Retorne los valores de `c2` por `c1`, ordenados y unidos con `:`."""
    path = Path(__file__).resolve().parents[1] / "data" / "tbl0.tsv"
    table = pd.read_csv(path, sep="\t")
    result = table.groupby("c1")["c2"].agg(
        lambda values: ":".join(str(value) for value in sorted(values))
    ).to_frame()
    result.index.name = "_c1"
    return result
    # raise NotImplementedError
