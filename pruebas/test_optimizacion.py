"""Pruebas de la optimización: reducción, posa_lk, rp, portafolio y lns.

Ejecutar desde la raíz::

    python3 -m unittest pruebas.test_optimizacion -v
"""
import glob
import os
import random
import unittest

from pruebas.grafos_prueba import ciclo5, grafo_con_ciclo
from pruebas.probar_algoritmo import verificar_resultado
from src.algoritmos import lns, portafolio, posa_lk, rp
from src.fitness import costo, es_ciclo_hamiltoniano
from src.grafo import leer_hcp, leer_tour
from src.reduccion import SinCiclo, reducir

FHCP = sorted(glob.glob("datos/fhcp/graph*.hcp"))


class TestReduccion(unittest.TestCase):
    def test_conserva_soluciones_oficiales(self):
        """Ninguna regla elimina una arista del ciclo oficial y todas las forzadas están en él."""
        for archivo in FHCP:
            _, n, adj = leer_hcp(archivo)
            ruta = leer_tour(archivo + ".tou")
            adj_red, forz = reducir(adj)
            self.assertEqual(costo(ruta, adj_red), 0, archivo)
            aristas = {frozenset((ruta[i - 1], ruta[i])) for i in range(n)}
            for u in range(n):
                for v in forz[u]:
                    self.assertIn(frozenset((u, v)), aristas, archivo)

    def test_grado_dos_y_subciclo(self):
        # Camino 0-1-2 forzado por el grado 2 de 1; la cuerda 0-2 cerraría un triángulo.
        adj = [{1, 2, 3}, {0, 2}, {0, 1, 3}, {0, 2}]
        adj_red, forz = reducir(adj)
        self.assertNotIn(2, adj_red[0])
        self.assertEqual(sorted(map(len, forz)), [2, 2, 2, 2])

    def test_contradiccion(self):
        estrella = [{1, 2, 3}, {0}, {0}, {0}]
        with self.assertRaises(SinCiclo):
            reducir(estrella)

    def test_forzadas_externas(self):
        adj = [set(a) for a in ciclo5()]
        _, forz = reducir(adj, [(0, 1)])
        self.assertIn(1, forz[0])


class TestAlgoritmosNuevos(unittest.TestCase):
    def casos(self):
        yield ciclo5()
        for n in (10, 30, 66, 120):
            yield grafo_con_ciclo(n, n // 2, n)[0]

    def test_contrato_y_exito(self):
        for modulo in (posa_lk, rp, portafolio, lns):
            for adj in self.casos():
                r = modulo.resolver(adj, 1_000_000, 3, tiempo_max=20)
                verificar_resultado(r, adj, 1_000_000)
                self.assertTrue(es_ciclo_hamiltoniano(r["ruta"], adj), modulo.__name__)

    def test_reproducible(self):
        adj = grafo_con_ciclo(80, 40, 5)[0]
        for modulo in (posa_lk, rp):
            a = modulo.resolver(adj, 1_000_000, 11, tiempo_max=20)
            b = modulo.resolver(adj, 1_000_000, 11, tiempo_max=20)
            self.assertEqual(a["ruta"], b["ruta"])

    def test_respeta_max_evals(self):
        _, _, adj = leer_hcp("datos/fhcp/graph24.hcp")
        for modulo in (posa_lk, rp):
            r = modulo.resolver(adj, 500, 0, tiempo_max=20)
            verificar_resultado(r, adj, 500)

    def test_fhcp_pequenos(self):
        """El portafolio resuelve graph1..graph12 del FHCP (los métodos originales: 6 de 12)."""
        for i in range(1, 13):
            _, _, adj = leer_hcp(f"datos/fhcp/graph{i}.hcp")
            r = portafolio.resolver(adj, 10 ** 12, 0, tiempo_max=30)
            self.assertTrue(es_ciclo_hamiltoniano(r["ruta"], adj), f"graph{i}")


class TestLNS(unittest.TestCase):
    def test_comprimir_expandir_es_identidad(self):
        rng = random.Random(0)
        _, n, adj = leer_hcp("datos/fhcp/graph20.hcp")
        adjs = [set(a) for a in adj]
        tour = list(range(n))
        rng.shuffle(tour)
        for _ in range(20):
            libre = lns.ventana_bfs(adjs, [rng.randrange(n)], rng.randrange(5, 60), n)
            orig, sub, forz, tramos, ruta_sub = lns.comprimir(tour, adjs, libre)
            nuevo = lns.expandir(ruta_sub, orig, tramos, n)
            self.assertEqual(costo(nuevo, adj), costo(tour, adj))
            self.assertEqual(sorted(nuevo), list(range(n)))

    @unittest.skipUnless(os.path.exists("datos/fhcp_completo/graph150.hcp"), "set completo")
    def test_grafo_grande(self):
        _, _, adj = leer_hcp("datos/fhcp_completo/graph150.hcp")
        r = lns.resolver(adj, 10 ** 12, 0, tiempo_max=15)
        verificar_resultado(r, adj, 10 ** 12)


if __name__ == "__main__":
    unittest.main()
