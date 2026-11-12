"""Algoritmo genético de control para buscar ciclos hamiltonianos.

Las rutas son permutaciones de 0..n-1. El vértice 0 se deja al principio para
evitar rotaciones equivalentes; el cierre de la ruta queda implícito. Los
operadores también se comparten con la adaptación discreta de ABC.
"""

import random
import time

from src.fitness import costo, ruta_aleatoria


def _indices(ruta, rng):
    """Elige dos posiciones distintas sin mover el vértice inicial."""
    if len(ruta) < 3:
        return None
    return sorted(rng.sample(range(1, len(ruta)), 2))


def mutar_swap(ruta, rng, *, con_indices=False):
    """Devuelve una copia con dos posiciones intercambiadas.

    ``con_indices=True`` devuelve además (i, j) para calcular el costo por
    delta en ABC. Nunca modifica la ruta recibida.
    """
    nueva = list(ruta)
    indices = _indices(ruta, rng)
    if indices is not None:
        i, j = indices
        nueva[i], nueva[j] = nueva[j], nueva[i]
    return (nueva, indices) if con_indices else nueva


def mutar_inversion(ruta, rng, *, con_indices=False):
    """Devuelve una copia con un tramo invertido, conservando el inicio."""
    nueva = list(ruta)
    indices = _indices(ruta, rng)
    if indices is not None:
        i, j = indices
        nueva[i:j + 1] = reversed(nueva[i:j + 1])
    return (nueva, indices) if con_indices else nueva


def cruce_ox(p1, p2, rng):
    """Cruce de orden OX: conserva un tramo de p1 y el orden restante de p2.

    Ambos padres deben contener los mismos vértices y comenzar por el mismo.
    El descendiente siempre es una permutación válida y conserva ese inicio.
    """
    n = len(p1)
    if n != len(p2) or n < 3 or p1[0] != p2[0] or set(p1) != set(p2):
        raise ValueError("OX requiere dos permutaciones compatibles de al menos 3 vértices")
    i, j = sorted(rng.sample(range(1, n), 2))
    hijo = [None] * n
    hijo[0] = p1[0]
    hijo[i:j + 1] = p1[i:j + 1]
    presentes = set(hijo[i:j + 1]) | {p1[0]}
    # En OX se recorren padre y descendiente desde el punto posterior al corte.
    posiciones = list(range(j + 1, n)) + list(range(1, j + 1))
    valores = [p2[k] for k in posiciones if p2[k] not in presentes]
    huecos = [k for k in posiciones if hijo[k] is None]
    for k, valor in zip(huecos, valores):
        hijo[k] = valor
    assert None not in hijo and len(set(hijo)) == n
    return hijo


def _ruta_inicial(n, rng):
    ruta = ruta_aleatoria(n, rng)
    inicio = ruta.index(0)
    return ruta[inicio:] + ruta[:inicio]


def _torneo(poblacion, tam_torneo, rng):
    candidatos = rng.sample(poblacion, min(tam_torneo, len(poblacion)))
    return min(candidatos, key=lambda individuo: individuo[1])[0]


def resolver(adj, max_evals, semilla, tiempo_max=60, tam_poblacion=40,
             prob_cruce=0.9, prob_mutacion=0.3, tam_torneo=3,
             elitismo=2, prob_inversion=0.5):
    """Busca un ciclo con OX, torneo, mutación y elitismo.

    Cada ruta nueva evaluada cuenta una evaluación; copiar élites no cuenta.
    ``iters`` y ``historial`` incluyen la población inicial como generación 1.
    El tiempo se revisa antes de cada evaluación posterior a la primera.
    """
    n = len(adj)
    if n < 3 or not isinstance(max_evals, int) or max_evals < 1:
        raise ValueError("Se requieren n >= 3 y max_evals >= 1")
    if tiempo_max <= 0 or tam_poblacion < 2 or tam_torneo < 1 or not 0 <= elitismo < tam_poblacion:
        raise ValueError("Parámetros de tiempo, población, torneo o elitismo inválidos")
    if any(not 0 <= p <= 1 for p in (prob_cruce, prob_mutacion, prob_inversion)):
        raise ValueError("Las probabilidades deben estar entre 0 y 1")

    rng = random.Random(semilla)
    inicio_t = time.perf_counter()
    poblacion = []
    mejor, mejor_costo = None, n + 1
    evals = 0
    for _ in range(min(tam_poblacion, max_evals)):
        if evals and time.perf_counter() - inicio_t >= tiempo_max:
            break
        ruta = _ruta_inicial(n, rng)
        valor = costo(ruta, adj)
        evals += 1
        poblacion.append((ruta, valor))
        if valor < mejor_costo:
            mejor, mejor_costo = ruta[:], valor
        if valor == 0:
            break

    iters = 1
    historial = [mejor_costo]
    while evals < max_evals and mejor_costo > 0 and time.perf_counter() - inicio_t < tiempo_max:
        objetivo = len(poblacion)
        elites = sorted(poblacion, key=lambda individuo: individuo[1])[:min(elitismo, objetivo - 1)]
        nueva_poblacion = [(ruta[:], valor) for ruta, valor in elites]
        generados = 0
        while (len(nueva_poblacion) < objetivo and evals < max_evals
               and time.perf_counter() - inicio_t < tiempo_max):
            p1 = _torneo(poblacion, tam_torneo, rng)
            p2 = _torneo(poblacion, tam_torneo, rng)
            cruzado = rng.random() < prob_cruce
            hijo = cruce_ox(p1, p2, rng) if cruzado else p1[:]
            # Sin cruce, mutar siempre: evaluar una copia exacta del padre gasta presupuesto.
            if not cruzado or rng.random() < prob_mutacion:
                mutar = mutar_inversion if rng.random() < prob_inversion else mutar_swap
                hijo = mutar(hijo, rng)
            valor = costo(hijo, adj)
            evals += 1
            generados += 1
            nueva_poblacion.append((hijo, valor))
            if valor < mejor_costo:
                mejor, mejor_costo = hijo[:], valor
            if valor == 0:
                break
        if not generados:
            break
        poblacion = nueva_poblacion
        iters += 1
        historial.append(mejor_costo)

    return {"ruta": mejor, "costo": mejor_costo, "evals": evals,
            "iters": iters, "historial": historial}
