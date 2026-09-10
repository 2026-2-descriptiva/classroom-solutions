import os

import matplotlib.pyplot as plt  # type: ignore
import networkx as nx  # type: ignore

try:
    from .plot_worldmap import (
        OUTPUT_DIR,
        _clean_countries,
        _count_country_frequency,
        _create_countries_column,
        _load_affiliations,
        _remove_na_rows,
    )
except ImportError:
    from plot_worldmap import (
        OUTPUT_DIR,
        _clean_countries,
        _count_country_frequency,
        _create_countries_column,
        _load_affiliations,
        _remove_na_rows,
    )

CO_OCCURRENCES_FILE = f"{OUTPUT_DIR}/co_occurrences.csv"
NETWORK_FILE = f"{OUTPUT_DIR}/network.png"


def _select_most_frequent_countries(countries, n_countries):
    return countries.head(n_countries)


def _compute_co_occurrences(affiliations, most_frequent_countries):

    affiliations = affiliations.copy()
    co_occurrences = affiliations[["countries"]].copy()
    co_occurrences = co_occurrences.rename(columns={"countries": "node_a"})
    co_occurrences["node_b"] = co_occurrences["node_a"]

    co_occurrences["node_a"] = co_occurrences["node_a"].str.split(", ")
    co_occurrences = co_occurrences.explode("node_a")
    co_occurrences = co_occurrences[
        co_occurrences["node_a"].isin(most_frequent_countries.index)
    ]

    co_occurrences["node_b"] = co_occurrences["node_b"].str.split(", ")
    co_occurrences = co_occurrences.explode("node_b")
    co_occurrences = co_occurrences[
        co_occurrences["node_b"].isin(most_frequent_countries.index)
    ]

    co_occurrences = co_occurrences[
        co_occurrences["node_a"] != co_occurrences["node_b"]
    ]
    co_occurrences = co_occurrences[co_occurrences["node_a"] > co_occurrences["node_b"]]

    co_occurrences = co_occurrences.groupby(
        ["node_a", "node_b"],
        as_index=False,
    ).size()

    #
    co_occurrences.to_csv(CO_OCCURRENCES_FILE)
    #

    return co_occurrences


def _make_network(countries, co_occurrences):

    G = nx.Graph()

    for _, row in co_occurrences.iterrows():
        G.add_edge(row["node_a"], row["node_b"], weight=row["size"])

    pos = nx.spring_layout(G)

    countries_list = list(G)
    node_size = countries[countries_list].values

    nx.draw(
        G,
        pos,
        with_labels=False,
        node_size=node_size,
        node_color="grey",
        edge_color="lightgrey",
        font_size=8,
        alpha=0.4,
    )

    for country, (x, y) in pos.items():
        # x, y = pos[country]
        plt.text(x, y, country, fontsize=7, ha="center", va="center")

    plt.savefig(NETWORK_FILE)


def plot_collaboration_network(n_countries):

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    affiliations = _load_affiliations()
    affiliations = _remove_na_rows(affiliations)
    affiliations = _create_countries_column(affiliations)
    affiliations = _clean_countries(affiliations)

    countries_frequency = _count_country_frequency(affiliations)
    most_frequent_countries = _select_most_frequent_countries(
        countries_frequency, n_countries
    )
    co_occurrences = _compute_co_occurrences(
        affiliations,
        most_frequent_countries,
    )
    _make_network(most_frequent_countries, co_occurrences)


if __name__ == "__main__":
    plot_collaboration_network(n_countries=20)
