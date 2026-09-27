"""Funciones analíticas que alimentan el dashboard de campañas."""

from pathlib import Path

import pandas as pd


DATA_FILE = Path("data/campaign_data.csv")
SUMMARY_FILE = Path("submission/source_summary.csv")
REQUIRED_COLUMNS = {
    "utc_date",
    "traffic_source",
    "country",
    "template_name",
    "impressions",
    "paid_clicks",
    "revenue",
    "ad_spend",
}
NUMERIC_COLUMNS = ("impressions", "paid_clicks", "revenue", "ad_spend")


def load_campaign_data(input_file=DATA_FILE):
    data = pd.read_csv(input_file)
    missing_columns = REQUIRED_COLUMNS - set(data.columns)
    if missing_columns:
        raise ValueError(f"Faltan columnas requeridas: {', '.join(sorted(missing_columns))}.")

    data["utc_date"] = pd.to_datetime(data["utc_date"], errors="raise")
    for column in NUMERIC_COLUMNS:
        data[column] = pd.to_numeric(data[column], errors="raise")
    if (data[list(NUMERIC_COLUMNS)] < 0).any().any():
        raise ValueError("Las métricas de campaña no pueden ser negativas.")

    data["gross_profit"] = data["revenue"] - data["ad_spend"]
    return data


def safe_divide(numerator, denominator):
    return None if denominator == 0 else numerator / denominator


def filter_campaign_data(data, start_date, end_date, traffic_sources=None, countries=None):
    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)
    if start_date > end_date:
        raise ValueError("La fecha inicial no puede ser posterior a la fecha final.")

    filtered = data.loc[data["utc_date"].between(start_date, end_date)].copy()
    if traffic_sources is not None:
        filtered = filtered.loc[filtered["traffic_source"].isin(traffic_sources)].copy()
    if countries is not None:
        filtered = filtered.loc[filtered["country"].isin(countries)].copy()
    return filtered


def calculate_kpis(data):
    impressions = int(data["impressions"].sum())
    paid_clicks = int(data["paid_clicks"].sum())
    revenue = float(data["revenue"].sum())
    ad_spend = float(data["ad_spend"].sum())
    return {
        "impressions": impressions,
        "paid_clicks": paid_clicks,
        "revenue": revenue,
        "ad_spend": ad_spend,
        "gross_profit": revenue - ad_spend,
        "roas": safe_divide(revenue, ad_spend),
        "cpc": safe_divide(ad_spend, paid_clicks),
    }


def summarize_by_day(data):
    return (
        data.groupby("utc_date", as_index=False)
        .agg(
            revenue=("revenue", "sum"),
            ad_spend=("ad_spend", "sum"),
            gross_profit=("gross_profit", "sum"),
        )
        .sort_values("utc_date")
    )


def summarize_by_source(data):
    summary = (
        data.groupby("traffic_source", as_index=False)
        .agg(
            impressions=("impressions", "sum"),
            paid_clicks=("paid_clicks", "sum"),
            revenue=("revenue", "sum"),
            ad_spend=("ad_spend", "sum"),
            gross_profit=("gross_profit", "sum"),
        )
        .sort_values("gross_profit", ascending=False)
    )
    summary["roas"] = summary.apply(
        lambda row: safe_divide(row["revenue"], row["ad_spend"]), axis=1
    )
    summary["cpc"] = summary.apply(
        lambda row: safe_divide(row["ad_spend"], row["paid_clicks"]), axis=1
    )
    return summary


def summarize_by_campaign(data):
    return (
        data.groupby("template_name", as_index=False)
        .agg(
            impressions=("impressions", "sum"),
            paid_clicks=("paid_clicks", "sum"),
            revenue=("revenue", "sum"),
            ad_spend=("ad_spend", "sum"),
            gross_profit=("gross_profit", "sum"),
        )
        .sort_values("gross_profit", ascending=False)
    )


def create_source_summary(input_file=DATA_FILE, output_file=SUMMARY_FILE):
    data = load_campaign_data(input_file)
    summary = summarize_by_source(data)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(output_file, index=False)
    return summary
