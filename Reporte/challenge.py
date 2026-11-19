"""Ejecuta el FHCP Challenge con 45 semillas por grafo y algoritmo.

Desde cualquier carpeta::

    python Reporte/challenge.py --dry-run
    python Reporte/challenge.py --procesos 10
    python Reporte/challenge.py --resumen

Por defecto usa los 1001 grafos y 45 semillas (0..44). Cada configuración
se guarda en un archivo distinto para poder reanudarla sin mezclar resultados.
"""

import argparse
import collections
import csv
import json
import os
from pathlib import Path
import sys


RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from src import experimentos  # noqa: E402


def reutilizar_diseno_b(salida):
    """Copia una vez las 400 corridas B equivalentes para evitar repetirlas."""
    origen = RAIZ / "resultados/disenoB.jsonl"
    if os.path.exists(salida) or not origen.is_file():
        return
    filas = []
    claves = set()
    with origen.open(encoding="utf-8") as archivo:
        for linea in archivo:
            r = json.loads(linea)
            clave = (r["grafo"], r["algoritmo"], r["semilla"])
            if (r["tiempo_max"] != 120 or r["max_evals"] != 12_000_000
                    or r["algoritmo"] not in ("aco_posa", "abc")
                    or r["semilla"] not in (0, 1) or clave in claves):
                raise ValueError("El diseño B existente no coincide con este experimento")
            claves.add(clave)
            filas.append(linea)
    if len(filas) != 400:
        raise ValueError(f"Se esperaban 400 corridas B; se encontraron {len(filas)}")
    with open(salida, "x", encoding="utf-8") as archivo:
        archivo.writelines(filas)
    print(f"Se reutilizaron {len(filas)} corridas verificadas de {origen}.", flush=True)


def resumir(salida, instancias, algoritmos, semillas):
    """Genera un resumen global y otro por grafo a partir de resultados completos o parciales."""
    if not os.path.exists(salida):
        print(f"Todavía no hay resultados en {salida}.")
        return 0

    vistas = set()
    invalidas = 0
    ejecuciones = collections.Counter()
    exitos_algoritmo = collections.Counter()
    resueltas_algoritmo = collections.defaultdict(set)
    resueltas_total = set()
    tamanos = {}
    por_grafo = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
    with open(salida, encoding="utf-8") as archivo:
        for linea in archivo:
            try:
                r = json.loads(linea)
                clave = (r["grafo"], r["algoritmo"], r["semilla"])
                numero = int(r["grafo"].removeprefix("graph").removesuffix(".hcp"))
                if not (1 <= numero <= instancias and r["algoritmo"] in algoritmos
                        and type(r["semilla"]) is int and 0 <= r["semilla"] < semillas):
                    invalidas += 1
                    continue
                exito = bool(r["exito"])
                tamano = r["n"]
                if clave in vistas:
                    continue
                vistas.add(clave)
                grafo, algoritmo = r["grafo"], r["algoritmo"]
                tamanos[grafo] = tamano
                ejecuciones[algoritmo] += 1
                exitos_algoritmo[algoritmo] += exito
                celda = por_grafo[grafo][algoritmo]
                celda[0] += exito
                celda[1] += 1
                if exito:
                    resueltas_algoritmo[algoritmo].add(grafo)
                    resueltas_total.add(grafo)
            except (AttributeError, KeyError, ValueError, TypeError, json.JSONDecodeError):
                invalidas += 1

    total = instancias * len(algoritmos) * semillas
    terminadas = len(vistas)

    base = os.path.splitext(salida)[0]
    resumen = base + "_resumen.csv"
    detalle = base + "_grafos.csv"
    with open(resumen, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(("algoritmo", "ejecuciones", "esperadas", "exitos",
                           "tasa_exito_ejecutadas", "grafos_resueltos"))
        for algoritmo in algoritmos:
            n = ejecuciones[algoritmo]
            exitos = exitos_algoritmo[algoritmo]
            resueltos = len(resueltas_algoritmo[algoritmo])
            escritor.writerow((algoritmo, n, instancias * semillas, exitos,
                               f"{exitos / n:.4f}" if n else "", resueltos))
            print(f"{algoritmo}: {n}/{instancias * semillas} corridas; "
                  f"{exitos} éxitos; {resueltos}/{instancias} grafos resueltos")
        exitos_total = sum(exitos_algoritmo.values())
        grafos_resueltos = len(resueltas_total)
        escritor.writerow(("total", terminadas, total, exitos_total,
                           f"{exitos_total / terminadas:.4f}" if terminadas else "",
                           grafos_resueltos))

    with open(detalle, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(("grafo", "n", "resuelto_por_alguno")
                           + tuple(f"{a}_exitos" for a in algoritmos)
                           + tuple(f"{a}_ejecuciones" for a in algoritmos))
        for i in range(1, instancias + 1):
            nombre = f"graph{i}.hcp"
            celdas = por_grafo[nombre]
            escritor.writerow((nombre, tamanos.get(nombre, ""),
                               int(any(celdas[a][0] for a in algoritmos)))
                              + tuple(celdas[a][0] for a in algoritmos)
                              + tuple(celdas[a][1] for a in algoritmos))

    print(f"Total: {terminadas}/{total} corridas; "
          f"{grafos_resueltos}/{instancias} grafos resueltos por al menos un algoritmo. "
          f"Resultados: {resumen} y {detalle}.")
    if invalidas:
        print(f"Se omitieron {invalidas} líneas inválidas o ajenas a este experimento.")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instancias", type=int, choices=(100, 1001), default=1001,
                        help="cantidad de grafos del Challenge (por defecto: 1001)")
    parser.add_argument("--semillas", type=int, default=45,
                        help="semillas 0 a N-1 (por defecto: 45)")
    parser.add_argument("--procesos", type=int, default=10,
                        help="corridas simultáneas (por defecto: 10)")
    parser.add_argument("--salida", help="archivo JSONL de salida")
    parser.add_argument("--dry-run", action="store_true",
                        help="mostrar las corridas pendientes sin ejecutarlas")
    parser.add_argument("--resumen", action="store_true",
                        help="generar CSV global y por grafo desde resultados existentes")
    parser.add_argument("--preparar", action="store_true",
                        help="reutilizar las 400 corridas B equivalentes sin iniciar el benchmark")
    args = parser.parse_args(argv)
    if args.procesos < 1:
        parser.error("--procesos debe ser mayor que cero")
    if args.semillas < 1:
        parser.error("--semillas debe ser mayor que cero")

    diseno = experimentos.DISENOS["B"].copy()
    diseno["semillas"] = range(args.semillas)
    diseno["grafos"] = [f"datos/fhcp_completo/graph{i}.hcp"
                        for i in range(1, args.instancias + 1)]
    diseno["salida"] = f"resultados/challenge_{args.instancias}_{args.semillas}.jsonl"
    experimentos.DISENOS["B"] = diseno
    salida = args.salida or diseno["salida"]

    os.chdir(RAIZ)  # Las rutas del ejecutor son relativas a la raíz del repositorio.
    if args.resumen:
        return resumir(salida, args.instancias, diseno["algoritmos"], args.semillas)
    if args.preparar:
        if args.salida or args.instancias != 1001 or args.semillas != 45:
            parser.error("--preparar solo aplica al Challenge completo de 45 semillas")
        reutilizar_diseno_b(salida)
        return 0
    if (not args.dry_run and not args.salida and args.instancias == 1001
            and args.semillas == 45):
        reutilizar_diseno_b(salida)

    opciones = ["B", "--procesos", str(args.procesos)]
    if args.salida:
        opciones.extend(("--salida", args.salida))
    if args.dry_run:
        opciones.append("--dry-run")

    return experimentos.main(opciones)


if __name__ == "__main__":
    sys.exit(main())
