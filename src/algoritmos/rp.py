"""Ramificación y poda con propagación de restricciones (búsqueda exacta con reinicios).

Complementa a las metaheurísticas: en grafos cúbicos con muy pocos ciclos hamiltonianos
(frecuentes en el FHCP) la búsqueda local queda a una arista del ciclo, mientras que aquí
cada decisión desencadena muchas deducciones.

Estado: aristas disponibles y aristas forzadas (caminos). Reglas de propagación (las de
``src.reduccion`` aplicadas en cada nodo):
  * vértice con 2 aristas disponibles → ambas forzadas;
  * vértice con 2 forzadas → se eliminan las demás;
  * extremos de un camino forzado que no cubre el grafo → no pueden unirse (subciclo);
  * el grafo de aristas disponibles debe seguir conexo (se comprueba en cada nodo).

Ramificación: el extremo de camino con menos alternativas (*fail-first*), probando primero
los vecinos con menos aristas (Warnsdorff). Si se agota un límite de nodos se reinicia con
otro orden aleatorio y el límite crece (serie de Luby), lo que evita quedar atrapado en un
subárbol malo. Sin límite de tiempo la búsqueda es completa.

Si no encuentra el ciclo, devuelve la ruta de Warnsdorff para cumplir el contrato.
"""
import random
import time

from src.fitness import costo, validar_parametros


def luby(i):
    """Serie de Luby 1,1,2,1,1,2,4,1,1,2,..."""
    k = 1
    while (1 << k) - 1 < i:
        k += 1
    while True:
        if i == (1 << k) - 1:
            return 1 << (k - 1)
        i -= (1 << (k - 1)) - 1
        k = 1
        while (1 << k) - 1 < i:
            k += 1


class _Busqueda:
    def __init__(self, adj, rng, conexidad=True, forzadas=()):
        n = self.n = len(adj)
        self.adj = [set(a) for a in adj]
        self.forz = [[] for _ in range(n)]
        self.ext = list(range(n))
        self.tam = [1] * n
        self.trail = []
        self.rng = rng
        self.conexidad = conexidad
        self.nforz = 0
        self.forzadas = list(forzadas)

    # ---- operaciones con registro para deshacer ----
    def quitar(self, u, v, cola):
        if v in self.forz[u]:
            return False
        self.adj[u].discard(v)
        self.adj[v].discard(u)
        self.trail.append((0, u, v))
        cola.append(u)
        cola.append(v)
        return True

    def forzar(self, u, v, cola):
        fu, fv = self.forz[u], self.forz[v]
        if v in fu:
            return True
        if len(fu) == 2 or len(fv) == 2 or v not in self.adj[u]:
            return False
        ext, tam = self.ext, self.tam
        a, b = ext[u], ext[v]
        if a == v and tam[u] != self.n:
            return False  # cerraría un subciclo
        fu.append(v)
        fv.append(u)
        self.nforz += 1
        self.trail.append((1, u, v))
        cola.append(u)
        cola.append(v)
        if a == v:
            return True
        self.trail.append((2, a, ext[a], tam[a]))
        self.trail.append((2, b, ext[b], tam[b]))
        total = tam[u] + tam[v]
        ext[a], ext[b] = b, a
        tam[a] = tam[b] = total
        if total < self.n and b in self.adj[a] and b not in self.forz[a]:
            return self.quitar(a, b, cola)
        return True

    def deshacer(self, marca):
        trail, adj, forz, ext, tam = self.trail, self.adj, self.forz, self.ext, self.tam
        while len(trail) > marca:
            op = trail.pop()
            if op[0] == 0:
                adj[op[1]].add(op[2])
                adj[op[2]].add(op[1])
            elif op[0] == 1:
                forz[op[1]].pop()
                forz[op[2]].pop()
                self.nforz -= 1
            else:
                ext[op[1]] = op[2]
                tam[op[1]] = op[3]

    def propagar(self, cola):
        adj, forz = self.adj, self.forz
        while cola:
            v = cola.pop()
            av = adj[v]
            if len(av) < 2:
                return False
            if len(av) == 2:
                for w in tuple(av):
                    if not self.forzar(v, w, cola):
                        return False
            fv = forz[v]
            if len(fv) == 2 and len(av) > 2:
                for w in [w for w in av if w not in fv]:
                    if not self.quitar(v, w, cola):
                        return False
        return True

    def conexo(self):
        """True si el grafo de aristas disponibles es 2-conexo (sin vértices de corte).

        Un grafo hamiltoniano es 2-conexo, así que un vértice de corte poda la rama.
        Tarjan iterativo, O(n + m).
        """
        adj = self.adj
        n = self.n
        disc = [0] * n
        low = [0] * n
        tiempo = 1
        disc[0] = low[0] = 1
        hijos_raiz = 0
        pila = [(0, -1, iter(adj[0]))]
        visitados = 1
        while pila:
            u, padre, it = pila[-1]
            avanzo = False
            for w in it:
                if w == padre:
                    continue
                if disc[w]:
                    if disc[w] < low[u]:
                        low[u] = disc[w]
                else:
                    tiempo += 1
                    disc[w] = low[w] = tiempo
                    visitados += 1
                    pila.append((w, u, iter(adj[w])))
                    avanzo = True
                    break
            if avanzo:
                continue
            pila.pop()
            if padre >= 0:
                if low[u] < low[padre]:
                    low[padre] = low[u]
                if padre == 0:
                    hijos_raiz += 1
                    if hijos_raiz > 1:
                        return False
                elif low[u] >= disc[padre]:
                    return False  # padre es vértice de corte
        return visitados == n

    def elegir(self):
        """Extremo de camino con menos alternativas; si no hay caminos, vértice de menor grado."""
        adj, forz = self.adj, self.forz
        mejor, mv = None, None
        for v in range(self.n):
            k = len(forz[v])
            if k == 2:
                continue
            opciones = len(adj[v]) - k
            clave = (k == 0, opciones)
            if mejor is None or clave < mejor:
                mejor, mv = clave, v
                if clave == (False, 1):
                    break
        v = mv
        cands = [w for w in adj[v] if w not in forz[v]]
        self.rng.shuffle(cands)
        cands.sort(key=lambda w: len(adj[w]) - len(forz[w]))
        return v, cands

    def ciclo(self):
        forz = self.forz
        ruta = [0]
        prev, cur = -1, 0
        for _ in range(self.n - 1):
            a, b = forz[cur]
            prev, cur = cur, (b if a == prev else a)
            ruta.append(cur)
        return ruta

    def buscar(self, limite_nodos, t_fin):
        """DFS iterativa. Devuelve ruta, None (sin solución en el subárbol) o 'limite'."""
        base = len(self.trail)
        cola = list(range(self.n))
        if not all(self.forzar(u, v, cola) for u, v in self.forzadas):
            self.deshacer(base)
            return None
        if not self.propagar(cola) or (self.conexidad and not self.conexo()):
            self.deshacer(base)
            return None
        pila = []
        nodos = 0
        nuevo_nodo = True
        while True:
            if nuevo_nodo:
                if self.nforz == self.n:
                    return self.ciclo()
                v, cands = self.elegir()
                pila.append([len(self.trail), v, cands, 0])
            marco = pila[-1]
            marca, v, cands, i = marco
            self.deshacer(marca)
            if i >= len(cands):
                pila.pop()
                if not pila:
                    self.deshacer(base)
                    return None
                nuevo_nodo = False
                continue
            marco[3] = i + 1
            nodos += 1
            if nodos > limite_nodos or ((nodos & 127) == 0 and time.perf_counter() > t_fin):
                self.deshacer(base)
                return "limite"
            cola = []
            ok = self.forzar(v, cands[i], cola) and self.propagar(cola)
            if ok and self.conexidad and not self.conexo():
                ok = False
            nuevo_nodo = ok


def resolver(adj, max_evals, semilla, tiempo_max=60, nodos_base=200, conexidad=True,
             forzadas=()):
    """Contrato común. ``evals`` = nodos explorados; ``iters`` = reinicios."""
    n = len(adj)
    validar_parametros(n, max_evals, tiempo_max)
    rng = random.Random(semilla)
    t0 = time.perf_counter()
    t_fin = t0 + tiempo_max
    b = _Busqueda(adj, rng, conexidad, forzadas)
    evals = iters = 0
    historial = []
    ruta = None
    while time.perf_counter() < t_fin and evals < max_evals:
        iters += 1
        limite = min(nodos_base * luby(iters), max_evals - evals)
        r = b.buscar(limite, t_fin)
        evals += limite if r == "limite" else 0
        if isinstance(r, list):
            ruta = r
            break
        if r is None:
            break  # árbol completo sin solución: el grafo no es hamiltoniano
        historial.append(n)
    if ruta is None:
        from src.algoritmos.posa_lk import construir
        ruta = construir([tuple(a) for a in adj], [()] * n, rng)
    c = costo(ruta, adj)
    historial.append(c)
    return {"ruta": ruta, "costo": c, "evals": max(evals, 1), "iters": iters,
            "historial": historial}
