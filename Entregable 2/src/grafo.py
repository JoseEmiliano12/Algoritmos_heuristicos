"""Lectura de grafos del FHCP Challenge Set y escritura de soluciones en formato TOUR.

Formato de entrada (TSPLIB/HCP, el que usan los 1001 archivos del FHCP)::

    NAME : graph1.hcp
    TYPE : HCP
    DIMENSION : 66
    EDGE_DATA_FORMAT : EDGE_LIST
    EDGE_DATA_SECTION
    1 3
    ...
    -1
    EOF

Los archivos numeran los vértices 1..n; internamente se usan 0..n-1 (``adj: list[set[int]]``).
Al escribir un TOUR se vuelve a sumar 1.

Probar: ``python -m src.grafo datos/fhcp/graph1.hcp`` desde la raíz del repositorio.
"""
import os


def leer_hcp(ruta_archivo):
    """Lee un archivo .hcp y devuelve ``(nombre, n, adj)`` con vértices 0..n-1.

    Ignora lazos y aristas repetidas (avisa con ``ValueError`` si un vértice está fuera de
    1..n). El grafo resultante es simple y no dirigido.
    """
    nombre, n = os.path.basename(ruta_archivo), None
    with open(ruta_archivo, encoding="utf-8") as archivo:
        lineas = iter(archivo.read().splitlines())
    for linea in lineas:
        linea = linea.strip()
        if not linea:
            continue
        if linea.startswith("EDGE_DATA_SECTION"):
            break
        clave, _, valor = linea.partition(":")
        clave, valor = clave.strip().upper(), valor.strip()
        if clave == "NAME":
            nombre = valor
        elif clave == "DIMENSION":
            n = int(valor)
        elif clave == "EDGE_DATA_FORMAT" and valor.upper() != "EDGE_LIST":
            raise ValueError(f"Formato de aristas no soportado: {valor}")
    if n is None or n < 1:
        raise ValueError(f"{ruta_archivo}: falta DIMENSION")

    adj = [set() for _ in range(n)]
    numeros = []
    for linea in lineas:
        linea = linea.strip()
        if linea == "EOF":
            break
        numeros.extend(int(t) for t in linea.split())
        if numeros and numeros[-1] == -1:
            numeros.pop()
            break
    if len(numeros) % 2:
        raise ValueError(f"{ruta_archivo}: EDGE_DATA_SECTION con un número impar de valores")
    for k in range(0, len(numeros), 2):
        u, v = numeros[k] - 1, numeros[k + 1] - 1
        if not (0 <= u < n and 0 <= v < n):
            raise ValueError(f"{ruta_archivo}: arista ({u + 1}, {v + 1}) fuera de 1..{n}")
        if u != v:
            adj[u].add(v)
            adj[v].add(u)
    return nombre, n, adj


def leer_tour(ruta_archivo):
    """Lee un archivo TOUR (p. ej. las soluciones oficiales ``graphX.hcp.tou``) como lista 0..n-1."""
    ruta, dentro = [], False
    with open(ruta_archivo, encoding="utf-8") as archivo:
        for linea in archivo:
            linea = linea.strip()
            if linea.startswith("TOUR_SECTION"):
                dentro = True
                continue
            if not dentro or not linea:
                continue
            if linea in ("-1", "EOF"):
                break
            ruta.extend(int(t) - 1 for t in linea.split())
    return ruta


def escribir_tour(ruta, ruta_archivo, nombre):
    """Escribe ``ruta`` (vértices 0..n-1) en formato TOUR con vértices 1..n."""
    carpeta = os.path.dirname(ruta_archivo)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)
    with open(ruta_archivo, "w", encoding="utf-8") as archivo:
        archivo.write(f"NAME : {nombre}\nTYPE : TOUR\nDIMENSION : {len(ruta)}\nTOUR_SECTION\n")
        archivo.writelines(f"{v + 1}\n" for v in ruta)
        archivo.write("-1\nEOF\n")


def num_aristas(adj):
    return sum(len(vecinos) for vecinos in adj) // 2


if __name__ == "__main__":
    import sys

    from src.fitness import es_ciclo_hamiltoniano

    for ruta_hcp in sys.argv[1:]:
        nombre, n, adj = leer_hcp(ruta_hcp)
        grados = [len(a) for a in adj]
        print(f"{nombre}: n={n} m={num_aristas(adj)} grado min={min(grados)} max={max(grados)}")
        if os.path.exists(ruta_hcp + ".tou"):
            oficial = leer_tour(ruta_hcp + ".tou")
            print("  solución oficial válida:", es_ciclo_hamiltoniano(oficial, adj))
