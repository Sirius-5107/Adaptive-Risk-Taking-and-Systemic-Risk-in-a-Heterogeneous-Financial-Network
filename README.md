# Adaptive Risk-Taking and Systemic Risk in a Heterogeneous Financial Network

Research-style computational project inspired by systemic risk, heterogeneous financial networks, clearing, contagion, and adaptive risk-taking.

## Research question
How does the fraction and intensity of risk-taking affect private returns and systemic losses in an interconnected financial network, and how does the system-aware optimum change when institutions internalize systemic damage?

This is **not a reproduction of any published theorem**. It is an undergraduate-scale computational investigation designed to make the mathematical mechanisms explicit and reproducible.

## Core pipeline
Random financial network → external shock → payment clearing → contagion → systemic-risk measurement → risk-taking optimization → adaptive strategy dynamics.

## Frozen project scope
1. Deterministic clearing tests
2. Random heterogeneous network
3. Stochastic simulation
4. Monte Carlo systemic-risk estimation
5. Connectivity, shock, and heterogeneity experiments
6. Risk-intensity and risk-participation optimization
7. Adaptive strategy dynamics

The model is now frozen for the current research presentation. Broader robustness (E9) and optional ML (E10) are deferred and are not presented as completed results.

## Main result
Two distinct risk decisions are studied:

- **Risk intensity:** how much risky-asset exposure a high-risk institution takes, q_R.
- **Risk participation:** what fraction of institutions use the high-risk strategy, x.

For both, the project evaluates

J = U - λL

where U is the relevant terminal-equity payoff and L is mean unpaid interbank obligations.

### Risk intensity
Best tested q_R:
- λ=0.00 → 0.80
- λ=0.05 → 0.80
- λ=0.10 → 0.80
- λ=0.20 → 0.50
- λ=0.50 → 0.35

### Risk participation
Best tested x:
- λ=0.00 → 0.95
- λ=0.05 → 0.55
- λ=0.10 → 0.40
- λ=0.20 → 0.30
- λ=0.50 → 0.20

These are **best tested grid points**, not continuous analytical optima, equilibrium proofs, or universal policy recommendations.

The key interpretation is that private incentives can favour substantially more risk-taking than a system-aware objective once network losses are internalized.

## Important negative result
Binary systemic failure remained at 0% across the main risk-intensity sweep. This does **not** mean risk-taking has no systemic effect.

Continuous measures showed increasing payment shortfall, distressed-bank fraction, and unpaid interbank obligations. These measures therefore carry the main systemic-distress signal in the current experiments.

## Reproducibility
Primary optimization sweeps:
- seed: 20261001
- E5 trials per grid point: 2000
- E7 trials per grid point: 2000
- q_L: 0.20
- q_R for E7: 0.80
- systemic threshold: 0.30
- confidence level: 0.95

See docs/FINAL_STATUS.md for the presentation checkpoint and docs/ for model, experiments, implementation, validation, and limitations.

## Research principles
- Validate the simulator before large experiments.
- Record parameters, seeds, and code version.
- Compare against baselines.
- Quantify Monte Carlo uncertainty.
- Separate simulation uncertainty from model uncertainty.
- Do not cherry-pick parameters or results.
- Treat negative results as results.
- Clearly distinguish published theory from project simplifications.