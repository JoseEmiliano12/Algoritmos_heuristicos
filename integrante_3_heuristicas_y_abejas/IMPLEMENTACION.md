# Implementación local: GA y ABC

Esta parte agrega `src/algoritmos/ga.py` y `src/algoritmos/abc.py` a la estructura
compartida del proyecto. Ambos módulos importan `src/fitness.py` y cumplen el
contrato de `PLAN_IMPLEMENTACION.md`:

```python
from src.algoritmos.ga import resolver as resolver_ga
from src.algoritmos.abc import resolver as resolver_abc

resultado_ga = resolver_ga(adj, max_evals=10_000, semilla=0, tiempo_max=60)
resultado_abc = resolver_abc(adj, max_evals=10_000, semilla=0, tiempo_max=60)
```

`adj` es una lista de conjuntos de vecinos de un grafo **no dirigido**, con
vértices `0..n-1`. Cada resultado contiene `ruta`, `costo`, `evals`, `iters` e
`historial`. La ruta comienza por 0; el regreso a 0 es implícito y sí se cuenta
en el costo. `costo == 0` indica un candidato que el coordinador de experimentos
debe confirmar con `es_ciclo_hamiltoniano(ruta, adj)`. Si se agota el presupuesto
con costo positivo, solo significa que esa ejecución no encontró un ciclo.

## Algoritmo genético

Población inicial de permutaciones, selección por torneo, cruce de orden OX,
mutación por intercambio o inversión, y elitismo. Los operadores `cruce_ox`,
`mutar_swap` y `mutar_inversion` están en `ga.py` y ABC reutiliza las mutaciones.
El cruce y las mutaciones conservan una permutación y el vértice inicial.

Parámetros: `tam_poblacion=40`, `prob_cruce=0.9`, `prob_mutacion=0.3`,
`tam_torneo=3`, `elitismo=2`, `prob_inversion=0.5`. Son valores iniciales de
implementación, todavía no calibrados con FHCP. La población inicial cuenta
como generación 1 en `iters` e `historial`; copiar una élite no gasta una nueva
evaluación.

## Colonia artificial de abejas

ABC usa una fuente de alimento por ruta. En cada ciclo las empleadas intentan
mejorar todas las fuentes; las observadoras eligen una fuente con pesos
`1 / (1 + costo)`; y las exploradoras reemplazan las fuentes que acumulan
`limite` intentos sin mejora. Un empate cuenta como intento fallido. El mejor
resultado histórico permanece aunque se abandone su fuente.

Parámetros: `fuentes=20`, `limite=100`, `operador="swap"`. El operador `swap`
coincide con la adaptación del PDF de investigación. También se puede elegir
`inversion` o `mixto` como variantes para calibración posterior. El costo de
cada vecina se obtiene mediante `delta_swap` o `delta_inversion`, pero cuenta
como una evaluación de fitness. `iters` cuenta ciclos de ABC realizados;
`historial` registra el mejor costo al final de cada uno. La inicialización
también consume evaluaciones.

## Pruebas

Desde la raíz del proyecto:

```bash
python3 -m unittest discover -s integrante_3_heuristicas_y_abejas -p 'test_*.py' -v
```

Las pruebas comprueban permutaciones, deltas frente a `costo`, presupuesto,
reproducibilidad, contrato y verificación de un ciclo encontrado. Aún falta la
calibración y comparación sobre instancias FHCP cuando el equipo disponga del
lector y del conjunto de datos.
