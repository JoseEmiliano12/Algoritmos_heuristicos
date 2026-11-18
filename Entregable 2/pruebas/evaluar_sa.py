"""Prueba didáctica reproducible sobre diez grafos plantados de 30 vértices.

Ejecutar desde la raíz: python -m pruebas.evaluar_sa
No descarga ni utiliza el FHCP y no cambia los parámetros entre semillas.
"""

from pruebas.grafos_prueba import grafo_con_ciclo
from pruebas.probar_algoritmo import verificar_resultado
from src.algoritmos.sa import resolver


def main():
    for vecino in ('swap', 'mixto'):
        exitos = 0
        for semilla in range(10):
            # Usar la misma semilla en ambos shuffles puede revelar por accidente
            # el ciclo plantado como ruta inicial. Son dos semillas distintas.
            adj, _ = grafo_con_ciclo(30, 15, 1000 + semilla)
            resultado = resolver(adj, 200_000, semilla, tiempo_max=60, vecino=vecino)
            verificar_resultado(resultado, adj, 200_000)
            exitos += resultado['costo'] == 0
            print(f"{vecino}: semilla={semilla}, costo={resultado['costo']}, "
                  f"evals={resultado['evals']}")
        print(f"{vecino}: {exitos}/10 ciclos verificados")


if __name__ == '__main__':
    main()
