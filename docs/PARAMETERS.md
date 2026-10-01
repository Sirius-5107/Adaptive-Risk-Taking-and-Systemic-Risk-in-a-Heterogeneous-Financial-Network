# Parameters

## Baseline configuration

| Parameter | Baseline |
|---|---:|
| N | 100 |
| Fraction L | 0.50 |
| p_w | 0.10 |
| p_c | 0.05 |
| q_L | 0.20 |
| q_R | 0.60 |
| R_H | 1.10 |
| R_L | 0.70 |
| π | 0.20 |
| A_0 | 1.00 |
| X_0 | 0.50 |
| exposure scale e_0 | 0.05 |
| systemic threshold τ | 0.30 |
| clearing tolerance ε | 1e-10 |
| payment tolerance δ | 1e-8 |
| max clearing iterations | 1000 |
| Monte Carlo runs M | 2000 |
| seed | 20261001 |
| adaptation rate η | 0.10 |

Use N=20 while debugging.

## Suggested sweeps
- p_c: 0 to 0.20 by 0.02
- R_L: 0.90, 0.80, 0.70, 0.60, 0.50
- q_R: 0.40, 0.50, 0.60, 0.70, 0.80
- x_0: 0.10, 0.30, 0.50, 0.70, 0.90
- η: 0.01, 0.05, 0.10, 0.20

## Parameter policy
Never change parameters merely because a graph looks better. If a parameter is selected after seeing results, label the analysis as sensitivity analysis and preserve the original baseline.
