"""Optimización por Enjambre de Partículas (PSO) adaptada a permutaciones con *random keys*.

Cada partícula tiene una posición ``x`` (n claves en [0, 1]) y una velocidad ``v``. La
posición se decodifica con ``representacion.claves_a_permutacion`` (orden de los vértices por
clave) y se evalúa con ``fitness.costo``: la ruta siempre es una permutación válida.

Ecuaciones con inercia (Shi y Eberhart, 1998), clave a clave::

    v ← w·v + c1·r1·(p_i − x) + c2·r2·(g − x)      con r1, r2 ~ U(0, 1)
    v ← recortar(v, −v_max, v_max)
    x ← recortar(x + v, 0, 1)

``p_i`` es la mejor posición de la partícula y ``g`` la mejor del enjambre; ``g`` se actualiza
después de cada partícula (versión asíncrona, como en la investigación). Cada evaluación de
una partícula cuenta como 1 evaluación.

Reinicio por estancamiento: con random keys el enjambre colapsa rápido sobre ``g`` y deja de
explorar (en pruebas se atascaba incluso con n = 8). Si ``g`` no mejora en ``reinicio``
pasadas, todas las partículas salvo la que contiene a ``g`` reciben posición y velocidad
nuevas (su mejor personal pasa a ser la nueva posición). ``reinicio=0`` lo desactiva.

Probar: ``python -m pruebas.probar_algoritmo pso`` desde la raíz del repositorio.
"""
import random
import time

from src.fitness import costo, validar_parametros
from src.representacion import claves_a_permutacion, recortar


def resolver(adj, max_evals, semilla, tiempo_max=60, particulas=30, w=0.729, c1=1.49445,
             c2=1.49445, v_max=0.2, reinicio=30):
    """Contrato común: ruta (mejor permutación), costo, evals, iters (pasadas del enjambre), historial."""
    n = len(adj)
    validar_parametros(n, max_evals, tiempo_max)
    if particulas < 1 or not v_max > 0:
        raise ValueError("Se requieren particulas >= 1 y v_max > 0.")

    rng = random.Random(semilla)
    inicio_t = time.perf_counter()

    def hay_presupuesto():
        return evals < max_evals and time.perf_counter() - inicio_t < tiempo_max

    X, V, P, costo_p = [], [], [], []
    g, costo_g, mejor = None, n + 1, None
    evals = 0
    while len(X) < particulas and (evals == 0 or hay_presupuesto()):
        x = [rng.random() for _ in range(n)]
        ruta = claves_a_permutacion(x)
        c = costo(ruta, adj)
        evals += 1
        X.append(x)
        V.append([rng.uniform(-v_max, v_max) for _ in range(n)])
        P.append(x[:])
        costo_p.append(c)
        if c < costo_g:
            g, costo_g, mejor = x[:], c, ruta
        if c == 0:
            break

    iters, historial, sin_mejora = 1, [costo_g], 0
    while costo_g > 0 and hay_presupuesto():
        costo_antes = costo_g
        if reinicio and sin_mejora >= reinicio:
            lider = costo_p.index(costo_g)
            for i in range(len(X)):
                if i != lider:
                    X[i] = [rng.random() for _ in range(n)]
                    V[i] = [rng.uniform(-v_max, v_max) for _ in range(n)]
                    P[i], costo_p[i] = X[i][:], n + 1  # se fija al evaluarla
            sin_mejora = 0
        for i in range(len(X)):
            if not hay_presupuesto() or costo_g == 0:
                break
            x, v, p = X[i], V[i], P[i]
            for j in range(n):
                vj = (w * v[j] + c1 * rng.random() * (p[j] - x[j])
                      + c2 * rng.random() * (g[j] - x[j]))
                v[j] = recortar(vj, -v_max, v_max)
                x[j] = recortar(x[j] + v[j], 0.0, 1.0)
            ruta = claves_a_permutacion(x)
            c = costo(ruta, adj)
            evals += 1
            if c <= costo_p[i]:
                P[i], costo_p[i] = x[:], c
                if c < costo_g:
                    g, costo_g, mejor = x[:], c, ruta
        sin_mejora = 0 if costo_g < costo_antes else sin_mejora + 1
        iters += 1
        historial.append(costo_g)

    return {"ruta": mejor, "costo": costo_g, "evals": evals, "iters": iters,
            "historial": historial}
