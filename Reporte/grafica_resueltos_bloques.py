"""Gráfica de grafos resueltos por bloque de 100 en la campaña ``python3 -m src.challenge``.

Uso desde la raíz del repositorio (se puede repetir mientras la campaña sigue en marcha)::

    .venv/bin/python Reporte/grafica_resueltos_bloques.py

Lee ``resultados/challenge.jsonl`` y ``datos/instancias.csv``. Escribe
``Reporte/figuras/challenge/resueltos_por_bloque.png`` (y .pdf) y un CSV con las cifras.
"""

import csv
import json
import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-fhcp-challenge")

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

REGISTRO = RAIZ / "resultados" / "challenge.jsonl"
INSTANCIAS = RAIZ / "datos" / "instancias.csv"
SALIDA = RAIZ / "Reporte" / "figuras" / "challenge"

SERIE = "#2a78d6"      # serie única
PISTA = "#e6e5e1"      # capacidad del bloque (grafos del bloque)
TEXTO = "#0b0b0b"
TEXTO_2 = "#52514e"
REJILLA = "#e3e2de"
FONDO = "#ffffff"
GANADORES = 985


def bloques():
    """[(inicio, fin)], el último bloque incluye el grafo 1001."""
    b = [(a, a + 99) for a in range(1, 901, 100)]
    b.append((901, 1001))
    return b


def leer():
    resueltos = set()
    with open(REGISTRO) as f:
        for linea in f:
            try:
                d = json.loads(linea)
            except json.JSONDecodeError:
                continue
            if d.get("exito"):
                resueltos.add(d["num"])
    n = {}
    with open(INSTANCIAS) as f:
        for fila in csv.DictReader(f):
            n[int(fila["grafo"].removeprefix("graph").removesuffix(".hcp"))] = int(fila["n"])
    return resueltos, n


def barra(ax, x, alto, ancho, color):
    if alto > 0:
        ax.bar(x, alto, ancho, color=color, linewidth=0)


def main():
    resueltos, n = leer()
    filas = []
    for a, b in bloques():
        total = b - a + 1
        ok = sum(1 for g in resueltos if a <= g <= b)
        tam = [n[g] for g in range(a, b + 1)]
        filas.append({"bloque": f"{a}–{b}", "grafos": total, "resueltos": ok,
                      "n_min": min(tam), "n_max": max(tam)})

    SALIDA.mkdir(parents=True, exist_ok=True)
    with open(SALIDA / "resueltos_por_bloque.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
    fig, ax = plt.subplots(figsize=(8.6, 4.6), dpi=200)
    fig.patch.set_facecolor(FONDO)
    ax.set_facecolor(FONDO)

    ancho = 0.62
    for i, f_ in enumerate(filas):
        barra(ax, i, f_["grafos"], ancho, PISTA)
        barra(ax, i, f_["resueltos"], ancho, SERIE)
        ax.text(i, f_["resueltos"] + 2.5, str(f_["resueltos"]), ha="center", va="bottom",
                fontsize=10, fontweight="bold", color=TEXTO)

    ax.set_xlim(-0.6, len(filas) - 0.4)
    ax.set_ylim(0, 112)
    ax.set_xticks(range(len(filas)))
    ax.set_xticklabels([f"{f_['bloque']}\n{f_['n_min']}–{f_['n_max']}"
                        for f_ in filas], fontsize=7.4, color=TEXTO_2)
    ax.set_yticks(range(0, 101, 25))
    ax.tick_params(axis="y", colors=TEXTO_2, length=0, labelsize=8.5)
    ax.tick_params(axis="x", length=0, pad=6)
    ax.yaxis.grid(True, color=REJILLA, linewidth=0.8)
    ax.set_axisbelow(True)
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color("#b9b8b3")
    ax.set_ylabel("Grafos con ciclo verificado", color=TEXTO_2, fontsize=9)
    ax.set_xlabel("Bloque de grafos del FHCP Challenge Set (rango de vértices)",
                  color=TEXTO_2, fontsize=9, labelpad=8)

    total = len(resueltos)
    fig.text(0.075, 0.955, "Grafos resueltos por bloque de 100", fontsize=13,
             fontweight="bold", color=TEXTO, ha="left")
    fig.text(0.075, 0.905,
             f"Total: {total} de 1 001 con ciclo hamiltoniano verificado "
             f"(ganadores del concurso: {GANADORES}). La barra gris marca los grafos del bloque.",
             fontsize=8.8, color=TEXTO_2, ha="left")
    fig.subplots_adjust(left=0.075, right=0.985, top=0.85, bottom=0.2)

    for ext in ("png", "pdf"):
        fig.savefig(SALIDA / f"resueltos_por_bloque.{ext}", facecolor=FONDO)
    print(f"{total}/1001 resueltos -> {SALIDA / 'resueltos_por_bloque.png'}")
    for f_ in filas:
        print(f"  {f_['bloque']:>9}: {f_['resueltos']:3d}/{f_['grafos']}")


if __name__ == "__main__":
    main()
