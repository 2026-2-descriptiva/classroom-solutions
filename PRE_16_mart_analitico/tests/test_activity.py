"""Verificaciones del taller de mart analítico."""

import sqlite3
from pathlib import Path

import nbformat
import pandas as pd
import pytest


@pytest.fixture(autouse=True)
def require_developed_solution():
    """Omite la evaluación hasta que exista el entregable de la solución."""
    if not (Path(__file__).resolve().parents[1] / "submission/sales_mart.db").is_file():
        pytest.skip("La solución aún no ha publicado submission/sales_mart.db.")


def test_mart_preserves_the_fact_grain_and_dimensions():
    source = pd.read_csv("data/order_lines.csv")
    with sqlite3.connect("submission/sales_mart.db") as connection:
        fact = pd.read_sql_query("SELECT * FROM fact_sales", connection)
        tables = pd.read_sql_query(
            "SELECT name FROM sqlite_master WHERE type='table'", connection
        )["name"].tolist()

    assert len(fact) == len(source)
    assert not fact[["order_id", "line_id"]].duplicated().any()
    assert {"fact_sales", "dim_date", "dim_customer", "dim_product"}.issubset(tables)


def test_notebook_makes_fact_and_dimension_design_explicit():
    notebook = nbformat.read("notebooks/notebook.ipynb", as_version=4)
    source = "\n".join(cell.source for cell in notebook.cells)

    assert all(cell.cell_type == "code" for cell in notebook.cells)
    assert "fact_sales" in source
    assert "dim_date" in source
