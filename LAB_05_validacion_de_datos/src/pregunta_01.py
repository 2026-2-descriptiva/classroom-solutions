import json
import re
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = [
    "supplier_id",
    "supplier",
    "country",
    "city",
    "purchase_date",
    "amount",
    "discount",
    "weight",
    "units",
    "unit_price",
    "contact_email",
]


def normalize_column_name(name):
    """Convierte un encabezado a minúsculas, sin espacios externos ni BOM."""
    return re.sub(r"\s+", "_", name.lstrip("\ufeff").strip().lower())


def validate_required_columns(dataframe, required_columns):
    """Retorna columnas requeridas ausentes y columnas inesperadas."""
    columns = set(dataframe.columns)
    required = set(required_columns)
    return {
        "missing_required_columns": sorted(required - columns),
        "unexpected_columns": sorted(columns - required),
    }


def build_quality_report(dataframe):
    """Construye un reporte serializable con los hallazgos de calidad."""
    structure = validate_required_columns(dataframe, REQUIRED_COLUMNS)
    email_pattern = r"[^@\s]+@[^@\s]+\.[^@\s]+"
    valid_email = dataframe["contact_email"].str.fullmatch(email_pattern, na=False)
    units = pd.to_numeric(dataframe["units"], errors="coerce")
    duplicate_supplier_ids = dataframe["supplier_id"].duplicated(keep=False)

    return {
        "row_count": int(len(dataframe)),
        "column_count": int(len(dataframe.columns)),
        **structure,
        "duplicate_row_count": int(dataframe.duplicated().sum()),
        "duplicate_supplier_id_row_count": int(duplicate_supplier_ids.sum()),
        "missing_value_count_by_column": {
            column: int(count) for column, count in dataframe.isna().sum().items()
        },
        "invalid_email_count": int((~valid_email).sum()),
        "invalid_unit_count": int(
            (units.notna() & ((units <= 0) | (units % 1 != 0))).sum()
        ),
        "country_values": sorted(dataframe["country"].dropna().unique().tolist()),
    }


def main():
    """
    Valide `data/ventas.csv` y escriba `submission/data_quality_report.json`.

    El archivo de origen posee encabezados inconsistentes, valores faltantes,
    filas repetidas y valores categóricos con representaciones distintas. El
    reporte debe preservar estos hallazgos: no limpie ni modifique los datos.

    El JSON debe incluir el tamaño de la tabla, validación de las columnas
    requeridas, filas duplicadas, duplicados de `supplier_id`, faltantes por
    columna, correos inválidos, unidades inválidas y los valores observados de
    `country`.
    """
    root = Path(__file__).resolve().parents[1]
    source_file = root / "data" / "ventas.csv"
    output_file = root / "submission" / "data_quality_report.json"

    dataframe = pd.read_csv(source_file, dtype="string")
    dataframe.columns = [normalize_column_name(column) for column in dataframe.columns]
    report = build_quality_report(dataframe)

    output_file.parent.mkdir(exist_ok=True)
    output_file.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return report
    # raise NotImplementedError
