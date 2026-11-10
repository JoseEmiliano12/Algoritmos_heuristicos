"""Comprobaciones comunes. Ejecutar desde la raíz: python -m pruebas.probar_algoritmo sa."""

import argparse
import importlib

from src.fitness import costo, es_ciclo_hamiltoniano
from pruebas.grafos_prueba import ciclo5, grafo_con_ciclo


def verificar_resultado(resultado, adj, max_evals):
    """Verifica el contrato sin exigir éxito en una búsqueda heurística."""
    assert {"ruta", "costo", "evals", "iters", "historial"} <= resultado.keys()
    assert sorted(resultado["ruta"]) == list(range(len(adj))), "La ruta debe ser permutación."
    assert resultado["costo"] == costo(resultado["ruta"], adj), "Costo inconsistente."
    assert isinstance(resultado["evals"], int) and 1 <= resultado["evals"] <= max_evals
    assert isinstance(resultado["iters"], int) and resultado["iters"] >= 0
    historial = resultado["historial"]
    assert historial and historial[-1] == resultado["costo"]
    assert all(a >= b for a, b in zip(historial, historial[1:])), "El mejor costo no debe subir."
    if resultado["costo"] == 0:
        assert es_ciclo_hamiltoniano(resultado["ruta"], adj), "Ciclo inválido."


def probar_algoritmo(resolver, max_evals=20_000, **params):
    """Recibe cualquier resolver compatible y compara dos ejecuciones por semilla.

    El tiempo amplio evita que el reloj, en lugar del presupuesto, determine la
    repetición. No se afirma que toda heurística resuelva todos los casos.
    """
    casos = [("ciclo5", ciclo5())]
    casos += [(f"plantado n={n}", grafo_con_ciclo(n, n // 2, n)[0])
              for n in (10, 30, 66)]
    for nombre, adj in casos:
        a = resolver(adj, max_evals, 7, tiempo_max=60, **params)
        b = resolver(adj, max_evals, 7, tiempo_max=60, **params)
        verificar_resultado(a, adj, max_evals)
        verificar_resultado(b, adj, max_evals)
        assert a == b, "La misma semilla debe reproducirse sin corte por tiempo."
        estado = "ciclo verificado" if a["costo"] == 0 else "inconcluso"
        print(f"{nombre}: {estado}, costo={a['costo']}, evals={a['evals']}")
    print("Contrato y reproducibilidad verificados en los cuatro grafos didácticos.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("algoritmo", choices=["sa", "aco"], nargs="?", default="sa")
    parser.add_argument("--max-evals", type=int, default=20_000)
    args = parser.parse_args()
    modulo = importlib.import_module(f"src.algoritmos.{args.algoritmo}")
    probar_algoritmo(modulo.resolver, max_evals=args.max_evals)
