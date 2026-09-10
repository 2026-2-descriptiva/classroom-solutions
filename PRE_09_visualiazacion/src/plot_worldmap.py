import os

import folium  # type: ignore
import pandas as pd  # type: ignore

INPUT_FILE = "https://raw.githubusercontent.com/jdvelasq/datalabs/master/datasets/scopus-papers.csv"
GEO_DATA_URL = "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/world-countries.json"

OUTPUT_DIR = "PRE_09_visualiazacion/temp"
COUNTRY_FREQUENCY_FILE = f"{OUTPUT_DIR}/countries.csv"
WORLD_MAP_FILE = f"{OUTPUT_DIR}/map.html"


def _load_affiliations():

    dataframe = pd.read_csv(
        INPUT_FILE,
        sep=",",
        index_col=None,
    )[["Affiliations"]]
    return dataframe


def _remove_na_rows(affiliations):
    return affiliations.dropna(subset=["Affiliations"])


def _create_countries_column(affiliations):

    affiliations = affiliations.copy()
    affiliations["countries"] = affiliations["Affiliations"].copy()
    affiliations["countries"] = affiliations["countries"].str.split(";")
    affiliations["countries"] = affiliations["countries"].map(
        lambda x: [y.split(",") for y in x]
    )
    affiliations["countries"] = affiliations["countries"].map(
        lambda x: [y[-1].strip() for y in x]
    )
    affiliations["countries"] = affiliations["countries"].map(set)
    affiliations["countries"] = affiliations["countries"].str.join(", ")

    return affiliations


def _clean_countries(affiliations):
    affiliations["countries"] = affiliations["countries"].str.replace(
        "United States", "United States of America"
    )
    return affiliations


def _count_country_frequency(affiliations):

    countries = affiliations["countries"].copy()
    countries = countries.str.split(", ")
    countries = countries.explode()
    countries = countries.value_counts()
    #
    countries.to_csv(COUNTRY_FREQUENCY_FILE)
    #
    return countries


def _make_worldmap(countries):

    countries = countries.copy()
    countries = countries.to_frame()
    countries = countries.reset_index()

    m = folium.Map(location=[0, 0], zoom_start=2)

    folium.Choropleth(
        geo_data=GEO_DATA_URL,
        data=countries,
        columns=["countries", "count"],
        key_on="feature.properties.name",
        fill_color="Greens",
    ).add_to(m)

    m.save(WORLD_MAP_FILE)


def plot_worldmap():

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    affiliations = _load_affiliations()
    affiliations = _remove_na_rows(affiliations)
    affiliations = _create_countries_column(affiliations)
    affiliations = _clean_countries(affiliations)

    countries = _count_country_frequency(affiliations)

    _make_worldmap(countries)


if __name__ == "__main__":
    plot_worldmap()
