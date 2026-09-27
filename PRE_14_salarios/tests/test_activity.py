"""Verificaciones del caso sintético de diagnóstico salarial."""

import nbformat
import pandas as pd


DATA_FILE = "data/salarios.csv"
NOTEBOOK_FILE = "notebooks/notebook.ipynb"


def test_01_salary_data_represents_the_required_organization():
    """La población contiene mil profesionales y los niveles organizacionales."""
    salaries = pd.read_csv(DATA_FILE)

    assert salaries.shape == (1_000, 7)
    assert salaries["gerencia"].nunique() == 4
    assert salaries["departamento"].nunique() == 7
    assert set(salaries["trayectoria"]) == {"Técnica", "Directiva"}
    assert salaries["salario_mensual_cop"].gt(0).all()


def test_02_case_contains_a_detectable_internal_pay_gap():
    """El caso permite identificar áreas con remuneración inferior a sus pares."""
    salaries = pd.read_csv(DATA_FILE)
    salaries["banda_experiencia"] = pd.cut(
        salaries["experiencia_tecnica_anios"],
        bins=[-1, 4, 9, 14, 100],
        labels=["0-4", "5-9", "10-14", "15+"],
    )
    peer_median = salaries.groupby(
        ["categoria", "trayectoria", "banda_experiencia"], observed=True
    )["salario_mensual_cop"].transform("median")
    salaries["brecha_vs_pares_pct"] = salaries["salario_mensual_cop"] / peer_median - 1
    department_gap = salaries.groupby("departamento")["brecha_vs_pares_pct"].median()

    assert department_gap.loc["Tesorería"] < -0.05
    assert department_gap.loc["Clientes menores"] < -0.05


def test_03_notebook_is_a_live_teaching_notebook_for_the_two_decisions():
    """El notebook usa solo código y cubre brecha, carrera técnica y privacidad."""
    notebook = nbformat.read(NOTEBOOK_FILE, as_version=4)
    assert all(cell.cell_type == "code" for cell in notebook.cells)

    source = "\n".join(cell.source for cell in notebook.cells)
    for concept in [
        "brecha_vs_pares_pct",
        "areas_a_revisar",
        "salario_alto",
        "technical_high_salary",
        "minimum_group_size",
        "compensation_recommendations.csv",
    ]:
        assert concept in source
