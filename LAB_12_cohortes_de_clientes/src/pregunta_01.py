"""Análisis de cohortes de clientes."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


ACTIVITY_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = ACTIVITY_DIR / "data" / "sales.csv"
SUBMISSION_DIR = ACTIVITY_DIR / "submission"


def build_cohort_analysis() -> pd.DataFrame:
    """
    Analice la retención mensual de clientes a partir de ``data/sales.csv``.

    Genere dos entregables en ``submission/``:

    - ``cohort_retention.csv`` con las columnas ``cohort_month``,
      ``period_index``, ``active_customers``, ``cohort_size`` y
      ``retention_rate``.
    - ``cohort_retention_heatmap.png``, un mapa de calor de la tasa de
      retención: una fila por cohorte y una columna por meses transcurridos
      desde la primera compra.

    Defina ``cohort_month`` como el mes de la primera compra de cada cliente.
    ``period_index`` es cero en ese primer mes, uno en el siguiente, y así
    sucesivamente. ``active_customers`` es el número de clientes distintos
    que compraron en cada combinación cohorte–período. ``cohort_size`` es el
    número de clientes de la cohorte en el período cero. Finalmente,
    ``retention_rate`` es ``active_customers / cohort_size``.

    El mapa debe mostrar porcentajes, identificar los meses de cohorte en el
    eje vertical y los meses desde la adquisición en el horizontal. Las celdas
    sin período observado no representan retención cero y deben mostrarse como
    ausentes, no como valores observados.
    """
    sales = pd.read_csv(DATA_FILE, parse_dates=["OrderDate"])
    sales["order_month"] = sales["OrderDate"].dt.to_period("M")
    sales["cohort_month"] = sales.groupby("CustomerID")["order_month"].transform(
        "min"
    )
    sales["period_index"] = (
        sales["order_month"].astype("int64")
        - sales["cohort_month"].astype("int64")
    )

    cohort_retention = (
        sales.groupby(["cohort_month", "period_index"])["CustomerID"]
        .nunique()
        .rename("active_customers")
        .reset_index()
    )
    cohort_sizes = cohort_retention[cohort_retention["period_index"].eq(0)][
        ["cohort_month", "active_customers"]
    ].rename(columns={"active_customers": "cohort_size"})
    cohort_retention = cohort_retention.merge(cohort_sizes, on="cohort_month")
    cohort_retention["retention_rate"] = (
        cohort_retention["active_customers"] / cohort_retention["cohort_size"]
    )
    cohort_retention = cohort_retention.sort_values(
        ["cohort_month", "period_index"]
    ).reset_index(drop=True)

    retention_matrix = cohort_retention.pivot(
        index="cohort_month", columns="period_index", values="retention_rate"
    )
    figure, axis = plt.subplots(figsize=(10, 6))
    image = axis.imshow(retention_matrix, cmap="YlOrRd", vmin=0, vmax=1, aspect="auto")
    axis.set_title("Retención mensual por cohorte de clientes")
    axis.set_xlabel("Meses desde la primera compra")
    axis.set_ylabel("Mes de primera compra")
    axis.set_xticks(range(len(retention_matrix.columns)))
    axis.set_xticklabels(retention_matrix.columns)
    axis.set_yticks(range(len(retention_matrix.index)))
    axis.set_yticklabels(retention_matrix.index.astype(str))
    colorbar = figure.colorbar(image, ax=axis, label="Tasa de retención")
    colorbar.ax.yaxis.set_major_formatter("{x:.0%}")

    for row_index, cohort_month in enumerate(retention_matrix.index):
        for column_index, period_index in enumerate(retention_matrix.columns):
            value = retention_matrix.loc[cohort_month, period_index]
            if pd.notna(value):
                axis.text(
                    column_index,
                    row_index,
                    f"{value:.0%}",
                    ha="center",
                    va="center",
                    color="white" if value >= 0.5 else "black",
                )

    figure.tight_layout()
    SUBMISSION_DIR.mkdir(exist_ok=True)
    cohort_retention.assign(cohort_month=cohort_retention["cohort_month"].astype(str)).to_csv(
        SUBMISSION_DIR / "cohort_retention.csv", index=False
    )
    figure.savefig(SUBMISSION_DIR / "cohort_retention_heatmap.png", dpi=150)
    plt.close(figure)

    return cohort_retention
    # raise NotImplementedError


if __name__ == "__main__":
    build_cohort_analysis()
