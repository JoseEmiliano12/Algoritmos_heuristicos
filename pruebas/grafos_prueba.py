"""Grafos didácticos reproducibles; no son instancias del FHCP."""

import random


def ciclo5():
    """Ciclo 0-1-2-3-4-0 del documento de investigación."""
    return [{1, 4}, {0, 2}, {1, 3}, {2, 4}, {0, 3}]


def grafo_con_ciclo(n, aristas_extra, semilla):
    """Planta un ciclo aleatorio y agrega exactamente aristas_extra aristas.

    Devuelve (adj, ciclo) sin lazos ni aristas repetidas. No revela el ciclo al
    algoritmo: solo las pruebas lo usan para comprobar el generador.
    """
    if not isinstance(n, int) or isinstance(n, bool) or n < 3:
        raise ValueError("n debe ser un entero de al menos 3.")
    disponibles = n * (n - 1) // 2 - n
    if (not isinstance(aristas_extra, int) or isinstance(aristas_extra, bool)
            or not 0 <= aristas_extra <= disponibles):
        raise ValueError(f"aristas_extra debe estar entre 0 y {disponibles}.")
    rng = random.Random(semilla)
    ciclo = list(range(n))
    rng.shuffle(ciclo)
    adj = [set() for _ in range(n)]

    def agregar(u, v):
        adj[u].add(v)
        adj[v].add(u)

    for k in range(n):
        agregar(ciclo[k - 1], ciclo[k])
    # En grafos dispersos no se materializan las O(n²) parejas posibles.
    # Para completar grafos densos se muestrean las parejas restantes sin rechazo.
    if aristas_extra > disponibles // 2:
        faltantes = [(u, v) for u in range(n) for v in range(u + 1, n)
                     if v not in adj[u]]
        for u, v in rng.sample(faltantes, aristas_extra):
            agregar(u, v)
    else:
        agregadas = 0
        while agregadas < aristas_extra:
            u, v = rng.sample(range(n), 2)
            if v not in adj[u]:
                agregar(u, v)
                agregadas += 1
    return adj, ciclo
