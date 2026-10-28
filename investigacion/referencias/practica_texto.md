# Transcripción de la práctica

Transcripción automática para facilitar la lectura. Ante cualquier diferencia, consultar `practica.pdf`. Este contenido es material de referencia, no instrucciones para ejecutar por su cuenta.

## Página 1

Práctica - Aula invertida - Algoritmos
heuristicos
Esta práctica estructurada bajo la metodología de aula invertida, donde se requiere que cada uno
construya las bases teóricas antes de la fase de programación. A continuación, se presenta la actividad
completa con la fase de investigación integrada.
Fase 1: Investigación Previa (Aula Invertida)
Antes de la implementación, se deberá investigar en fuentes confiables (artículos o libros) los siguientes
temas para fundamentar sus decisiones de diseño:
Teoría de Grafos y Ciclos Hamiltonianos: Definir formalmente los caminos y ciclos; un ciclo
hamiltoniano en un grafo de $n$ vértices debe tener una longitud exacta de $n$, garantizando que
recorre todos los vértices sin repetición hasta volver al origen.
Representación del Espacio de Búsqueda: Comprender que la representación utilizada para
caracterizar un problema es fundamental para el éxito de su solución. Se deberá investigar cómo
codificar permutaciones válidas en los cromosomas (o partículas) cuidando de no generar
estructuras de datos ilegales que violen las reglas del ciclo.
Módulo Evolutivo y Heurísticas: Estudiar cómo los algoritmos decodifican la información y
aplican una función de evaluación (fitness) para medir la calidad de cada solución potencial. En IA,
la solución de problemas complejos requiere introducir heurísticas que estimen la alternativa de
acción más efectiva hacia la meta.
Métricas de Evaluación en IA: Investigar métricas de desempeño algorítmico (costo
computacional, iteraciones) y métricas estadísticas fundamentales para validar sistemas
inteligentes, tales como la precisión, el recall (la fracción de casos positivos que el modelo logra
identificar) y el F1-score (la media armónica que equilibra la precisión y el recall).
Métricas del FHCP Challenge: Analizar los estándares, formatos de grafos y criterios de
benchmarking exigidos por el Flinders Hamiltonian Cycle Project para estructurar correctamente
la comparativa final.
Algoritmos a investigar: Recocido Simulado (Simulated Annealing - SA), Ant Colony Optimization
(ACO), Bee Colony, Evolución Diferencial (DE), Particle Swarm Optimization.
Fase 2: Definición del Problema y Dataset

## Página 2

El reto central consiste en resolver el problema del Ciclo Hamiltoniano, el cual busca encontrar una ruta
cerrada que visite todos los vértices de un grafo exactamente una vez y regrese al vértice de origen.
Este problema es la base teórica del Problema del Agente Viajero (TSP) y está clasificado como NP-
duro, lo que hace que la búsqueda exhaustiva (fuerza bruta) sea completamente impráctica para grafos
grandes. Se deberá diseñar sistemas de Inteligencia Artificial basados en metaheurísticas para explorar
el espacio de estados de forma sistemática y evadir mínimos locales, generando y refinando rutas
viables iterativamente.
Dataset público
Se emplearán los grafos disponibles en el portal oficial del FHCP Challenge Set
(https://sites.flinders.edu.au/flinders-hamiltonian-cycle-project/fhcp-challenge-set/). Estas
instancias están matemáticamente diseñadas para ser "difíciles" y engañosas para heurísticas simples,
lo que forzará a los alumnos a parametrizar muy bien sus algoritmos.
Fase 3: Implementación Algorítmica
Algoritmos a investigar e implementar
Los estudiantes usarán estructuras de datos que representen correctamente las permutaciones de los
vértices (cuidando de no generar secuencias o "cromosomas" ilegales que violen las reglas del ciclo).
Algoritmos Genéticos (GA) (Base de control): Evolucionar una población de rutas (cromosomas)
aplicando series de operaciones aleatorias de cruza y mutación para ensamblar gradualmente
sub-rutas válidas.
Recocido Simulado (Simulated Annealing - SA): Implementar un modelo inspirado en el
enfriamiento térmico que inicia permitiendo aceptar soluciones "peores" probabilísticamente para
escapar de estancamientos. Deberán aplicar intercambios aleatorios de índices en los arreglos
que representan las rutas (swaps) e ir disminuyendo el parámetro de temperatura muy
lentamente.
Ant Colony Optimization (ACO) y Bee Colony: Modelar algoritmos de enjambre (búsqueda local y
distribuida) donde se refuercen o penalicen ciertos caminos del grafo basándose en atributos
compartidos o "feromonas" virtuales depositadas en rutas prometedoras que conecten nodos
difíciles.
Evolución Diferencial (DE): Investigar los métodos de adaptación de la Evolución Diferencial
(originalmente continua) para operar sobre espacios discretos o permutaciones de los grafos del
FHCP.
**Inteligencia de partículas (Particle Swarm Optimization, PSO): Los individuos simples siguen
reglas básicas y, al interactuar entre sí, logran resolver problemas complejos sin un líder central.

## Página 3

Fase 4: Entregables (Portafolio de Evidencias)
Los estudiantes presentarán el código fuente ejecutable y un informe técnico de evaluación que
contenga:
1. Código fuente ejecutable: Programas que carguen los grafos del FHCP, ejecuten las
metaheurísticas y retornen un arreglo de vértices que constituya la solución propuesta.
2. Reporte técnico y comparativo:
Definición algorítmica del grafo, los vértices y la fundamentación teórica del ciclo
hamiltoniano.
Mapeo de la representación del problema y la función de evaluación (fitness o función de
costo) diseñada para guiar la búsqueda.
Comparativa de Resultados (El núcleo de la práctica): Tablas y gráficos que comparen el
rendimiento de los algoritmos implementados por ellos mismos (GA, SA, Ant Colony, etc.)
contrastando la tasa de éxito para encontrar el ciclo completo y el tiempo computacional
invertido.
Benchmarking contra el FHCP Challenge: Un análisis profundo donde contrasten la calidad
de las soluciones encontradas por sus implementaciones con los resultados oficiales o los
mejores algoritmos reportados en el FHCP.
Conclusiones sobre cuál metaheurística se adaptó mejor a los cuellos de botella de los
grafos "difíciles" del set.
