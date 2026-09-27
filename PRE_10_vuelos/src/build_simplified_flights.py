"""Construye los datos simplificados del taller PRE_11_vuelos.

Los archivos crudos de BTS se conservan en ``data/`` y se procesan por
fragmentos. Los estudiantes solo necesitan los dos CSV comprimidos que este
programa deja en ``data/``.

Ejemplo:
    python src/build_simplified_flights.py
    python src/build_simplified_flights.py --output-dir data
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


INPUT_COLUMNS = [
    "YEAR",
    "MONTH",
    "DAY_OF_WEEK",
    "CRS_DEP_TIME",
    "REPORTING_AIRLINE",
    "FLIGHTS",
    "CANCELLED",
    "DEP_DEL15",
    "DEP_DELAY",
]

# BTS usa OP_UNIQUE_CARRIER en los archivos de 2006--2008. En otras
# extracciones el campo equivalente se llama REPORTING_AIRLINE. Para este
# taller ambos representan la aerolínea que opera el vuelo.
CARRIER_COLUMNS = {"REPORTING_AIRLINE", "OP_UNIQUE_CARRIER"}

METRIC_COLUMNS = [
    "scheduled_flights",
    "cancelled_flights",
    "operated_flights",
    "delayed_departure_15_flights",
    "positive_departure_delay_minutes",
]

DAY_HOUR_GRAIN = [
    "year",
    "month",
    "day_of_week",
    "scheduled_departure_hour",
    "reporting_airline",
]

MONTH_GRAIN = ["year", "month", "reporting_airline"]


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Agrega los archivos crudos de vuelos para PRE_11_vuelos."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data",
        help="Carpeta con los 36 archivos .zip descargados de BTS.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data",
        help="Carpeta en la que se escribirán los archivos del alumnado.",
    )
    parser.add_argument(
        "--chunksize",
        type=int,
        default=250_000,
        help="Filas leídas por fragmento; mantiene bajo el uso de memoria.",
    )
    return parser.parse_args()


def input_files(input_dir: Path) -> list[Path]:
    """Devuelve los archivos mensuales y evita leer los agregados generados."""
    files = sorted(path for path in input_dir.glob("*.zip") if path.is_file())
    if not files:
        raise FileNotFoundError(f"No se encontraron archivos .zip en {input_dir}")
    return files


def validate_columns(file: Path) -> None:
    """Falla antes de procesar si el archivo descargado no tiene el esquema final."""
    header = pd.read_csv(file, compression="zip", nrows=0)
    available = {column.strip().upper() for column in header.columns}
    missing = sorted((set(INPUT_COLUMNS) - {"REPORTING_AIRLINE"}) - available)
    if not available.intersection(CARRIER_COLUMNS):
        missing.append("OP_UNIQUE_CARRIER o REPORTING_AIRLINE")
    if missing:
        raise ValueError(
            f"{file.name} no contiene las columnas requeridas: {', '.join(missing)}. "
            "Vuelva a descargar el archivo con el esquema definitivo de PRE_11_vuelos."
        )


def prepare_chunk(chunk: pd.DataFrame) -> pd.DataFrame:
    """Normaliza un fragmento y crea solamente medidas aditivas."""
    chunk.columns = [column.strip().upper() for column in chunk.columns]
    if "REPORTING_AIRLINE" not in chunk.columns:
        chunk = chunk.rename(columns={"OP_UNIQUE_CARRIER": "REPORTING_AIRLINE"})

    for column in ["YEAR", "MONTH", "DAY_OF_WEEK", "CRS_DEP_TIME", "FLIGHTS", "CANCELLED", "DEP_DEL15", "DEP_DELAY"]:
        chunk[column] = pd.to_numeric(chunk[column], errors="coerce")

    missing_schedule = chunk["CRS_DEP_TIME"].isna().sum()
    if missing_schedule:
        raise ValueError(
            f"Se encontraron {missing_schedule} vuelos sin hora programada de salida. "
            "No es posible asignarlos a una hora sin alterar el denominador."
        )

    result = pd.DataFrame(
        {
            "year": chunk["YEAR"].astype("int16"),
            "month": chunk["MONTH"].astype("int8"),
            "day_of_week": chunk["DAY_OF_WEEK"].astype("int8"),
            # 2400 representa medianoche; el módulo lo convierte en 0.
            "scheduled_departure_hour": (
                (chunk["CRS_DEP_TIME"].astype("int32") // 100) % 24
            ).astype("int8"),
            "reporting_airline": chunk["REPORTING_AIRLINE"].astype("string").str.strip(),
        }
    )

    flights = chunk["FLIGHTS"].fillna(0).clip(lower=0)
    cancelled = chunk["CANCELLED"].fillna(0).eq(1)
    operated = ~cancelled
    delayed = chunk["DEP_DEL15"].fillna(0).eq(1) & operated

    result["scheduled_flights"] = flights
    result["cancelled_flights"] = flights.where(cancelled, 0)
    result["operated_flights"] = flights.where(operated, 0)
    result["delayed_departure_15_flights"] = flights.where(delayed, 0)
    result["positive_departure_delay_minutes"] = (
        chunk["DEP_DELAY"].fillna(0).clip(lower=0).where(operated, 0) * flights
    )

    return result


def aggregate(frame: pd.DataFrame, grain: list[str]) -> pd.DataFrame:
    return frame.groupby(grain, as_index=False, dropna=False)[METRIC_COLUMNS].sum()


def combine(parts: list[pd.DataFrame], grain: list[str]) -> pd.DataFrame:
    return aggregate(pd.concat(parts, ignore_index=True), grain).sort_values(grain)


def validate_outputs(day_hour: pd.DataFrame, monthly: pd.DataFrame) -> None:
    """Comprueba conservación de conteos y coherencia entre ambos archivos."""
    if not day_hour["scheduled_departure_hour"].between(0, 23).all():
        raise ValueError("Hay horas programadas fuera del intervalo 0–23.")

    for frame_name, frame in {"día-hora": day_hour, "mes": monthly}.items():
        if not (frame["cancelled_flights"] <= frame["scheduled_flights"]).all():
            raise ValueError(f"Cancelaciones mayores que vuelos programados en {frame_name}.")
        if not (frame["operated_flights"] <= frame["scheduled_flights"]).all():
            raise ValueError(f"Vuelos operados mayores que programados en {frame_name}.")
        if not (
            frame["delayed_departure_15_flights"] <= frame["operated_flights"]
        ).all():
            raise ValueError(f"Retrasos mayores que vuelos operados en {frame_name}.")

    from_day_hour = aggregate(day_hour, MONTH_GRAIN)
    comparison = from_day_hour.merge(monthly, on=MONTH_GRAIN, suffixes=("_day_hour", "_month"))
    for metric in METRIC_COLUMNS:
        if not (comparison[f"{metric}_day_hour"] == comparison[f"{metric}_month"]).all():
            raise ValueError(f"El total mensual de {metric} no coincide con el agregado día-hora.")


def build(input_dir: Path, output_dir: Path, chunksize: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    day_hour_parts: list[pd.DataFrame] = []
    monthly_parts: list[pd.DataFrame] = []

    for file in input_files(input_dir):
        validate_columns(file)
        print(f"Procesando {file.name}")
        for chunk in pd.read_csv(
            file,
            compression="zip",
            # La fuente puede entregar MAYÚSCULAS o nombres en Title_Case.
            # La normalización posterior deja un único esquema interno.
            usecols=lambda column: (
                column.strip().upper() in INPUT_COLUMNS
                or column.strip().upper() in CARRIER_COLUMNS
            ),
            chunksize=chunksize,
            low_memory=False,
        ):
            prepared = prepare_chunk(chunk)
            day_hour_parts.append(aggregate(prepared, DAY_HOUR_GRAIN))
            monthly_parts.append(aggregate(prepared, MONTH_GRAIN))

    day_hour = combine(day_hour_parts, DAY_HOUR_GRAIN)
    monthly = combine(monthly_parts, MONTH_GRAIN)
    validate_outputs(day_hour, monthly)

    output_dir.mkdir(parents=True, exist_ok=True)
    day_hour.to_csv(output_dir / "flights_by_carrier_day_hour.csv.gz", index=False, compression="gzip")
    monthly.to_csv(output_dir / "flights_by_carrier_month.csv.gz", index=False, compression="gzip")
    return day_hour, monthly


def main() -> None:
    arguments = parse_arguments()
    day_hour, monthly = build(
        input_dir=arguments.input_dir,
        output_dir=arguments.output_dir,
        chunksize=arguments.chunksize,
    )
    print(
        "Archivos creados: "
        f"{len(day_hour):,} filas por día-hora y {len(monthly):,} filas por mes."
    )


if __name__ == "__main__":
    main()
