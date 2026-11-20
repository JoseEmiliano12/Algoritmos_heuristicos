"""Búsqueda local tipo Lin-Kernighan con rotaciones de Pósa (ILS + tabú), en Python puro.

Misma función de costo que el resto del proyecto (conexiones consecutivas que no son
arista). El movimiento es la rotación de Pósa escrita como 2-opt:

    ruta cortada en una conexión rota (e, f):   f ... x y ... e
    si x es vecino de e en el grafo:           f ... x e ... y      (se invierte y..e)

Se agrega la arista real (x, e) y se quita (x, y); el nuevo cierre es (y, f).
Ganancia = [(x, y) estaba rota] + [(y, f) es arista] >= 0, es decir, **una rotación nunca
empeora la ruta**: la búsqueda camina por mesetas (ganancia 0) y baja en cuanto puede
(primero la mayor ganancia). Para no dar vueltas en la meseta se usa una lista tabú sobre
los extremos recientes, y si no hay mejora en ``estanc`` pasos se aplica una perturbación
(ILS: volver a la mejor ruta y hacer inversiones aleatorias), como en el recocido/ABC.

Antes de buscar se reduce el grafo (``src.reduccion``): aristas forzadas por vértices de
grado 2, que nunca se quitan de la ruta y se prefieren al rotar.

Detalles de rendimiento (solo biblioteca estándar): adyacencia en ``set`` (O(1)), ruta en
lista + ``pos`` (sucesor O(1)), inversión del lado más corto con *slicing*.
"""
import random
import time

from src.fitness import costo, validar_parametros
from src.reduccion import SinCiclo, reducir


def construir(adjl, fz, rng):
    """Recorrido de Warnsdorff que respeta aristas forzadas; los atascos saltan al azar."""
    n = len(adjl)
    vis = [False] * n
    libre = [len(a) for a in adjl]
    pendientes = list(range(n))
    rng.shuffle(pendientes)
    ip = 0
    ruta = []
    cur = -1
    while len(ruta) < n:
        if cur < 0:
            while vis[pendientes[ip]]:
                ip += 1
            cur = pendientes[ip]
        vis[cur] = True
        ruta.append(cur)
        for w in adjl[cur]:
            libre[w] -= 1
        sig = -1
        for w in fz[cur]:
            if not vis[w]:
                sig = w
                break
        if sig < 0:
            mejor = n + 1
            empates = 0
            for w in adjl[cur]:
                if vis[w]:
                    continue
                lw = libre[w]
                if lw < mejor:
                    mejor, sig, empates = lw, w, 1
                elif lw == mejor:
                    empates += 1
                    if rng.randrange(empates) == 0:
                        sig = w
        cur = sig
    return ruta


def resolver(adj, max_evals, semilla, tiempo_max=60, tenure=None, estanc=None, patada=8,
             max_cand=24, reducir_grafo=True, ruta_inicial=None, use3=True, forzadas=()):
    """Contrato común: dict con ruta, costo, evals, iters e historial.

    Una evaluación = un candidato de rotación cuyo delta se calcula en O(1).
    ``iters`` = rotaciones aplicadas. ``historial`` = mejor costo cada 1000 rotaciones.
    ``tenure`` (tabú) por defecto ``min(50, n // 10 + 5)``; ``estanc`` por defecto ``20·n``.
    """
    n = len(adj)
    validar_parametros(n, max_evals, tiempo_max)
    rng = random.Random(semilla)
    t0 = time.perf_counter()
    if tenure is None:
        tenure = min(50, n // 10 + 5)
    if estanc is None:
        estanc = 20 * n

    adjs, fz = [set(a) for a in adj], [()] * n
    if reducir_grafo:
        try:
            adjs, forz = reducir(adj, forzadas)
            fz = [tuple(f) for f in forz]
        except SinCiclo:
            pass  # contradicción: buscar en el grafo original (no debería ocurrir en el FHCP)
    adjl = [tuple(a) for a in adjs]
    fzs = [frozenset(f) for f in fz]

    tour = list(ruta_inicial) if ruta_inicial is not None else construir(adjl, fz, rng)
    pos = [0] * n
    for i, v in enumerate(tour):
        pos[v] = i

    # Conexiones rotas (lista con limpieza perezosa) y costo actual.
    bad = [(tour[i - 1], tour[i]) for i in range(n) if tour[i] not in adjs[tour[i - 1]]]
    c_act = len(bad)
    mejor, c_mejor = tour[:], c_act
    historial = [c_mejor]
    evals = 1
    paso = ultimo = chequeo = 0
    stamp = [-(1 << 40)] * n
    randrange = rng.randrange
    ahora = time.perf_counter

    def invertir(i, j):
        """Invierte las posiciones i..j (cíclicas); invierte el lado más corto."""
        largo = (j - i) % n + 1
        if 2 * largo > n:
            i, j = (j + 1) % n, (i - 1) % n
            largo = n - largo
        if largo < 2:
            return
        if i <= j:
            seg = tour[i:j + 1]
            seg.reverse()
            tour[i:j + 1] = seg
            for k, v in enumerate(seg, i):
                pos[v] = k
        else:
            seg = tour[i:] + tour[:j + 1]
            seg.reverse()
            m = n - i
            tour[i:] = seg[:m]
            tour[:j + 1] = seg[m:]
            for k, v in enumerate(seg, i):
                pos[v] = k - n if k >= n else k

    def dos_opt(a, c):
        """Quita (a, suc a) y (c, suc c); agrega (a, c) y (suc a, suc c). Devuelve delta."""
        pb = pos[a] + 1
        b = tour[pb] if pb < n else tour[0]
        pd = pos[c] + 1
        d = tour[pd] if pd < n else tour[0]
        antes = (b not in adjs[a]) + (d not in adjs[c])
        invertir(pos[b], pos[c])
        ac = c not in adjs[a]
        bd = d not in adjs[b]
        if ac:
            bad.append((a, c))
        if bd:
            bad.append((b, d))
        return ac + bd - antes

    def suc(v):
        p = pos[v] + 1
        return tour[p] if p < n else tour[0]

    def mover(a, b, c, d):
        """2-opt que quita las conexiones (a, b) y (c, d) de la ruta y agrega (a, c) y (b, d).

        ``b`` y ``d`` deben seguir a ``a`` y ``c`` en el mismo sentido de recorrido; funciona
        aunque una inversión previa haya espejado la ruta.
        """
        if suc(a) == b:
            return dos_opt(a, c)
        return dos_opt(d, b)

    def patear(k):
        hecho = 0
        for _ in range(20 * k):
            if hecho == k:
                break
            a, c = tour[randrange(n)], tour[randrange(n)]
            b, d = suc(a), suc(c)
            if a == c or b == c or d == a or b in fzs[a] or d in fzs[c]:
                continue
            hecho += 1
            yield dos_opt(a, c)

    evals_agotadas = False
    while c_act > 0 and evals < max_evals and not evals_agotadas:
        if paso >= chequeo:
            if ahora() - t0 >= tiempo_max:
                break
            chequeo = paso + 128
        if paso - ultimo > estanc:  # ILS: volver a la mejor y perturbar
            if c_act > c_mejor:
                tour[:] = mejor
                for i, v in enumerate(tour):
                    pos[v] = i
                bad[:] = [(tour[i - 1], tour[i]) for i in range(n)
                          if tour[i] not in adjs[tour[i - 1]]]
                c_act = c_mejor
            c_act += sum(patear(1 + randrange(patada)))
            ultimo = paso

        # Elegir una conexión rota vigente.
        if len(bad) > 8 * n + 1024:
            bad[:] = [(tour[i - 1], tour[i]) for i in range(n) if tour[i] not in adjs[tour[i - 1]]]
        while True:
            k = randrange(len(bad))
            u, v = bad[k]
            if suc(u) == v or suc(v) == u:
                break
            bad[k] = bad[-1]
            bad.pop()
        if rng.random() < 0.5:
            e, f = u, v
        else:
            e, f = v, u
        dirp = suc(e) == f  # True: ... x y ... e f ...   False: ... f e ... y x ...

        for _ in range(64):  # cadena de movimientos mientras el cierre (e, f) siga roto
            paso += 1
            stamp[e] = paso
            vec = adjl[e]
            deg = len(vec)
            if deg > max_cand:
                vec = [vec[randrange(deg)] for _ in range(max_cand)]
            fe = fzs[e]
            adj_f = adjs[f]
            pf = pos[f]
            # Candidatos: (ganancia, tipo, x, w, z, z2, nuevo_extremo)
            cands = []
            mejor_g = 0
            for x in vec:
                if x == f:
                    continue
                px = pos[x]
                if dirp:
                    y = tour[px + 1] if px + 1 < n else tour[0]
                    w = tour[px - 1]
                else:
                    y = tour[px - 1]
                    w = tour[px + 1] if px + 1 < n else tour[0]
                fx = fzs[x]
                # 1) Rotación de Pósa (2-opt): quita (x, y), agrega (x, e).
                if y != e and y not in fx:
                    g = (y not in adjs[x]) + (y in adj_f)
                    cands.append((g, 0, x, y, 0, 0, y))
                    if g > mejor_g:
                        mejor_g = g
                # 2) Movimiento de profundidad 3: agregar (e, x) y quitar (w, x) separa el
                #    ciclo x..e; se reinserta uniendo w con un z del ciclo y cortando junto a z.
                if w == f or w == e or w in fx or not use3:
                    continue
                gwx = w not in adjs[x]
                ix = (px - pf) % n if dirp else (pf - px) % n
                vw = adjl[w]
                if len(vw) > max_cand:
                    vw = [vw[randrange(len(vw))] for _ in range(max_cand)]
                for z in vw:
                    if z == x:
                        continue
                    pz = pos[z]
                    iz = (pz - pf) % n if dirp else (pf - pz) % n
                    if iz <= ix:
                        continue  # z no está en el ciclo x..e
                    fzz = fzs[z]
                    adz = adjs[z]
                    if z != e:  # caso A: corte en el sucesor de z
                        if dirp:
                            z2 = tour[pz + 1] if pz + 1 < n else tour[0]
                        else:
                            z2 = tour[pz - 1]
                        if z2 not in fzz:
                            g = gwx + (z2 not in adz) + (z2 in adj_f)
                            cands.append((g, 1, x, w, z, z2, z2))
                            if g > mejor_g:
                                mejor_g = g
                    # caso B: corte en el antecesor de z (z2 está en el ciclo, puede ser x)
                    if dirp:
                        z2 = tour[pz - 1]
                    else:
                        z2 = tour[pz + 1] if pz + 1 < n else tour[0]
                    if z2 not in fzz:
                        g = gwx + (z2 not in adz) + (z2 in adj_f)
                        cands.append((g, 2, x, w, z, z2, z2))
                        if g > mejor_g:
                            mejor_g = g
            if not cands or evals + len(cands) > max_evals:
                evals_agotadas = bool(cands)
                break
            evals += len(cands)
            if mejor_g > 0:
                buenos = [c for c in cands if c[0] == mejor_g]
            else:
                buenos = [c for c in cands if c[1] == 0 and c[2] in fe]  # arista forzada pendiente
                if not buenos:
                    buenos = [c for c in cands if paso - stamp[c[6]] > tenure] or cands
            _, tipo, x, w, z, z2, y = buenos[randrange(len(buenos))]
            if tipo == 0:
                c_act += mover(x, w, e, f)          # aquí w es y = sig(x)
            elif tipo == 1:
                c_act += mover(w, x, z, z2)
                c_act += mover(x, z2, e, f)
            else:
                c_act += mover(w, x, e, f)
                c_act += mover(w, e, z, z2)
                c_act += mover(e, z2, x, f)
            if c_act < c_mejor:
                c_mejor = c_act
                mejor = tour[:]
                ultimo = paso
                if c_mejor == 0:
                    break
            if (paso % 1000) == 0:
                historial.append(c_mejor)
            if y in adj_f:
                break  # el cierre quedó conectado: tomar otra conexión rota
            e = y
            dirp = suc(e) == f
            if evals >= max_evals:
                break

    c_final = costo(mejor, adj)  # en el grafo original (el reducido tiene menos aristas)
    historial = [min(h, c_final) for h in historial] + [c_final]
    return {"ruta": mejor, "costo": c_final, "evals": evals, "iters": paso,
            "historial": historial}
