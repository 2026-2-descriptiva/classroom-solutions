import os

FOLDER = "PRE_08_analisis_chatgpt"


def test_01():

    assert os.path.exists(f"{FOLDER}/data/output/summary.csv")
    assert os.path.exists(f"{FOLDER}/data/plots/top10_drivers.png")
