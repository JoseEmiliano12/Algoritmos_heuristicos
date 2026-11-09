"""Representación y función de fitness comunes a todos los algoritmos.

Convenciones (PLAN_IMPLEMENTACION.md):
- Grafo no dirigido como lista de adyacencia ``adj: list[set[int]]``, vértices 0..n-1.
- Ruta = permutación cíclica de los n vértices (``list[int]``); el par
  ``ruta[-1] -> ruta[0]`` es el cierre.
- Costo a minimizar = número de pares consecutivos (incluido el cierre) que NO son
  arista. ``costo == 0`` si y solo si la ruta es un ciclo hamiltoniano.

Probar: ``python -m src.fitness`` desde la raíz del repositorio.
"""


def costo(ruta, adj):
    """Número de pares consecutivos de ``ruta`` (incluido el cierre) que no son arista."""
    # i = 0 compara ruta[-1] con ruta[0]: es el cierre del ciclo.
    return sum(ruta[i - 1] not in adj[ruta[i]] for i in range(len(ruta)))


def delta_swap(ruta, i, j, adj):
    """Cambio de costo si se intercambian ``ruta[i]`` y ``ruta[j]``, en O(1).

    No modifica ``ruta``. Funciona con índices vecinos, iguales y con los extremos
    (el cierre). Uso: ``nuevo_costo = costo_actual + delta_swap(ruta, i, j, adj)``.
    """
    n = len(ruta)
    if i == j:
        return 0
    # Solo cambian los pares que empiezan en i-1, i, j-1 y j; el conjunto evita contarlos
    # dos veces cuando i y j son vecinos.
    pares = {(i - 1) % n, i, (j - 1) % n, j}

    def tras_swap(p):
        p %= n
        return ruta[j] if p == i else ruta[i] if p == j else ruta[p]

    antes = sum(ruta[(k + 1) % n] not in adj[ruta[k]] for k in pares)
    despues = sum(tras_swap(k + 1) not in adj[tras_swap(k)] for k in pares)
    return despues - antes


def delta_inversion(ruta, i, j, adj):
    """Cambio de costo si se invierte el tramo ``ruta[i..j]`` (movimiento 2-opt), en O(1).

    No modifica ``ruta``. Si ``i > j`` se intercambian. Como el grafo es no dirigido,
    las aristas internas del tramo no cambian: solo los dos bordes.
    Para aplicarla: ``ruta[i:j + 1] = ruta[i:j + 1][::-1]``.
    """
    n = len(ruta)
    if i > j:
        i, j = j, i
    if j - i + 1 >= n:  # invertir toda la ruta recorre el mismo ciclo al revés
        return 0
    a, b = ruta[i - 1], ruta[(j + 1) % n]
    x, y = ruta[i], ruta[j]
    antes = (x not in adj[a]) + (b not in adj[y])
    despues = (y not in adj[a]) + (b not in adj[x])
    return despues - antes


def es_ciclo_hamiltoniano(ruta, adj):
    """Verificación independiente: n >= 3 vértices, todos, sin repetir, con aristas y cierre."""
    n = len(adj)
    return (
        n >= 3
        and len(ruta) == n
        and set(ruta) == set(range(n))
        and costo(ruta, adj) == 0
    )


def ruta_aleatoria(n, rng):
    """Permutación aleatoria de 0..n-1. ``rng``: ``random.Random`` o ``numpy.random.Generator``."""
    ruta = list(range(n))
    rng.shuffle(ruta)
    return ruta


if __name__ == "__main__":
    import random

    # Ejemplo de 7 vértices de la investigación (allí numerados 1..7; aquí 0..6).
    aristas = [(1, 2), (1, 4), (1, 7), (2, 3), (2, 6), (3, 4), (3, 6), (4, 5), (5, 6), (6, 7)]
    adj7 = [set() for _ in range(7)]
    for u, v in aristas:
        adj7[u - 1].add(v - 1)
        adj7[v - 1].add(u - 1)

    def base0(r):
        return [v - 1 for v in r]

    assert costo(base0([1, 4, 3, 6, 7, 2, 5]), adj7) == 3
    assert costo(base0([2, 3, 4, 1, 7, 6, 5]), adj7) == 1  # solo falta el cierre
    assert es_ciclo_hamiltoniano(base0([1, 2, 3, 4, 5, 6, 7]), adj7)
    assert es_ciclo_hamiltoniano(base0([1, 7, 6, 5, 4, 3, 2]), adj7)
    assert not es_ciclo_hamiltoniano(base0([2, 3, 4, 1, 7, 6, 5]), adj7)
    assert not es_ciclo_hamiltoniano(base0([1, 2, 3, 4, 5, 6]), adj7)  # falta un vértice
    assert not es_ciclo_hamiltoniano(base0([1, 2, 3, 4, 5, 6, 6]), adj7)  # repetido

    # Prueba principal: los deltas coinciden con costo(después) - costo(antes).
    rng = random.Random(0)
    casos = 0
    for n in [3, 4, 5, 8, 20, 60]:
        for _ in range(30):
            adj = [set() for _ in range(n)]
            densidad = rng.choice([0.1, 0.3, 0.6, 0.9])
            for u in range(n):
                for v in range(u + 1, n):
                    if rng.random() < densidad:
                        adj[u].add(v)
                        adj[v].add(u)
            ruta = ruta_aleatoria(n, rng)
            assert sorted(ruta) == list(range(n))
            c = costo(ruta, adj)
            # Pares fijos de bordes y vecinos más pares aleatorios.
            pares = [(0, n - 1), (n - 1, 0), (0, 1), (n - 2, n - 1), (0, 0)]
            pares += [(k, k + 1) for k in range(n - 1)]
            pares += [(rng.randrange(n), rng.randrange(n)) for _ in range(50)]
            for i, j in pares:
                otra = ruta[:]
                otra[i], otra[j] = otra[j], otra[i]
                assert delta_swap(ruta, i, j, adj) == costo(otra, adj) - c, ("swap", n, i, j)

                a, b = min(i, j), max(i, j)
                otra = ruta[:]
                otra[a:b + 1] = otra[a:b + 1][::-1]
                assert delta_inversion(ruta, i, j, adj) == costo(otra, adj) - c, ("inv", n, i, j)
                casos += 2
    print(f"fitness.py: todas las pruebas pasan ({casos} deltas verificados)")
