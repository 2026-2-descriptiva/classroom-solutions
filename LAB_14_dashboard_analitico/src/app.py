"""Interfaz Streamlit para explorar el desempeño de campañas."""

import plotly.express as px
import streamlit as st

try:
    from .pregunta_01 import (
        DATA_FILE,
        calculate_kpis,
        filter_campaign_data,
        load_campaign_data,
        summarize_by_campaign,
        summarize_by_day,
        summarize_by_source,
    )
except ImportError:  # Permite ejecutar `streamlit run src/app.py`.
    from pregunta_01 import (
        DATA_FILE,
        calculate_kpis,
        filter_campaign_data,
        load_campaign_data,
        summarize_by_campaign,
        summarize_by_day,
        summarize_by_source,
    )


@st.cache_data
def get_campaign_data():
    return load_campaign_data(DATA_FILE)


def format_currency(value):
    return "No disponible" if value is None else f"USD {value:,.2f}"


def main():
    st.set_page_config(page_title="Dashboard de campañas", layout="wide")
    st.title("Desempeño de campañas de marketing")

    data = get_campaign_data()
    minimum_date = data["utc_date"].min().date()
    maximum_date = data["utc_date"].max().date()
    with st.sidebar:
        st.header("Filtros")
        selected_dates = st.date_input(
            "Período", (minimum_date, maximum_date), minimum_date, maximum_date
        )
        selected_sources = st.multiselect(
            "Fuente de tráfico", sorted(data["traffic_source"].unique()),
            default=sorted(data["traffic_source"].unique()),
        )
        selected_countries = st.multiselect(
            "País", sorted(data["country"].unique()),
            default=sorted(data["country"].unique()),
        )

    if len(selected_dates) != 2:
        st.info("Seleccione una fecha inicial y una fecha final.")
        st.stop()
    filtered = filter_campaign_data(
        data, selected_dates[0], selected_dates[1], selected_sources, selected_countries
    )
    if filtered.empty:
        st.warning("Los filtros seleccionados no contienen campañas.")
        st.stop()

    kpis = calculate_kpis(filtered)
    columns = st.columns(5)
    columns[0].metric("Utilidad bruta", format_currency(kpis["gross_profit"]))
    columns[1].metric("Ingreso", format_currency(kpis["revenue"]))
    columns[2].metric("Inversión", format_currency(kpis["ad_spend"]))
    columns[3].metric("ROAS", f"{kpis['roas']:.2f}" if kpis["roas"] is not None else "No disponible")
    columns[4].metric("CPC", format_currency(kpis["cpc"]))

    daily = summarize_by_day(filtered)
    st.plotly_chart(px.line(daily, x="utc_date", y="gross_profit", markers=True,
        title="Utilidad bruta diaria"), width="stretch")
    sources = summarize_by_source(filtered)
    st.plotly_chart(px.bar(sources, x="gross_profit", y="traffic_source", orientation="h",
        title="Utilidad bruta por fuente"), width="stretch")
    st.subheader("Detalle por campaña")
    st.dataframe(summarize_by_campaign(filtered), width="stretch", hide_index=True)


if __name__ == "__main__":
    main()
