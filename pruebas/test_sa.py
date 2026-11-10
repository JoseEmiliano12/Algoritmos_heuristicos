"""Pruebas automáticas: python -m unittest discover -s pruebas -v."""

import random
import unittest
from unittest.mock import patch

from pruebas.grafos_prueba import ciclo5, grafo_con_ciclo
from pruebas.probar_algoritmo import verificar_resultado
from src.algoritmos import sa
from src.fitness import costo, es_ciclo_hamiltoniano


class GrafosPruebaTests(unittest.TestCase):
    def test_ciclo5_y_copias_independientes(self):
        self.assertTrue(es_ciclo_hamiltoniano(list(range(5)), ciclo5()))
        adj = ciclo5()
        adj[0].clear()
        self.assertEqual(ciclo5()[0], {1, 4})

    def test_ciclo_plantado_y_numero_exacto_de_aristas(self):
        for n in (3, 5, 30, 66):
            max_extra = n * (n - 1) // 2 - n
            for extra in (0, max_extra // 2, max_extra):
                with self.subTest(n=n, extra=extra):
                    adj, ciclo = grafo_con_ciclo(n, extra, 12)
                    self.assertTrue(es_ciclo_hamiltoniano(ciclo, adj))
                    self.assertEqual(sum(map(len, adj)) // 2, n + extra)
                    self.assertTrue(all(u not in vecinos for u, vecinos in enumerate(adj)))
                    self.assertTrue(all(u in adj[v] for u, vecinos in enumerate(adj) for v in vecinos))
                    self.assertEqual((adj, ciclo), grafo_con_ciclo(n, extra, 12))

    def test_generador_rechaza_entradas_invalidas(self):
        for n, extra in ((2, 0), (5, -1), (3, 1), (5, 6), (5, 0.5)):
            with self.subTest(n=n, extra=extra), self.assertRaises(ValueError):
                grafo_con_ciclo(n, extra, 0)


class SATests(unittest.TestCase):
    def test_presupuesto_incluye_inicial_y_vecinos_rechazados(self):
        adj = [set() for _ in range(8)]  # No puede tener ciclo; no habrá parada por éxito.
        for limite in (1, 2, 100, 101):
            with self.subTest(limite=limite):
                r = sa.resolver(adj, limite, 4)
                verificar_resultado(r, adj, limite)
                self.assertEqual(r['evals'], limite)
                self.assertEqual(r['iters'], limite - 1)
        # El costo completo solo se calcula al iniciar; los vecinos usan el delta.
        with patch.object(sa, 'costo', wraps=costo) as calcular:
            sa.resolver(adj, 20, 4)
            self.assertEqual(calcular.call_count, 1)
        with patch.object(sa, 'delta_swap', return_value=1000):
            r = sa.resolver(adj, 20, 4, T0=0.01, vecino='swap')
            self.assertEqual(r['evals'], 20)
            self.assertEqual(r['costo'], 8)

    def test_solucion_inicial_se_verifica_y_termina(self):
        adj = [{1, 2}, {0, 2}, {0, 1}]
        with patch.object(sa, 'es_ciclo_hamiltoniano', wraps=es_ciclo_hamiltoniano) as validar:
            r = sa.resolver(adj, 100, 5)
            self.assertEqual((r['costo'], r['evals'], r['iters']), (0, 1, 0))
            validar.assert_called_once()

    def test_no_hamiltoniano_no_se_reporta_como_solucion(self):
        adj = [{1}, {0, 2}, {1, 3}, {2, 4}, {3}]
        r = sa.resolver(adj, 300, 7)
        verificar_resultado(r, adj, 300)
        self.assertGreater(r['costo'], 0)

    def test_costo_y_repetibilidad_de_cada_vecindario(self):
        adj, _ = grafo_con_ciclo(12, 6, 101)
        estado_global = random.getstate()
        for vecino in ('swap', 'inversion', 'mixto'):
            with self.subTest(vecino=vecino):
                a = sa.resolver(adj, 3000, 7, vecino=vecino)
                b = sa.resolver(adj, 3000, 7, vecino=vecino)
                verificar_resultado(a, adj, 3000)
                self.assertEqual(a, b)
                self.assertEqual(a['ruta'][0], 0)
        self.assertEqual(random.getstate(), estado_global)

    def test_no_modifica_el_grafo(self):
        adj = ciclo5()
        copia = [vecinos.copy() for vecinos in adj]
        sa.resolver(adj, 100, 4)
        self.assertEqual(adj, copia)

    def test_parada_por_temperatura(self):
        r = sa.resolver([set() for _ in range(5)], 100, 0,
                        T0=1, T_min=0.75, alfa=0.5)
        self.assertEqual(r['evals'], 2)

    def test_parada_por_tiempo(self):
        with patch.object(sa.time, 'perf_counter', side_effect=[0, 2]):
            r = sa.resolver([set() for _ in range(5)], 100, 0, tiempo_max=1)
        self.assertEqual(r['evals'], 1)

    def test_parametros_y_grafos_invalidos(self):
        for params in ({'max_evals': 0}, {'max_evals': 1.5}, {'tiempo_max': 0},
                       {'T0': 0}, {'alfa': 1}, {'T_min': 0}, {'T0': float('nan')},
                       {'vecino': 'otro'}):
            args = {'max_evals': 100, 'semilla': 0, **params}
            with self.subTest(params=params), self.assertRaises(ValueError):
                sa.resolver(ciclo5(), **args)
        for adj in ([], [{1}, set(), set()], [{0}, set(), set()],
                    [{3}, set(), set()]):
            with self.subTest(adj=adj), self.assertRaises(ValueError):
                sa.resolver(adj, 100, 0)


if __name__ == '__main__':
    unittest.main()
