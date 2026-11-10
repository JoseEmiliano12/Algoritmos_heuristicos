"""Convierte los resultados de los experimentos en tablas LaTeX y copia las figuras al reporte.

Uso (desde la raíz del repositorio, después de correr experimentos y gráficas)::

    python Reporte/actualizar.py

Lee  resultados/diseno{A,B,C}.jsonl  y  resultados/diseno{A,B,C}/*.png|csv
Escribe  Reporte/tablas/*.tex,  Reporte/figuras/diseno{A,B,C}/*.png  y  Reporte/tablas/datos.tex
(macros con cifras clave para citarlas en el texto sin copiarlas a mano).
"""
import collections
import csv
import inspect
import json
import os
import platform
import shutil
import statistics as st
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
from src.algoritmos import ALGORITMOS, obtener  # noqa: E402

REP = os.path.join(RAIZ, "Reporte")
RES = os.path.join(RAIZ, "resultados")
TAB = os.path.join(REP, "tablas")
FIG = os.path.join(REP, "figuras")

ORDEN = ["ga", "sa_swap", "sa", "aco", "aco_posa", "abc", "de", "pso"]
NOMBRE = {"ga": "GA", "sa_swap": "SA (swap)", "sa": "SA (mixto)", "aco": "ACO",
          "aco_posa": "ACO + Pósa", "abc": "ABC", "de": "DE", "pso": "PSO"}
MACRO = {"ga": "GA", "sa_swap": "SAswap", "sa": "SA", "aco": "ACO", "aco_posa": "ACOposa",
         "abc": "ABC", "de": "DE", "pso": "PSO"}


def esc(s):
    return str(s).replace("_", r"\_").replace("%", r"\%").replace("#", r"\#")


def num(x, d=2):
    if x in ("", None):
        return "---"
    x = float(x)
    if x == int(x) and d == 0:
        return f"{int(x):,}".replace(",", r"\,")
    return f"{x:,.{d}f}".replace(",", r"\,")


def cargar(d):
    ruta = os.path.join(RES, f"diseno{d}.jsonl")
    if not os.path.exists(ruta):
        return []
    filas = []
    with open(ruta) as f:
        for linea in f:
            try:
                filas.append(json.loads(linea))
            except json.JSONDecodeError:
                pass
    return filas


def escribir(nombre, texto):
    with open(os.path.join(TAB, nombre), "w") as f:
        f.write("% Generado por Reporte/actualizar.py; no editar a mano.\n" + texto)


def tabla_resumen(d, filas):
    csvp = os.path.join(RES, f"diseno{d}", "resumen_algoritmos.csv")
    if not os.path.exists(csvp):
        return
    rows = {r["algoritmo"]: r for r in csv.DictReader(open(csvp))}
    lineas = []
    for a in ORDEN:
        if a not in rows:
            continue
        r = rows[a]
        lineas.append(
            f"{NOMBRE[a]} & {r['exitos']}/{r['ejecuciones']} & {num(r['tasa_exito'])} "
            f"[{num(r['ic95_inf'])}, {num(r['ic95_sup'])}] & {r['instancias_resueltas']}/{r['instancias']} & "
            f"{num(r['tiempo_medio_s'], 1)} $\\pm$ {num(r['tiempo_de_s'], 1)} & "
            f"{num(r['evals_mediana_exito'], 0)} & {num(r['costo_final_medio'])} & {num(r['f1'])} \\\\")
    escribir(f"resumen_{d}.tex", r"""\begin{tabular}{lrcrrrrr}
\toprule
Algoritmo & Éxitos & Tasa de éxito [IC 95\,\%] & Grafos resueltos & Tiempo (s) & Evaluaciones hasta el éxito & Aristas faltantes (prom.) & F1 \\
\midrule
""" + "\n".join(lineas) + "\n\\bottomrule\n\\end{tabular}\n")


def tabla_instancias_A(filas):
    csvp = os.path.join(RES, "disenoA", "exito_por_instancia.csv")
    if not os.path.exists(csvp):
        return
    m = {r["grafo"]: r["m"] for r in filas}
    rows = list(csv.DictReader(open(csvp)))
    algs = [a for a in ORDEN if a in rows[0]]
    cab = " & ".join(NOMBRE[a] for a in algs)
    cuerpo = []
    for r in rows:
        celdas = []
        for a in algs:
            k = r[a].split("/")[0]
            celdas.append(f"\\textbf{{{r[a]}}}" if k != "0" else r[a])
        cuerpo.append(f"{esc(r['grafo'].removesuffix('.hcp'))} & {r['n']} & {m.get(r['grafo'], '')} & "
                      + " & ".join(celdas) + r" \\")
    escribir("instancias_A.tex", f"\\begin{{tabular}}{{lrr{'c' * len(algs)}}}\n\\toprule\n"
             f"Grafo & $n$ & $m$ & {cab} \\\\\n\\midrule\n" + "\n".join(cuerpo)
             + "\n\\bottomrule\n\\end{tabular}\n")


def tabla_presupuesto(d, filas):
    por = collections.defaultdict(list)
    for r in filas:
        por[r["algoritmo"]].append(r)
    lineas = []
    for a in ORDEN:
        v = por.get(a)
        if not v:
            continue
        fallos = [r for r in v if not r["exito"]]
        t = sum(r["tiempo_s"] >= 0.98 * r["tiempo_max"] for r in fallos)
        e = sum(r["evals"] >= r["max_evals"] for r in fallos)
        ev = st.median(r["evals"] for r in v)
        lineas.append(f"{NOMBRE[a]} & {num(ev, 0)} & {len(fallos)} & {t} & {e} & "
                      f"{num(st.mean(r['tiempo_s'] for r in v), 1)} \\\\")
    escribir(f"presupuesto_{d}.tex", r"""\begin{tabular}{lrrrrr}
\toprule
Algoritmo & Evaluaciones (mediana) & Corridas sin éxito & Paró por tiempo & Paró por evaluaciones & Tiempo promedio (s) \\
\midrule
""" + "\n".join(lineas) + "\n\\bottomrule\n\\end{tabular}\n")


def tabla_escalabilidad(filas):
    if not filas:
        return
    grafos = sorted({(r["n"], r["grafo"], r["m"]) for r in filas})
    algs = [a for a in ORDEN if any(r["algoritmo"] == a for r in filas)]
    costo = {(r["grafo"], r["algoritmo"]): r for r in filas}
    cuerpo = []
    for n, g, m in grafos:
        celdas = []
        for a in algs:
            r = costo.get((g, a))
            if r is None:
                celdas.append("---")
            else:
                mejor = min(costo[(g, b)]["costo"] for b in algs if (g, b) in costo)
                c = "0 \\checkmark" if r["exito"] else str(r["costo"])
                celdas.append(f"\\textbf{{{c}}}" if r["costo"] == mejor else c)
        cuerpo.append(f"{esc(g.removesuffix('.hcp'))} & {n} & {m} & " + " & ".join(celdas) + r" \\")
    escribir("escalabilidad_C.tex", f"\\begin{{tabular}}{{lrr{'r' * len(algs)}}}\n\\toprule\n"
             f"Grafo & $n$ & $m$ & " + " & ".join(NOMBRE[a] for a in algs) + " \\\\\n\\midrule\n"
             + "\n".join(cuerpo) + "\n\\bottomrule\n\\end{tabular}\n")


def tabla_benchmarking(filas):
    if not filas:
        return
    algs = [a for a in ORDEN if any(r["algoritmo"] == a for r in filas)]
    grafos = sorted({r["grafo"] for r in filas}, key=lambda g: int("".join(c for c in g if c.isdigit())))
    nn = {r["grafo"]: r["n"] for r in filas}
    ok = collections.defaultdict(set)
    for r in filas:
        if r["exito"]:
            ok[r["algoritmo"]].add(r["grafo"])
    bloques = [grafos[i:i + 25] for i in range(0, len(grafos), 25)]
    cuerpo = []
    for b in bloques:
        ns = [nn[g] for g in b]
        alguno = set().union(*(ok[a] for a in algs)) & set(b)
        cuerpo.append(f"{esc(b[0].removesuffix('.hcp'))}--{esc(b[-1].removesuffix('.hcp'))} & {min(ns)}--{max(ns)} & "
                      + " & ".join(str(len(ok[a] & set(b))) for a in algs)
                      + f" & {len(alguno)} & {len(b)} \\\\")
    tot = set().union(*(ok[a] for a in algs))
    cuerpo.append("\\midrule\nTotal & & " + " & ".join(str(len(ok[a])) for a in algs)
                  + f" & {len(tot)} & {len(grafos)} \\\\")
    escribir("benchmarking_B.tex", f"\\begin{{tabular}}{{lr{'r' * len(algs)}rr}}\n\\toprule\n"
             "Instancias & $n$ & " + " & ".join(NOMBRE[a] for a in algs)
             + " & Cualquiera de los dos & Con solución oficial \\\\\n\\midrule\n" + "\n".join(cuerpo)
             + "\n\\bottomrule\n\\end{tabular}\n")
    lista = []
    for a in algs:
        gs = sorted(ok[a], key=lambda g: int("".join(c for c in g if c.isdigit())))
        lista.append(f"\\item[{NOMBRE[a]}] " + (", ".join(esc(g.removesuffix('.hcp')) for g in gs) or "ninguna") + ".")
    escribir("resueltas_B.tex", "\\begin{description}\n" + "\n".join(lista) + "\n\\end{description}\n")


def tabla_parametros():
    lineas = []
    for a in ORDEN:
        resolver, fijos = obtener(a)
        ps = {k: p.default for k, p in inspect.signature(resolver).parameters.items()
              if k not in ("adj", "max_evals", "semilla", "tiempo_max")}
        ps.update(fijos)
        txt = ", ".join(f"{esc(k)} $=$ {'auto' if v is None else esc(v)}" for k, v in ps.items())
        lineas.append(f"{NOMBRE[a]} & \\texttt{{{esc(ALGORITMOS[a][0])}.py}} & {txt} \\\\")
    escribir("parametros.tex", r"""\begin{tabularx}{\textwidth}{llL}
\toprule
Algoritmo & Archivo & Parámetros usados \\
\midrule
""" + "\n".join(lineas) + "\n\\bottomrule\n\\end{tabularx}\n")


def tabla_cubicos(datos):
    ruta = os.path.join(RAIZ, "datos", "instancias.csv")
    if not os.path.exists(ruta):
        return
    inst = {r["grafo"]: r for r in csv.DictReader(open(ruta))}
    lineas = []
    for d, nombre in (("A", "A (graph4--graph24)"), ("B", "B (graph1--graph100)")):
        filas = datos[d]
        if not filas:
            continue
        gs = {r["grafo"] for r in filas}
        ok = {r["grafo"] for r in filas if r["exito"]}
        cub = {g for g in gs if inst[g]["grado_max"] == "3"}
        resto = gs - cub
        lineas.append(f"{nombre} & {len(cub & ok)} de {len(cub)} & {len(resto & ok)} de {len(resto)} \\\\")
    escribir("cubicos.tex", r"""\begin{tabular}{lcc}
\toprule
Experimento & Grafos cúbicos resueltos & Grafos no cúbicos resueltos \\
\midrule
""" + "\n".join(lineas) + "\n\\bottomrule\n\\end{tabular}\n")


def macros(datos):
    m = []
    def nuevo(nombre, valor):
        m.append(f"\\newcommand{{\\{nombre}}}{{{valor}}}")
    for d, filas in datos.items():
        nuevo(f"ejec{d}", len(filas))
        nuevo(f"exitos{d}", sum(r["exito"] for r in filas))
        if filas:
            nuevo(f"tiempo{d}", filas[0]["tiempo_max"])
            nuevo(f"evals{d}", num(filas[0]["max_evals"], 0))
            nuevo(f"semillas{d}", len({r["semilla"] for r in filas}))
            nuevo(f"grafos{d}", len({r["grafo"] for r in filas}))
        for a in ORDEN:
            v = [r for r in filas if r["algoritmo"] == a]
            if v:
                nuevo(f"exitos{d}{MACRO[a]}", sum(r["exito"] for r in v))
                nuevo(f"resueltas{d}{MACRO[a]}", len({r["grafo"] for r in v if r["exito"]}))
    try:
        cpu = next(l.split(":", 1)[1].strip() for l in subprocess.run(
            ["lscpu"], capture_output=True, text=True).stdout.splitlines()
            if l.startswith(("Model name", "Nombre del modelo")))
    except Exception:
        cpu = platform.processor() or "desconocido"
    nuevo("cpu", esc(cpu))
    nuevo("hilos", os.cpu_count())
    nuevo("versionpython", platform.python_version())
    nuevo("sistema", esc(f"{platform.system()} {platform.release()}"))
    escribir("datos.tex", "\n".join(m) + "\n")


def copiar_figuras():
    copiadas = 0
    for d in "ABC":
        org = os.path.join(RES, f"diseno{d}")
        if not os.path.isdir(org):
            continue
        dst = os.path.join(FIG, f"diseno{d}")
        os.makedirs(dst, exist_ok=True)
        for f in os.listdir(org):
            if f.endswith(".png"):
                shutil.copy2(os.path.join(org, f), dst)
                copiadas += 1
    return copiadas


def main():
    os.makedirs(TAB, exist_ok=True)
    datos = {d: cargar(d) for d in "ABC"}
    for d, filas in datos.items():
        if filas:
            tabla_resumen(d, filas)
    tabla_instancias_A(datos["A"])
    tabla_presupuesto("A", datos["A"])
    tabla_escalabilidad(datos["C"])
    tabla_benchmarking(datos["B"])
    tabla_parametros()
    tabla_cubicos(datos)
    macros(datos)
    n = copiar_figuras()
    print(f"Tablas en {os.path.relpath(TAB, RAIZ)}/, {n} figuras en {os.path.relpath(FIG, RAIZ)}/ "
          f"(A={len(datos['A'])}, B={len(datos['B'])}, C={len(datos['C'])} ejecuciones)")


if __name__ == "__main__":
    main()
