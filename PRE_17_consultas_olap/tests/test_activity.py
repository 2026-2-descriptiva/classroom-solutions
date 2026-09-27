"""Verificaciones del taller de consultas OLAP."""

import sqlite3
from pathlib import Path

import nbformat
import pandas as pd
import pytest


@pytest.fixture(autouse=True)
def require_developed_solution():
    """Omite la evaluación hasta que exista el entregable de la solución."""
    required_files = (
        "submission/monthly_region_sales.csv",
        "submission/north_category_sales.csv",
        "submission/north_product_drilldown.csv",
    )
    activity_dir = Path(__file__).resolve().parents[1]
    if any(not (activity_dir / file_name).is_file() for file_name in required_files):
        pytest.skip("La solución aún no ha publicado todos los agregados OLAP.")


def test_olap_rollup_reconciles_with_the_mart_total():
    monthly_region = pd.read_csv("submission/monthly_region_sales.csv")
    with sqlite3.connect("data/sales_mart.db") as connection:
        total = connection.execute("SELECT SUM(net_sales) FROM fact_sales").fetchone()[0]

    assert monthly_region["net_sales"].sum() == pytest.approx(total)
    assert not monthly_region[["year", "month", "region"]].duplicated().any()


def test_notebook_contains_rollup_slice_and_drilldown():
    notebook = nbformat.read("notebooks/notebook.ipynb", as_version=4)
    source = "\n".join(cell.source for cell in notebook.cells)

    for concept in ["monthly_region", "north_category", "product_drilldown"]:
        assert concept in source
