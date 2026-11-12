# Integrante 3 — José Emiliano: Algoritmo Genético (control) + Colonia de Abejas (ABC)

Plan general y contrato: `PLAN_IMPLEMENTACION.md` (raíz). Investigación: capítulo 4 del PDF integrado.

Tienes dos algoritmos porque tu investigación cubrió GA y ABC. Ambos usan permutaciones y comparten
operadores, así que pon los operadores una sola vez en `ga.py` y en `abc.py` impórtalos de ahí.

## Fase 1 (puedes empezar ya)

Programa los operadores contra el contrato; solo necesitas `fitness.costo` y `fitness.ruta_aleatoria`
(si aún no existen, usa una versión temporal tuya y bórrala cuando Fabian suba `fitness.py`).

- `cruce_ox(p1, p2, rng)`: cruce de orden. Siempre da una permutación válida (agrega un assert).
- `mutar_swap(ruta, rng)`, `mutar_inversion(ruta, rng)`.

## Fase 2 — `src/algoritmos/ga.py` (base de control)

Población de permutaciones aleatorias → selección por torneo → cruce OX → mutación → elitismo (1–2 mejores).
Cada hijo evaluado = 1 evaluación. Parámetros: tamaño de población, prob. de cruce, prob. de mutación, tamaño de torneo.

## Fase 2 — `src/algoritmos/abc.py`

- Fuente de alimento = permutación; nº de fuentes = SN.
- Empleadas: a cada fuente aplicar swap/inversión (con `fitness.delta_*`); quedarse con la mejor (selección voraz).
- Observadoras: eligen fuentes con probabilidad proporcional a la calidad, p. ej. `1 / (1 + costo)`.
- Exploradoras: una fuente que no mejora en `limite` intentos se reemplaza por una ruta aleatoria.

Parámetros: SN, `limite`.

## Terminado cuando

`pruebas/probar_algoritmo.py` pasa con GA y con ABC.

## Reporte

Módulo evolutivo (cómo se decodifica y evalúa cada solución), GA como control y ABC.
