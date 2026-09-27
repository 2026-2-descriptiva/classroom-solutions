"""Diagnóstico de indicadores de ventas y devoluciones."""

from pathlib import Path

import pandas as pd


ACTIVITY_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = ACTIVITY_DIR / "data" / "sales.csv"
SUBMISSION_DIR = ACTIVITY_DIR / "submission"


def diagnose_kpis() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Diagnostique el desempeño comercial de ``data/sales.csv`` y genere tres
    archivos persistentes en ``submission/``:

    - ``kpi_summary.csv`` con una fila y las columnas ``orders``,
      ``customers``, ``gross_sales``, ``returned_amount``, ``net_sales``,
      ``return_rate_by_orders``, ``return_rate_by_value`` y
      ``net_sales_per_order``.
    - ``category_summary.csv`` con una fila por ``Category`` y las columnas
      ``orders``, ``gross_sales``, ``returned_amount``, ``net_sales`` y
      ``return_rate``. Ordénelo por ``net_sales`` de mayor a menor.
    - ``priority_segments.csv`` con los cinco segmentos categoría–canal que
      se deben priorizar para investigar y reducir devoluciones. Considere
      solamente segmentos con al menos 50 órdenes y ordénelos por
      ``returned_amount`` de mayor a menor. Incluya ``Category``,
      ``SalesChannel``, ``orders``, ``gross_sales``, ``returned_amount`` y
      ``return_rate``.

    Para calcular los indicadores, derive ``returned_amount`` como el valor
    total de una orden devuelta y cero en otro caso. La venta neta es la venta
    bruta menos el valor devuelto. El diagnóstico debe mantener separados el
    volumen de devoluciones y su tasa: un segmento se prioriza por impacto en
    dinero, no solamente por porcentaje.
    """
    sales = pd.read_csv(DATA_FILE)
    sales["returned_amount"] = sales["TotalAmount"].where(sales["IsReturned"].eq(1), 0)
    sales["net_sales"] = sales["TotalAmount"] - sales["returned_amount"]

    kpi_summary = pd.DataFrame(
        {
            "orders": [sales["OrderID"].nunique()],
            "customers": [sales["CustomerID"].nunique()],
            "gross_sales": [sales["TotalAmount"].sum()],
            "returned_amount": [sales["returned_amount"].sum()],
            "net_sales": [sales["net_sales"].sum()],
        }
    )
    kpi_summary["return_rate_by_orders"] = sales["IsReturned"].mean()
    kpi_summary["return_rate_by_value"] = (
        kpi_summary["returned_amount"] / kpi_summary["gross_sales"]
    )
    kpi_summary["net_sales_per_order"] = kpi_summary["net_sales"] / kpi_summary["orders"]

    category_summary = (
        sales.groupby("Category")
        .agg(
            orders=("OrderID", "size"),
            gross_sales=("TotalAmount", "sum"),
            returned_amount=("returned_amount", "sum"),
            net_sales=("net_sales", "sum"),
            return_rate=("IsReturned", "mean"),
        )
        .reset_index()
        .sort_values("net_sales", ascending=False)
    )

    priority_segments = (
        sales.groupby(["Category", "SalesChannel"])
        .agg(
            orders=("OrderID", "size"),
            gross_sales=("TotalAmount", "sum"),
            returned_amount=("returned_amount", "sum"),
            return_rate=("IsReturned", "mean"),
        )
        .reset_index()
    )
    priority_segments = priority_segments[priority_segments["orders"] >= 50]
    priority_segments = priority_segments.nlargest(5, "returned_amount")

    SUBMISSION_DIR.mkdir(exist_ok=True)
    kpi_summary.to_csv(SUBMISSION_DIR / "kpi_summary.csv", index=False)
    category_summary.to_csv(SUBMISSION_DIR / "category_summary.csv", index=False)
    priority_segments.to_csv(SUBMISSION_DIR / "priority_segments.csv", index=False)

    return kpi_summary, category_summary, priority_segments
    # raise NotImplementedError


if __name__ == "__main__":
    diagnose_kpis()
