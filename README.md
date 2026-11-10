# Ciclo hamiltoniano con metaheurísticas (FHCP Challenge Set)

Práctica de Algoritmos Heurísticos. Implementa GA (control), SA, ACO, ABC, DE y PSO bajo un
mismo contrato y una misma función de costo. Plan y decisiones: `PLAN_IMPLEMENTACION.md`.
Investigación (Fase 1): `Plantilla d trabajo/main.pdf`.

Requisitos: **Python ≥ 3.10, solo biblioteca estándar** (no hay que instalar nada).

## Uso rápido (desde la raíz del repositorio)

```bash
python3 -m src --listar                                   # algoritmos disponibles
python3 -m src datos/fhcp/graph1.hcp --alg aco_posa       # resuelve y muestra la ruta (1..n)
python3 -m src datos/fhcp/graph1.hcp --alg sa --semilla 3 --max-evals 1000000 --tiempo 60 --json
python3 -m src datos/fhcp/graph1.hcp --alg abc --param fuentes=40 --tour resultados/tours/g1.tour
python3 -m src.grafo datos/fhcp/graph1.hcp                # n, m, grados y validez del tour oficial
```

Código de salida `0` = ciclo hamiltoniano encontrado **y verificado**; `1` = inconcluso
(agotar el presupuesto no prueba que el grafo no sea hamiltoniano).

## Pruebas

```bash
python3 -m src.fitness                         # 25 440 deltas contra el costo completo
python3 -m unittest discover -s pruebas -t . -v
python3 -m pruebas.probar_algoritmo todos      # contrato + reproducibilidad de cada algoritmo
```

## Estructura

| Archivo | Contenido |
|---|---|
| `src/grafo.py` | `leer_hcp`, `leer_tour`, `escribir_tour` (formato FHCP/TSPLIB, vértices 1..n ↔ 0..n-1) |
| `src/fitness.py` | `costo` (conexiones faltantes, incluido el cierre; 0 ⇔ ciclo), `delta_swap`, `delta_inversion`, `es_ciclo_hamiltoniano`, `ruta_aleatoria`, `ruta_anclada`, `validar_parametros` |
| `src/representacion.py` | random keys → permutación (`argsort` estable, empates por id) para DE y PSO |
| `src/operadores.py` | `inversion_guiada`: 2-opt que repara una conexión rota con una arista real |
| `src/algoritmos/` | `ga.py sa.py aco.py abc.py de.py pso.py` + registro `ALGORITMOS` en `__init__.py` |
| `src/__main__.py` | programa ejecutable (carga `.hcp`, ejecuta, devuelve el arreglo de vértices) |
| `pruebas/` | grafos con ciclo plantado, verificador común y tests unitarios |
| `datos/fhcp/` | las 24 instancias más pequeñas del FHCP (n = 66…198) con su solución oficial `.tou` |
| `datos/instancias.csv` | las 1001 instancias: n, m, grados; las 1001 soluciones oficiales pasan nuestro verificador |
| `datos/descargar_fhcp.sh` | descarga el set completo en `datos/fhcp_completo/` (ignorado por git) |

## Algoritmos registrados

| Nombre | Representación | Movimiento / operador | Nota |
|---|---|---|---|
| `ga` | permutación (0 fijo al inicio) | torneo, cruce OX, mutación swap/inversión, elitismo | base de control |
| `sa` | permutación | swap + inversión 2-opt, Metropolis, enfriamiento geométrico | `alfa` se ajusta al presupuesto |
| `sa_swap` | permutación | solo swap de índices | versión literal del enunciado |
| `aco` | construcción sobre aristas reales | τ^α·η^β, η de Warnsdorff, MAX-MIN | |
| `aco_posa` | ídem | + rotaciones de Pósa al atascarse | búsqueda local sin costo en evaluaciones: reportar aparte |
| `abc` | permutación | empleadas/observadoras/exploradoras, 2-opt guiado por el grafo | |
| `de` | random keys → permutación | DE/rand/1/bin | |
| `pso` | random keys → permutación | inercia (Shi-Eberhart), reinicio por estancamiento | |

Ninguna estructura puede ser ilegal: los operadores de permutación conservan los vértices,
ACO completa con los no visitados, y las random keys siempre decodifican a una permutación.
Todo éxito se confirma con `es_ciclo_hamiltoniano` independientemente del algoritmo.

## Pendiente (Fase 4)

`src/experimentos.py` (instancias × algoritmos × semillas → `resultados/resultados.csv`) y
`src/graficas.py` (tasa de éxito, tiempo, convergencia, benchmarking contra las soluciones
oficiales). Calibración de parámetros con 3 instancias de `datos/fhcp/`.
