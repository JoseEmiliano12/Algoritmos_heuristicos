"""Portafolio: alterna ramificación y poda (``rp``) con la búsqueda local ``posa_lk``.

Los dos métodos fallan en grafos distintos: ``rp`` resuelve en milisegundos grafos cúbicos
con muy pocos ciclos (donde la búsqueda local se queda a una arista), y ``posa_lk`` resuelve
grafos más densos o grandes donde el árbol de búsqueda explota. Se ejecutan por turnos con
ventanas de tiempo que se duplican; ``posa_lk`` continúa desde su mejor ruta anterior.
"""
import time

from src.algoritmos import posa_lk, rp
from src.fitness import validar_parametros


def resolver(adj, max_evals, semilla, tiempo_max=60, ventana=2.0, **params):
    n = len(adj)
    validar_parametros(n, max_evals, tiempo_max)
    t_fin = time.perf_counter() + tiempo_max
    evals = iters = 0
    historial = []
    mejor = None
    ronda = 0
    while True:
        resto = t_fin - time.perf_counter()
        if resto <= 0 or evals >= max_evals:
            break
        v = min(resto, ventana * 2 ** ronda)
        for i, metodo in enumerate((rp, posa_lk)):
            resto = t_fin - time.perf_counter()
            if resto <= 0 or evals >= max_evals:
                break
            extra = {}
            if metodo is posa_lk and mejor is not None and mejor["costo"] > 0:
                extra["ruta_inicial"] = mejor["ruta"]
            r = metodo.resolver(adj, max_evals - evals, semilla * 1000 + 2 * ronda + i,
                                tiempo_max=min(v, resto), **extra)
            evals += r["evals"]
            iters += r["iters"]
            if mejor is None or r["costo"] < mejor["costo"]:
                mejor = r
            historial.append(mejor["costo"])
            if mejor["costo"] == 0:
                break
        if mejor["costo"] == 0:
            break
        ronda += 1
    return {"ruta": mejor["ruta"], "costo": mejor["costo"], "evals": max(evals, 1),
            "iters": iters, "historial": historial}
