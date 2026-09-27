import re
from pathlib import Path

import pandas as pd


def pregunta_01():
    """
    Construya y retorne un DataFrame de Pandas a partir de
    `data/clusters_report.txt`.

    El reporte contiene una tabla visualmente alineada, pero las palabras clave
    de cada clúster pueden continuar en varias líneas. El resultado debe tener
    las columnas `cluster`, `cantidad_de_palabras_clave`,
    `porcentaje_de_palabras_clave` y `principales_palabras_clave`.

    Convierta el porcentaje a número decimal, use nombres de columna en
    minúscula y una sola separación después de cada coma en las palabras clave.
    """
    path = Path(__file__).resolve().parents[1] / "data" / "clusters_report.txt"
    pattern = re.compile(r"^\s*(\d+)\s+(\d+)\s+(\d+,\d+)\s+%\s+(.*)$")
    records = []
    current = None

    for line in path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            if current is not None:
                records.append(current)
            cluster, count, percentage, keywords = match.groups()
            current = {
                "cluster": int(cluster),
                "cantidad_de_palabras_clave": int(count),
                "porcentaje_de_palabras_clave": float(percentage.replace(",", ".")),
                "keywords": [keywords],
            }
        elif current is not None and line.strip():
            current["keywords"].append(line.strip())

    if current is not None:
        records.append(current)

    for record in records:
        keywords = " ".join(record.pop("keywords"))
        keywords = re.sub(r"\s*,\s*", ", ", keywords)
        keywords = re.sub(r"\s+", " ", keywords).strip().rstrip(".")
        record["principales_palabras_clave"] = keywords

    return pd.DataFrame(records)
    # raise NotImplementedError
