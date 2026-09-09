import os


def test_01():

    assert os.path.exists("PRE_08_analisis_chatgpt/data/output/summary.csv")
    assert os.path.exists("PRE_08_analisis_chatgpt/data/plots/top10_drivers.png")
