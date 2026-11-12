# Integrante 1 — Barbie: grafos de prueba + Recocido Simulado (SA)

Plan general y contrato: `PLAN_IMPLEMENTACION.md` (raíz). Investigación: capítulo 2 del PDF integrado.

## Primero (Fase 1, bloquea a todos) — `pruebas/grafos_prueba.py`

Sin dependencias: puedes empezar hoy.

```python
def grafo_con_ciclo(n, aristas_extra, semilla) -> tuple[list[set[int]], list[int]]:
    """Baraja 0..n-1 para formar un ciclo oculto, agrega sus n aristas y luego
    `aristas_extra` aristas aleatorias (sin lazos ni repetidas). Devuelve (adj, ciclo)."""

def ciclo5() -> list[set[int]]:
    """El ejemplo del PDF: aristas 0-1, 1-2, 2-3, 3-4, 4-0."""
```

Sugerencia de tamaños para todos: n = 10, 30, 66 con aristas_extra ≈ n/2 (grado ~3, como el FHCP).

## Después — `pruebas/probar_algoritmo.py`

Script que recibe un `resolver` y lo corre con `ciclo5()` y `grafo_con_ciclo(...)`, comprobando con
asserts que: `ruta` es permutación de 0..n-1, `costo == fitness.costo(ruta, adj)`, `evals <= max_evals`,
y que con la misma semilla el resultado se repite. Lo usan los 6 algoritmos.

## Fase 2 — `src/algoritmos/sa.py`

Usa: `fitness.costo`, `fitness.delta_swap`, `fitness.delta_inversion`, `fitness.ruta_aleatoria` (de Fabian).

- Estado: una permutación. Vecino: **swap de dos índices** (lo exige la práctica); opcional inversión 2-opt.
- Aceptación de Metropolis: aceptar si Δ ≤ 0, si no con probabilidad `exp(-Δ / T)`.
- Enfriamiento geométrico lento `T ← α·T` (α ≈ 0.999–0.99999); temperatura inicial tal que al
  principio se acepte ~80 % de los empeoramientos.
- Usa `delta_swap` (O(1)); no recalcules el costo completo en cada paso. Cada vecino evaluado cuenta como 1 evaluación.
- Opcional: recalentamiento si pasan muchas iteraciones sin mejorar.

Parámetros a calibrar: `T0`, `alfa`, `T_min`, tipo de vecino.

## Terminado cuando

- `probar_algoritmo.py` pasa con SA.
- SA encuentra el ciclo en `grafo_con_ciclo(30, 15, s)` para la mayoría de semillas.

## Reporte

Definición algorítmica del grafo, los vértices y fundamento del ciclo hamiltoniano; sección de SA
(diseño, parámetros elegidos y por qué).
