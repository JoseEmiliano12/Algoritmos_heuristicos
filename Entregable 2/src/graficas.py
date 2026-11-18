"""Tablas y gráficas a partir de un .jsonl de experimentos.

Uso::

    python3 -m src.graficas resultados/disenoA.jsonl            # -> resultados/disenoA/
    python3 -m src.graficas resultados/disenoA.jsonl --salida informe/figs

Genera:
    resumen_algoritmos.md / .csv   éxito (IC 95 % de Wilson), tiempo, evals, costo final, precisión/recall/F1
    exito_por_instancia.csv        tasa de éxito algoritmo × instancia
    exito_algoritmos.png           barras de tasa de éxito con IC 95 %
    heatmap_exito.png              éxito por instancia (filas) y algoritmo (columnas)
    tiempo_boxplot.png             tiempo por ejecución (escala log)
    costo_final_boxplot.png        aristas faltantes al terminar (0 = ciclo)
    convergencia_<grafo>.png       mediana del mejor costo frente a evaluaciones (3 instancias)

Puede ejecutarse con el experimento a medias: usa lo que haya.
"""
import argparse
import collections
import csv
import json
import math
import os
import statistics as st
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ORDEN = ["ga", "sa_swap", "sa", "aco", "aco_posa", "abc", "de", "pso"]


def wilson(k, n, z=1.96):
    if n == 0:
        return 0.0, 0.0
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return max(0.0, c - h), min(1.0, c + h)


def num_grafo(g):
    dig = "".join(ch for ch in g if ch.isdigit())
    return int(dig) if dig else 0


def cargar(ruta):
    filas = []
    with open(ruta) as f:
        for linea in f:
            try:
                filas.append(json.loads(linea))
            except json.JSONDecodeError:
                pass
    return filas


def resumen(filas, algs):
    out = []
    for a in algs:
        v = [r for r in filas if r["algoritmo"] == a]
        ok = [r for r in v if r["exito"]]
        k, n = len(ok), len(v)
        lo, hi = wilson(k, n)
        t = [r["tiempo_s"] for r in v]
        # Todas las instancias del FHCP tienen ciclo: detección = ciclo verificado.
        recall = k / n if n else 0.0
        precision = 1.0 if k else 0.0
        f1 = 2 * precision * recall / (precision + recall) if k else 0.0
        out.append({
            "algoritmo": a, "ejecuciones": n, "exitos": k, "tasa_exito": round(recall, 3),
            "ic95_inf": round(lo, 3), "ic95_sup": round(hi, 3),
            "instancias_resueltas": len({r["grafo"] for r in ok}),
            "instancias": len({r["grafo"] for r in v}),
            "tiempo_medio_s": round(st.mean(t), 2) if t else None,
            "tiempo_de_s": round(st.stdev(t), 2) if len(t) > 1 else 0.0,
            "tiempo_mediano_exito_s": round(st.median([r["tiempo_s"] for r in ok]), 2) if ok else None,
            "evals_mediana_exito": int(st.median([r["evals"] for r in ok])) if ok else None,
            "costo_final_medio": round(st.mean(r["costo"] for r in v), 2) if v else None,
            "precision": precision, "recall": round(recall, 3), "f1": round(f1, 3),
        })
    return out


def escribir_tablas(res, filas, algs, grafos, carpeta):
    with open(os.path.join(carpeta, "resumen_algoritmos.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(res[0]))
        w.writeheader()
        w.writerows(res)

    def fmt(x):
        return "—" if x is None else str(x)

    lineas = ["| Algoritmo | Éxitos | Tasa (IC 95 %) | Instancias resueltas | Tiempo medio ± DE (s) "
              "| Evals mediana (éxitos) | Costo final medio | F1 |",
              "|---|---|---|---|---|---|---|---|"]
    for r in res:
        lineas.append(
            f"| `{r['algoritmo']}` | {r['exitos']}/{r['ejecuciones']} | {r['tasa_exito']:.2f} "
            f"[{r['ic95_inf']:.2f}, {r['ic95_sup']:.2f}] | {r['instancias_resueltas']}/{r['instancias']} "
            f"| {fmt(r['tiempo_medio_s'])} ± {fmt(r['tiempo_de_s'])} | {fmt(r['evals_mediana_exito'])} "
            f"| {fmt(r['costo_final_medio'])} | {r['f1']:.2f} |")
    lineas += ["", "Precisión = 1 siempre que hay detecciones (todas las instancias del FHCP tienen ciclo), "
               "así que F1 depende solo del recall (= tasa de éxito). Sin ciclo al agotar el presupuesto "
               "= inconcluso, no «no hamiltoniano»."]
    with open(os.path.join(carpeta, "resumen_algoritmos.md"), "w") as f:
        f.write("\n".join(lineas) + "\n")

    with open(os.path.join(carpeta, "exito_por_instancia.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["grafo", "n"] + algs)
        for g in grafos:
            v = [r for r in filas if r["grafo"] == g]
            fila = [g, v[0]["n"]]
            for a in algs:
                va = [r for r in v if r["algoritmo"] == a]
                fila.append(f"{sum(r['exito'] for r in va)}/{len(va)}" if va else "")
            w.writerow(fila)
    return "\n".join(lineas)


def graficas(res, filas, algs, grafos, carpeta):
    x = np.arange(len(algs))
    tasa = np.array([r["tasa_exito"] for r in res])
    err = np.array([[r["tasa_exito"] - r["ic95_inf"] for r in res],
                    [r["ic95_sup"] - r["tasa_exito"] for r in res]])
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(x, tasa, yerr=err, capsize=4, color="#4C72B0")
    ax.set_xticks(x, algs)
    ax.set_ylim(0, 1)
    ax.set_ylabel("Tasa de éxito (IC 95 %)")
    ax.set_title("Ciclo hamiltoniano verificado por algoritmo")
    for i, r in enumerate(res):
        ax.text(i, min(0.97, r["tasa_exito"] + 0.03), f"{r['exitos']}/{r['ejecuciones']}",
                ha="center", fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(carpeta, "exito_algoritmos.png"), dpi=150)
    plt.close(fig)

    M = np.full((len(grafos), len(algs)), np.nan)
    for i, g in enumerate(grafos):
        for j, a in enumerate(algs):
            v = [r["exito"] for r in filas if r["grafo"] == g and r["algoritmo"] == a]
            if v:
                M[i, j] = sum(v) / len(v)
    fig, ax = plt.subplots(figsize=(8, max(4, 0.32 * len(grafos) + 1.5)))
    im = ax.imshow(M, cmap="viridis", vmin=0, vmax=1, aspect="auto")
    ns = {r["grafo"]: r["n"] for r in filas}
    ax.set_xticks(range(len(algs)), algs, rotation=30)
    ax.set_yticks(range(len(grafos)), [f"{g.removesuffix('.hcp')} (n={ns[g]})" for g in grafos], fontsize=8)
    for i in range(len(grafos)):
        for j in range(len(algs)):
            if not np.isnan(M[i, j]):
                ax.text(j, i, f"{M[i, j]:.1f}", ha="center", va="center", fontsize=7,
                        color="black" if M[i, j] > 0.5 else "white")
    fig.colorbar(im, ax=ax, label="tasa de éxito")
    ax.set_title("Tasa de éxito por instancia")
    fig.tight_layout()
    fig.savefig(os.path.join(carpeta, "heatmap_exito.png"), dpi=150)
    plt.close(fig)

    for campo, nombre, etiqueta, log in [("tiempo_s", "tiempo_boxplot.png", "tiempo por ejecución (s)", True),
                                         ("costo", "costo_final_boxplot.png",
                                          "aristas faltantes al terminar (0 = ciclo)", False)]:
        datos = [[r[campo] for r in filas if r["algoritmo"] == a] for a in algs]
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.boxplot(datos, showfliers=True)
        ax.set_xticks(range(1, len(algs) + 1), algs)
        if log:
            ax.set_yscale("log")
        ax.set_ylabel(etiqueta)
        fig.tight_layout()
        fig.savefig(os.path.join(carpeta, nombre), dpi=150)
        plt.close(fig)

    # Convergencia: instancia más pequeña, intermedia y más grande con curvas guardadas.
    con_curva = [g for g in grafos if any(r.get("curva") for r in filas if r["grafo"] == g)]
    elegidos = sorted({con_curva[0], con_curva[len(con_curva) // 2], con_curva[-1]},
                      key=num_grafo) if con_curva else []
    for g in elegidos:
        fig, ax = plt.subplots(figsize=(8, 4))
        for a in algs:
            curvas = [r["curva"] for r in filas if r["grafo"] == g and r["algoritmo"] == a and r.get("curva")]
            if not curvas:
                continue
            xmax = max(c[-1][0] for c in curvas)
            xs = np.unique(np.geomspace(1, max(xmax, 2), 200).astype(int))
            ys = []
            for c in curvas:
                cx, cy = [p[0] for p in c], [p[1] for p in c]
                idx = np.searchsorted(cx, xs, side="right") - 1
                # Antes del primer punto: costo inicial; después del último (ya paró): costo final.
                ys.append(np.array(cy)[np.clip(idx, 0, len(cy) - 1)])
            ax.plot(xs, np.median(ys, axis=0), label=a)
        ax.set_xscale("log")
        ax.set_xlabel("evaluaciones de fitness (aprox.)")
        ax.set_ylabel("mejor costo (mediana entre semillas)")
        ax.set_title(f"Convergencia en {g.removesuffix('.hcp')}")
        ax.legend(fontsize=8, ncol=2)
        fig.tight_layout()
        fig.savefig(os.path.join(carpeta, f"convergencia_{g.removesuffix('.hcp')}.png"), dpi=150)
        plt.close(fig)


def main(argv=None):
    p = argparse.ArgumentParser(prog="python3 -m src.graficas", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("jsonl")
    p.add_argument("--salida", help="carpeta de salida (por defecto, junto al .jsonl)")
    args = p.parse_args(argv)

    filas = cargar(args.jsonl)
    if not filas:
        sys.exit("El archivo no tiene resultados.")
    carpeta = args.salida or os.path.splitext(args.jsonl)[0]
    os.makedirs(carpeta, exist_ok=True)
    presentes = {r["algoritmo"] for r in filas}
    algs = [a for a in ORDEN if a in presentes] + sorted(presentes - set(ORDEN))
    grafos = sorted({r["grafo"] for r in filas}, key=num_grafo)

    res = resumen(filas, algs)
    print(escribir_tablas(res, filas, algs, grafos, carpeta))
    graficas(res, filas, algs, grafos, carpeta)
    print(f"\n{len(filas)} ejecuciones · tablas y gráficas en {carpeta}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
