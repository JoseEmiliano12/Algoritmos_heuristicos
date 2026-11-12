"""Registro único de metaheurísticas.

Cada entrada asocia un nombre corto con ``(módulo, parámetros fijos)``. Todas cumplen el
contrato de ``PLAN_IMPLEMENTACION.md``::

    resolver(adj, max_evals, semilla, tiempo_max=60, **params) -> dict(ruta, costo, evals, iters, historial)

Las variantes (``sa_swap``, ``aco_posa``) se registran aparte para reportarlas por separado:
``sa_swap`` es la versión literal del enunciado (solo intercambios de índices) y
``aco_posa`` es ACO con rotaciones de Pósa (búsqueda local que no consume evaluaciones).
"""
import importlib

ALGORITMOS = {
    "ga": ("ga", {}),
    "sa": ("sa", {"vecino": "mixto"}),
    "sa_swap": ("sa", {"vecino": "swap"}),
    "aco": ("aco", {}),
    "aco_posa": ("aco", {"rotaciones": 50}),
    "abc": ("abc", {}),
    "de": ("de", {}),
    "pso": ("pso", {}),
}


def obtener(nombre):
    """Devuelve ``(resolver, params_fijos)`` del algoritmo ``nombre``."""
    if nombre not in ALGORITMOS:
        raise KeyError(f"Algoritmo desconocido: {nombre}. Opciones: {', '.join(ALGORITMOS)}")
    modulo, params = ALGORITMOS[nombre]
    return importlib.import_module(f"src.algoritmos.{modulo}").resolver, dict(params)
