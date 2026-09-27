"""Genera datos sintéticos para el taller de diagnóstico salarial."""

from pathlib import Path

import numpy as np
import pandas as pd


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "salarios.csv"
RANDOM_SEED = 20260925

DEPARTMENTS = {
    "Finanzas": ["Tesorería", "Planeación financiera"],
    "Talento": ["Recursos humanos"],
    "Comercial": ["Clientes mayoristas", "Clientes menores"],
    "Operaciones": ["Operaciones", "Tecnología"],
}
DEPARTMENT_PROBABILITIES = [0.13, 0.12, 0.12, 0.16, 0.14, 0.18, 0.15]
DEPARTMENT_ADJUSTMENTS = {
    "Tesorería": -700_000,
    "Planeación financiera": 150_000,
    "Recursos humanos": -300_000,
    "Clientes mayoristas": 250_000,
    "Clientes menores": -950_000,
    "Operaciones": -100_000,
    "Tecnología": 500_000,
}
CATEGORY_BASE_SALARY = {
    "Analista": 3_400_000,
    "Profesional": 5_000_000,
    "Especialista": 7_200_000,
    "Senior": 10_200_000,
    "Principal": 14_000_000,
}


def generate_salary_data(n_employees=1_000, random_seed=RANDOM_SEED):
    """Crea una población salarial ficticia con brechas y carreras técnicas."""
    rng = np.random.default_rng(random_seed)
    departments = [department for values in DEPARTMENTS.values() for department in values]
    department_to_management = {
        department: management
        for management, values in DEPARTMENTS.items()
        for department in values
    }
    department = rng.choice(
        departments, size=n_employees, p=DEPARTMENT_PROBABILITIES
    )
    career_path = rng.choice(
        ["Técnica", "Directiva"], size=n_employees, p=[0.78, 0.22]
    )

    category = []
    for path in career_path:
        if path == "Técnica":
            category.append(
                rng.choice(
                    ["Analista", "Profesional", "Especialista", "Senior", "Principal"],
                    p=[0.18, 0.28, 0.27, 0.19, 0.08],
                )
            )
        else:
            category.append(
                rng.choice(
                    ["Profesional", "Especialista", "Senior", "Principal"],
                    p=[0.08, 0.22, 0.43, 0.27],
                )
            )

    category = np.array(category)
    minimum_experience = pd.Series(category).map(
        {"Analista": 0, "Profesional": 2, "Especialista": 5, "Senior": 8, "Principal": 12}
    ).to_numpy()
    technical_experience = np.maximum(
        minimum_experience,
        np.rint(rng.normal(minimum_experience + 4, 3, size=n_employees)).astype(int),
    )
    technical_experience = np.clip(technical_experience, 0, 35)

    base_salary = pd.Series(category).map(CATEGORY_BASE_SALARY).to_numpy(dtype=float)
    management_premium = np.where(career_path == "Directiva", 1_800_000, 0)
    experience_premium = technical_experience * 240_000
    department_adjustment = pd.Series(department).map(DEPARTMENT_ADJUSTMENTS).to_numpy()
    variability = rng.normal(0, 350_000, size=n_employees)
    monthly_salary = (
        base_salary
        + management_premium
        + experience_premium
        + department_adjustment
        + variability
    )

    return pd.DataFrame(
        {
            "employee_id": [f"E{number:04d}" for number in range(1, n_employees + 1)],
            "gerencia": [department_to_management[value] for value in department],
            "departamento": department,
            "trayectoria": career_path,
            "categoria": category,
            "experiencia_tecnica_anios": technical_experience,
            "salario_mensual_cop": np.rint(monthly_salary).astype(int),
        }
    )


def main():
    """Genera el archivo de datos permanente del taller."""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    generate_salary_data().to_csv(DATA_FILE, index=False)


if __name__ == "__main__":
    main()
