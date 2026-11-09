# Plan de implementación — Ciclo Hamiltoniano (FHCP)

Documento base para empezar a programar. Las decisiones salen de la investigación integrada
(`Plantilla d trabajo/main.pdf`, capítulos SA, ACO, ABC, DE, FHCP/PSO y Síntesis).

---

## 1. Decisiones de diseño (acordadas antes de programar)

| Tema | Decisión |
|---|---|
| Lenguaje | Python 3 + `numpy` + `matplotlib` (sin más dependencias). |
| Grafo | No dirigido. Lista de adyacencia `adj: list[set[int]]`, vértices **0..n-1** internamente (el archivo HCP usa 1..n; se suma 1 al exportar). |
| Representación | **Permutación cíclica** de los n vértices (`list[int]`). Todo algoritmo debe entregar una permutación válida: sin repetidos y con todos los vértices. Nunca se evalúa una lista con duplicados. |
| Fitness (costo, minimizar) | `costo(ruta) = nº de pares consecutivos (ruta[i], ruta[i+1 mod n]) que NO son arista`. Incluye el cierre. **costo = 0 ⇔ ciclo hamiltoniano**. |
| Verificación | Función independiente `es_ciclo_hamiltoniano(ruta, adj)`: longitud n, sin repetidos, todas las adyacencias y el cierre. Solo se reporta “éxito” si pasa la verificación. |
| Salida | Cada ciclo encontrado se guarda en formato **TOUR** del FHCP (`resultados/tours/<grafo>_<alg>_<semilla>.tour`). |
| Presupuesto (justo para todos) | Mismo límite de **evaluaciones de fitness** (`max_evals`, p. ej. 10⁶) **y** tiempo máximo de pared (p. ej. 60 s); lo que ocurra primero. Una generación de una población cuenta *tamaño_población* evaluaciones. |
| Repeticiones | 10 semillas (0–9) por algoritmo × instancia. |
| Instancias | Las instancias más pequeñas del FHCP Challenge Set (empiezan en 66 vértices). Tras descargar: 3 para **calibrar** parámetros y 5–10 distintas para **evaluar**. Además grafos de juguete (ciclo de 5, grafos aleatorios con ciclo plantado) para pruebas. |

### ¿Qué algoritmo usar?

La práctica pide implementar y comparar **todos** (GA como control + SA, ACO, ABC, DE, PSO), así que la
pregunta real es cuál apostamos como el más fuerte y en cuál invertir más calibración:

**Algoritmo principal: ACO constructivo** (las hormigas solo caminan por aristas que existen).

Motivo: los grafos del FHCP son muy dispersos (casi todos los vértices tienen grado 3). En una
permutación aleatoria casi ninguna de las n conexiones existe, así que SA, DE y PSO arrancan con
costo ≈ n y un paisaje muy plano. ACO construye la ruta sobre el grafo y su heurística puede usar la
estructura: preferir el vecino no visitado con **menos vecinos libres** (regla de Warnsdorff), que es
justamente lo que atrapa los “nodos difíciles”. Cuando una hormiga se atasca, los vértices no
visitados se agregan al final y la ruta se evalúa con el mismo fitness que los demás (comparación justa).

Hipótesis a comprobar con los datos (no es un resultado): ACO > SA > GA/ABC > DE/PSO (random keys).

Referencia para el benchmarking: en el concurso FHCP el mejor equipo resolvió 985 de 1001 instancias
con métodos especializados (transformación a TSP + heurísticas tipo Lin–Kernighan). Nuestra
comparación es contra esa cobertura, sin pretender igualarla con metaheurísticas genéricas.

### Precisión / recall / F1

El FHCP solo tiene grafos con ciclo (todos positivos). Si “detección” = encontrar un ciclo verificado:
recall = tasa de éxito, precisión = 1 cuando hay detecciones y F1 depende solo del recall. Se reportan
igual (lo pide la práctica) pero explicando esta limitación en el reporte (ver Síntesis, sección 7.3).
Agotar el presupuesto sin ciclo es **“inconcluso”**, no “el grafo no es hamiltoniano”.

---

## 2. Estructura del código

```
src/
  grafo.py          leer_hcp(ruta_archivo) -> (nombre, n, adj)
                    escribir_tour(ruta, ruta_archivo, nombre)
  fitness.py        costo(ruta, adj) -> int
                    delta_swap(ruta, i, j, adj) -> int      # cambio de costo en O(1)
                    delta_inversion(ruta, i, j, adj) -> int # 2-opt, O(1)
                    es_ciclo_hamiltoniano(ruta, adj) -> bool
                    ruta_aleatoria(n, rng) -> list[int]
  algoritmos/
    ga.py  sa.py  aco.py  abc.py  de.py  pso.py
  experimentos.py   corre instancias × algoritmos × semillas -> resultados/resultados.csv
  graficas.py       tablas y gráficas desde el CSV
datos/              archivos .hcp del FHCP (no se suben a git si pesan mucho)
pruebas/
  grafos_prueba.py  grafo_con_ciclo(n, aristas_extra, semilla) -> (adj, ciclo)  # grafo con un ciclo hamiltoniano plantado
                    ciclo5() -> adj                                               # el ejemplo del PDF
  probar_algoritmo.py  corre cualquier resolver() sobre los grafos de prueba y valida el contrato
```

### Contrato común (todos los algoritmos lo cumplen)

```python
def resolver(adj, max_evals, semilla, tiempo_max=60, **params) -> dict:
    """adj: list[set[int]] con vértices 0..n-1."""
    return {
        "ruta": [...],     # permutación de 0..n-1 (la mejor encontrada)
        "costo": int,      # costo(ruta, adj); 0 = ciclo hamiltoniano
        "evals": int,      # evaluaciones de fitness usadas
        "iters": int,      # iteraciones/generaciones
        "historial": [...] # mejor costo cada k evaluaciones (para curvas de convergencia)
    }
```

- Usar `rng = random.Random(semilla)` (o `numpy.random.default_rng(semilla)`), nunca el global.
- Detenerse en cuanto `costo == 0`.
- `experimentos.py` mide el tiempo, llama a `es_ciclo_hamiltoniano` y escribe una fila por ejecución:
  `grafo, n, m, algoritmo, params, semilla, exito, costo_final, evals, iters, tiempo_s`.

### Notas por algoritmo (de la investigación)

- **GA (control):** población de permutaciones, cruce **OX** o PMX, mutación por swap/inversión, selección por torneo, elitismo.
- **SA:** vecino por **swap** (lo pide la práctica) y opcionalmente inversión 2-opt; aceptación de Metropolis `exp(-Δ/T)`; enfriamiento geométrico lento (α ≈ 0.999–0.99999). Usar `delta_swap` para que cada paso sea O(1).
- **ACO:** feromona τ en aristas del grafo; probabilidad ∝ τ^α · η^β con η = 1/(1 + vecinos libres); evaporación ρ; depósito proporcional a la longitud del camino construido. Variante MMAS (límites τ_min/τ_max) recomendada.
- **ABC:** fuentes de alimento = permutaciones; abejas empleadas/observadoras aplican swap/inversión; exploradoras reinician fuentes que superan el `limite` de intentos.
- **DE:** **random keys** (vector real por vértice → `argsort` → permutación); mutación DE/rand/1 y cruce binomial sobre las claves.
- **PSO:** también random keys; ecuaciones con inercia w (Shi & Eberhart 1998), recorte de claves a [0,1] y de velocidad a ±v_max.

---

## 3. Evaluación de tamaño → se divide en 5

Estimación en Python: núcleo (grafo + fitness + verificación) ≈ 150 líneas; cada algoritmo 100–200
líneas (6 algoritmos ≈ 900); experimentos + gráficas ≈ 200. **Total ≈ 1 200–1 400 líneas**: es largo,
así que **no se programa todo de una vez** y se reparte entre los 5 integrantes según el tema que
investigó cada uno.

Nombres de los integrantes 4 y 5 asumidos por tema investigado: **confirmar en el equipo**.

| Integrante | Código | Sección del reporte |
|---|---|---|
| **1 — Barbie** (grafos y SA) | `pruebas/grafos_prueba.py` **primero** + `pruebas/probar_algoritmo.py` + `algoritmos/sa.py` | Definición del grafo, vértices y fundamento del ciclo hamiltoniano; SA |
| **2 — Fabian** (representación y ACO) | `fitness.py` (costo, deltas, verificación, ruta aleatoria) **primero** + `algoritmos/aco.py` | Representación y función de fitness; ACO |
| **3 — José Emiliano** (heurísticas y abejas) | `algoritmos/ga.py` (control) + `algoritmos/abc.py` | Módulo evolutivo, GA y ABC |
| **4 — Jesús** (métricas y DE) | `experimentos.py` + `graficas.py` + `algoritmos/de.py` | Comparativa de resultados (tablas, gráficas, éxito, tiempo, recall/F1) ; DE |
| **5 — Israel** (FHCP y PSO) | `grafo.py` (lector HCP + escritor TOUR) **primero**, descarga del dataset en `datos/` + `algoritmos/pso.py` | Dataset, benchmarking contra el FHCP; PSO |

Conclusiones: entre todos al final.

### Orden de trabajo

**El dataset NO es necesario para empezar.** Los algoritmos se programan y prueban con grafos de
prueba generados (`pruebas/grafos_prueba.py`), donde ya se sabe que existe un ciclo. Los grafos reales
del FHCP hacen falta a partir de la Fase 3 (calibración); Israel los descarga en la Fase 1.

| Fase | Qué | Quién | Depende de |
|---|---|---|---|
| **0 — Hoy** | Subir la rama `integracion` (investigación unida + este plan) y crear `src/` vacío. Todos crean su rama desde ahí. | Fabian | — |
| **1 — Núcleo** (1–2 días, en paralelo) | `src/fitness.py` | Fabian | Fase 0 |
| | `pruebas/grafos_prueba.py` | Barbie | Fase 0 |
| | `src/grafo.py` + descargar FHCP en `datos/` + lista de tamaños de instancias | Israel | Fase 0 |
| | Esqueleto de `src/experimentos.py` (lee CSV de algoritmos falsos) | Jesús | Fase 0 |
| | Leer OX/PMX y random keys en la investigación; empezar `ga.py` con el contrato | José Emiliano | Fase 0 |
| **2 — Algoritmos** (en paralelo) | SA, ACO, GA, ABC, DE, PSO, cada uno en su rama `impl/<alg>`, probados con `pruebas/probar_algoritmo.py` | Cada uno el suyo | `fitness.py` + `grafos_prueba.py` |
| **3 — Calibración** | Ajustar parámetros con las 3 instancias de calibración; escoger y anotar los valores finales | Cada uno el suyo | Fase 2 + dataset |
| **4 — Experimentos** | Correr todo (6 alg × instancias × 10 semillas) → `resultados/resultados.csv` + gráficas | Jesús coordina; cada quien puede correr su algoritmo y entregar su CSV | Fase 3 |
| **5 — Reporte** | Cada quien su sección en el LaTeX de `Plantilla d trabajo/`; conclusiones entre todos | Todos | Fase 4 |

Las tareas detalladas de cada integrante están en `integrante_*/TAREAS_IMPLEMENTACION.md`.

Regla de ramas: nadie edita archivos de otro. Si alguien necesita un cambio en `fitness.py` o
`grafo.py`, se lo pide al dueño. Se integra a `integracion` con PR.

### Pendiente de acordar en equipo

- Valores exactos de `max_evals` y `tiempo_max` (ajustar cuando se vea cuánto tarda una evaluación).
- Qué instancias exactas (depende de los tamaños al descargar el set).
- Si se permite una búsqueda local común (p. ej. 2-opt) como variante híbrida; si se usa, aplicarla a todos por igual.
