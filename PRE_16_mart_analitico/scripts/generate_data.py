"""Genera fuentes operativas y un mart de ventas para los talleres de BI."""

from pathlib import Path
import sqlite3

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def make_sources():
    """Crea fuentes operativas pequeñas y reproducibles de ventas."""
    rng = np.random.default_rng(20260926)
    customers = pd.DataFrame(
        {
            "customer_id": range(1, 61),
            "region": np.repeat(["Norte", "Centro", "Sur"], 20),
            "segment": np.tile(["Corporativo", "Pyme", "Hogar"], 20),
        }
    )
    products = pd.DataFrame(
        {
            "product_id": range(1, 13),
            "product": [f"Producto {number}" for number in range(1, 13)],
            "category": ["Tecnología"] * 4 + ["Oficina"] * 4 + ["Servicios"] * 4,
            "unit_price": [780, 640, 510, 460, 350, 290, 240, 180, 920, 730, 610, 490],
        }
    )
    records = []
    for order_id in range(1, 241):
        order_date = pd.Timestamp("2024-01-01") + pd.Timedelta(days=(order_id * 3) % 365)
        customer_id = int(rng.integers(1, 61))
        for line_id in range(1, int(rng.integers(2, 5))):
            product_id = int(rng.integers(1, 13))
            quantity = int(rng.integers(1, 6))
            discount_pct = float(rng.choice([0, 0.05, 0.10], p=[0.55, 0.30, 0.15]))
            records.append(
                [order_id, line_id, order_date.strftime("%Y-%m-%d"), customer_id, product_id, quantity, discount_pct]
            )
    order_lines = pd.DataFrame(
        records,
        columns=["order_id", "line_id", "order_date", "customer_id", "product_id", "quantity", "discount_pct"],
    )
    return customers, products, order_lines


def build_mart(customers, products, order_lines):
    """Construye un mart estrella mínimo a partir de las fuentes operativas."""
    facts = order_lines.merge(products[["product_id", "unit_price"]], on="product_id", validate="many_to_one")
    facts["order_date"] = pd.to_datetime(facts["order_date"])
    facts["gross_sales"] = facts["quantity"] * facts["unit_price"]
    facts["net_sales"] = facts["gross_sales"] * (1 - facts["discount_pct"])
    dim_date = pd.DataFrame({"date": sorted(facts["order_date"].unique())})
    dim_date["date_key"] = range(1, len(dim_date) + 1)
    dim_date["date"] = pd.to_datetime(dim_date["date"])
    dim_date["year"] = dim_date["date"].dt.year
    dim_date["month"] = dim_date["date"].dt.month
    dim_customer = customers.assign(customer_key=customers["customer_id"])
    dim_product = products.assign(product_key=products["product_id"])
    fact_sales = (
        facts.merge(dim_date[["date", "date_key"]], left_on="order_date", right_on="date")
        [["order_id", "line_id", "date_key", "customer_id", "product_id", "quantity", "gross_sales", "discount_pct", "net_sales"]]
        .rename(columns={"customer_id": "customer_key", "product_id": "product_key"})
    )
    return dim_date, dim_customer, dim_product, fact_sales


def main():
    """Escribe fuentes y mart de referencia en la carpeta data."""
    DATA.mkdir(exist_ok=True)
    customers, products, order_lines = make_sources()
    customers.to_csv(DATA / "customers.csv", index=False)
    products.to_csv(DATA / "products.csv", index=False)
    order_lines.to_csv(DATA / "order_lines.csv", index=False)
    dim_date, dim_customer, dim_product, fact_sales = build_mart(customers, products, order_lines)
    with sqlite3.connect(DATA / "sales_mart.db") as connection:
        dim_date.to_sql("dim_date", connection, index=False, if_exists="replace")
        dim_customer.to_sql("dim_customer", connection, index=False, if_exists="replace")
        dim_product.to_sql("dim_product", connection, index=False, if_exists="replace")
        fact_sales.to_sql("fact_sales", connection, index=False, if_exists="replace")


if __name__ == "__main__":
    main()
