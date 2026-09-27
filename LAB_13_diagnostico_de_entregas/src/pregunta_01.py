"""Diagnóstico de cumplimiento de entregas."""

from pathlib import Path

import pandas as pd


ACTIVITY_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = ACTIVITY_DIR / "data" / "supply_chain.csv"
SUBMISSION_DIR = ACTIVITY_DIR / "submission"


def diagnose_deliveries() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Diagnostique el cumplimiento de entregas de ``data/supply_chain.csv`` y
    genere tres CSV en ``submission/``:

    - ``overall_delivery_kpis.csv`` con una fila y las columnas ``shipments``,
      ``line_item_value_usd``, ``on_time_rate``, ``median_days_vs_schedule`` y
      ``late_value_usd``.
    - ``shipment_mode_summary.csv`` con una fila por ``Shipment Mode`` y las
      columnas ``shipments``, ``on_time_rate``, ``avg_days_vs_schedule``,
      ``line_item_value_usd`` y ``late_value_usd``. Ordénelo por
      ``on_time_rate`` ascendente. Conserve como categoría faltante los envíos
      cuyo modo no esté informado.
    - ``priority_segments.csv`` con los diez segmentos país–modo que requieren
      investigación prioritaria. Incluya segmentos con al menos 30 envíos y
      las columnas ``Country``, ``Shipment Mode``, ``shipments``,
      ``on_time_rate`` y ``late_value_usd``. Ordénelos por ``late_value_usd``
      descendente y, ante empate, por ``on_time_rate`` ascendente.

    Convierta ``Scheduled Delivery Date`` y ``Delivered to Client Date`` con
    el formato ``%d-%b-%y``. Un envío está tarde únicamente si la fecha real
    es posterior a la fecha programada. ``on_time_rate`` es la proporción de
    envíos que no están tarde; ``late_value_usd`` es el valor de los envíos
    tardíos. Los segmentos seleccionados son prioridades de investigación,
    no evidencia de causalidad.
    """
    shipments = pd.read_csv(DATA_FILE)
    for column in ["Scheduled Delivery Date", "Delivered to Client Date"]:
        shipments[column] = pd.to_datetime(
            shipments[column], format="%d-%b-%y", errors="coerce"
        )

    shipments["days_vs_schedule"] = (
        shipments["Delivered to Client Date"] - shipments["Scheduled Delivery Date"]
    ).dt.days
    shipments["is_late"] = shipments["days_vs_schedule"].gt(0)

    overall_delivery_kpis = pd.DataFrame(
        {
            "shipments": [shipments["ID"].size],
            "line_item_value_usd": [shipments["Line Item Value"].sum()],
            "on_time_rate": [1 - shipments["is_late"].mean()],
            "median_days_vs_schedule": [shipments["days_vs_schedule"].median()],
            "late_value_usd": [
                shipments.loc[shipments["is_late"], "Line Item Value"].sum()
            ],
        }
    )

    shipment_mode_summary = (
        shipments.groupby("Shipment Mode", dropna=False)
        .agg(
            shipments=("ID", "size"),
            on_time_rate=("is_late", lambda values: 1 - values.mean()),
            avg_days_vs_schedule=("days_vs_schedule", "mean"),
            line_item_value_usd=("Line Item Value", "sum"),
            late_value_usd=(
                "Line Item Value",
                lambda values: values[shipments.loc[values.index, "is_late"]].sum(),
            ),
        )
        .reset_index()
        .sort_values("on_time_rate")
    )

    priority_segments = (
        shipments.groupby(["Country", "Shipment Mode"], dropna=False)
        .agg(
            shipments=("ID", "size"),
            on_time_rate=("is_late", lambda values: 1 - values.mean()),
            late_value_usd=(
                "Line Item Value",
                lambda values: values[shipments.loc[values.index, "is_late"]].sum(),
            ),
        )
        .reset_index()
    )
    priority_segments = priority_segments[priority_segments["shipments"] >= 30]
    priority_segments = priority_segments.sort_values(
        ["late_value_usd", "on_time_rate"], ascending=[False, True]
    ).head(10)

    SUBMISSION_DIR.mkdir(exist_ok=True)
    overall_delivery_kpis.to_csv(
        SUBMISSION_DIR / "overall_delivery_kpis.csv", index=False
    )
    shipment_mode_summary.to_csv(
        SUBMISSION_DIR / "shipment_mode_summary.csv", index=False
    )
    priority_segments.to_csv(SUBMISSION_DIR / "priority_segments.csv", index=False)

    return overall_delivery_kpis, shipment_mode_summary, priority_segments
    # raise NotImplementedError


if __name__ == "__main__":
    diagnose_deliveries()
