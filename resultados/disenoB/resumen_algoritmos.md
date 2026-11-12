| Algoritmo | Éxitos | Tasa (IC 95 %) | Instancias resueltas | Tiempo medio ± DE (s) | Evals mediana (éxitos) | Costo final medio | F1 |
|---|---|---|---|---|---|---|---|
| `aco_posa` | 14/200 | 0.07 [0.04, 0.11] | 9/100 | 112.48 ± 28.74 | 1281 | 30.54 | 0.13 |
| `abc` | 30/200 | 0.15 [0.11, 0.21] | 19/100 | 105.66 ± 35.87 | 291682 | 2.5 | 0.26 |

Precisión = 1 siempre que hay detecciones (todas las instancias del FHCP tienen ciclo), así que F1 depende solo del recall (= tasa de éxito). Sin ciclo al agotar el presupuesto = inconcluso, no «no hamiltoniano».
