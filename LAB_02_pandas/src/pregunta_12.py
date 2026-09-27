import pandas as pd
from pathlib import Path


def pregunta_12():
    """Retorne `tbl2` con pares `c5a:c5b` ordenados y unidos por comas."""
    path = Path(__file__).resolve().parents[1] / "data" / "tbl2.tsv"
    table = pd.read_csv(path, sep="\t")
    table["c5"] = table["c5a"] + ":" + table["c5b"].astype(str)
    result = table.groupby("c0", as_index=False).agg(list)
    result["c5"] = result["c5"].map(lambda values: ",".join(sorted(values)))
    return result[["c0", "c5"]]
    # raise NotImplementedError
