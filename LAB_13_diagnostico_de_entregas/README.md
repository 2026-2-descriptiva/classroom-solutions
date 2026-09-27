# Diagnóstico de entregas

## Propósito

Analizar cumplimiento de fechas comprometidas e identificar dónde se concentra el valor económico expuesto a entregas tardías.

## Competencia

Define indicadores operativos con sus denominadores correctos, segmenta un problema de cumplimiento y prioriza investigación por volumen y valor, sin atribuir causalidad.

## Datos

`data/supply_chain.csv` contiene líneas de envío internacional, fechas prometidas y reales, valor de productos, país y modo de transporte.

## Restricciones

Genere los tres CSV solicitados en `submission/`. Un envío está tarde solo si su fecha real es posterior a la programada; los segmentos prioritarios requieren al menos 30 envíos.
