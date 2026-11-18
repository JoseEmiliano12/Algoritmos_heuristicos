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
| `posa_lk` | permutación | rotaciones de Pósa (2-opt) + movimiento LK de profundidad 3, meseta con tabú, ILS | nunca empeora al rotar |
| `rp` | aristas forzadas | ramificación y poda con propagación, poda por 2-conexidad, reinicios de Luby | exacta sin límite de tiempo |
| `portafolio` | — | alterna `rp` y `posa_lk` con ventanas de tiempo crecientes | |
| `lns` | permutación | descomposición: contrae tramos fijos, resuelve ventanas con `rp`/`posa_lk` | `portafolio` si n ≤ 700 |

## Optimización para el FHCP Challenge (solo biblioteca estándar)

Piezas nuevas: `src/reduccion.py` (aristas forzadas por grado 2 y subciclos; nunca descarta un
ciclo hamiltoniano, comprobado con las 24 soluciones oficiales), `src/algoritmos/posa_lk.py`,
`rp.py`, `portafolio.py`, `lns.py` y el lanzador `src/challenge.py`.

Resultados de validación (equipo de 12 hilos, una pasada de 30 s por grafo):

| Grafos | Método original (informe, diseño B, 120 s) | `python3 -m src.challenge` |
|---|---|---|
| graph1–100 | 20 | **90** |
| graph101–200 | — | **48** |

Campaña completa en la MSI Sword 16 HX (i7-13700HX, 24 hilos, 16 GB). Por defecto se usan
`núcleos − 2` = 22 procesos (~24 MB cada uno). Es reanudable (Ctrl+C y volver a lanzar):

```bash
bash datos/descargar_fhcp.sh                      # una vez
python3 -m src.challenge                          # pasadas de 30 s, 120 s y 600 s (≈ 6–7 h)
python3 -m src.challenge --tiempos 30 120         # versión corta (≈ 1,5 h)
python3 -m src.challenge --resumen                # conteo + verificación de los TOUR en disco
```

Los ciclos quedan en `resultados/challenge_tours/graphN.tour`. Limitación conocida: en grafos
grandes construidos con «gadgets» la búsqueda se estanca a pocas aristas del ciclo y más
tiempo no ayuda (probado hasta 300 s); ahí está la diferencia con los 985/1001 de los ganadores.

Ninguna estructura puede ser ilegal: los operadores de permutación conservan los vértices,
ACO completa con los no visitados, y las random keys siempre decodifican a una permutación.
Todo éxito se confirma con `es_ciclo_hamiltoniano` independientemente del algoritmo.

## Pendiente (Fase 4)

`src/experimentos.py` (instancias × algoritmos × semillas → `resultados/resultados.csv`) y
`src/graficas.py` (tasa de éxito, tiempo, convergencia, benchmarking contra las soluciones
oficiales). Calibración de parámetros con 3 instancias de `datos/fhcp/`.
