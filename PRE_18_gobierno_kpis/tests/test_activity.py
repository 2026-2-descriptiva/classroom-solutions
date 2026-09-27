"""Verificaciones del taller de gobierno de KPI."""

from pathlib import Path

import nbformat
import pandas as pd
import pytest


@pytest.fixture(autouse=True)
def require_developed_solution():
    """Omite la evaluación hasta que exista el entregable de la solución."""
    required_files = (
        "submission/kpi_catalog.csv",
        "submission/kpi_quality_report.csv",
        "submission/metric_lineage.csv",
        "submission/kpi_publication_decision.csv",
    )
    activity_dir = Path(__file__).resolve().parents[1]
    if any(not (activity_dir / file_name).is_file() for file_name in required_files):
        pytest.skip("La solución aún no ha publicado los artefactos de gobierno de KPI.")


def test_kpi_governance_artifacts_are_publishable():
    catalog = pd.read_csv("submission/kpi_catalog.csv")
    checks = pd.read_csv("submission/kpi_quality_report.csv")
    decision = pd.read_csv("submission/kpi_publication_decision.csv")

    assert catalog.shape[0] == 3
    assert {"grano", "propietario", "fuente"}.issubset(catalog.columns)
    assert checks["estado"].eq("PASS").all()
    assert decision.loc[0, "estado"] == "APROBADO"


def test_notebook_keeps_definition_quality_and_lineage_together():
    notebook = nbformat.read("notebooks/notebook.ipynb", as_version=4)
    source = "\n".join(cell.source for cell in notebook.cells)

    for concept in ["kpi_catalog", "quality_checks", "metric_lineage"]:
        assert concept in source
