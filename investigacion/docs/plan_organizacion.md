# Plan de investigación y organización del equipo

Proyecto sobre ciclos hamiltonianos y métodos de búsqueda
Equipo de cinco integrantes  |  Versión 1.1  |  28 de octubre de 2026

### Propósito y acuerdo de trabajo

El primer objetivo es que cada integrante comprenda el problema y pueda explicar sus propuestas con fundamentos. Todos estudiarán los conceptos básicos, investigarán un método de búsqueda y compartirán lo aprendido. Después, el equipo elegirá las herramientas, organizará los programas y distribuirá las tareas de programación.

El plan mantiene las cuatro fases de la práctica: investigación, definición del problema y los datos, programación, y evaluación con informe. Por ahora, la prioridad es investigar. Las decisiones técnicas se tomarán cuando el equipo tenga información suficiente para justificarlas.

### Requisitos que mantenemos

- Estudiar qué es un ciclo hamiltoniano, cómo representar una posible solución, cómo evaluarla y cómo leer los grafos del conjunto de datos FHCP indicado en la práctica.

- Investigar y programar los seis algoritmos de la práctica: genético, recocido simulado, colonia de hormigas, colonia de abejas, evolución diferencial y enjambre de partículas. El algoritmo genético servirá como referencia para comparar resultados.

- Entregar programas que puedan ejecutarse y un informe que compare los resultados del equipo con los resultados de referencia del FHCP.

### Ajustes que aplicamos primero

- Asignar temas de investigación, con los mismos apartados de entrega para todos. Ofrecer apoyo cuando un tema resulte más difícil de lo previsto.

- Elegir más adelante el lenguaje de programación, las herramientas de apoyo, el medio de redacción y la organización de los archivos y programas.

- Distribuir la programación después de calcular el trabajo necesario. Cada parte compartida tendrá un responsable y otra persona que también la comprenda.

**Organización inicial. **Usaremos un espacio compartido accesible para todos, un registro de fuentes, una lista de tareas y reuniones de revisión. Elegir estos medios básicos no obliga a adoptar todavía todas las herramientas del proyecto.

## 1 Bases comunes antes de especializarnos

Cada integrante estudiará estos contenidos y preparará una explicación propia. El equipo puede compartir fuentes y resolver dudas en conjunto, pero todos deben comprender los fundamentos del proyecto.

Un grafo representa elementos y sus conexiones. Los elementos se llaman vértices y las conexiones, aristas. Un ciclo hamiltoniano es un recorrido cerrado que visita cada vértice una sola vez y regresa al punto inicial.

### Qué debe comprender cada integrante

- Reglas del problema. Distinguir un camino de un ciclo y explicar todas las condiciones de un ciclo hamiltoniano. Comprender la diferencia entre encontrar un recorrido válido y buscar uno de menor costo.

- Posibles soluciones. Escribir un orden de visita y comprobar que incluya todos los vértices sin repetirlos. Ese orden se llama permutación. También deben existir las conexiones entre vértices consecutivos y la conexión de regreso al inicio.

- Evaluación y comprobación. Explicar cómo asignar una puntuación a una posible solución para orientar la búsqueda. Distinguir esa puntuación de la comprobación completa de las reglas del ciclo.

- Funcionamiento de la búsqueda. Explicar cómo empieza el método, cómo cambia las posibles soluciones, qué decisiones toma al azar y cuándo termina. Reconocer que puede finalizar sin encontrar un ciclo válido.

- Datos y comparación. Revisar un archivo de ejemplo del FHCP e identificar sus vértices y conexiones. Comprender qué se debe registrar para que otra persona pueda repetir una prueba.

### Taller conjunto del algoritmo genético

El equipo estudiará en conjunto un ejemplo pequeño del algoritmo genético (GA). Seguirá sus pasos de selección, combinación de soluciones y cambios aleatorios. En cada paso revisará qué ocurre con las rutas y cómo cambia su puntuación.

El taller no sustituye la programación del GA. Más adelante se le asignarán un responsable y un revisor, igual que a los otros cinco algoritmos.

### Evidencia de la base común

Cada persona entregará una nota breve con un grafo pequeño, una secuencia que cierre un ciclo válido y otra que falle. Explicará la falla y evaluará ambos casos con una regla sencilla. El grupo revisará el ejemplo y registrará los acuerdos y las dudas que afecten a todos.

**Condición para avanzar. **Cada integrante debe explicar por qué su ejemplo cumple o incumple las reglas y por qué una buena puntuación no basta para afirmar que existe un ciclo hamiltoniano. Las dudas comunes se resuelven antes de tomar decisiones sobre el programa.

## 2 Reparto temporal de la investigación

El equipo asignará un tema principal a cada integrante. Este reparto corresponde a la investigación inicial. Las tareas de programación se decidirán después, según la dificultad de cada método y las partes que deban estar listas primero.

| Núm | Tema principal | Pregunta central |
| --- | --- | --- |
| 1 | Recocido simulado / SA | ¿Cómo modifica una ruta, cuándo acepta cambios y cómo ajusta su comportamiento durante la búsqueda? |
| 2 | Colonia de hormigas / ACO | ¿Cómo construye rutas, comparte información sobre ellas y actúa cuando no puede continuar? |
| 3 | Colonia de abejas / Bee Colony | ¿Qué versión del método se estudiará? ¿Cómo busca, mejora y descarta posibles soluciones? |
| 4 | Evolución diferencial / DE | ¿Cómo adaptar el método para trabajar con órdenes de visita sin repetir vértices? |
| 5 | Enjambre de partículas / PSO | ¿Cómo representar y actualizar una ruta a partir de la información de otras posibles soluciones? |

### Alcance de cada investigación

Cada responsable explicará el funcionamiento original del algoritmo y estudiará cómo aplicarlo al ciclo hamiltoniano. Comparará distintas opciones y describirá sus ventajas, dificultades y condiciones de uso. Una técnica encontrada durante la investigación será una opción por evaluar; su uso deberá justificarse antes de adoptarla.

Quien investigue colonia de abejas indicará el nombre de la versión estudiada y sus pasos. El grupo comprobará que no se mezclen procedimientos de métodos diferentes bajo un mismo nombre.

### Revisión entre compañeros

Cada investigación tendrá un revisor: el integrante 1 revisa al 2; el 2 al 3; el 3 al 4; el 4 al 5; y el 5 al 1. El revisor comprobará que puede seguir el ejemplo y consultar las fuentes que respaldan las propuestas. Todos asistirán a las explicaciones del equipo.

**Equilibrio de trabajo. **Todos entregan la ficha de la página siguiente. Si una adaptación exige más investigación, se registra y se ofrece apoyo. El número de algoritmos o de páginas escritas no demuestra por sí solo una carga equivalente.

## 3 Evidencia de una investigación a fondo

Cada integrante preparará una ficha de investigación con los siguientes apartados. La profundidad se demuestra al explicar y aplicar lo estudiado; la extensión del documento se ajustará a ese propósito.

**1 Funcionamiento. **Explicar con palabras propias qué hace el algoritmo, cómo representa una posible solución, qué pasos sigue y cuándo termina. Definir los términos técnicos y los ajustes que utiliza.

**2 Ejemplo manual. **Usar un grafo de aproximadamente cinco a ocho vértices para mostrar una ejecución parcial: estado inicial, decisiones, cambios y evaluación. Incluir el cierre de la ruta al comprobar si existe un ciclo.

**3 Aplicación al ciclo hamiltoniano. **Explicar cómo se representan los vértices y cómo se crean o modifican las posibles rutas. Indicar qué ocurre si se repiten vértices, faltan conexiones o la ruta no regresa al inicio. Explicar si el método evita esos casos, los corrige o les asigna una puntuación menor.

**4 Opciones de diseño. **Comparar al menos dos opciones importantes, cuando existan. Por ejemplo, distintas formas de guardar una ruta o modificarla. Explicar por qué se propone una opción y qué condiciones necesita para funcionar.

**5 Pasos y ajustes del algoritmo. **Escribir una lista ordenada de pasos sin usar todavía un lenguaje de programación. Esta descripción se llama pseudocódigo. Indicar qué datos recibe el método, qué devuelve, cómo evalúa las rutas, qué decide al azar y cuándo termina. Explicar cómo influyen sus ajustes, llamados parámetros.

**6 Recursos y dificultades. **Identificar qué operaciones pueden consumir más tiempo o memoria y en qué situaciones el método puede dejar de mejorar. Respaldar las explicaciones con fuentes o señalar qué falta comprobar.

**7 Fuentes consultadas. **Como pauta inicial, consultar al menos tres fuentes: un artículo original o libro de referencia, un estudio de aplicación a problemas de rutas u ordenación y otra fuente para comparar las opciones. Explicar si no se encuentra alguna de ellas. Registrar autor, título, año, enlace y capítulo o sección utilizados.

**8 Dudas y siguiente comprobación. **Separar lo comprendido, la propuesta propia y lo que todavía requiere evidencia. Formular una prueba pequeña o una pregunta concreta para resolver cada duda importante.

### Material que se entrega

Cada integrante guardará en el espacio compartido su ficha, las fuentes con una breve explicación de su utilidad, el ejemplo resuelto y la lista de pasos del algoritmo. Si utiliza asistentes de inteligencia artificial o resúmenes, comprobará las afirmaciones y referencias en los documentos originales. Solo incluirá fuentes que haya consultado.

## 4 Revisión del aprendizaje y secuencia de trabajo

La investigación se revisará mediante una explicación breve y una comprobación práctica entre compañeros. Una presentación por sí sola no cierra la tarea: el responsable debe poder responder preguntas y reproducir las decisiones de su ejemplo.

### Cómo revisaremos cada investigación

- El revisor sigue el ejemplo paso a paso y señala decisiones que no estén explicadas.

- El responsable explica cómo cambiaría el resultado al modificar una condición del ejemplo o un parámetro relevante.

- El equipo identifica qué pasos modifican las rutas, cuáles les asignan una puntuación y cuáles comprueban si cumplen las reglas.

- Las afirmaciones importantes tienen una fuente que se puede consultar. Las ideas todavía no verificadas se señalan como pendientes de comprobación.

- Las dudas que afectan al diseño quedan en una lista con una persona encargada de darles seguimiento.

**Resultado de la revisión. **El revisor indicará si la investigación permite pasar al diseño del programa, si necesita correcciones o si requiere apoyo. Explicará qué falta. Las correcciones se revisarán de nuevo; también debe comprobarse el ejemplo, aunque la exposición haya sido clara.

### Secuencia propuesta sin fechas impuestas

| Paso | Trabajo | Resultado para avanzar |
| --- | --- | --- |
| A | Leer la práctica y acordar entregables | Lista de requisitos y dudas para el profesor. |
| B | Estudiar las bases y realizar el taller de GA | Ejemplo individual revisado y acuerdos comunes. |
| C | Profundizar en cinco especialidades | Fichas con fuentes, ejemplo y pseudocódigo. |
| D | Exponer y revisar entre compañeros | Correcciones resueltas y dudas de diseño visibles. |
| E | Probar opciones y planificar la programación | Decisiones justificadas y tareas con responsables. |

A y B preparan el trabajo especializado; la búsqueda de fuentes de C puede empezar mientras se completa B. E requiere las revisiones de D. El equipo fijará fechas según la entrega real de la asignatura y su disponibilidad, dejando tiempo para correcciones.

**Coordinación. **En cada reunión cambiarán las personas encargadas de dirigir la conversación y anotar los acuerdos. Cada tarea tendrá responsable, resultado esperado, fecha y estado. Quien encuentre una dificultad la comunicará con una pregunta concreta para recibir apoyo a tiempo.

## 5 Decisiones técnicas y reparto de programación

Después de revisar las investigaciones, el equipo probará las herramientas antes de elegirlas. Puede evaluar Python para programar, GitHub para compartir el código y conservar el historial de cambios, y Overleaf para redactar el informe. Cada elección debe responder a una necesidad y ser manejable para el equipo.

### Decisiones que debemos justificar

- Herramientas para programar. Comprobar que todos pueden ejecutar el mismo ejemplo. Las herramientas de apoyo deben facilitar el trabajo sin reemplazar los algoritmos que el equipo debe desarrollar.

- Representación de los datos. Probar distintas formas de guardar un grafo pequeño. Acordar cómo identificar sus vértices, consultar sus conexiones y expresar el regreso al inicio de una ruta.

- Evaluación y comprobación. Elegir cómo puntuar las posibles soluciones y cómo comprobar, por separado, todas las condiciones de un ciclo válido.

- Formato de los resultados. Acordar qué datos recibe y devuelve cada programa: grafo, ajustes, límites de ejecución, ruta propuesta, validez, tiempo y número de operaciones que se decida registrar.

- Colaboración. Elegir cómo compartir el código, conservar los cambios y redactar el informe. Acordar cómo se revisará el trabajo antes de incorporarlo al programa común.

Cada decisión se registrará con el problema que resuelve, opciones consideradas, evidencia de la prueba, elección y motivo para revisarla. Las dudas sobre requisitos de la asignatura se resolverán con el profesor antes de convertirlas en restricciones del equipo.

### Cómo distribuiremos la implementación

Separaremos las tareas: leer los archivos, guardar los grafos, evaluar las rutas, comprobar su validez, programar los seis algoritmos, realizar las pruebas y preparar el informe. Con las investigaciones y las pruebas iniciales calcularemos el esfuerzo y el orden de trabajo.

Cada tarea tendrá un responsable y otra persona que la revise o pueda ayudar. El algoritmo genético deberá tener una asignación expresa. Si alguien programa dos algoritmos, asumirá menos tareas de otro tipo. Las partes que necesitan varios compañeros se documentarán para que al menos dos personas sepan utilizarlas y modificarlas.

**Primera prueba conjunta. **Usaremos un grafo pequeño para comprobar todo el proceso, desde la lectura del archivo hasta el resultado. Si el algoritmo no encuentra un ciclo válido, el programa debe registrarlo. Nunca debe presentar como válida una ruta que incumpla las reglas.

## 6 Evaluación y acciones para comenzar

### Cómo prepararemos la comparación

Primero haremos pruebas pequeñas para elegir los grafos y los límites de ejecución que permita el tiempo disponible. La comparación incluirá los seis algoritmos. Registraremos el tamaño de cada grafo sin suponer que un mayor tamaño implica siempre mayor dificultad.

- Anotar en cada prueba el grafo, algoritmo, ajustes, ruta propuesta, validez comprobada, tiempo, motivo de finalización y número de evaluaciones o repeticiones del proceso.

- Registrar también la semilla cuando corresponda. Es el valor inicial que permite repetir la secuencia de decisiones aleatorias de un programa bajo las mismas condiciones.

- Establecer límites comparables de tiempo o evaluaciones y explicar cómo se cuentan. Conservar los resultados fallidos y los casos en que se agota el tiempo.

- Decidir cuántas veces se repetirá cada prueba y justificarlo. Informar el porcentaje de éxitos y cuánto varían los resultados. Explicar cómo se incluyen los intentos sin éxito al resumir los tiempos.

- Registrar la computadora, las versiones de los programas y las condiciones de trabajo. Al comparar con resultados del FHCP, indicar las diferencias de datos, equipo y límites de ejecución.

### Precisión recall y F1

Estos indicadores aparecen en la práctica y deben investigarse. Antes de calcularlos, habrá que definir qué resultado se evalúa, con qué referencia se compara y qué cuenta como acierto o error. El porcentaje de conexiones válidas de una ruta puede describir su calidad, pero no basta con darle tres nombres distintos para obtener precisión, recall y F1. Consultaremos con el profesor cómo espera que se apliquen a este problema.

### Primera reunión del equipo

Asignaremos los cinco temas y sus revisores, elegiremos el espacio compartido y fijaremos fechas para estudiar los conceptos básicos, realizar el taller de GA y entregar las fichas. También abriremos una lista de dudas. Cada integrante terminará la reunión con una tarea concreta y una fecha de revisión. La meta inmediata es comprender y explicar las propuestas antes de programarlas.

### Documentos de referencia del equipo

Práctica Aula invertida Algoritmos heurísticos. Archivo practica.pdf, 3 páginas. Referencia de requisitos y entregables.

Directrices del equipo. Archivo Directrices_Equipo.txt. Propuesta previa de herramientas, arquitectura y reparto.

Documento Maestro de Organización, Arquitectura y Asignación de Roles. PDF de 5 páginas. Plan previo revisado por este documento.
