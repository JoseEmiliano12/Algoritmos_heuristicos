# Integrante 5 — Israel (confirmar): dataset FHCP, lector HCP + Enjambre de Partículas (PSO)

Plan general y contrato: `PLAN_IMPLEMENTACION.md` (raíz). Investigación: capítulo 6 del PDF integrado.

## Primero (Fase 1) — dataset y `src/grafo.py`

1. Descargar el FHCP Challenge Set de
   https://sites.flinders.edu.au/flinders-hamiltonian-cycle-project/fhcp-challenge-set/ y descomprimir en `datos/`.
2. Hacer una tabla `datos/instancias.csv` con `grafo, n, m` (vértices y aristas de cada archivo).
3. Proponer al equipo: 3 instancias de **calibración** y 5–10 de **evaluación** (las más pequeñas, distintas entre sí).
   Si el set completo pesa mucho, subir a git solo esas instancias y anotar el enlace de descarga.

```python
def leer_hcp(ruta_archivo) -> tuple[str, int, list[set[int]]]:
    """Lee NAME, DIMENSION y EDGE_DATA_SECTION (pares 1..n, termina en -1/EOF).
    Devuelve (nombre, n, adj) con vértices 0..n-1. Validar rangos y avisar si hay lazos o aristas repetidas."""

def escribir_tour(ruta, ruta_archivo, nombre):
    """Formato TOUR del PDF (cap. 6): vértices 1..n, uno por línea, termina en -1 y EOF."""
```

Probar con el ejemplo `ciclo5` del PDF: leer → escribir el tour → volver a leerlo.

## Fase 2 — `src/algoritmos/pso.py`

- Partícula = vector de n **random keys**; decodificar con `argsort` (empates por identificador) → `costo()`.
- `v ← w·v + c1·r1·(p_i − x) + c2·r2·(g − x)`, `x ← x + v`; recortar x a [0,1] y v a ±v_max.
- Actualizar el mejor global después de cada partícula (como dice la investigación).
- Parámetros: tamaño del enjambre S, w, c1, c2, v_max.

Si quieres, puedes reutilizar la decodificación por random keys de `de.py` (Jesús): pónganse de acuerdo en quién la escribe.

## Fase 5 — Benchmarking contra el FHCP

Contrastar nuestra cobertura (instancias resueltas) con los resultados oficiales (el mejor equipo resolvió
985 de 1001). **Falta investigar qué métodos usaron los mejores** (artículos del propio proyecto FHCP):
hace falta para esa sección del reporte.

## Terminado cuando

- `leer_hcp` carga todas las instancias elegidas sin errores y `datos/instancias.csv` existe.
- `pruebas/probar_algoritmo.py` pasa con PSO.

## Reporte

Dataset y formatos; benchmarking contra el FHCP; sección de PSO.
