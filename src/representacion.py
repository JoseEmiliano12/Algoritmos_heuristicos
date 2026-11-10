"""Decodificación por *random keys* para los algoritmos continuos (DE y PSO).

Cada individuo es un vector real ``x`` de n claves en [0, 1]; la clave ``x[v]`` es la
"prioridad" del vértice v. Ordenar los vértices por su clave produce **siempre** una
permutación válida de 0..n-1: ningún vector real puede generar repetidos ni omitir vértices.
Los empates se rompen por el identificador del vértice, así la decodificación es
determinista (misma entrada, misma ruta).
"""


def claves_a_permutacion(claves):
    """``argsort`` estable: vértices ordenados por (clave, identificador)."""
    return sorted(range(len(claves)), key=lambda v: (claves[v], v))


def permutacion_a_claves(ruta):
    """Inversa aproximada: claves equiespaciadas que decodifican exactamente a ``ruta``."""
    n = len(ruta)
    claves = [0.0] * n
    for posicion, v in enumerate(ruta):
        claves[v] = (posicion + 0.5) / n
    return claves


def recortar(valor, minimo, maximo):
    return minimo if valor < minimo else maximo if valor > maximo else valor
