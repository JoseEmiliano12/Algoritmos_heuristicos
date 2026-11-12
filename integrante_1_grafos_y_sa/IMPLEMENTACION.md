# Implementación de grafos de prueba y recocido simulado

Esta aportación implementa las tareas del integrante 1 en `TAREAS_IMPLEMENTACION.md`.
Usa Python 3 y únicamente su biblioteca estándar; no necesita instalar paquetes.
Reutiliza `src/fitness.py` y respeta el contrato de `PLAN_IMPLEMENTACION.md`.
Los archivos de ACO y el núcleo compartido se conservan sin modificaciones.

## Ejecutar desde la raíz del repositorio

```bash
python3 -m unittest discover -s pruebas -v
python3 -m src.fitness
python3 -m pruebas.probar_algoritmo sa --max-evals 200000
python3 -m pruebas.probar_algoritmo aco
python3 -m pruebas.evaluar_sa
```

`probar_algoritmo` también expone una función que recibe cualquier `resolver`
compatible, para los algoritmos que se añadan después. Comprueba permutación,
costo real, presupuesto, historial y repetibilidad. Un costo positivo se imprime
como **inconcluso**, sin afirmar que el grafo no es hamiltoniano.

## Uso desde otro módulo

```python
from pruebas.grafos_prueba import ciclo5
from src.algoritmos.sa import resolver
from src.fitness import es_ciclo_hamiltoniano

adj = ciclo5()
resultado = resolver(adj, max_evals=200000, semilla=7, tiempo_max=60)
print(resultado)
if resultado['costo'] == 0:
    assert es_ciclo_hamiltoniano(resultado['ruta'], adj)
    print('Ciclo:', resultado['ruta'] + [resultado['ruta'][0]])
else:
    print('No se encontró un ciclo dentro de los límites de búsqueda.')
```

Los identificadores son `0..n-1`. La ruta devuelta no repite el inicio: el cierre
es implícito y se incluye en el costo. En el ejemplo se repite solo al mostrarlo.

## Decisiones de implementación

- El estado es una permutación; se fija el vértice 0 al inicio mediante una
  rotación. No se entrega al algoritmo el ciclo oculto del generador.
- El costo cuenta conexiones ausentes, incluido el regreso al inicio.
- Se aceptan mejoras y empates. Los aumentos se aceptan con `exp(-delta/T)`.
  La comparación se hace contra la ruta actual y se conserva aparte la mejor.
- `vecino='mixto'` propone intercambio e inversión con la misma probabilidad,
  como en la investigación. `vecino='swap'` permite evaluar solo el intercambio
  exigido en el plan; `vecino='inversion'` permite la otra variante.
- Se reutilizan `delta_swap` y `delta_inversion`, sin recalcular toda la ruta en
  cada intento. La aplicación de una inversión aceptada sí recorre el segmento.
- Se cuenta la evaluación inicial y una evaluación por vecino, incluso si se
  rechaza. La verificación independiente final no es una evaluación de búsqueda.
- Se comprueba el presupuesto y el reloj antes de cada vecino. Se termina al
  encontrar costo cero, agotar `max_evals`, superar el tiempo o llegar a `T_min`.
  El reloj no interrumpe operaciones que ya comenzaron; puede haber un pequeño
  exceso por validación o por la operación en curso.
- `random.Random(semilla)` evita alterar el generador global. La repetibilidad
  exige que el reloj no corte antes el trabajo; el tiempo de máquina puede variar.
- El historial guarda el mejor costo inicial, cada 100 evaluaciones y el final.
  Su longitud no representa todas las evaluaciones ni coincide con `iters`.
  `iters` cuenta propuestas y `evals = iters + 1`.

## Parámetros iniciales

| Parámetro | Valor predeterminado | Interpretación |
|---|---|---|
| `T0` | `-1/log(0.8)`, aproximadamente 4.4814 | Acepta un aumento de costo de 1 con probabilidad 0.8 al inicio. No implica aceptar el 80 % de todos los aumentos. |
| `alfa` | `None` (antes `0.9999`) | Multiplica la temperatura después de cada propuesta. Con `None` se calcula `(T_min/T0)^(1/max_evals)` para usar todo el presupuesto; con `0.9999` SA paraba por temperatura a las ~153 000 evaluaciones. |
| `T_min` | `0.000001` | Umbral de temperatura para terminar. |
| `vecino` | `mixto` | Intercambio o inversión con igual probabilidad. |
| `tiempo_max` | `60` segundos | Límite de tiempo comprobado entre propuestas. |

Son valores de partida para pruebas didácticas. No se afirma que sean óptimos
ni que estén calibrados para FHCP. No se incorporan recalentamiento, reparación,
reinicios, bibliotecas nuevas ni búsquedas locales adicionales.

## Verificaciones realizadas el 9 de noviembre de 2026

Con Python 3.12.3 se ejecutaron las 11 pruebas automáticas de esta aportación.
Comprueban grafos plantados con el número exacto de aristas adicionales,
repetibilidad, validez, costo, límites, entradas inválidas y conservación del grafo.
La prueba existente de fitness también pasó sus 25440 comprobaciones de deltas.

El verificador común pasó para SA y para el ACO existente. Con SA, semilla 7,
presupuesto de 200000 evaluaciones y los cuatro grafos del verificador, se
encontraron ciclos válidos con 4, 12764, 50452 y 110713 evaluaciones para 5, 10,
30 y 66 vértices, respectivamente. Se repitió cada ejecución para comprobar la
reproducibilidad. Los grafos plantados usaron como semilla su número de vértices.

`python3 -m pruebas.evaluar_sa` permite repetir la comprobación sobre diez grafos
de 30 vértices y 15 aristas adicionales. Usa semillas del grafo `1000..1009` y
semillas del algoritmo `0..9`, con hasta 200000 evaluaciones y 60 segundos por caso.
Se obtuvo lo siguiente antes de elegir la mezcla como valor predeterminado:

| Variante | Ciclos verificados | Mejor costo final por semilla del algoritmo de 0 a 9 |
|---|---|---|
| Solo intercambio | 0 de 10 | 3, 4, 5, 4, 4, 4, 4, 3, 5, 3 |
| Mezcla de intercambio e inversión | 10 de 10 | 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 |

En la mezcla se utilizaron respectivamente 38659, 33775, 33415, 37019, 42369,
42767, 107568, 40937, 32747 y 40870 evaluaciones. El intercambio llegó al umbral
de temperatura con 153148 evaluaciones en cada caso, antes del máximo permitido.
El uso efectivo de recursos fue diferente por la terminación anticipada.
Esto es una comprobación didáctica sobre casos conocidos, no una comparación
general ni evidencia suficiente para elegir parámetros del experimento final.

## Relación con la investigación y límites

La regla de aceptación sigue a Kirkpatrick, Gelatt y Vecchi (1983),
*Optimization by Simulated Annealing*, Science 220(4598), 671–680:
https://doi.org/10.1126/science.220.4598.671

La representación, el costo por conexiones faltantes y la mezcla de movimientos
son las decisiones de adaptación explicadas en la investigación y en el capítulo
SA del repositorio. La fórmula incremental pertenece al núcleo compartido del
equipo. No se atribuyen a la publicación original esas decisiones particulares.

Esta implementación no descarga FHCP, no produce resultados del concurso y no
implementa los algoritmos asignados a otros integrantes. El lector HCP, la
exportación TOUR y el coordinador de experimentos siguen pendientes en la rama
recibida y corresponden a otras tareas del equipo. SA ya puede importarse desde
ese futuro coordinador a través de la interfaz común `resolver`.
