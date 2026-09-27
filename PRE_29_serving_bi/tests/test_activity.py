"""Verificaciones del taller de serving para BI."""

import sqlite3
from pathlib import Path

import nbformat
import pandas as pd
import pytest


@pytest.fixture(autouse=True)
def require_developed_solution():
    """Omite la evaluación hasta que exista el entregable de la solución."""
    required_files = (
        "submission/dashboard_sales.csv",
        "submission/serving_manifest.csv",
        "submission/bi_serving.db",
    )
    activity_dir = Path(__file__).resolve().parents[1]
    if any(not (activity_dir / file_name).is_file() for file_name in required_files):
        pytest.skip("La solución aún no ha publicado los artefactos de serving para BI.")


def test_serving_table_has_the_dashboard_grain_and_reconciles():
    dashboard_sales = pd.read_csv("submission/dashboard_sales.csv")
    with sqlite3.connect("data/sales_mart.db") as connection:
        mart_total = connection.execute("SELECT SUM(net_sales) FROM fact_sales").fetchone()[0]

    assert not dashboard_sales[["year", "month", "region", "category"]].duplicated().any()
    assert dashboard_sales["net_sales"].sum() == pytest.approx(mart_total)


def test_notebook_publishes_a_manifest_and_serving_database():
    manifest = pd.read_csv("submission/serving_manifest.csv")
    with sqlite3.connect("submission/bi_serving.db") as connection:
        tables = pd.read_sql_query(
            "SELECT name FROM sqlite_master WHERE type='table'", connection
        )["name"].tolist()
    notebook = nbformat.read("notebooks/notebook.ipynb", as_version=4)

    assert manifest.loc[0, "grano"] == "Una fila por mes, región y categoría"
    assert "dashboard_sales" in tables
    assert "serving_manifest" in "\n".join(cell.source for cell in notebook.cells)
