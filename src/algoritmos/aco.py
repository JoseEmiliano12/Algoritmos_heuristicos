"""Colonia de hormigas (variante MAX-MIN) para el ciclo hamiltoniano.

Las hormigas solo caminan por aristas que existen, así que nunca usan conexiones
ilegales. Cada una:
1. empieza en un vértice aleatorio;
2. avanza a un vecino no visitado con probabilidad proporcional a tau^alfa * eta^beta,
   con eta = 1 / (1 + vecinos libres del candidato) (regla de Warnsdorff);
3. si se atasca (opcional, ``rotaciones > 0``) aplica rotaciones de Pósa para cambiar de
   extremo y seguir, o para lograr el cierre;
4. si aun así no completa la ruta, agrega al final los vértices no visitados en orden
   aleatorio y se evalúa con ``costo()`` como cualquier otro algoritmo (1 evaluación).

Tras cada iteración: evaporación ``rho`` y depósito en las aristas de la mejor ruta de la
iteración, proporcional a la fracción de pares válidos; tau se acota a [tau_min, tau_max]
y se reinicia si la mejor ruta no mejora en ``reinicio`` iteraciones (MMAS).

Probar: ``python -m src.algoritmos.aco`` desde la raíz del repositorio.
"""
import random
import time

from src.fitness import costo, es_ciclo_hamiltoniano


def _construir(adj, tau, alfa, beta, rotaciones, rng):
    """Construye la ruta de una hormiga y la devuelve como permutación completa."""
    n = len(adj)
    inicio = rng.randrange(n)
    camino = [inicio]
    visitado = [False] * n
    visitado[inicio] = True
    libres = [len(a) for a in adj]  # vecinos no visitados de cada vértice
    for w in adj[inicio]:
        libres[w] -= 1

    while True:
        i = camino[-1]
        candidatos = [j for j in adj[i] if not visitado[j]]
        if candidatos:
            pesos = [tau[i][j] ** alfa * (1.0 / (1 + libres[j])) ** beta for j in candidatos]
            j = rng.choices(candidatos, pesos)[0]
            camino.append(j)
            visitado[j] = True
            for w in adj[j]:
                libres[w] -= 1
            continue
        if (len(camino) == n and inicio in adj[i]) or rotaciones == 0:
            break
        # Rotación de Pósa: si el extremo i es vecino de camino[p], invertir camino[p+1:]
        # deja como nuevo extremo a camino[p+1] (el camino sigue usando solo aristas).
        rotaciones -= 1
        posicion = {v: k for k, v in enumerate(camino)}
        pivotes = [posicion[w] for w in adj[i] if visitado[w] and posicion[w] < len(camino) - 2]
        if not pivotes:
            break
        p = rng.choice(pivotes)
        camino[p + 1:] = camino[:p:-1]

    resto = [v for v in range(n) if not visitado[v]]
    rng.shuffle(resto)
    return camino + resto


def resolver(adj, max_evals, semilla, tiempo_max=60, hormigas=10, alfa=1.0, beta=2.0,
             rho=0.1, tau_max=1.0, tau_min=None, rotaciones=0, reinicio=100):
    """Contrato común: devuelve dict con ruta, costo, evals, iters e historial.

    ``historial`` guarda el mejor costo al final de cada iteración (cada ``hormigas``
    evaluaciones). ``rotaciones = 0`` es ACO puro; ``> 0`` es la variante con Pósa.
    """
    rng = random.Random(semilla)
    n = len(adj)
    if tau_min is None:
        tau_min = tau_max / (2 * n)
    tau = [dict.fromkeys(adj[u], tau_max) for u in range(n)]
    inicio_t = time.perf_counter()

    mejor, mejor_costo = None, n + 1
    evals = iters = sin_mejora = 0
    historial = []
    while evals < max_evals and mejor_costo > 0 and time.perf_counter() - inicio_t < tiempo_max:
        iters += 1
        mejor_iter, costo_iter = None, n + 1
        for _ in range(min(hormigas, max_evals - evals)):
            ruta = _construir(adj, tau, alfa, beta, rotaciones, rng)
            c = costo(ruta, adj)
            evals += 1
            if c < costo_iter:
                mejor_iter, costo_iter = ruta, c
            if c == 0:
                break

        if costo_iter < mejor_costo:
            mejor, mejor_costo, sin_mejora = mejor_iter, costo_iter, 0
        else:
            sin_mejora += 1
        historial.append(mejor_costo)

        if sin_mejora >= reinicio:  # estancamiento: olvidar lo aprendido
            tau = [dict.fromkeys(adj[u], tau_max) for u in range(n)]
            sin_mejora = 0
            continue
        for u in range(n):
            for v in tau[u]:
                tau[u][v] *= 1 - rho
        deposito = (n - costo_iter) / n
        for k in range(n):
            u, v = mejor_iter[k - 1], mejor_iter[k]
            if v in adj[u]:
                tau[u][v] += deposito
                tau[v][u] += deposito
        for u in range(n):
            for v in tau[u]:
                tau[u][v] = min(tau_max, max(tau_min, tau[u][v]))

    return {"ruta": mejor, "costo": mejor_costo, "evals": evals, "iters": iters,
            "historial": historial}


if __name__ == "__main__":

    def grafo_con_ciclo(n, extra, semilla):
        """Grafo con un ciclo hamiltoniano plantado (oculto bajo una permutación) + aristas extra."""
        r = random.Random(semilla)
        ciclo = list(range(n))
        r.shuffle(ciclo)
        adj = [set() for _ in range(n)]
        aristas = [(ciclo[k - 1], ciclo[k]) for k in range(n)]
        aristas += [tuple(r.sample(range(n), 2)) for _ in range(extra)]
        for u, v in aristas:
            adj[u].add(v)
            adj[v].add(u)
        return adj

    # Ejemplo de 7 vértices de la investigación (0..6): ciclo único 0-1-2-3-4-5-6.
    adj7 = [set() for _ in range(7)]
    for u, v in [(1, 2), (1, 4), (1, 7), (2, 3), (2, 6), (3, 4), (3, 6), (4, 5), (5, 6), (6, 7)]:
        adj7[u - 1].add(v - 1)
        adj7[v - 1].add(u - 1)

    casos = [("ejemplo 7", adj7)] + [
        (f"plantado n={n}", grafo_con_ciclo(n, n // 2, s)) for n, s in [(30, 1), (60, 2), (100, 3)]
    ]
    for rot in [0, 50]:
        for nombre, adj in casos:
            exitos = 0
            for semilla in range(5):
                res = resolver(adj, max_evals=20_000, semilla=semilla, tiempo_max=20, rotaciones=rot)
                assert sorted(res["ruta"]) == list(range(len(adj))), "la ruta debe ser permutación"
                assert res["costo"] == costo(res["ruta"], adj)
                assert res["evals"] <= 20_000 and len(res["historial"]) == res["iters"]
                assert res["historial"] == sorted(res["historial"], reverse=True)
                exitos += es_ciclo_hamiltoniano(res["ruta"], adj)
            print(f"rotaciones={rot:>2}  {nombre:<16} éxito {exitos}/5")
    # Reproducibilidad: misma semilla, mismo resultado.
    a = resolver(casos[2][1], 2000, 7, rotaciones=0)
    b = resolver(casos[2][1], 2000, 7, rotaciones=0)
    assert a["ruta"] == b["ruta"] and a["evals"] == b["evals"]
    print("aco.py: contrato y reproducibilidad verificados")
