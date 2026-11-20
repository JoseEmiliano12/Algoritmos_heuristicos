"""Verificación independiente de las campañas ampliadas del FHCP.

Ejecutar desde la raíz: python3 pruebas/verificar_challenge.py
"""
import json
from pathlib import Path
from verificar_resultados import cost, load_hcp, load_tour

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'datos/fhcp_completo'
RESULTS = ROOT / 'resultados'


def rows(path):
    with path.open(encoding='utf-8') as f:
        for number, line in enumerate(f, 1):
            if line.strip():
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f'{path.name}:{number}: JSON inválido') from exc


def verify():
    errors = []
    cache = {}

    def graph(number):
        if number not in cache:
            cache[number] = load_hcp(DATA / f'graph{number}.hcp')
        return cache[number]

    old = list(rows(RESULTS / 'challenge.jsonl'))
    seen = set()
    solved = set()
    verified_tours = 0
    for r in old:
        num = r['num']
        key = num, r['pasada']
        if key in seen:
            errors.append(f'Intento LNS duplicado: {key}')
        seen.add(key)
        if not r['exito']:
            continue  # Estas corridas no guardan la ruta candidata.
        solved.add(num)
        n, adjacency = graph(num)
        tour = ROOT / r['tour'] if r.get('tour') else None
        if not tour or not tour.is_file():
            errors.append(f'TOUR ausente: graph{num}')
            continue
        route = load_tour(tour)
        if (len(route) != n or set(route) != set(range(1, n + 1))
                or cost(route, adjacency) != 0 or r['costo'] != 0):
            errors.append(f'TOUR inválido: graph{num}')
        else:
            verified_tours += 1

    new = list(rows(RESULTS / 'challenge_1001_45.jsonl'))
    triples = set()
    successes = 0
    solved_45 = set()
    for r in new:
        num = int(r['grafo'].removeprefix('graph').removesuffix('.hcp'))
        key = num, r['algoritmo'], r['semilla']
        if key in triples:
            errors.append(f'Corrida de 45 semillas duplicada: {key}')
        triples.add(key)
        n, adjacency = graph(num)
        route = r['ruta']  # Los registros de experimentos usan vértices 1..n.
        if len(route) != n or set(route) != set(range(1, n + 1)):
            errors.append(f'Ruta incompleta: {key}')
            continue
        actual = cost(route, adjacency)
        if actual != r['costo'] or (actual == 0) != bool(r['exito']):
            errors.append(f'Costo/éxito incongruente: {key}')
        if r['exito']:
            successes += 1
            solved_45.add(num)
            tour = ROOT / r['tour'] if r.get('tour') else None
            if not tour or not tour.is_file() or load_tour(tour) != route:
                errors.append(f'TOUR ausente o distinto: {key}')

    print(f'LNS: {len(old)} intentos; {len(solved)} grafos distintos; {verified_tours} TOUR válidos.')
    print(f'Campaña 45 semillas: {len(new)} corridas; {successes} éxitos; '
          f'{len(solved_45)} grafos distintos; {len(new)} costos recalculados.')
    if errors:
        print(f'ERRORES ({len(errors)}):')
        for error in errors[:20]:
            print(' -', error)
        return 1
    print('Verificación correcta.')
    return 0


if __name__ == '__main__':
    raise SystemExit(verify())
