# Dashboard analítico

Construya un tablero en Streamlit para analizar el desempeño de campañas de marketing. Use `data/campaign_data.csv` como fuente y conserve los cálculos analíticos en `src/pregunta_01.py`.

El tablero debe permitir filtrar por período, fuente de tráfico y país. Para la población filtrada debe mostrar impresiones, clics pagados, ingresos, inversión, utilidad bruta, ROAS y CPC; además debe incluir una tendencia diaria, una comparación por fuente y una tabla por campaña.

La función `create_source_summary()` debe generar `submission/source_summary.csv`. El archivo debe contener una fila por fuente de tráfico, sus métricas agregadas y los indicadores ROAS y CPC calculados a partir de los totales de cada fuente.
