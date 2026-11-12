"""Verifica los resultados sin importar ningún módulo de ``src``.

Desde la raíz del proyecto::

    python3 pruebas/verificar_resultados.py --allow-missing
    bash datos/descargar_fhcp.sh
    python3 pruebas/verificar_resultados.py

La primera orden revisa todos los registros y los grafos incluidos. La segunda
permite recalcular los costos de las 2 112 corridas contra el set completo.
"""

import argparse
import itertools
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ALGORITHMS = ("ga", "sa", "sa_swap", "aco", "aco_posa", "abc", "de", "pso")
DESIGNS = {
    "A": (range(4, 25), ALGORITHMS, range(10)),
    "B": (range(1, 101), ("aco_posa", "abc"), range(2)),
    "C": ((50, 200, 500, 1001), ALGORITHMS, range(1)),
}


def load_hcp(path):
    """Lee de forma independiente el formato HCP/EDGE_LIST (vértices 1..n)."""
    lines = path.read_text(encoding="utf-8").splitlines()
    n = None
    start = None
    for i, line in enumerate(lines):
        if line.startswith("DIMENSION"):
            n = int(line.split(":", 1)[1].strip())
        if line.strip() == "EDGE_DATA_SECTION":
            start = i + 1
            break
    if n is None or start is None:
        raise ValueError(f"Cabecera HCP incompleta: {path}")
    adjacency = [set() for _ in range(n + 1)]
    for line in lines[start:]:
        if line.strip() == "-1":
            break
        u, v = map(int, line.split())
        if not (1 <= u <= n and 1 <= v <= n):
            raise ValueError(f"Arista fuera de rango en {path}: {u}, {v}")
        adjacency[u].add(v)
        adjacency[v].add(u)
    return n, adjacency


def load_tour(path):
    """Lee una ruta TOUR sin usar el lector del proyecto."""
    lines = path.read_text(encoding="utf-8").splitlines()
    try:
        start = lines.index("TOUR_SECTION") + 1
    except ValueError as exc:
        raise ValueError(f"Falta TOUR_SECTION: {path}") from exc
    route = []
    for line in lines[start:]:
        if line.strip() == "-1":
            return route
        route.extend(map(int, line.split()))
    raise ValueError(f"Falta terminador -1: {path}")


def cost(route, adjacency):
    return sum(route[i - 1] not in adjacency[route[i]] for i in range(len(route)))


def graph_path(name):
    for folder in (ROOT / "datos/fhcp", ROOT / "datos/fhcp_completo"):
        candidate = folder / name
        if candidate.is_file():
            return candidate
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-missing", action="store_true",
                        help="acepta grafos ausentes; verifica por completo los disponibles")
    args = parser.parse_args()
    errors = []
    records = []
    graph_cache = {}
    checked_costs = 0
    missing_graphs = set()
    max_time_excess = 0.0
    checked_tours = set()

    for design, (graphs, algorithms, seeds) in DESIGNS.items():
        file = ROOT / "resultados" / f"diseno{design}.jsonl"
        try:
            rows = [json.loads(line) for line in file.read_text(encoding="utf-8").splitlines()
                    if line.strip()]
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"No se puede leer {file}: {exc}")
            continue
        expected = {(f"graph{i}.hcp", algorithm, seed)
                    for i, algorithm, seed in itertools.product(graphs, algorithms, seeds)}
        seen = [(row["grafo"], row["algoritmo"], row["semilla"]) for row in rows]
        if len(seen) != len(set(seen)):
            errors.append(f"Diseño {design}: combinaciones repetidas")
        if set(seen) != expected:
            errors.append(f"Diseño {design}: faltan {len(expected - set(seen))} combinaciones "
                          f"y sobran {len(set(seen) - expected)}")
        print(f"Diseño {design}: {len(rows)}/{len(expected)} corridas, "
              f"{sum(row['exito'] for row in rows)} éxitos")
        records.extend(rows)

    for row in records:
        name = f"{row['grafo']} {row['algoritmo']} semilla={row['semilla']}"
        n, route = row["n"], row["ruta"]
        if len(route) != n or set(route) != set(range(1, n + 1)):
            errors.append(f"Ruta sin permutación válida: {name}")
            continue
        if (row["costo"] == 0) != row["exito"]:
            errors.append(f"Costo y éxito incongruentes: {name}")
        if row["evals"] > row["max_evals"]:
            errors.append(f"Exceso de evaluaciones: {name}")
        max_time_excess = max(max_time_excess, row["tiempo_s"] - row["tiempo_max"])
        curve = row["curva"]
        if not curve or curve[-1][1] != row["costo"] or any(
            curve[i][0] < curve[i - 1][0] or curve[i][1] > curve[i - 1][1]
            for i in range(1, len(curve))
        ):
            errors.append(f"Curva de convergencia incoherente: {name}")

        if row["exito"]:
            tour_name = row.get("tour")
            if not tour_name or not (ROOT / tour_name).is_file():
                errors.append(f"Falta TOUR: {name}")
            elif load_tour(ROOT / tour_name) != route:
                errors.append(f"TOUR distinto de la ruta registrada: {name}")
            else:
                checked_tours.add(tour_name)

        path = graph_path(row["grafo"])
        if path is None:
            missing_graphs.add(row["grafo"])
            continue
        if path not in graph_cache:
            graph_cache[path] = load_hcp(path)
        graph_n, adjacency = graph_cache[path]
        edges = sum(len(neighbors) for neighbors in adjacency) // 2
        if (graph_n, edges) != (n, row["m"]):
            errors.append(f"Tamaño o aristas del grafo incongruentes: {name}")
        if cost(route, adjacency) != row["costo"]:
            errors.append(f"Costo recalculado distinto: {name}")
        checked_costs += 1

    official = 0
    for path in sorted((ROOT / "datos/fhcp").glob("*.hcp")):
        tour = Path(str(path) + ".tou")
        if tour.is_file():
            n, adjacency = graph_cache.get(path) or load_hcp(path)
            route = load_tour(tour)
            if len(route) != n or set(route) != set(range(1, n + 1)) or cost(route, adjacency):
                errors.append(f"Solución oficial inválida: {tour}")
            official += 1

    print(f"Costos recalculados: {checked_costs}/{len(records)}; "
          f"TOUR cotejados: {len(checked_tours)}; soluciones oficiales: {official}")
    print(f"Mayor exceso sobre el tiempo nominal: {max_time_excess:.4f} s")
    if missing_graphs:
        print(f"Faltan {len(missing_graphs)} grafos para verificar todas las rutas; "
              "ejecuta bash datos/descargar_fhcp.sh")
        if not args.allow_missing:
            errors.append("No se pudieron comprobar todas las rutas contra sus grafos")
    if errors:
        for error in errors[:20]:
            print("ERROR:", error)
        if len(errors) > 20:
            print(f"... y {len(errors) - 20} errores más")
        return 1
    print("Verificación correcta.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
