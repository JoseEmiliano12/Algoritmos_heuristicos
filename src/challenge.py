"""Campaña sobre los 1001 grafos del FHCP Challenge Set con pasadas de tiempo creciente.

Uso (desde la raíz del repositorio; requiere ``bash datos/descargar_fhcp.sh``)::

    python3 -m src.challenge                          # pasadas 30 s, 120 s, 600 s, núcleos - 2
    python3 -m src.challenge --tiempos 10 60 --procesos 8
    python3 -m src.challenge --grafos 1-100           # subconjunto
    python3 -m src.challenge --resumen                # solo imprime el conteo actual

Cada pasada ejecuta el algoritmo (``lns`` por defecto: portafolio rp + posa_lk si n ≤ 700,
descomposición si es mayor) sobre los grafos que aún no
tienen ciclo, con su propia semilla. Es **reanudable**: lee ``resultados/challenge.jsonl`` y
salta los grafos ya resueltos y las combinaciones (grafo, pasada) ya hechas. Cada ciclo se
verifica con ``es_ciclo_hamiltoniano`` y se guarda en ``resultados/challenge_tours/``
(formato TOUR, el que exigía el concurso).

Grafos grandes primero dentro de cada pasada: así los procesos no se quedan esperando al
final por una instancia lenta.
"""
import argparse
import json
import multiprocessing as mp
import os
import sys
import time

from src.algoritmos import obtener
from src.fitness import es_ciclo_hamiltoniano
from src.grafo import escribir_tour, leer_hcp, leer_tour

CARPETA = "datos/fhcp_completo"
SALIDA = "resultados/challenge.jsonl"
TOURS = "resultados/challenge_tours"


def ejecutar(tarea):
    num, pasada, tiempo, alg = tarea
    archivo = f"{CARPETA}/graph{num}.hcp"
    nombre, n, adj = leer_hcp(archivo)
    resolver, params = obtener(alg)
    inicio = time.perf_counter()
    try:
        res = resolver(adj, 10 ** 12, pasada, tiempo_max=tiempo, **params)
    except Exception as e:  # un grafo que falle no debe tumbar la campaña entera
        return {"grafo": nombre, "num": num, "n": n, "pasada": pasada, "algoritmo": alg,
                "tiempo_max": tiempo, "exito": False, "costo": -1,
                "tiempo_s": round(time.perf_counter() - inicio, 2), "evals": 0, "tour": None,
                "error": f"{type(e).__name__}: {e}"}
    t = time.perf_counter() - inicio
    exito = es_ciclo_hamiltoniano(res["ruta"], adj)
    tour = None
    if exito:
        tour = f"{TOURS}/graph{num}.tour"
        escribir_tour(res["ruta"], tour, nombre)
    return {"grafo": nombre, "num": num, "n": n, "pasada": pasada, "algoritmo": alg,
            "tiempo_max": tiempo, "exito": exito, "costo": res["costo"],
            "tiempo_s": round(t, 2), "evals": res["evals"], "tour": tour}


def leer_registro(salida):
    resueltos, hechas = set(), set()
    if os.path.exists(salida):
        with open(salida) as f:
            for linea in f:
                try:
                    d = json.loads(linea)
                except json.JSONDecodeError:
                    continue
                hechas.add((d["num"], d["pasada"]))
                if d["exito"]:
                    resueltos.add(d["num"])
    return resueltos, hechas


def verificar_tours(nums):
    """Recomprueba desde disco cada TOUR guardado (independiente de la ejecución)."""
    ok = 0
    for num in nums:
        _, n, adj = leer_hcp(f"{CARPETA}/graph{num}.hcp")
        ruta = leer_tour(f"{TOURS}/graph{num}.tour")
        ok += es_ciclo_hamiltoniano(ruta, adj)
    return ok


def rango(texto):
    a, _, b = texto.partition("-")
    return list(range(int(a), int(b or a) + 1))


def main(argv=None):
    p = argparse.ArgumentParser(prog="python3 -m src.challenge", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--tiempos", type=float, nargs="+", default=[30, 120, 600],
                   help="segundos por grafo en cada pasada")
    p.add_argument("--procesos", type=int, default=max(1, (os.cpu_count() or 2) - 2),
                   help="por defecto núcleos lógicos - 2 (22 en el i7-13700HX de 24 hilos)")
    p.add_argument("--alg", default="lns")
    p.add_argument("--grafos", type=rango, default=rango("1-1001"), help="p. ej. 1-100")
    p.add_argument("--salida", default=SALIDA)
    p.add_argument("--resumen", action="store_true")
    args = p.parse_args(argv)

    resueltos, hechas = leer_registro(args.salida)
    objetivo = [g for g in args.grafos if os.path.exists(f"{CARPETA}/graph{g}.hcp")]
    if len(objetivo) < len(args.grafos):
        sys.exit(f"Faltan grafos en {CARPETA}: ejecuta antes bash datos/descargar_fhcp.sh")
    if args.resumen:
        r = [g for g in objetivo if g in resueltos]
        print(f"Resueltos: {len(r)}/{len(objetivo)} | TOUR verificados desde disco: "
              f"{verificar_tours(r)}")
        print("Sin resolver:", [g for g in objetivo if g not in resueltos])
        return 0

    tamanos = {}
    os.makedirs(os.path.dirname(args.salida) or ".", exist_ok=True)
    os.makedirs(TOURS, exist_ok=True)
    with open(args.salida, "a") as f:
        for pasada, tiempo in enumerate(args.tiempos):
            pendientes = [g for g in objetivo if g not in resueltos and (g, pasada) not in hechas]
            if not pendientes:
                continue
            for g in pendientes:
                if g not in tamanos:
                    with open(f"{CARPETA}/graph{g}.hcp") as h:
                        tamanos[g] = next(int(l.split(":")[1]) for l in h if l.startswith("DIMENSION"))
            pendientes.sort(key=lambda g: -tamanos[g])
            print(f"Pasada {pasada + 1}/{len(args.tiempos)}: {len(pendientes)} grafos × {tiempo:g} s "
                  f"con {args.procesos} procesos (≤ {len(pendientes) * tiempo / args.procesos / 60:.0f} min). "
                  f"Resueltos hasta ahora: {len(resueltos)}/{len(objetivo)}", flush=True)
            tareas = [(g, pasada, tiempo, args.alg) for g in pendientes]
            with mp.Pool(args.procesos) as pool:
                for r in pool.imap_unordered(ejecutar, tareas):
                    f.write(json.dumps(r) + "\n")
                    f.flush()
                    if r["exito"]:
                        resueltos.add(r["num"])
                    print(f"  {r['grafo']:<14} n={r['n']:<5} "
                          f"{'CICLO' if r['exito'] else 'faltan ' + str(r['costo']):<10} "
                          f"{r['tiempo_s']:7.1f}s | resueltos {len(resueltos)}/{len(objetivo)}",
                          flush=True)
    print(f"Total: {len([g for g in objetivo if g in resueltos])}/{len(objetivo)} grafos con ciclo "
          f"hamiltoniano verificado (ganadores del concurso: 985/1001).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
