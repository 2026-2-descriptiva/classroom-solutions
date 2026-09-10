import pandas as pd

INPUT_FILE = "PRE_04_limpieza/data/ventas.csv"
OUTPUT_FILE = "PRE_04_limpieza/submission/ventas.csv"


def print_collisions(series, fn):
    df = pd.DataFrame(series)
    df["collision_key"] = df.iloc[:, 0].apply(fn)
    df = df.groupby("collision_key").filter(lambda x: len(x) > 1)

    for collision_key, group in df.groupby("collision_key"):
        print()
        print(f"{collision_key}")
        for value in group.iloc[:, 0]:
            print(f"  {value}")

    print()


def fn(x):
    x = x.lower().strip().replace(".", "")
    x = (
        x.replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
        .replace("ñ", "n")
        .replace("Á", "a")
        .replace("É", "e")
        .replace("Í", "i")
        .replace("Ó", "o")
        .replace("Ú", "u")
        .replace("Ñ", "n")
    )
    return x


def print_by_length(series):
    df = pd.DataFrame(series)
    df["length"] = df.iloc[:, 0].apply(len)
    df = df.sort_values("length")

    for length, group in df.groupby("length"):
        print()
        print(f"{length}")
        for value in group.iloc[:, 0]:
            print(f"  {value}")

    print()


def main():
    df = pd.read_csv(OUTPUT_FILE)
    series = df["supplier"]
    series = series.drop_duplicates()
    series = series.sort_values()
    #
    # print_collisions(series, fn)
    # print_by_length(series)

    #
    print(series)


if __name__ == "__main__":
    main()
