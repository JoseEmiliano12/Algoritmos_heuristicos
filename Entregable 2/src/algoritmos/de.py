"""Evolución Diferencial (DE/rand/1/bin) adaptada a permutaciones con *random keys*.

DE trabaja con vectores reales, así que no puede operar directamente sobre una ruta. Cada
individuo es un vector de n claves en [0, 1]; ``representacion.claves_a_permutacion`` lo
convierte en una permutación válida de 0..n-1 (orden de los vértices por clave), que se evalúa
con ``fitness.costo``. Así ninguna mutación o cruce de DE puede producir una ruta ilegal.

Por generación, para cada individuo ``x_i``:

1. mutación   ``v = x_r1 + F · (x_r2 − x_r3)`` con r1, r2, r3 distintos entre sí y de i;
2. cruce binomial: cada clave se toma de ``v`` con probabilidad CR (al menos una, ``j_rand``);
3. recorte de las claves a [0, 1];
4. selección uno a uno: el ensayo reemplaza a ``x_i`` si su costo es menor o igual.

Cada ensayo evaluado cuenta como 1 evaluación; la población inicial también.

Probar: ``python -m pruebas.probar_algoritmo de`` desde la raíz del repositorio.
"""
import random
import time

from src.fitness import costo, validar_parametros
from src.representacion import claves_a_permutacion, recortar


def resolver(adj, max_evals, semilla, tiempo_max=60, tam_poblacion=30, F=0.5, CR=0.9):
    """Contrato común: ruta (mejor permutación), costo, evals, iters (generaciones), historial."""
    n = len(adj)
    validar_parametros(n, max_evals, tiempo_max)
    if tam_poblacion < 4:
        raise ValueError("DE/rand/1 necesita una población de al menos 4 individuos.")
    if not 0 < F <= 2 or not 0 <= CR <= 1:
        raise ValueError("Se requiere 0 < F <= 2 y 0 <= CR <= 1.")

    rng = random.Random(semilla)
    inicio_t = time.perf_counter()

    def hay_presupuesto():
        return evals < max_evals and time.perf_counter() - inicio_t < tiempo_max

    poblacion, costos = [], []
    mejor, mejor_costo, evals = None, n + 1, 0
    while len(poblacion) < tam_poblacion and (evals == 0 or hay_presupuesto()):
        x = [rng.random() for _ in range(n)]
        ruta = claves_a_permutacion(x)
        c = costo(ruta, adj)
        evals += 1
        poblacion.append(x)
        costos.append(c)
        if c < mejor_costo:
            mejor, mejor_costo = ruta, c
        if c == 0:
            break

    iters, historial = 1, [mejor_costo]
    np_real = len(poblacion)
    while np_real >= 4 and mejor_costo > 0 and hay_presupuesto():
        for i in range(np_real):
            if not hay_presupuesto() or mejor_costo == 0:
                break
            r1, r2, r3 = rng.sample([k for k in range(np_real) if k != i], 3)
            a, b, c3, xi = poblacion[r1], poblacion[r2], poblacion[r3], poblacion[i]
            j_rand = rng.randrange(n)
            ensayo = [
                recortar(a[j] + F * (b[j] - c3[j]), 0.0, 1.0)
                if (rng.random() < CR or j == j_rand) else xi[j]
                for j in range(n)
            ]
            ruta = claves_a_permutacion(ensayo)
            c = costo(ruta, adj)
            evals += 1
            if c <= costos[i]:
                poblacion[i], costos[i] = ensayo, c
                if c < mejor_costo:
                    mejor, mejor_costo = ruta, c
        iters += 1
        historial.append(mejor_costo)

    return {"ruta": mejor, "costo": mejor_costo, "evals": evals, "iters": iters,
            "historial": historial}
