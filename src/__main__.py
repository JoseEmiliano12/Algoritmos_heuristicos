"""Programa ejecutable: carga un grafo del FHCP, ejecuta una metaheurística y devuelve la ruta.

Uso (desde la raíz del repositorio)::

    python -m src datos/fhcp/graph1.hcp --alg aco
    python -m src datos/fhcp/graph1.hcp --alg sa --semilla 3 --max-evals 500000 --tiempo 60
    python -m src datos/fhcp/graph1.hcp --alg aco_posa --tour resultados/tours/graph1_aco_posa_0.tour
    python -m src --listar

Imprime el arreglo de vértices (numeración 1..n del archivo) y si es un ciclo hamiltoniano
verificado. Código de salida 0 = ciclo encontrado y verificado, 1 = inconcluso.
"""
import argparse
import json
import sys
import time

from src.algoritmos import ALGORITMOS, obtener
from src.fitness import es_ciclo_hamiltoniano
from src.grafo import escribir_tour, leer_hcp, num_aristas


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m src", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("grafo", nargs="?", help="archivo .hcp")
    parser.add_argument("--alg", default="aco", choices=sorted(ALGORITMOS))
    parser.add_argument("--semilla", type=int, default=0)
    parser.add_argument("--max-evals", type=int, default=1_000_000)
    parser.add_argument("--tiempo", type=float, default=60.0, help="segundos máximos")
    parser.add_argument("--param", action="append", default=[], metavar="CLAVE=VALOR",
                        help="parámetro extra del algoritmo (valor en JSON), p. ej. --param alfa=0.99999")
    parser.add_argument("--tour", help="guardar la ruta en formato TOUR si es un ciclo")
    parser.add_argument("--json", action="store_true", help="salida completa en JSON")
    parser.add_argument("--listar", action="store_true", help="listar algoritmos y salir")
    args = parser.parse_args(argv)

    if args.listar:
        for nombre, (modulo, params) in ALGORITMOS.items():
            print(f"{nombre:<9} src/algoritmos/{modulo}.py {params or ''}")
        return 0
    if not args.grafo:
        parser.error("falta el archivo .hcp")

    nombre, n, adj = leer_hcp(args.grafo)
    resolver, params = obtener(args.alg)
    for item in args.param:
        clave, _, valor = item.partition("=")
        try:
            params[clave] = json.loads(valor)
        except json.JSONDecodeError:
            params[clave] = valor

    inicio = time.perf_counter()
    res = resolver(adj, args.max_evals, args.semilla, tiempo_max=args.tiempo, **params)
    tiempo = time.perf_counter() - inicio
    exito = es_ciclo_hamiltoniano(res["ruta"], adj)
    ruta_1n = [v + 1 for v in res["ruta"]]

    if exito and args.tour:
        escribir_tour(res["ruta"], args.tour, nombre)
    if args.json:
        print(json.dumps({"grafo": nombre, "n": n, "m": num_aristas(adj), "algoritmo": args.alg,
                          "params": params, "semilla": args.semilla, "exito": exito,
                          "costo": res["costo"], "evals": res["evals"], "iters": res["iters"],
                          "tiempo_s": round(tiempo, 4), "ruta": ruta_1n}))
    else:
        estado = "CICLO HAMILTONIANO VERIFICADO" if exito else f"inconcluso (faltan {res['costo']} aristas)"
        print(f"{nombre} n={n} m={num_aristas(adj)} | {args.alg} semilla={args.semilla} | "
              f"{estado} | evals={res['evals']} tiempo={tiempo:.2f}s")
        print(ruta_1n)
    return 0 if exito else 1


if __name__ == "__main__":
    sys.exit(main())
