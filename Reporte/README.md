# Reporte técnico y comparativo

Documento principal: `main.tex` (el PDF ya generado es `main.pdf`). La plantilla de la Fase 1
(`Plantilla d trabajo/`) no se modificó.

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

## Compilar

Requiere en Debian: `sudo apt install texlive-latex-extra texlive-lang-spanish latexmk`
(o subir la carpeta `Reporte/` a Overleaf).

```bash
cd Reporte
latexmk -pdf main.tex
```
