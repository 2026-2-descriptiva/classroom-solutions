"""Anonimización de registros de clientes."""

import hashlib
import hmac
from pathlib import Path

import pandas as pd


ACTIVITY_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ACTIVITY_DIR / "data"
SUBMISSION_FILE = ACTIVITY_DIR / "submission" / "anonymized.csv"
SECRET_KEY = b"clave-secreta-del-programa"

CITY_TO_DEPARTMENT = {
    "Medellín": "Antioquia",
    "Bello": "Antioquia",
    "Envigado": "Antioquia",
    "Itagüí": "Antioquia",
    "Rionegro": "Antioquia",
    "Bogotá": "Bogotá D.C.",
    "Cali": "Valle del Cauca",
    "Barranquilla": "Atlántico",
    "Manizales": "Caldas",
    "Pereira": "Risaralda",
    "Cartagena": "Bolívar",
    "Bucaramanga": "Santander",
}

DEPARTMENT_TO_REGION = {
    "Antioquia": "Andina",
    "Bogotá D.C.": "Andina",
    "Caldas": "Andina",
    "Risaralda": "Andina",
    "Santander": "Andina",
    "Atlántico": "Caribe",
    "Bolívar": "Caribe",
    "Valle del Cauca": "Pacífica",
}

OCCUPATION_TO_GROUP = {
    "Administradora": "Servicios profesionales",
    "Abogada": "Servicios profesionales",
    "Analista financiera": "Servicios profesionales",
    "Contadora": "Servicios profesionales",
    "Arquitecta": "Tecnología y diseño",
    "Diseñadora gráfica": "Tecnología y diseño",
    "Ingeniero de sistemas": "Tecnología y diseño",
    "Médico": "Salud y educación",
    "Enfermera": "Salud y educación",
    "Docente": "Salud y educación",
    "Comerciante": "Comercio y oficios",
    "Técnico electricista": "Comercio y oficios",
}


def pseudonymize(document_id: object) -> str:
    """Crea un identificador estable que no revela el documento original."""
    digest = hmac.new(
        SECRET_KEY,
        str(document_id).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"CUST-{digest[:12].upper()}"


def anonymize_customers() -> pd.DataFrame:
    """
    Construya ``submission/anonymized.csv`` a partir de ``data/raw.csv``.

    El archivo publicado debe conservar únicamente ``loyalty_card_number``,
    ``annual_spend``, ``customer_id``, ``age_group``, ``region`` y
    ``occupation_group``. No incluya ``name``, ``document_id`` ni ``email``.

    Aplique las siguientes medidas:

    - Enmascare ``loyalty_card_number``: conserve solamente sus últimos cuatro
      dígitos y reemplace los demás por ocho asteriscos.
    - Cree ``customer_id`` seudonimizando ``document_id`` mediante HMAC-SHA256
      y la clave ``clave-secreta-del-programa``. Use el prefijo ``CUST-`` y los
      primeros doce caracteres hexadecimales en mayúscula.
    - Reemplace ``age`` por los grupos ``20-29``, ``30-39``, ``40-49``,
      ``50-59`` y ``60-69``.
    - Generalice ``city`` a ``region`` mediante departamento: Antioquia,
      Bogotá D.C., Caldas, Risaralda y Santander pertenecen a Andina; Atlántico
      y Bolívar a Caribe; y Valle del Cauca a Pacífica.
    - Generalice ``occupation`` a ``occupation_group`` con las cuatro familias
      definidas en ``OCCUPATION_TO_GROUP``.

    Verifique con ``data/auxiliary.csv`` que, al cruzar por ``age_group``,
    ``region`` y ``occupation_group``, ningún perfil público tenga una única
    coincidencia. Conserve ``annual_spend`` para mantener utilidad analítica.
    """
    raw = pd.read_csv(DATA_DIR / "raw.csv")
    anonymized = raw.drop(columns=["name", "email"]).copy()

    card_number = anonymized["loyalty_card_number"].astype(str).str.zfill(12)
    anonymized["loyalty_card_number"] = "********" + card_number.str[-4:]

    anonymized["customer_id"] = anonymized["document_id"].map(pseudonymize)
    anonymized = anonymized.drop(columns=["document_id"])

    anonymized["age_group"] = pd.cut(
        anonymized["age"],
        bins=[20, 30, 40, 50, 60, 70],
        labels=["20-29", "30-39", "40-49", "50-59", "60-69"],
        right=False,
    )
    anonymized = anonymized.drop(columns=["age"])

    department = anonymized["city"].map(CITY_TO_DEPARTMENT)
    anonymized["region"] = department.map(DEPARTMENT_TO_REGION)
    anonymized = anonymized.drop(columns=["city"])

    anonymized["occupation_group"] = anonymized["occupation"].map(
        OCCUPATION_TO_GROUP
    )
    anonymized = anonymized.drop(columns=["occupation"])

    SUBMISSION_FILE.parent.mkdir(exist_ok=True)
    anonymized.to_csv(SUBMISSION_FILE, index=False)

    return anonymized
    # raise NotImplementedError


if __name__ == "__main__":
    anonymize_customers()
