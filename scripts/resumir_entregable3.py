"""Regenera tablas CSV de los resultados incluidos, sin dependencias externas."""
import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
R = ROOT / "resultados"


def load(name):
    with (R / name).open(encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def write(name, header, rows):
    with (R / name).open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(rows)


def summary():
    datasets = {
        "A": load("disenoA.jsonl"),
        "B": load("disenoB.jsonl"),
        "C": load("disenoC.jsonl"),
        "LNS": load("challenge.jsonl"),
        "45 semillas (parcial)": load("challenge_1001_45.jsonl"),
    }
    specs = {"A": 1680, "B": 400, "C": 32, "LNS": 2656,
             "45 semillas (parcial)": 90090}

    general = []
    algorithms = []
    for design, rows in datasets.items():
        successes = [r for r in rows if r["exito"]]
        graph_name = lambda r: r["num"] if design == "LNS" else r["grafo"]
        graphs = len({graph_name(r) for r in successes})
        general.append((design, len(rows), specs[design], len(successes), graphs,
                        "parcial" if design.startswith("45") else "completo"))
        for alg in sorted({r["algoritmo"] for r in rows}):
            subset = [r for r in rows if r["algoritmo"] == alg]
            successful = [r for r in subset if r["exito"]]
            algorithms.append((
                design, alg, len(subset), len(successful),
                len({graph_name(r) for r in successful}),
                round(statistics.median(r["tiempo_s"] for r in successful), 3)
                if successful else "",
                round(statistics.median(r["tiempo_s"] for r in subset), 3)
            ))
    write("resumen_entregable3.csv",
          ("campaña", "corridas_registradas", "corridas_planificadas",
           "corridas_exitosas", "grafos_distintos_resueltos", "estado"), general)
    write("algoritmos_entregable3.csv",
          ("campaña", "algoritmo", "corridas", "exitos", "grafos_resueltos",
           "mediana_tiempo_exitos_s", "mediana_tiempo_todas_s"), algorithms)

    lns = datasets["LNS"]
    passes = []
    cumulative = 0
    for pass_id, limit in enumerate((30, 120, 600)):
        subset = [r for r in lns if r["pasada"] == pass_id]
        solved = sum(bool(r["exito"]) for r in subset)
        cumulative += solved
        passes.append((pass_id + 1, limit, len(subset), solved,
                       cumulative, round(sum(r["tiempo_s"] for r in subset) / 3600, 2)))
    write("challenge_pasadas.csv",
          ("pasada", "limite_s", "intentos", "nuevos_ciclos",
           "ciclos_acumulados", "suma_tiempos_h"), passes)

    with (ROOT / "datos/instancias.csv").open(encoding="utf-8", newline="") as file:
        metadata = list(csv.DictReader(file))
    baseline = {int(r["grafo"].removeprefix("graph").removesuffix(".hcp"))
                for r in datasets["B"] if r["exito"]}
    by_graph = defaultdict(list)
    for row in lns:
        by_graph[row["num"]].append(row)
    partial = defaultdict(list)
    for row in datasets["45 semillas (parcial)"]:
        num = int(row["grafo"].removeprefix("graph").removesuffix(".hcp"))
        partial[num, row["algoritmo"]].append(row)

    detail = []
    for row in metadata:
        num = int(row["grafo"].removeprefix("graph").removesuffix(".hcp"))
        attempts = by_graph[num]
        solved = next((r for r in attempts if r["exito"]), None)
        aco = partial[num, "aco_posa"]
        abc = partial[num, "abc"]
        detail.append((row["grafo"], int(row["n"]),
                       int(num in baseline) if num <= 100 else "",
                       int(solved is not None),
                       solved["pasada"] + 1 if solved else "",
                       solved["tiempo_s"] if solved else "",
                       len(attempts),
                       len(aco), sum(r["exito"] for r in aco),
                       len(abc), sum(r["exito"] for r in abc)))
    write("challenge_por_grafo.csv",
          ("grafo", "vertices", "disenoB_exito_si_primeros100",
           "lns_exito", "lns_pasada_exito", "lns_tiempo_exito_s",
           "lns_intentos", "aco_posa_45_intentos", "aco_posa_45_exitos",
           "abc_45_intentos", "abc_45_exitos"), detail)
    print("Tablas actualizadas: resumen, algoritmos, pasadas y 1001 grafos.")


if __name__ == "__main__":
    summary()
