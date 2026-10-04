# Adaptive Risk-Taking and Systemic Risk in a Heterogeneous Financial Network

Research-style computational project inspired by work on systemic risk, heterogeneous financial networks, clearing, contagion, and adaptive risk-taking.

## Research question

How does the fraction and intensity of risk-taking affect private returns and systemic losses in an interconnected financial network, and how does the system-aware optimum change when institutions internalize systemic damage?

This is **not a reproduction of any published theorem**. It is an undergraduate-scale computational investigation designed to make the mathematical mechanisms explicit and reproducible.

## Core pipeline

Random financial network → external shock → payment clearing → contagion → systemic-risk measurement → risk-taking optimization → adaptive strategy dynamics.

## Project stages

1. Deterministic clearing tests
2. Random heterogeneous network
3. One complete stochastic simulation
4. Monte Carlo systemic-risk estimation
5. Connectivity, shock, and heterogeneity experiments
6. Risk-exposure and risk-composition optimization
7. Adaptive risky/conservative dynamics
8. Robustness and sensitivity analysis
9. Optional simple ML analysis

## Main result so far

Two distinct risk decisions are now studied:

- **Risk intensity:** how much risky-asset exposure a high-risk institution takes, (q_R).
- **Risk participation:** what fraction of institutions use the high-risk strategy, (x).

For both, the project evaluates a system-aware objective

[
J = U - \lambda L,
]

where (U) is terminal equity and (L) is unpaid interbank obligations.

For risk intensity, the tested optimum moved from (q_R=0.80) at (lambda=0) to (q_R=0.50) at (lambda=0.20) and (q_R=0.35) at (lambda=0.50).

For risk participation, the tested optimum moved from (x=0.95) at (lambda=0) to (x=0.30) at (lambda=0.20) and (x=0.20) at (lambda=0.50).

These are **best tested grid points**, not continuous analytical optima.

The key research interpretation is that private incentives can favour substantially more risk-taking than a system-aware objective once network losses are internalized.

## Research principles

- Validate the simulator before large experiments.
- Record parameters, seeds, and code version.
- Always compare against baselines.
- Quantify Monte Carlo uncertainty.
- Separate model uncertainty from simulation uncertainty.
- Do not cherry-pick parameters or results.
- Treat negative results as results.
- Clearly distinguish published theory from our simplifications.

See `docs/` for the full model, implementation plan, experiments, validation, limitations, and presentation plan.
