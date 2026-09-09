import os


def test_01():

    assert os.path.exists("PRE_07_analisis_sqlite/data/output/summary.csv")
    assert os.path.exists("PRE_07_analisis_sqlite/data/plots/top10_drivers.png")
