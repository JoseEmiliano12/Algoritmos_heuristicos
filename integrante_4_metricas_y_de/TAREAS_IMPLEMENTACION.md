# Integrante 4 — Jesús (confirmar): experimentos, gráficas + Evolución Diferencial (DE)

Plan general y contrato: `PLAN_IMPLEMENTACION.md` (raíz). Investigación: capítulo 5 y síntesis del PDF integrado.

## Fase 1 — esqueleto de `src/experimentos.py` (puedes empezar ya)

No necesitas el dataset ni los algoritmos: pruébalo con un `resolver` falso que devuelva una ruta aleatoria.

- Entrada: lista de archivos `.hcp`, lista de algoritmos (`{"sa": sa.resolver, ...}`), semillas 0–9, `max_evals`, `tiempo_max`.
- Por ejecución: medir tiempo de pared (`time.perf_counter`), verificar con `fitness.es_ciclo_hamiltoniano`,
  guardar el TOUR si hubo éxito (`grafo.escribir_tour`) y agregar una fila a `resultados/resultados.csv`:
  `grafo, n, m, algoritmo, params, semilla, exito, costo_final, evals, iters, tiempo_s`.
- Escribir el CSV fila por fila (si se corta a la mitad no se pierde lo anterior).
- Opción por línea de comandos para correr un solo algoritmo, así cada quien corre el suyo y se juntan los CSV.

## Fase 2 — `src/algoritmos/de.py`

- Individuo = vector real de n **random keys** en [0,1]; decodificar con `argsort` → permutación → `costo()`.
- Mutación DE/rand/1: `v = x_r1 + F·(x_r2 − x_r3)`; cruce binomial con CR; selección uno a uno.
- Recortar claves a [0,1]. Parámetros: tamaño de población NP, F, CR.

## Fase 4 — `src/graficas.py`

A partir del CSV:
- Tabla: tasa de éxito por algoritmo × instancia (con nº de éxitos/10), tiempo medio ± desviación, evaluaciones medias.
- Barras de tasa de éxito; boxplot de tiempo; curvas de convergencia (campo `historial`).
- Recall = tasa de éxito, precisión y F1 con la aclaración de la síntesis (FHCP solo tiene positivos).

## Terminado cuando

- `experimentos.py` corre de punta a punta con el resolver falso sobre `pruebas/grafos_prueba.py`.
- `pruebas/probar_algoritmo.py` pasa con DE.

## Reporte

Comparativa de resultados (tablas, gráficas y métricas); sección de DE.
