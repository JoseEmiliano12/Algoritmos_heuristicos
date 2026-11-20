"""Genera tablas y gráficas legibles para el FHCP Challenge completo.

Uso desde la raíz del repositorio::

    python Reporte/graficas_challenge.py

Acepta datos parciales: los grafos todavía no ejecutados aparecen en gris.
"""

import argparse
import json
import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-fhcp-challenge")

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from challenge import resumir  # noqa: E402


ALGORITMOS = ("aco_posa", "abc")
ETIQUETAS = ("ACO + Pósa", "ABC")
COLORES = ("#71314b", "#168474")


def wilson(exitos, total, z=1.96):
    if not total:
        return 0.0, 0.0
    p = exitos / total
    denom = 1 + z * z / total
    centro = (p + z * z / (2 * total)) / denom
    margen = z * np.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denom
    return max(0.0, centro - margen), min(1.0, centro + margen)


def cargar(ruta, instancias, semillas):
    corridas = np.zeros((instancias, len(ALGORITMOS)), dtype=int)
    exitos = np.zeros_like(corridas)
    tiempos = {a: [] for a in ALGORITMOS}
    claves = set()
    with open(ruta, encoding="utf-8") as archivo:
        for linea in archivo:
            try:
                r = json.loads(linea)
                nombre, alg, semilla = r["grafo"], r["algoritmo"], r["semilla"]
                numero = int(nombre.removeprefix("graph").removesuffix(".hcp"))
                if not (1 <= numero <= instancias and alg in ALGORITMOS
                        and type(semilla) is int and 0 <= semilla < semillas):
                    continue
                clave = (numero, alg, semilla)
                if clave in claves:
                    continue
                claves.add(clave)
                j = ALGORITMOS.index(alg)
                corridas[numero - 1, j] += 1
                exitos[numero - 1, j] += bool(r["exito"])
                tiempos[alg].append(float(r["tiempo_s"]))
            except (AttributeError, KeyError, TypeError, ValueError, json.JSONDecodeError):
                continue
    return corridas, exitos, tiempos


def generar(ruta, salida, instancias, semillas):
    if not ruta.is_file():
        raise SystemExit(f"Todavía no existe {ruta}")
    corridas, exitos, tiempos = cargar(ruta, instancias, semillas)
    terminadas = int(corridas.sum())
    esperadas = instancias * len(ALGORITMOS) * semillas
    if not terminadas:
        raise SystemExit("El archivo no contiene corridas válidas.")
    salida.mkdir(parents=True, exist_ok=True)
    resumir(str(ruta), instancias, ALGORITMOS, semillas)
    estado = "completo" if terminadas == esperadas else "parcial"
    subtitulo = f"{terminadas:,} de {esperadas:,} corridas ({estado})".replace(",", "\u202f")
    plt.rcParams.update({"font.family": "serif", "font.size": 10, "savefig.dpi": 150})

    # Tasa global por algoritmo, siempre calculada sobre corridas ya terminadas.
    n = corridas.sum(axis=0)
    k = exitos.sum(axis=0)
    tasas = np.divide(k, n, out=np.zeros(len(ALGORITMOS), dtype=float), where=n > 0)
    intervalos = [wilson(int(k[j]), int(n[j])) for j in range(len(ALGORITMOS))]
    errores = np.array([[tasas[j] - intervalos[j][0] for j in range(len(ALGORITMOS))],
                        [intervalos[j][1] - tasas[j] for j in range(len(ALGORITMOS))]])
    fig, ax = plt.subplots(figsize=(7, 4.2))
    barras = ax.bar(ETIQUETAS, tasas * 100, color=COLORES, width=.55)
    ax.errorbar(range(len(ALGORITMOS)), tasas * 100, yerr=errores * 100,
                fmt="none", ecolor="#333333", capsize=5)
    ax.set_ylim(0, max(15, float(max(intervalos, key=lambda x: x[1])[1] * 130)))
    ax.set_ylabel("Corridas exitosas (%)")
    ax.set_title("Tasa de éxito (IC 95 %)\n" + subtitulo)
    for j, barra in enumerate(barras):
        ax.text(barra.get_x() + barra.get_width() / 2, barra.get_height() + 1,
                f"{k[j]}/{n[j]}", ha="center", va="bottom")
    fig.tight_layout()
    fig.savefig(salida / "tasa_exito.png")
    plt.close(fig)

    # Cobertura acumulada: número de grafos con al menos una semilla exitosa.
    fig, ax = plt.subplots(figsize=(9, 4.4))
    ultimo_probado = int(np.flatnonzero(corridas.sum(axis=1))[-1] + 1)
    for j, etiqueta in enumerate(ETIQUETAS):
        ax.plot(np.arange(1, ultimo_probado + 1),
                np.cumsum(exitos[:, j] > 0)[:ultimo_probado],
                label=etiqueta, color=COLORES[j], linewidth=2)
    ax.set(xlim=(1, max(2, ultimo_probado)), ylim=(0, None),
           xlabel="Índice del grafo FHCP",
           ylabel="Grafos resueltos acumulados")
    ax.set_title(f"Cobertura hasta graph{ultimo_probado}\n" + subtitulo)
    ax.grid(axis="y", alpha=.2)
    ax.legend()
    fig.tight_layout()
    fig.savefig(salida / "grafos_resueltos.png")
    plt.close(fig)

    # Mapa de las 1001 instancias; gris significa que no hay ninguna corrida.
    mapa = np.divide(exitos, corridas,
                     out=np.zeros_like(exitos, dtype=float), where=corridas > 0)
    mapa = np.ma.masked_where(corridas == 0, mapa)
    cmap = plt.colormaps["viridis"].copy()
    cmap.set_bad("#e6e6e6")
    fig, ax = plt.subplots(figsize=(6.5, 15))
    imagen = ax.imshow(mapa, aspect="auto", interpolation="nearest", vmin=0, vmax=1,
                       cmap=cmap)
    ax.set_xticks(range(len(ALGORITMOS)), ETIQUETAS)
    marcas = np.unique(np.r_[0, np.arange(99, instancias, 100), instancias - 1])
    ax.set_yticks(marcas, [str(i + 1) for i in marcas])
    ax.set_ylabel("Grafo FHCP")
    ax.set_title("Éxito por grafo\n" + subtitulo)
    fig.colorbar(imagen, ax=ax, label="Fracción de semillas exitosas", shrink=.65)
    fig.tight_layout()
    fig.savefig(salida / "mapa_exito.png")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.boxplot([tiempos[a] for a in ALGORITMOS], tick_labels=ETIQUETAS,
               showfliers=False, patch_artist=True,
               boxprops={"facecolor": "#e8e5e2", "edgecolor": "#71314b"})
    ax.set_ylabel("Tiempo por corrida (s)")
    ax.set_title("Distribución del tiempo de ejecución\n" + subtitulo)
    ax.grid(axis="y", alpha=.2)
    fig.tight_layout()
    fig.savefig(salida / "tiempos.png")
    plt.close(fig)

    total_resueltos = int(np.any(exitos > 0, axis=1).sum())
    (salida / "RESUMEN.md").write_text(
        f"# FHCP Challenge ({estado})\n\n"
        f"Corridas: {terminadas:,}/{esperadas:,}. Grafos resueltos por al menos un algoritmo: "
        f"{total_resueltos}/{instancias}.\n\n"
        + "\n".join(f"- {ETIQUETAS[j]}: {int(k[j])}/{int(n[j])} corridas exitosas; "
                    f"{int((exitos[:, j] > 0).sum())}/{instancias} grafos resueltos."
                    for j in range(len(ALGORITMOS)))
        + "\n\nLas tasas parciales usan solo las corridas terminadas. "
        "En el mapa, el gris indica grafos sin ejecuciones.\n",
        encoding="utf-8")
    print(f"Gráficas ({estado}): {salida}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jsonl", type=Path,
                        default=RAIZ / "resultados/challenge_1001_45.jsonl")
    parser.add_argument("--salida", type=Path,
                        default=RAIZ / "resultados/challenge_1001_45_graficas")
    parser.add_argument("--instancias", type=int, default=1001)
    parser.add_argument("--semillas", type=int, default=45)
    args = parser.parse_args()
    generar(args.jsonl.resolve(), args.salida.resolve(), args.instancias, args.semillas)


if __name__ == "__main__":
    main()
