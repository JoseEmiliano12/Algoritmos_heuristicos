# Integrante 2 — Fabian: representación/fitness + Colonia de Hormigas (ACO)

Plan general y contrato: `PLAN_IMPLEMENTACION.md` (raíz). Investigación: capítulo 3 del PDF integrado.

## Fase 0 (hoy)

1. Subir la rama `integracion`: `git push -u origin integracion`.
2. Avisar al equipo que creen su rama desde ahí: `git fetch && git switch -c impl/<alg> origin/integracion`.

## Primero (Fase 1, bloquea a todos) — `src/fitness.py`

Sin dependencias. Grafo = `adj: list[set[int]]`, vértices 0..n-1.

```python
def costo(ruta, adj) -> int
    # nº de pares consecutivos (incluido el cierre ruta[-1] -> ruta[0]) que NO son arista
def delta_swap(ruta, i, j, adj) -> int
    # cambio de costo si se intercambian ruta[i] y ruta[j], en O(1) (cuidado con i, j vecinos y con el cierre)
def delta_inversion(ruta, i, j, adj) -> int
    # cambio de costo si se invierte ruta[i..j] (2-opt), O(1)
def es_ciclo_hamiltoniano(ruta, adj) -> bool
    # longitud n, sin repetidos, todos los vértices, todas las aristas y el cierre
def ruta_aleatoria(n, rng) -> list[int]
```

Incluir un `if __name__ == "__main__":` con asserts: los deltas coinciden con
`costo(después) - costo(antes)` en miles de swaps/inversiones aleatorios (incluidos índices vecinos y los extremos).
Esa es la prueba más importante del proyecto: SA, ABC y GA dependen de ella.

## Fase 2 — `src/algoritmos/aco.py` (algoritmo principal)

- Feromona τ solo en aristas que existen (`dict` o matriz n×n si n es pequeño).
- Cada hormiga: vértice inicial aleatorio, avanza a un vecino **no visitado** con probabilidad ∝ τ^α · η^β,
  η = 1 / (1 + nº de vecinos libres de ese vecino) (regla de Warnsdorff).
- Si se atasca: agregar los no visitados al final → permutación completa → `costo()` (1 evaluación por hormiga).
- Evaporación ρ y depósito en las aristas del camino de la mejor hormiga (variante MMAS con τ_min/τ_max).
- Opcional: extensión por rotación de Pósa cuando la hormiga se atasca. Si se usa, documentarlo como variante.

Parámetros a calibrar: nº de hormigas, α, β, ρ, τ_min/τ_max.

## Terminado cuando

- Los asserts de `fitness.py` pasan.
- `pruebas/probar_algoritmo.py` (de Barbie) pasa con ACO.

## Reporte

Mapeo de la representación del problema y la función de fitness; sección de ACO.
