import os


def test_01():

    assert os.path.exists("PRE_06_analisis_pandas/data/output/summary.csv")
    assert os.path.exists("PRE_06_analisis_pandas/data/plots/top10_drivers.png")
