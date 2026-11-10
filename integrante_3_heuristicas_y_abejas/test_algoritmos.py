"""Pruebas de los módulos asignados al integrante 3.

Ejecutar desde la raíz: python3 -m unittest discover \
    -s integrante_3_heuristicas_y_abejas -p 'test_*.py'
"""

import random
import unittest

from src.algoritmos.abc import resolver as resolver_abc
from src.algoritmos.ga import cruce_ox, mutar_inversion, mutar_swap, resolver as resolver_ga
from src.fitness import costo, delta_inversion, delta_swap, es_ciclo_hamiltoniano


def grafo_ciclo(n):
    adj = [set() for _ in range(n)]
    for i in range(n):
        u, v = i, (i + 1) % n
        adj[u].add(v)
        adj[v].add(u)
    return adj


def grafo_camino(n):
    adj = [set() for _ in range(n)]
    for i in range(n - 1):
        adj[i].add(i + 1)
        adj[i + 1].add(i)
    return adj


class OperadoresTest(unittest.TestCase):
    def test_ox_y_mutaciones_conservan_permutacion_e_inicio(self):
        rng = random.Random(42)
        for n in (3, 4, 7, 20):
            for _ in range(100):
                p1 = [0] + rng.sample(range(1, n), n - 1)
                p2 = [0] + rng.sample(range(1, n), n - 1)
                for hijo in (cruce_ox(p1, p2, rng), mutar_swap(p1, rng),
                             mutar_inversion(p1, rng)):
                    self.assertEqual(hijo[0], 0)
                    self.assertEqual(sorted(hijo), list(range(n)))
                self.assertEqual(sorted(p1), list(range(n)))

    def test_delta_de_vecinas_coincide_con_costo_completo(self):
        rng = random.Random(71)
        adj = grafo_ciclo(10)
        for _ in range(100):
            ruta = [0] + rng.sample(range(1, 10), 9)
            base = costo(ruta, adj)
            swap, (i, j) = mutar_swap(ruta, rng, con_indices=True)
            inversion, (a, b) = mutar_inversion(ruta, rng, con_indices=True)
            self.assertEqual(base + delta_swap(ruta, i, j, adj), costo(swap, adj))
            self.assertEqual(base + delta_inversion(ruta, a, b, adj), costo(inversion, adj))


class ContratoTest(unittest.TestCase):
    def comprobar(self, resultado, adj, presupuesto):
        self.assertEqual(sorted(resultado["ruta"]), list(range(len(adj))))
        self.assertEqual(resultado["ruta"][0], 0)
        self.assertEqual(resultado["costo"], costo(resultado["ruta"], adj))
        self.assertLessEqual(resultado["evals"], presupuesto)
        self.assertGreaterEqual(resultado["evals"], 1)
        self.assertEqual(len(resultado["historial"]), resultado["iters"])
        self.assertEqual(resultado["historial"], sorted(resultado["historial"], reverse=True))
        if resultado["costo"] == 0:
            self.assertTrue(es_ciclo_hamiltoniano(resultado["ruta"], adj))

    def test_ciclo_encontrado_y_verificado(self):
        adj = grafo_ciclo(5)
        for resolver in (resolver_ga, resolver_abc):
            resultado = resolver(adj, max_evals=500, semilla=3, tiempo_max=5)
            self.comprobar(resultado, adj, 500)
            self.assertEqual(resultado["costo"], 0)

    def test_presupuesto_y_reproducibilidad_sin_ciclo(self):
        adj = grafo_camino(9)
        configuraciones = ((resolver_ga, {"tam_poblacion": 4}),
                           (resolver_abc, {"fuentes": 3, "limite": 1}))
        for resolver, params in configuraciones:
            a = resolver(adj, max_evals=17, semilla=12, tiempo_max=5, **params)
            b = resolver(adj, max_evals=17, semilla=12, tiempo_max=5, **params)
            self.comprobar(a, adj, 17)
            self.assertEqual(a["evals"], 17)
            self.assertEqual(a, b)
            self.assertGreater(a["costo"], 0)

    def test_abc_operadores_alternativos(self):
        adj = grafo_camino(8)
        for operador in ("swap", "inversion", "mixto"):
            resultado = resolver_abc(adj, 31, 4, fuentes=4, operador=operador)
            self.comprobar(resultado, adj, 31)

    def test_presupuesto_de_una_evaluacion(self):
        adj = grafo_camino(6)
        for resolver in (resolver_ga, resolver_abc):
            resultado = resolver(adj, 1, 9)
            self.comprobar(resultado, adj, 1)


if __name__ == "__main__":
    unittest.main()
