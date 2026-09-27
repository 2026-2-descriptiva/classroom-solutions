"""Diagnóstico de demoras y cancelaciones de vuelos."""

from pathlib import Path

import pandas as pd


ACTIVITY_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ACTIVITY_DIR / "data"
SUBMISSION_DIR = ACTIVITY_DIR / "submission"

METRIC_COLUMNS = [
    "scheduled_flights",
    "cancelled_flights",
    "operated_flights",
    "delayed_departure_15_flights",
    "positive_departure_delay_minutes",
]


def add_rates(frame: pd.DataFrame) -> pd.DataFrame:
    """Añade tasas usando el denominador operacional correspondiente."""
    result = frame.copy()
    result["cancellation_rate"] = (
        result["cancelled_flights"] / result["scheduled_flights"]
    )
    result["delay_rate"] = (
        result["delayed_departure_15_flights"] / result["operated_flights"]
    )
    result["mean_positive_delay_minutes"] = (
        result["positive_departure_delay_minutes"] / result["operated_flights"]
    )
    return result


def analyze_flights() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Analice los agregados de vuelos de ``data/`` y genere cuatro archivos en
    ``submission/``:

    - ``overall_kpis.csv``: una fila con los cinco conteos base y las tasas
      ``cancellation_rate``, ``delay_rate`` y ``mean_positive_delay_minutes``.
    - ``monthly_national_kpis.csv``: los mismos indicadores por ``year`` y
      ``month``, ordenados cronológicamente.
    - ``carrier_summary.csv``: indicadores por ``reporting_airline``,
      ordenados por ``delay_rate`` de mayor a menor.
    - ``priority_segments.csv``: los diez segmentos
      aerolínea–día–hora con mayor ``delay_rate`` entre aquellos con al menos
      25 000 vuelos operados. Incluya las tres dimensiones, los conteos base y
      las tres tasas.

    ``flights_by_carrier_month.csv.gz`` y la reagrupación mensual de
    ``flights_by_carrier_day_hour.csv.gz`` deben coincidir exactamente en las
    cinco medidas aditivas. La tasa de cancelación se calcula sobre vuelos
    programados; las tasas de demora y minutos se calculan sobre vuelos
    operados. No priorice segmentos usando solamente una tasa sin verificar
    volumen suficiente.
    """
    day_hour = pd.read_csv(DATA_DIR / "flights_by_carrier_day_hour.csv.gz")
    monthly = pd.read_csv(DATA_DIR / "flights_by_carrier_month.csv.gz")

    recomputed_monthly = (
        day_hour.groupby(["year", "month", "reporting_airline"])[METRIC_COLUMNS]
        .sum()
        .reset_index()
        .sort_values(["year", "month", "reporting_airline"])
        .reset_index(drop=True)
    )
    provided_monthly = (
        monthly.sort_values(["year", "month", "reporting_airline"])
        .reset_index(drop=True)
    )
    pd.testing.assert_frame_equal(recomputed_monthly, provided_monthly)

    overall_kpis = add_rates(monthly[METRIC_COLUMNS].sum().to_frame().T)

    monthly_national_kpis = add_rates(
        monthly.groupby(["year", "month"])[METRIC_COLUMNS].sum().reset_index()
    ).sort_values(["year", "month"])

    carrier_summary = add_rates(
        monthly.groupby("reporting_airline")[METRIC_COLUMNS].sum().reset_index()
    ).sort_values("delay_rate", ascending=False)

    priority_segments = add_rates(
        day_hour.groupby(
            ["reporting_airline", "day_of_week", "scheduled_departure_hour"]
        )[METRIC_COLUMNS]
        .sum()
        .reset_index()
    )
    priority_segments = priority_segments[
        priority_segments["operated_flights"] >= 25_000
    ].nlargest(10, "delay_rate")

    SUBMISSION_DIR.mkdir(exist_ok=True)
    overall_kpis.to_csv(SUBMISSION_DIR / "overall_kpis.csv", index=False)
    monthly_national_kpis.to_csv(
        SUBMISSION_DIR / "monthly_national_kpis.csv", index=False
    )
    carrier_summary.to_csv(SUBMISSION_DIR / "carrier_summary.csv", index=False)
    priority_segments.to_csv(SUBMISSION_DIR / "priority_segments.csv", index=False)

    return overall_kpis, monthly_national_kpis, carrier_summary, priority_segments
    # raise NotImplementedError


if __name__ == "__main__":
    analyze_flights()
