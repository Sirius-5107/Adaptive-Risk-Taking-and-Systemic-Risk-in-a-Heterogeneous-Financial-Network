# Final Research Status

## Scope frozen
The computational model is frozen for the current research presentation. The project contains:
1. heterogeneous directed financial network generation;
2. external risky-asset shocks;
3. fixed-point interbank payment clearing;
4. default and systemic-failure measurement;
5. continuous network-distress metrics;
6. risk-intensity sweep and system-aware optimization;
7. risk-participation sweep and system-aware optimization;
8. population-level adaptive dynamics.

No additional mechanism is required for the presentation.

## Main research question
How does the fraction and intensity of risk-taking affect private returns and systemic losses in an interconnected financial network, and how does the system-aware optimum change when institutions internalize systemic damage?

## Main empirical result
More risk-taking increases private/aggregate terminal equity in the tested model, but network losses increase much faster once risk becomes sufficiently widespread or intense.

Using J = U - λL, with U as the relevant terminal-equity payoff and L as mean unpaid interbank obligations, increasing the systemic-loss penalty shifts the best tested choice toward less risk.

### Risk intensity
| λ | Best tested q_R |
|---:|---:|
| 0.00 | 0.80 |
| 0.05 | 0.80 |
| 0.10 | 0.80 |
| 0.20 | 0.50 |
| 0.50 | 0.35 |

### Risk participation
| λ | Best tested x |
|---:|---:|
| 0.00 | 0.95 |
| 0.05 | 0.55 |
| 0.10 | 0.40 |
| 0.20 | 0.30 |
| 0.50 | 0.20 |

These are discrete-grid optima under the stated model and parameters. They are not universal policy recommendations, continuous optima, or equilibrium proofs.

## Important negative result
The binary systemic-failure event remained at 0% throughout the main E5 risk-intensity sweep. This does not mean risk-taking has no systemic effect.

Continuous measures showed increasing payment shortfall, distressed-bank fraction, and unpaid interbank obligations. The final analysis therefore does not rely on a single binary failure indicator.

## Reproducibility
- seed: 20261001
- E5 trials per grid point: 2000
- E7 trials per grid point: 2000
- q_L: 0.20
- q_R for E7: 0.80
- systemic threshold: 0.30
- confidence level: 0.95

The exact implementation and experiment definitions are in src/experiments.py and docs/.

## Known limitations
The model uses simulated networks, simplified balance sheets, a two-state risky return, simplified behaviour, finite network size, and an experiment-specific systemic-loss objective.

Monte Carlo confidence intervals quantify simulation uncertainty conditional on this model; they do not establish that the model describes real financial systems.

## Deferred work
E9 robustness and E10 ML are deliberately deferred. They should not be presented as completed results.

## Presentation status
**Ready for presentation preparation.**

The next stage should focus on explaining the model, showing the key trade-off, presenting the optimization result, and defending assumptions and limitations rather than adding new mechanisms.