from pathlib import Path

import pandas as pd


def pregunta_01():
    """
    Construya dos tablas de texto a partir de los directorios `data/train/`
    y `data/test/`. Cada división contiene las carpetas `negative`,
    `neutral` y `positive`; cada archivo `.txt` representa una frase.

    Genere los archivos permanentes:

    - `submission/train_dataset.csv`
    - `submission/test_dataset.csv`

    Ambos archivos deben tener las columnas `phrase` y `target`. `phrase`
    contiene el texto de cada archivo y `target` corresponde al nombre de su
    carpeta de sentimiento. Procese las carpetas y archivos en orden
    alfabético para producir resultados reproducibles.

    El archivo CSV resultante debe tener una estructura como esta:

    ```csv
    phrase,target
    "Operating profit increased during the period",positive
    "The company operates in Finland",neutral
    "Sales decreased compared with last year",negative
    ```
    """
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data"
    submission_dir = root / "submission"
    submission_dir.mkdir(exist_ok=True)

    datasets = {}
    for split in ("train", "test"):
        records = []
        for target_dir in sorted((data_dir / split).iterdir()):
            for text_file in sorted(target_dir.glob("*.txt")):
                records.append(
                    {
                        "phrase": text_file.read_text(encoding="utf-8").strip(),
                        "target": target_dir.name,
                    }
                )
        dataset = pd.DataFrame(records, columns=["phrase", "target"])
        dataset.to_csv(submission_dir / f"{split}_dataset.csv", index=False)
        datasets[split] = dataset

    return datasets["train"], datasets["test"]
    # raise NotImplementedError
