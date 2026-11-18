"""Pruebas de las piezas agregadas para completar la Fase 3.

Lector/escritor HCP-TOUR, decodificación random keys, DE, PSO, operador guiado, registro de
algoritmos, CLI y correcciones de ABC, SA y ACO. Ejecutar desde la raíz::

    python3 -m unittest discover -s pruebas -t . -v
"""

import contextlib
import io
import os
import random
import tempfile
import unittest

from pruebas.grafos_prueba import ciclo5, grafo_con_ciclo
from pruebas.probar_algoritmo import verificar_resultado
from src import __main__ as cli
from src.algoritmos import ALGORITMOS, obtener
from src.algoritmos import abc, aco, de, pso, sa
from src.fitness import costo, delta_inversion, es_ciclo_hamiltoniano, es_permutacion
from src.grafo import escribir_tour, leer_hcp, leer_tour, num_aristas
from src.operadores import inversion_guiada
from src.representacion import claves_a_permutacion, permutacion_a_claves

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAPH1 = os.path.join(RAIZ, "datos", "fhcp", "graph1.hcp")


def escribir_hcp(ruta, n, aristas):
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(f"NAME : prueba\nTYPE : HCP\nDIMENSION : {n}\nEDGE_DATA_FORMAT : EDGE_LIST\n"
                "EDGE_DATA_SECTION\n")
        f.writelines(f"{u + 1} {v + 1}\n" for u, v in aristas)
        f.write("-1\nEOF\n")


class GrafoTest(unittest.TestCase):
    def test_ida_y_vuelta_hcp_y_tour(self):
        adj = ciclo5()
        aristas = [(u, v) for u in range(5) for v in adj[u] if u < v]
        with tempfile.TemporaryDirectory() as d:
            ruta_hcp = os.path.join(d, "c5.hcp")
            escribir_hcp(ruta_hcp, 5, aristas + [(2, 2), (0, 1)])  # lazo y repetida
            nombre, n, leido = leer_hcp(ruta_hcp)
            self.assertEqual((nombre, n, leido), ("prueba", 5, adj))
            ruta_tour = os.path.join(d, "sub", "c5.tour")
            escribir_tour([0, 1, 2, 3, 4], ruta_tour, nombre)
            self.assertEqual(leer_tour(ruta_tour), [0, 1, 2, 3, 4])

    def test_rechaza_vertices_fuera_de_rango(self):
        with tempfile.TemporaryDirectory() as d:
            ruta = os.path.join(d, "malo.hcp")
            escribir_hcp(ruta, 3, [(0, 5)])
            with self.assertRaises(ValueError):
                leer_hcp(ruta)

    @unittest.skipUnless(os.path.exists(GRAPH1), "falta datos/fhcp/graph1.hcp")
    def test_instancia_real_y_solucion_oficial(self):
        nombre, n, adj = leer_hcp(GRAPH1)
        self.assertEqual(n, 66)
        self.assertTrue(all(len(a) >= 2 for a in adj))
        self.assertGreater(num_aristas(adj), n)
        self.assertTrue(es_ciclo_hamiltoniano(leer_tour(GRAPH1 + ".tou"), adj))


class RepresentacionTest(unittest.TestCase):
    def test_random_keys_siempre_da_permutacion(self):
        rng = random.Random(3)
        for n in (3, 7, 50):
            for _ in range(200):
                claves = [rng.choice([0.0, 0.5, 1.0, rng.random()]) for _ in range(n)]
                self.assertTrue(es_permutacion(claves_a_permutacion(claves), n))
        self.assertEqual(claves_a_permutacion([0.5, 0.5, 0.1]), [2, 0, 1])  # empate por id

    def test_inversa(self):
        ruta = [3, 0, 4, 1, 2]
        self.assertEqual(claves_a_permutacion(permutacion_a_claves(ruta)), ruta)


class OperadorGuiadoTest(unittest.TestCase):
    def test_crea_una_arista_real_y_conserva_inicio(self):
        rng = random.Random(5)
        adj, _ = grafo_con_ciclo(40, 20, 9)
        usados = 0
        for _ in range(300):
            ruta = [0] + rng.sample(range(1, 40), 39)
            par = inversion_guiada(ruta, adj, rng)
            if par is None:
                continue
            i, j = par
            nueva = ruta[:]
            nueva[i:j + 1] = nueva[i:j + 1][::-1]
            self.assertEqual(nueva[0], 0)
            self.assertTrue(es_permutacion(nueva, 40))
            self.assertTrue(nueva[i] in adj[nueva[i - 1]] or nueva[(j + 1) % 40] in adj[nueva[j]])
            self.assertEqual(costo(ruta, adj) + delta_inversion(ruta, i, j, adj), costo(nueva, adj))
            usados += 1
        self.assertGreater(usados, 200)


class AlgoritmosTest(unittest.TestCase):
    def test_todos_los_registrados_cumplen_el_contrato(self):
        adj, _ = grafo_con_ciclo(20, 10, 4)
        for nombre in ALGORITMOS:
            with self.subTest(alg=nombre):
                resolver, params = obtener(nombre)
                a = resolver(adj, 3000, 1, tiempo_max=30, **params)
                b = resolver(adj, 3000, 1, tiempo_max=30, **params)
                verificar_resultado(a, adj, 3000)
                self.assertEqual(a, b)

    def test_presupuesto_minimo_nunca_da_estructura_ilegal(self):
        adj, _ = grafo_con_ciclo(10, 5, 1)
        for nombre in ALGORITMOS:
            for presupuesto in (1, 2, 5):
                with self.subTest(alg=nombre, presupuesto=presupuesto):
                    resolver, params = obtener(nombre)
                    r = resolver(adj, presupuesto, 0, **params)
                    verificar_resultado(r, adj, presupuesto)

    def test_parametros_invalidos(self):
        for resolver in (aco.resolver, de.resolver, pso.resolver):
            for args in ((0, 0, 1), (1.5, 0, 1), (10, 0, 0)):
                with self.subTest(resolver=resolver.__module__, args=args), \
                        self.assertRaises(ValueError):
                    resolver(ciclo5(), args[0], args[1], tiempo_max=args[2])

    def test_de_y_pso_resuelven_grafos_faciles(self):
        adj, _ = grafo_con_ciclo(8, 6, 2)
        for resolver in (de.resolver, pso.resolver):
            r = resolver(adj, 20_000, 0, tiempo_max=30)
            self.assertEqual(r["costo"], 0)
            self.assertTrue(es_ciclo_hamiltoniano(r["ruta"], adj))

    def test_sa_con_alfa_automatico_usa_todo_el_presupuesto(self):
        adj = [set() for _ in range(12)]  # sin ciclo: solo para por presupuesto o temperatura
        r = sa.resolver(adj, 5000, 0)
        self.assertEqual(r["evals"], 5000)

    def test_abc_guiado_mejora_frente_a_swap(self):
        adj, _ = grafo_con_ciclo(30, 15, 1001)
        guiado = abc.resolver(adj, 30_000, 0, tiempo_max=30)
        swap = abc.resolver(adj, 30_000, 0, tiempo_max=30, operador="swap", limite=100)
        self.assertLess(guiado["costo"], swap["costo"])


class CLITest(unittest.TestCase):
    def test_cli_resuelve_y_escribe_tour(self):
        adj, _ = grafo_con_ciclo(12, 6, 3)
        aristas = [(u, v) for u in range(12) for v in adj[u] if u < v]
        with tempfile.TemporaryDirectory() as d:
            hcp, tour = os.path.join(d, "g.hcp"), os.path.join(d, "g.tour")
            escribir_hcp(hcp, 12, aristas)
            salida = io.StringIO()
            with contextlib.redirect_stdout(salida):
                codigo = cli.main([hcp, "--alg", "aco", "--tour", tour, "--tiempo", "20"])
            self.assertEqual(codigo, 0)
            self.assertIn("VERIFICADO", salida.getvalue())
            self.assertTrue(es_ciclo_hamiltoniano(leer_tour(tour), adj))


if __name__ == "__main__":
    unittest.main()
