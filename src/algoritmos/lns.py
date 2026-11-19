"""Búsqueda de vecindario grande (LNS) por descomposición, para grafos grandes.

En Python cada inversión de una ruta de miles de vértices es cara, y la búsqueda exacta
(``rp``) no escala a 10⁴ vértices. Idea (fijación de segmentos, como en LKH/POPMUSIC):

1. Se obtiene una ruta inicial rápida con ``posa_lk``.
2. Se elige una *ventana*: los vértices a distancia pequeña (BFS en el grafo) de una o de
   todas las conexiones rotas, hasta ``ventana`` vértices. Esos vértices quedan libres.
3. Cada tramo maximal de vértices fijos se contrae a sus dos extremos unidos por una
   **arista forzada** (virtual si el tramo contiene conexiones rotas lejanas, que quedan
   congeladas). El subgrafo tiene pocos cientos de vértices y solo contiene las conexiones
   rotas de la ventana.
4. El subproblema se resuelve con ``rp`` (exacto: o repara todas las conexiones rotas de la
   ventana o lo descarta) y, si no, con ``posa_lk``; la solución se expande (cada arista
   forzada vuelve a ser su tramo) y se acepta si no empeora la ruta completa.

Si la ventana contiene todas las conexiones rotas, un ciclo del subgrafo se expande a un
ciclo hamiltoniano del grafo original.
"""
import random
import time
from collections import deque

from src.algoritmos import posa_lk, rp
from src.fitness import costo, validar_parametros


def comprimir(tour, adjs, libre):
    """Contrae los tramos fijos de ``tour``. Devuelve (orig, sub_adj, forzadas, tramos, ruta)."""
    n = len(tour)
    inicio = next(i for i, v in enumerate(tour) if libre[v])
    t = tour[inicio:] + tour[:inicio]
    orig, tramos = [], {}
    i = 0
    while i < n:
        v = t[i]
        if libre[v]:
            orig.append(v)
            i += 1
            continue
        j = i
        while j + 1 < n and not libre[t[j + 1]]:
            j += 1
        orig.append(t[i])
        if j > i:  # tramo fijo (puede incluir conexiones rotas lejanas): arista forzada virtual
            orig.append(t[j])
            tramos[(t[i], t[j])] = t[i + 1:j]
        i = j + 1
    idx = {v: k for k, v in enumerate(orig)}
    sub = [{idx[w] for w in adjs[v] if w in idx} for v in orig]
    forz = []
    for a, b in tramos:
        ia, ib = idx[a], idx[b]
        sub[ia].add(ib)
        sub[ib].add(ia)
        forz.append((ia, ib))
    return orig, sub, forz, tramos, list(range(len(orig)))


def expandir(ruta_sub, orig, tramos, n):
    m = len(ruta_sub)
    salida = []
    for k in range(m):
        u, v = orig[ruta_sub[k]], orig[ruta_sub[(k + 1) % m]]
        salida.append(u)
        if (u, v) in tramos:
            salida.extend(tramos[(u, v)])
        elif (v, u) in tramos:
            salida.extend(reversed(tramos[(v, u)]))
    if len(salida) != n or len(set(salida)) != n:
        return None
    return salida


def ventana_bfs(adjs, semillas, tam, n):
    libre = bytearray(n)
    cola = deque()
    cuenta = 0
    for s in semillas:
        if not libre[s]:
            libre[s] = 1
            cuenta += 1
            cola.append(s)
    while cola and cuenta < tam:
        u = cola.popleft()
        for w in adjs[u]:
            if not libre[w]:
                libre[w] = 1
                cuenta += 1
                cola.append(w)
                if cuenta >= tam:
                    break
    return libre


def resolver(adj, max_evals, semilla, tiempo_max=60, ventana=500, t_sub=2.0, t_inicial=None,
             umbral=700):
    """Contrato común. ``iters`` = subproblemas resueltos; ``evals`` = suma de evaluaciones."""
    n = len(adj)
    validar_parametros(n, max_evals, tiempo_max)
    t_fin = time.perf_counter() + tiempo_max
    if n <= umbral:  # grafo pequeño: no hace falta descomponer
        from src.algoritmos import portafolio
        return portafolio.resolver(adj, max_evals, semilla, tiempo_max=tiempo_max)

    rng = random.Random(semilla)
    adjs = [set(a) for a in adj]
    if t_inicial is None:
        t_inicial = min(tiempo_max * 0.15, 5 + n / 1000)
    r0 = posa_lk.resolver(adj, max_evals, semilla, tiempo_max=t_inicial)
    tour, c = r0["ruta"], r0["costo"]
    evals, iters = r0["evals"], 0
    historial = [c]
    tam_sub = []

    while c > 0 and evals < max_evals:
        resto = t_fin - time.perf_counter()
        if resto <= 0.05:
            break
        rotas = [i for i in range(n) if tour[i] not in adjs[tour[i - 1]]]
        extremos = [tour[i - 1] for i in rotas] + [tour[i] for i in rotas]
        todas = c <= 6
        if todas:
            semillas = extremos
        else:
            i = rng.choice(rotas)
            semillas = [tour[i - 1], tour[i]]
        libre = ventana_bfs(adjs, semillas, max(ventana, 4 * len(semillas)), n)
        orig, sub, forz, tramos, ruta_sub = comprimir(tour, adjs, libre)
        tam_sub.append(len(sub))
        mejor_sub = None
        t = min(resto, t_sub)
        sem = rng.randrange(1 << 30)
        if rng.random() < 0.7:  # búsqueda exacta: repara todas las rotas de la ventana o nada
            r = rp.resolver(sub, max_evals, sem, tiempo_max=t / 2, forzadas=forz)
            evals += r["evals"]
            if r["costo"] == 0:
                mejor_sub = r["ruta"]
        if mejor_sub is None:
            t_lk = min(t, t_fin - time.perf_counter())
            if t_lk <= 0.01:  # el presupuesto se agotó durante comprimir/rp
                break
            r = posa_lk.resolver(sub, max_evals, sem, tiempo_max=t_lk,
                                 ruta_inicial=ruta_sub, forzadas=forz)
            evals += r["evals"]
            mejor_sub = r["ruta"]
        iters += 1
        nuevo = expandir(mejor_sub, orig, tramos, n)
        if nuevo is not None:
            cn = costo(nuevo, adj)
            if cn <= c:
                tour, c = nuevo, cn
        historial.append(c)
    return {"ruta": tour, "costo": c, "evals": max(evals, 1), "iters": iters,
            "historial": historial, "tam_sub": tam_sub}
