"""Reducción del grafo por aristas forzadas (preprocesamiento exacto, no heurístico).

Reglas clásicas para el ciclo hamiltoniano, aplicadas hasta un punto fijo:

1. Un vértice de grado 2 obliga a usar sus dos aristas.
2. Un vértice con dos aristas forzadas no puede usar ninguna otra: se eliminan.
3. Las aristas forzadas forman caminos; si los extremos ``a`` y ``b`` de un camino forzado
   que no cubre todos los vértices son adyacentes, la arista ``a-b`` cerraría un ciclo
   prematuro: se elimina.

Ninguna regla descarta un ciclo hamiltoniano, así que todo ciclo del grafo reducido lo es
también del original. En el FHCP, 536 de los 1001 grafos tienen vértices de grado 2.

Probar: ``python3 -m src.reduccion datos/fhcp/graph5.hcp``
"""
from collections import deque


class SinCiclo(Exception):
    """La reducción demostró que el grafo no tiene ciclo hamiltoniano."""


def reducir(adj, forzadas=()):
    """Devuelve ``(adj_reducido, forzadas)``; ``forzadas[v]`` es una lista de ≤ 2 vecinos.

    ``forzadas`` (opcional): pares ``(u, v)`` que se imponen desde fuera (p. ej. tramos de
    ruta contraídos por ``lns``). No modifica ``adj``. Lanza ``SinCiclo`` si hay contradicción.
    """
    n = len(adj)
    adj = [set(a) for a in adj]
    forz = [[] for _ in range(n)]
    extremo = list(range(n))  # extremo[a] = otro extremo del camino forzado de a
    tam = [1] * n             # vértices del camino (válido en los extremos)
    cola = deque(range(n))
    en_cola = [True] * n

    def encolar(v):
        if not en_cola[v]:
            en_cola[v] = True
            cola.append(v)

    def quitar(u, v):
        if v in forz[u]:
            raise SinCiclo(f"habría que quitar la arista forzada {u}-{v}")
        adj[u].discard(v)
        adj[v].discard(u)
        encolar(u)
        encolar(v)

    def forzar(u, v):
        if v in forz[u]:
            return
        if len(forz[u]) == 2 or len(forz[v]) == 2:
            raise SinCiclo(f"un vértice tendría tres aristas forzadas ({u}-{v})")
        a, b = extremo[u], extremo[v]
        if a == v:  # u y v ya son extremos del mismo camino: se cierra un ciclo
            if tam[u] != n:
                raise SinCiclo("las aristas forzadas cierran un ciclo que no cubre el grafo")
        forz[u].append(v)
        forz[v].append(u)
        encolar(u)
        encolar(v)
        if a == v:
            return
        total = tam[u] + tam[v]
        extremo[a], extremo[b] = b, a
        tam[a] = tam[b] = total
        if total < n and b in adj[a] and b not in forz[a]:
            quitar(a, b)

    for u, v in forzadas:
        if v not in adj[u]:
            raise SinCiclo(f"la arista forzada {u}-{v} no existe")
        forzar(u, v)

    while cola:
        v = cola.popleft()
        en_cola[v] = False
        if len(adj[v]) < 2:
            raise SinCiclo(f"el vértice {v} quedó con grado {len(adj[v])}")
        if len(adj[v]) == 2:
            for w in list(adj[v]):
                forzar(v, w)
        if len(forz[v]) == 2:
            for w in [w for w in adj[v] if w not in forz[v]]:
                quitar(v, w)
    return adj, forz


def resumen(adj, adj_red, forz):
    m0 = sum(map(len, adj)) // 2
    m1 = sum(map(len, adj_red)) // 2
    f = sum(map(len, forz)) // 2
    return {"aristas": m0, "aristas_reducidas": m1, "forzadas": f}


if __name__ == "__main__":
    import sys

    from src.grafo import leer_hcp

    for ruta in sys.argv[1:]:
        nombre, n, adj = leer_hcp(ruta)
        adj_red, forz = reducir(adj)
        print(nombre, n, resumen(adj, adj_red, forz))
