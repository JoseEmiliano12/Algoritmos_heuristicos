# Investigación integrada — Fase 1

Abrir `main.tex` como documento principal. Todo lo necesario para el documento está en esta carpeta; `investigacion.tex` de la raíz se conserva sin modificar.

## Compilación

Con una instalación de TeX Live o MiKTeX que incluya los paquetes usados, ejecutar desde esta carpeta:

```sh
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

También se puede subir esta carpeta completa a Overleaf y seleccionar `main.tex` como archivo principal. La bibliografía está en `fuentes.tex` y `fuentes_complementarias.tex` y usa `thebibliography`: no necesita BibTeX, Biber ni el archivo ausente `apalike-es.bst`.

La compilación local con TeX Live 2026 y latexmk se verificó correctamente y generó `main.pdf` (66 páginas). Se corrigieron dos errores de integración que la revisión estática no detectaba: el entorno `definicion` y comandos `\noindent` unidos al texto. Puede haber advertencias de maquetación; no equivalen a errores de compilación.

Hay configuración de LaTeX Workshop en `.vscode/settings.json`, tanto en la raíz del proyecto como en esta carpeta. Usa explícitamente TeX Live instalado en `/srv/sst/.local/texlive`. Después de abrir esta carpeta en VS Code, recargar la ventana y crear una terminal nueva. En una terminal externa, activar la ruta con:

```bash
export PATH="/srv/sst/.local/texlive/bin/x86_64-linux:$PATH"
latexmk -pdf main.tex
```


## Contenido y procedencia

Se consultaron las referencias de ramas disponibles localmente, sin incorporar contenido de `main` ni `origin/main`:

| Fuente | Revisión | Incorporación |
| --- | --- | --- |
| `origin/1`, `integrante_1_grafos_y_sa/Investigación.pdf` | `d3d38bd` | Capítulo `sa.tex`: transcripción adaptada de fundamentos, aceptación, ejemplo, pseudocódigo, parámetros, limitaciones y fuentes. |
| `origin/representacion_y_aco`, `integrante_2_representacion_y_aco/investigacion.tex` | `96751f4` | Capítulo `aco.tex`: contenido, ejemplo, figura, pseudocódigo y referencias. |
| `origin/Heuristicas-y-colonia-de-abejas`, `integrante_3_heuristicas_y_abejas/investigacion.tex` | `531909e` | Capítulo `abc.tex`: módulo evolutivo, GA, ABC, ejemplos, pseudocódigo y referencias. |
| `D4` / `origin/D4` | `b02a0e1` | Esta revisión solo contiene README; no hay investigación versionada en ella. |
| `origin/documentacion/investigacion-equipo` | `78e7e2a` | README de distribución temática; no contiene un documento de investigación adicional. |
| `Plantilla d trabajo/main.tex` original, archivo local sin seguimiento | Copia en `fuentes_originales` | Investigación extensa de métricas y DE, integrada en `de.tex`. No se atribuye a una rama que no la contiene. |
| `investigacion.tex` de la raíz, archivo local sin seguimiento | Copia en `fuentes_originales` | Complemento de FHCP, PSO y propuesta experimental, además de la síntesis de fundamentos y correcciones. |

Los PDF y TEX de una misma aportación no se duplican como capítulos. Se conservan copias de los documentos fuente en `fuentes_originales`. El PDF anterior de la plantilla se encuentra allí como `pdf_plantilla_anterior.pdf`; no es el resultado de esta integración.

## Formato y correcciones

- Se conserva literalmente el bloque de portada de la plantilla y su fondo `Portada.pdf`, además de nombres, materia, profesor y fecha.
- El original invocaba `\programa` sin definirlo. Se define vacío para conservar el espacio sin inventar una carrera. Se puede completar en `main.tex`.
- El cuerpo usa tipografía y encabezados estándar de la clase `report`, sin colores de texto, recuadros ni negritas/cursivas decorativas. Se conservan ecuaciones, tablas, figura y pseudocódigo como contenido; las tablas anchas se ajustan al ancho disponible.
- Se unifican citas numéricas y se separan las etiquetas internas de cada capítulo. Se mantienen las notas de los autores sobre fuentes pendientes de consulta completa.
- Se distingue permutación válida de ciclo factible y resultado inconcluso de prueba de no hamiltonicidad.
- Se corrige la afirmación de que tomar una componente del donante en DE garantiza cambiar la solución.
- Se distinguen reglas históricas del FHCP y protocolo académico propuesto; se incluyen ejemplos completos HCP/TOUR.
- Se atribuye la inercia de PSO a la modificación de 1998 y se completa su adaptación, pseudocódigo y ejemplo.
- Los ejemplos conservados o añadidos son didácticos, no resultados experimentales.

Las referencias repetidas entre aportaciones conservan entradas separadas para mantener la trazabilidad y las notas sobre lo que respalda cada fuente. La página oficial del FHCP se contrastó durante la integración: https://sites.flinders.edu.au/flinders-hamiltonian-cycle-project/fhcp-challenge-set/
