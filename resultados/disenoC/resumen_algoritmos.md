| Algoritmo | Éxitos | Tasa (IC 95 %) | Instancias resueltas | Tiempo medio ± DE (s) | Evals mediana (éxitos) | Costo final medio | F1 |
|---|---|---|---|---|---|---|---|
| `ga` | 0/4 | 0.00 [0.00, 0.49] | 0/4 | 120.0 ± 0.0 | — | 3126.25 | 0.00 |
| `sa_swap` | 0/4 | 0.00 [0.00, 0.49] | 0/4 | 78.97 ± 25.41 | — | 1784 | 0.00 |
| `sa` | 0/4 | 0.00 [0.00, 0.49] | 0/4 | 82.25 ± 29.61 | — | 2437.25 | 0.00 |
| `aco` | 0/4 | 0.00 [0.00, 0.49] | 0/4 | 120.01 ± 0.01 | — | 3007.75 | 0.00 |
| `aco_posa` | 0/4 | 0.00 [0.00, 0.49] | 0/4 | 120.02 ± 0.01 | — | 2259.75 | 0.00 |
| `abc` | 0/4 | 0.00 [0.00, 0.49] | 0/4 | 120.0 ± 0.0 | — | 29.75 | 0.00 |
| `de` | 0/4 | 0.00 [0.00, 0.49] | 0/4 | 120.0 ± 0.0 | — | 3456 | 0.00 |
| `pso` | 0/4 | 0.00 [0.00, 0.49] | 0/4 | 120.01 ± 0.01 | — | 3479.5 | 0.00 |

Precisión = 1 siempre que hay detecciones (todas las instancias del FHCP tienen ciclo), así que F1 depende solo del recall (= tasa de éxito). Sin ciclo al agotar el presupuesto = inconcluso, no «no hamiltoniano».
