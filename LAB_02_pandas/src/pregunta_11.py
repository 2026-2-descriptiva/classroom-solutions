import pandas as pd
from pathlib import Path


def pregunta_11():
    """Retorne `tbl1` con los elementos de `c4` ordenados dentro de cada registro."""
    path = Path(__file__).resolve().parents[1] / "data" / "tbl1.tsv"
    table = pd.read_csv(path, sep="\t")
    result = table.groupby("c0", as_index=False).agg(list)
    result["c4"] = result["c4"].map(lambda values: ",".join(sorted(values)))
    return result[["c0", "c4"]]
    # raise NotImplementedError
