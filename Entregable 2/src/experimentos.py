"""Ejecuta un diseño experimental completo y guarda una línea JSON por ejecución.

Uso (desde la raíz del repositorio)::

    python3 -m src.experimentos A                 # diseño A completo, 10 procesos
    python3 -m src.experimentos A --procesos 6    # menos núcleos
    python3 -m src.experimentos A --dry-run       # solo cuenta cuántas ejecuciones faltan

Diseños:
    A  comparativa principal: graph4..graph24 × 8 algoritmos × semillas 0..9, 60 s, 6·10⁶ evals
    B  benchmarking FHCP: graph1..graph100 (datos/fhcp_completo) × aco_posa, abc × semillas 0,1, 120 s
    C  escalabilidad: graph50, 200, 500, 1001 (datos/fhcp_completo) × 8 algoritmos × semilla 0, 120 s

Se puede **retomar**: al arrancar lee el archivo de salida y salta las combinaciones
(grafo, algoritmo, semilla) que ya estén. Si se corta (Ctrl+C, apagón), basta con volver a
lanzar el mismo comando. Cada ciclo hamiltoniano encontrado se guarda en formato TOUR en
``resultados/tours/``.
"""
import argparse
import json
import multiprocessing as mp
import os
import sys
import time

from src.algoritmos import ALGORITMOS, obtener
from src.fitness import es_ciclo_hamiltoniano
from src.grafo import escribir_tour, leer_hcp, num_aristas

TODOS = list(ALGORITMOS)
PUNTOS_CURVA = 100  # puntos de la curva de convergencia que se guardan por ejecución

DISENOS = {
    "A": dict(grafos=[f"datos/fhcp/graph{i}.hcp" for i in range(4, 25)], algoritmos=TODOS,
              semillas=range(10), tiempo=60, max_evals=6_000_000, salida="resultados/disenoA.jsonl"),
    "B": dict(grafos=[f"datos/fhcp_completo/graph{i}.hcp" for i in range(1, 101)],
              algoritmos=["aco_posa", "abc"], semillas=range(2), tiempo=120, max_evals=12_000_000,
              salida="resultados/disenoB.jsonl"),
    "C": dict(grafos=[f"datos/fhcp_completo/graph{i}.hcp" for i in (50, 200, 500, 1001)],
              algoritmos=TODOS, semillas=range(1), tiempo=120, max_evals=12_000_000,
              salida="resultados/disenoC.jsonl"),
}


def submuestrear(historial, evals, k=PUNTOS_CURVA):
    """Reduce el historial a ≤k puntos [evals_aprox, mejor_costo].

    Cada algoritmo registra el historial con su propio paso (por iteración, cada 100 evals…),
    así que el eje x se aproxima repartiendo las evaluaciones totales de forma uniforme.
    """
    if not historial:
        return []
    m = len(historial)
    idx = sorted({round(i * (m - 1) / (k - 1)) for i in range(k)}) if m > k else range(m)
    return [[round((i + 1) * evals / m), historial[i]] for i in idx]


def ejecutar(tarea):
    archivo, alg, semilla, tiempo_max, max_evals = tarea
    nombre, n, adj = leer_hcp(archivo)
    resolver, params = obtener(alg)
    inicio = time.perf_counter()
    res = resolver(adj, max_evals, semilla, tiempo_max=tiempo_max, **params)
    tiempo = time.perf_counter() - inicio
    exito = es_ciclo_hamiltoniano(res["ruta"], adj)
    tour = None
    if exito:
        tour = f"resultados/tours/{nombre.removesuffix('.hcp')}_{alg}_{semilla}.tour"
        escribir_tour(res["ruta"], tour, nombre)
    return {"grafo": nombre, "n": n, "m": num_aristas(adj), "algoritmo": alg, "params": params,
            "semilla": semilla, "exito": exito, "costo": res["costo"], "evals": res["evals"],
            "iters": res["iters"], "tiempo_s": round(tiempo, 4), "tiempo_max": tiempo_max,
            "max_evals": max_evals, "tour": tour,
            "curva": submuestrear(res["historial"], res["evals"]),
            "ruta": [v + 1 for v in res["ruta"]]}


def hechas(salida):
    vistas = set()
    if os.path.exists(salida):
        with open(salida) as f:
            for linea in f:
                try:
                    d = json.loads(linea)
                except json.JSONDecodeError:
                    continue  # línea cortada por una interrupción
                vistas.add((d["grafo"], d["algoritmo"], d["semilla"]))
    return vistas


def main(argv=None):
    p = argparse.ArgumentParser(prog="python3 -m src.experimentos", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("diseno", choices=sorted(DISENOS))
    p.add_argument("--procesos", type=int, default=10)
    p.add_argument("--salida", help="archivo .jsonl (por defecto el del diseño)")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args(argv)

    d = DISENOS[args.diseno]
    salida = args.salida or d["salida"]
    faltan_grafos = [g for g in d["grafos"] if not os.path.exists(g)]
    if faltan_grafos:
        sys.exit(f"Faltan {len(faltan_grafos)} grafos (p. ej. {faltan_grafos[0]}). "
                 "Para B y C ejecuta antes: bash datos/descargar_fhcp.sh")

    ya = hechas(salida)
    # Orden: por semilla primero, para que un corte deje todas las instancias con alguna semilla.
    tareas = [(g, a, s, d["tiempo"], d["max_evals"])
              for s in d["semillas"] for g in d["grafos"] for a in d["algoritmos"]
              if (os.path.basename(g), a, s) not in ya]
    total = len(d["grafos"]) * len(d["algoritmos"]) * len(d["semillas"])
    horas = len(tareas) * d["tiempo"] / args.procesos / 3600
    print(f"Diseño {args.diseno}: {total - len(tareas)}/{total} hechas, faltan {len(tareas)} "
          f"(≤ {horas:.1f} h con {args.procesos} procesos). Salida: {salida}", flush=True)
    if args.dry_run or not tareas:
        return 0

    os.makedirs(os.path.dirname(salida) or ".", exist_ok=True)
    os.makedirs("resultados/tours", exist_ok=True)
    inicio = time.time()
    with open(salida, "a") as f, mp.Pool(args.procesos) as pool:
        for i, r in enumerate(pool.imap_unordered(ejecutar, tareas), 1):
            f.write(json.dumps(r) + "\n")
            f.flush()
            trans = time.time() - inicio
            resta = trans / i * (len(tareas) - i)
            print(f"[{i}/{len(tareas)}] {r['grafo']:<12} {r['algoritmo']:<9} s={r['semilla']} "
                  f"{'ÉXITO' if r['exito'] else 'costo=' + str(r['costo']):<9} {r['tiempo_s']:6.1f}s "
                  f"| quedan ~{resta / 60:.0f} min", flush=True)
    print("Terminado.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
