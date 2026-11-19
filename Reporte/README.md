# Reporte técnico y comparativo

Documento principal: `main.tex` (el PDF ya generado es `main.pdf`). La investigación
previa de la Fase 1 está en `../Investigacion_previa.pdf`.

El diseño interior usa un estilo de tesis con encabezado institucional, fondo geométrico
discreto, numeración, índice general e índice analítico. El
logotipo del encabezado se extrajo de `Portada.pdf`; la portada original se conserva.

| Archivo | Sección |
|---|---|
| `capitulos/introduccion.tex` | 1. Introducción |
| `capitulos/grafo.tex` | 2. El grafo y el ciclo hamiltoniano |
| `capitulos/representacion.tex` | 3. Representación y función de costo |
| `capitulos/algoritmos.tex` | 4. Algoritmos (GA, SA, ACO, ABC, DE, PSO) |
| `capitulos/diseno.tex` | 5. Cómo hicimos los experimentos y verificación |
| `capitulos/comparativa.tex` | 6. Comparación de resultados |
| `capitulos/benchmarking.tex` | 7. Comparación con el FHCP Challenge |
| `capitulos/conclusiones.tex` | 8. Conclusiones |
| `capitulos/anexo_codigo.tex` | Anexo: cómo ejecutar el código |

No edites `tablas/` ni `figuras/`: se generan. Las cifras del texto usan macros de
`tablas/datos.tex` (p. ej. `\exitosAABC`), así que se actualizan solas.

## Actualizar tablas y figuras (si se vuelven a correr los experimentos)

```bash
# desde la raíz del repositorio, con el entorno activado
python -m src.graficas resultados/disenoA.jsonl   # y B, C
python Reporte/actualizar.py
```

Ojo: algunas frases del texto citan números concretos (tiempos medianos, aristas faltantes en
graph1001, etc.). Si cambian los resultados, revisa las secciones 6, 7 y 8.

## FHCP Challenge completo con 45 semillas

Desde la raíz del repositorio, con `datos/fhcp_completo/` descargado:

```bash
python Reporte/challenge.py --dry-run       # muestra las corridas pendientes
python Reporte/challenge.py --procesos 10   # 1001 grafos × 2 algoritmos × 45 semillas
python Reporte/challenge.py --resumen       # genera CSV global y por grafo
python Reporte/graficas_challenge.py        # genera gráficas desde el JSONL
```

Para iniciar o reanudar todo el proceso y generar las gráficas automáticamente al
terminar, ejecuta `bash Reporte/ejecutar_challenge_completo.sh 10`. El avance se
guarda en `Reporte/challenge_1001_45.log` cuando se lanza en segundo plano.

El experimento usa las semillas 0 a 44, guarda las corridas en
`resultados/challenge_1001_45.jsonl` y se puede reanudar con el mismo comando. Los CSV son
`resultados/challenge_1001_45_resumen.csv` y `resultados/challenge_1001_45_grafos.csv`.
Para usar otra cantidad de semillas, añade `--semillas N` a los comandos;
cada configuración tiene sus propios archivos.
El resumen indica cuántas corridas se han completado; las tasas de un experimento parcial
solo describen las corridas ya terminadas. El reporte actual sigue reflejando el diseño B
anterior (100 grafos, 2 semillas) hasta que se incorporen los resultados nuevos.
Las gráficas se guardan en `resultados/challenge_1001_45_graficas/` y señalan si
los datos son parciales.

## Compilar

Requiere en Debian: `sudo apt install texlive-latex-extra texlive-lang-spanish texlive-pictures latexmk`
(o subir la carpeta `Reporte/` a Overleaf).

```bash
cd Reporte
latexmk -pdf main.tex
```
