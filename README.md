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
bash datos/descargar_fhcp.sh
python3 pruebas/verificar_resultados.py
```
