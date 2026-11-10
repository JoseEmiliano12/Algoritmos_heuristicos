"""Artificial Bee Colony discreto para el ciclo hamiltoniano.

Cada fuente es una permutación con el vértice 0 fijo al principio. Las empleadas
intentan mejorar todas las fuentes; las observadoras eligen fuentes con probabilidad
proporcional a ``exp(-(costo - costo_min))`` (con costos cercanos a n, ``1/(1+costo)`` es
casi uniforme y no distingue calidad); las exploradoras reemplazan fuentes estancadas,
salvo la mejor fuente actual. El mejor resultado histórico se conserva aparte.

Selección voraz con empates (``<=``): en grafos dispersos casi todos los movimientos
dejan el costo igual y rechazarlos congela la búsqueda. Un empate no reinicia el contador
de fallos, así que el abandono por estancamiento sigue funcionando.

Operadores: ``swap`` (adaptación del PDF), ``inversion``, ``mixto`` y ``guiado`` (por
defecto). ``guiado`` es la versión "camino prometedor" del enunciado: busca una conexión
rota y la sustituye por una arista real del grafo (``operadores.inversion_guiada``).
"""

import random
import time

import math

from src.fitness import costo, delta_inversion, delta_swap, ruta_anclada
from src.algoritmos.ga import mutar_inversion, mutar_swap
from src.operadores import inversion_guiada


def resolver(adj, max_evals, semilla, tiempo_max=60, fuentes=20,
             limite=None, operador="guiado"):
    """Devuelve la mejor ruta, costo, evaluaciones, ciclos e historial.

    Hay ``fuentes`` empleadas y otras tantas observadoras por ciclo completo.
    ``operador`` admite ``guiado`` (predeterminado), ``swap`` (adaptación del PDF),
    ``inversion`` o ``mixto``. ``limite=None`` usa ``2·n`` intentos sin mejora.
    Una evaluación por cada vecina o exploradora; los deltas dan el costo exacto
    de la vecina sin recorrer la ruta completa. ``historial`` guarda el mejor
    costo histórico tras la inicialización (ciclo 1) y al final de cada ciclo.
    """
    n = len(adj)
    if n < 3 or not isinstance(max_evals, int) or max_evals < 1:
        raise ValueError("Se requieren n >= 3 y max_evals >= 1")
    if tiempo_max <= 0 or not isinstance(fuentes, int) or fuentes < 1:
        raise ValueError("tiempo_max y fuentes deben ser positivos")
    if limite is None:
        limite = 2 * n
    if not isinstance(limite, int) or limite < 1:
        raise ValueError("limite debe ser al menos 1")
    if operador not in {"swap", "inversion", "mixto", "guiado"}:
        raise ValueError("operador debe ser guiado, swap, inversion o mixto")

    rng = random.Random(semilla)
    inicio_t = time.perf_counter()
    rutas, costos, fallos = [], [], []
    mejor, mejor_costo = None, n + 1
    evals = 0

    for _ in range(min(fuentes, max_evals)):
        if evals and time.perf_counter() - inicio_t >= tiempo_max:
            break
        ruta = ruta_anclada(n, rng)
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
        indices = inversion_guiada(rutas[indice], adj, rng) if tipo == "guiado" else None
        if tipo == "guiado" and indices is None:
            tipo = "inversion"  # ruta sin conexiones rotas aprovechables: 2-opt aleatorio
        if tipo == "guiado":
            i, j = indices
            candidata = rutas[indice][:]
            candidata[i:j + 1] = candidata[i:j + 1][::-1]
            diferencia = delta_inversion(rutas[indice], i, j, adj)
        elif tipo == "swap":
            candidata, indices = mutar_swap(rutas[indice], rng, con_indices=True)
            diferencia = delta_swap(rutas[indice], *indices, adj)
        else:
            candidata, indices = mutar_inversion(rutas[indice], rng, con_indices=True)
            diferencia = delta_inversion(rutas[indice], *indices, adj)
        valor = costos[indice] + diferencia
        evals += 1
        if valor <= costos[indice]:
            # Un empate se acepta (deriva por la meseta) pero cuenta como fallo.
            fallos[indice] = 0 if valor < costos[indice] else fallos[indice] + 1
            rutas[indice], costos[indice] = candidata, valor
            if valor < mejor_costo:
                mejor, mejor_costo = candidata[:], valor
        else:
            fallos[indice] += 1

    iters = 1
    historial = [mejor_costo]
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
            minimo = min(costos)
            pesos = [math.exp(minimo - valor) for valor in costos]
            i = rng.choices(range(len(rutas)), weights=pesos)[0]
            intentar(i)
            intentos += 1

        protegida = costos.index(min(costos))
        for i in range(len(rutas)):  # Exploradoras: reemplazo por estancamiento.
            if not hay_presupuesto() or mejor_costo == 0:
                break
            if fallos[i] >= limite and i != protegida:
                ruta = ruta_anclada(n, rng)
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
