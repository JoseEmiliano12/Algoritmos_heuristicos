# Entregable 3 — Ciclo hamiltoniano y FHCP

Este directorio contiene el programa, las instancias del FHCP Challenge Set, los registros de ejecución, las rutas encontradas, las tablas y el reporte final. El reporte formal está en **Reporte.pdf**. No se necesita el código fuente de LaTeX para consultar el entregable.

## Contenido

- `Reporte.pdf`: fundamentos, método, diseños A/B/C, resultados anteriores, comparación entre equipos, optimización y nuevas pruebas, limitaciones y conclusiones.
- `src/`: lectura de grafos, función de costo, verificación de ciclos y algoritmos. Incluye GA, SA, ACO, ABC, DE, PSO y los métodos combinados añadidos para el Challenge.
- `datos/`: ejemplos y el conjunto completo de 1,001 instancias FHCP, con sus archivos de solución oficial.
- `resultados/`: registros JSONL, rutas TOUR, tablas CSV, figuras y `Resumen_Entregable_3.xlsx`. Se conservan también los archivos de repetición de la Dell G7 para respaldar la comparación del reporte.
- `pruebas/`: pruebas automáticas y verificadores independientes de los resultados registrados.
- `scripts/`: generación de resúmenes y gráficas, más el lanzador de la campaña de 45 semillas.
- `requirements.txt`: dependencias para generar las figuras.

## Estado de las campañas

| Campaña | Registro disponible | Resultado |
|---|---:|---|
| Diseño A | 1,680/1,680 corridas | Completo |
| Diseño B | 400/400 corridas | Completo |
| Diseño C | 32/32 corridas | Completo |
| Método combinado LNS, 1,001 grafos | 2,656 intentos | 200 grafos con ciclo verificado y archivo TOUR |
| Extensión ACO + Pósa y ABC, 45 semillas previstas | 1,315/90,090 corridas | Parcial; 55 corridas exitosas y 31 grafos distintos |

Las dos campañas nuevas usan presupuestos y métodos distintos. Sus cifras de éxito no deben sumarse como si fueran una misma ejecución. La extensión de 45 semillas solo tiene registros para las semillas 0 y 1; las demás siguen pendientes. Las duraciones acumuladas de los intentos no representan tiempo total de reloj cuando se usan varios procesos.

## Cómo revisar y ejecutar

Desde esta carpeta:

```bash
python3 -m unittest discover -s pruebas -t . -q
python3 pruebas/verificar_resultados.py
python3 pruebas/verificar_challenge.py
python3 -m src.challenge --resumen
python3 scripts/challenge.py --resumen
```

Para consultar las corridas pendientes antes de continuar:

```bash
python3 -m src.experimentos A --dry-run
python3 scripts/challenge.py --dry-run
```

Ejemplos de ejecución:

```bash
python3 -m src datos/fhcp_completo/graph4.hcp --alg lns --semilla 0 --tiempo 10
python3 -m src.challenge --procesos 6
python3 scripts/challenge.py --procesos 6
```

Las campañas leen los registros existentes y omiten combinaciones ya ejecutadas. Conviene usar un número de procesos acorde con la memoria disponible. Para regenerar las figuras se instalan primero las dependencias con `python3 -m pip install -r requirements.txt`.

Conjunto oficial: <https://sites.flinders.edu.au/flinders-hamiltonian-cycle-project/fhcp-challenge-set/>.
