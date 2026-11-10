"""Recocido simulado para grafos simples no dirigidos, sin dependencias externas.

Se minimizan las conexiones faltantes, incluido el cierre, usando src.fitness.
La evaluación inicial y cada vecino (incluso rechazado) consumen presupuesto.
Los parámetros son valores de partida, no una calibración sobre el FHCP.
"""

import math
import random
import time

from src.fitness import (
    costo, delta_inversion, delta_swap, es_ciclo_hamiltoniano, ruta_aleatoria,
)


def resolver(adj, max_evals, semilla, tiempo_max=60, T0=None, alfa=0.9999,
             T_min=1e-6, vecino="mixto"):
    """Devuelve ruta, costo, evals, iters e historial según el contrato común.

    ``vecino``: "swap", "inversion" o "mixto" (predeterminado: mitad de cada uno).
    Se fija el primer vértice y se eligen uniformemente dos índices restantes.
    ``T0=None`` acepta un aumento de costo de 1 con probabilidad inicial 0.8.
    Se enfría tras cada propuesta; iters cuenta las propuestas evaluadas.
    historial contiene el mejor costo inicial y luego cada 100 evaluaciones,
    incluyendo siempre el valor final. Los deltas cuestan O(1); aplicar una
    inversión aceptada cuesta O(longitud del segmento).

    El tiempo se comprueba entre propuestas; no interrumpe operaciones en curso.
    Con presupuesto suficiente la misma semilla reproduce el resultado. Si el
    reloj corta una ejecución, el número de propuestas puede variar.
    """
    inicio = time.perf_counter()
    n = len(adj)
    if n < 3:
        raise ValueError("El grafo debe tener al menos tres vértices.")
    for u, vecinos in enumerate(adj):
        for v in vecinos:
            if (not isinstance(v, int) or not 0 <= v < n or v == u
                    or u not in adj[v]):
                raise ValueError("Se requiere un grafo simple no dirigido con vértices 0..n-1.")
    if not isinstance(max_evals, int) or isinstance(max_evals, bool) or max_evals < 1:
        raise ValueError("max_evals debe ser un entero positivo.")
    if T0 is None:
        T0 = -1.0 / math.log(0.8)
    if not all(math.isfinite(x) for x in (T0, T_min, alfa, tiempo_max)):
        raise ValueError("Los parámetros numéricos deben ser finitos.")
    if not T0 > T_min > 0 or not 0 < alfa < 1 or tiempo_max <= 0:
        raise ValueError("Se requiere T0 > T_min > 0, 0 < alfa < 1 y tiempo_max > 0.")
    if vecino not in ("swap", "inversion", "mixto"):
        raise ValueError("vecino debe ser swap, inversion o mixto.")

    rng = random.Random(semilla)
    actual = ruta_aleatoria(n, rng)
    # Rotar conserva el ciclo y permite mantener el vértice 0 en el inicio.
    posicion = actual.index(0)
    actual = actual[posicion:] + actual[:posicion]
    c_actual = costo(actual, adj)
    mejor, c_mejor = actual[:], c_actual
    evals, iters = 1, 0
    historial = [c_mejor]
    T = T0

    while (evals < max_evals and c_mejor > 0 and T > T_min
           and time.perf_counter() - inicio < tiempo_max):
        i, j = sorted(rng.sample(range(1, n), 2))
        movimiento = vecino
        if movimiento == "mixto":
            movimiento = rng.choice(("swap", "inversion"))
        delta = (delta_swap(actual, i, j, adj) if movimiento == "swap"
                 else delta_inversion(actual, i, j, adj))
        evals += 1
        iters += 1
        if delta <= 0 or rng.random() < math.exp(-delta / T):
            if movimiento == "swap":
                actual[i], actual[j] = actual[j], actual[i]
            else:
                actual[i:j + 1] = actual[i:j + 1][::-1]
            c_actual += delta
            if c_actual < c_mejor:
                mejor, c_mejor = actual[:], c_actual
        if evals % 100 == 0:
            historial.append(c_mejor)
        T *= alfa

    # Una comprobación completa adicional no participa en la búsqueda ni en
    # su presupuesto de fitness, como la validación externa del experimento.
    if c_mejor == 0 and not es_ciclo_hamiltoniano(mejor, adj):
        raise RuntimeError("El costo cero no pasó la verificación del ciclo.")
    if evals % 100 != 0 and evals != 1:
        historial.append(c_mejor)
    return {"ruta": mejor, "costo": c_mejor, "evals": evals,
            "iters": iters, "historial": historial}


if __name__ == "__main__":
    from pruebas.probar_algoritmo import probar_algoritmo

    probar_algoritmo(resolver, max_evals=200_000)
