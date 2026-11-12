| Algoritmo | Éxitos | Tasa (IC 95 %) | Instancias resueltas | Tiempo medio ± DE (s) | Evals mediana (éxitos) | Costo final medio | F1 |
|---|---|---|---|---|---|---|---|
| `ga` | 0/210 | 0.00 [0.00, 0.02] | 0/21 | 60.0 ± 0.0 | — | 11.75 | 0.00 |
| `sa_swap` | 0/210 | 0.00 [0.00, 0.02] | 0/21 | 41.63 ± 8.95 | — | 20.89 | 0.00 |
| `sa` | 17/210 | 0.08 [0.05, 0.13] | 5/21 | 34.51 ± 9.26 | 2722431 | 0.97 | 0.15 |
| `aco` | 0/210 | 0.00 [0.00, 0.02] | 0/21 | 60.0 ± 0.0 | — | 9.28 | 0.00 |
| `aco_posa` | 59/210 | 0.28 [0.23, 0.34] | 7/21 | 45.27 ± 24.39 | 1993 | 0.73 | 0.44 |
| `abc` | 62/210 | 0.29 [0.24, 0.36] | 7/21 | 44.1 ± 23.46 | 282443 | 0.7 | 0.46 |
| `de` | 0/210 | 0.00 [0.00, 0.02] | 0/21 | 60.0 ± 0.0 | — | 79.37 | 0.00 |
| `pso` | 0/210 | 0.00 [0.00, 0.02] | 0/21 | 60.0 ± 0.0 | — | 119.3 | 0.00 |

Precisión = 1 siempre que hay detecciones (todas las instancias del FHCP tienen ciclo), así que F1 depende solo del recall (= tasa de éxito). Sin ciclo al agotar el presupuesto = inconcluso, no «no hamiltoniano».
