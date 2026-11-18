"""Operadores de vecindario guiados por el grafo (comparten GA/ABC/SA si se desea).

``inversion_guiada`` es un 2-opt que en lugar de elegir índices al azar busca una conexión
rota ``ruta[i] -> ruta[i+1]`` y la sustituye por una arista real ``ruta[i] - w``, con ``w``
vecino de ``ruta[i]`` en el grafo. Siempre invierte un tramo, así que la ruta sigue siendo una
permutación válida; además nunca mueve la posición 0 (compatible con rutas ancladas en 0).
Es la forma en que ABC aprovecha "caminos prometedores" del grafo (ver ``abc.py``).
"""


def inversion_guiada(ruta, adj, rng, intentos=8):
    """Devuelve ``(i, j)`` con ``1 <= i < j < n`` para invertir ``ruta[i..j]``, o ``None``.

    Tras invertir, el vértice ``u = ruta[k]`` (con conexión rota a su sucesor) queda junto a
    un vecino ``w`` suyo en el grafo. ``fitness.delta_inversion`` da el cambio de costo en O(1).
    """
    n = len(ruta)
    for _ in range(intentos):
        k = rng.randrange(n)
        u = ruta[k]
        if ruta[(k + 1) % n] in adj[u] or not adj[u]:
            continue  # esa conexión ya existe: buscar otra rota
        w = rng.choice(tuple(adj[u]))
        q = ruta.index(w)
        if q > k:      # invertir k+1..q deja w justo después de u
            i, j = k + 1, q
        else:          # invertir q+1..k deja u justo después de w
            i, j = q + 1, k
        if 1 <= i < j:
            return i, j
    return None
