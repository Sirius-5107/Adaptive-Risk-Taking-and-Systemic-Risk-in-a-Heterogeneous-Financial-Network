# Implementation Plan

## Modules
- `network.py`: groups, directed network, exposures, obligations
- `agents.py`: institution state, group, strategy, risk exposure, payoff
- `shocks.py`: risky outcomes and seeded shocks
- `financial_system.py`: assemble system state
- `clearing.py`: incoming payments, fixed-point solver, convergence, defaults
- `metrics.py`: default fraction, systemic event, group losses, Monte Carlo estimates and intervals
- `simulation.py`: one full simulation
- `dynamics.py`: strategy payoffs, shares, adaptive updates
- `ml.py`: optional statistical-learning stage

## Build order
1. Deterministic toy network
2. Clearing unit tests
3. Random heterogeneous network
4. One stochastic simulation
5. Monte Carlo
6. Parameter sweeps
7. Adaptive dynamics
8. Optional ML

## Reproducibility
Every experiment should record:
- parameter configuration
- random seed
- Git commit
- summary results
- software/package versions where practical

Use a NumPy Generator rather than global random state.

## Coding standards
Small functions, explicit arrays, type hints, docstrings, no hidden global state, no magic numbers, and no notebook-only logic.


## Optimization experiments

The optimization layer is deliberately separated from the simulator.

- E5 generates Monte Carlo sweep points using common random numbers.
- Risk-intensity optimization post-processes E5 to choose the best tested q_R for each systemic-loss penalty.
- Risk-composition optimization runs a new Monte Carlo sweep over the fraction x of high-risk institutions and then post-processes it with the same objective form.
- The objective is always explicit:
  J = private/aggregate terminal equity - lambda_systemic × unpaid interbank obligations.
- Optimization results are discrete-grid optima unless an interpolation or continuous optimization method is explicitly added later.
- The code records continuous distress measures because binary systemic failure can remain zero while partial-payment losses increase.
