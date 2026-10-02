# Adaptive Risk-Taking and Systemic Risk in a Heterogeneous Financial Network

Research-style computational project inspired by work on systemic risk, heterogeneous financial networks, clearing, contagion, and adaptive risk-taking.

## Research question
How can adaptive choices between risky and conservative financial strategies change the probability of systemic failure in an interconnected financial network?

This is **not a reproduction of any published theorem**. It is an undergraduate-scale computational investigation designed to make the mathematical mechanisms explicit and reproducible.

## Core pipeline
Random financial network → external shock → payment clearing → contagion → systemic-risk measurement → strategy adaptation.

## Project stages
1. Deterministic clearing tests
2. Random heterogeneous network
3. One complete stochastic simulation
4. Monte Carlo systemic-risk estimation
5. Connectivity, shock, and heterogeneity experiments
6. Adaptive risky/conservative dynamics
7. Robustness and sensitivity analysis
8. Optional simple ML analysis

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
