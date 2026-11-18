# Entrega: ciclo hamiltoniano con metaheurísticas

Esta carpeta reúne los entregables de la práctica de Algoritmos Heurísticos.

## Archivos principales

| Ruta | Contenido |
|---|---|
| `Investigacion_previa.pdf` | Investigación de grafos, representación, métricas, FHCP y metaheurísticas (fase 1). |
| `Reporte/main.pdf` | Informe técnico y comparativo final (fase 4). |
| `src/` | Código ejecutable de GA, SA, ACO, ABC, DE y PSO. |
| `datos/fhcp/` | 24 grafos FHCP con sus soluciones oficiales para pruebas locales. |
| `datos/instancias.csv` | Metadatos de las 1 001 instancias FHCP. |
| `resultados/` | Registros de las 2 112 corridas, gráficas y ciclos encontrados en formato TOUR. |
| `pruebas/` | Pruebas del código y verificador independiente de resultados. |
| `Reporte/` | Código fuente LaTeX, tablas y figuras necesarios para reconstruir el informe. |

## Ejecutar y verificar

Se requiere Python 3.10 o superior. Los algoritmos y las pruebas usan la biblioteca estándar.
Para regenerar gráficas, instala las dependencias de `requirements.txt`.

```bash
python3 -m src --listar
python3 -m src datos/fhcp/graph4.hcp --alg abc --semilla 0
python3 -m unittest discover -s pruebas -t . -q
python3 pruebas/verificar_resultados.py --allow-missing
```

La última orden valida todos los registros y coteja las rutas de los 24 grafos incluidos.
Para comprobar también las corridas de grafos mayores y repetir los experimentos B y C,
descarga el conjunto público completo y ejecuta el verificador sin la opción parcial:

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
