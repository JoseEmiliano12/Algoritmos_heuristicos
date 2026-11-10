"""Artificial Bee Colony discreto para el ciclo hamiltoniano.

Cada fuente es una permutación con el vértice 0 fijo al principio. Las empleadas
intentan mejorar todas las fuentes; las observadoras eligen según 1/(1+costo);
las exploradoras reemplazan fuentes estancadas. La selección es estrictamente
voraz y el mejor resultado histórico se conserva aparte.
"""

import random
import time

from src.fitness import costo, delta_inversion, delta_swap, ruta_aleatoria
from src.algoritmos.ga import mutar_inversion, mutar_swap


def _ruta_inicial(n, rng):
    ruta = ruta_aleatoria(n, rng)
    inicio = ruta.index(0)
    return ruta[inicio:] + ruta[:inicio]


def resolver(adj, max_evals, semilla, tiempo_max=60, fuentes=20,
             limite=100, operador="swap"):
    """Devuelve la mejor ruta, costo, evaluaciones, ciclos e historial.

    Hay ``fuentes`` empleadas y otras tantas observadoras por ciclo completo.
    ``operador`` admite ``swap`` (adaptación del PDF), ``inversion`` o ``mixto``.
    Una evaluación por cada vecina o exploradora; los deltas dan el costo exacto
    de la vecina sin recorrer la ruta completa. ``historial`` guarda el mejor
    costo histórico al final de cada ciclo realizado.
    """
    n = len(adj)
    if n < 3 or not isinstance(max_evals, int) or max_evals < 1:
        raise ValueError("Se requieren n >= 3 y max_evals >= 1")
    if tiempo_max <= 0 or not isinstance(fuentes, int) or fuentes < 1:
        raise ValueError("tiempo_max y fuentes deben ser positivos")
    if not isinstance(limite, int) or limite < 1:
        raise ValueError("limite debe ser al menos 1")
    if operador not in {"swap", "inversion", "mixto"}:
        raise ValueError("operador debe ser swap, inversion o mixto")

    rng = random.Random(semilla)
    inicio_t = time.perf_counter()
    rutas, costos, fallos = [], [], []
    mejor, mejor_costo = None, n + 1
    evals = 0

    for _ in range(min(fuentes, max_evals)):
        if evals and time.perf_counter() - inicio_t >= tiempo_max:
            break
        ruta = _ruta_inicial(n, rng)
        valor = costo(ruta, adj)
        evals += 1
        rutas.append(ruta)
        costos.append(valor)
        fallos.append(0)
        if valor < mejor_costo:
            mejor, mejor_costo = ruta[:], valor
        if valor == 0:
            break

    def hay_presupuesto():
        return evals < max_evals and time.perf_counter() - inicio_t < tiempo_max

    def intentar(indice):
        nonlocal evals, mejor, mejor_costo
        tipo = rng.choice(("swap", "inversion")) if operador == "mixto" else operador
        if tipo == "swap":
            candidata, indices = mutar_swap(rutas[indice], rng, con_indices=True)
            diferencia = delta_swap(rutas[indice], *indices, adj)
        else:
            candidata, indices = mutar_inversion(rutas[indice], rng, con_indices=True)
            diferencia = delta_inversion(rutas[indice], *indices, adj)
        valor = costos[indice] + diferencia
        evals += 1
        if valor < costos[indice]:
            rutas[indice], costos[indice], fallos[indice] = candidata, valor, 0
            if valor < mejor_costo:
                mejor, mejor_costo = candidata[:], valor
        else:
            fallos[indice] += 1

    iters = 0
    historial = []
    while hay_presupuesto() and mejor_costo > 0:
        intentos = 0
        for i in range(len(rutas)):  # Empleadas: una por fuente.
            if not hay_presupuesto() or mejor_costo == 0:
                break
            intentar(i)
            intentos += 1

        for _ in range(len(rutas)):  # Observadoras: selección por calidad.
            if not hay_presupuesto() or mejor_costo == 0:
                break
            pesos = [1.0 / (1 + valor) for valor in costos]
            i = rng.choices(range(len(rutas)), weights=pesos)[0]
            intentar(i)
            intentos += 1

        for i in range(len(rutas)):  # Exploradoras: reemplazo por estancamiento.
            if not hay_presupuesto() or mejor_costo == 0:
                break
            if fallos[i] >= limite:
                ruta = _ruta_inicial(n, rng)
                valor = costo(ruta, adj)
                evals += 1
                intentos += 1
                rutas[i], costos[i], fallos[i] = ruta, valor, 0
                if valor < mejor_costo:
                    mejor, mejor_costo = ruta[:], valor

        if not intentos:
            break
        iters += 1
        historial.append(mejor_costo)

    return {"ruta": mejor, "costo": mejor_costo, "evals": evals,
            "iters": iters, "historial": historial}
