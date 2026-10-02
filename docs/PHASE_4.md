# Phase 4 — Monte Carlo Systemic-Risk Estimation

## Goal

Repeat the complete Phase 3 simulation many times and estimate the probability that the system crosses a predefined systemic-failure threshold.

For trial m:

    Y_m = 1 if default_fraction >= tau
          0 otherwise

Then:

    SR_hat = (Y_1 + ... + Y_M) / M

and:

    SE = sqrt(SR_hat * (1 - SR_hat) / M)

The implementation reports a normal-approximation confidence interval.

## Baseline

- trials: 2,000
- systemic-failure threshold: 30% of institutions
- confidence level: 95%
- seed: 20261001
- all other parameters: Phase 3 baseline

The threshold is an explicit experimental choice, not an empirical fact about real financial systems.

## Why Monte Carlo?

One simulated network and one shock tell us what happened in one possible world.

Monte Carlo asks:

> Across many independently generated possible networks and shock realizations, how often does systemic failure occur?

That turns the simulator into a statistical experiment.

## Reproducibility

Trial m uses seed = base seed + m.

This makes the complete experiment deterministic while giving each trial a distinct seed.

## Important uncertainty distinction

The confidence interval quantifies **Monte Carlo sampling uncertainty** conditional on the model.

It does not quantify uncertainty about whether the model itself is a good representation of real financial systems.

## Validation

Tests cover:

- systemic threshold logic;
- probability and standard-error calculation;
- invalid counts;
- reproducibility;
- bounded probability and confidence interval.

## Next phase

The next experiment will vary one structural parameter at a time, beginning with cross-group connectivity p_cross, and measure how estimated systemic-failure probability changes.
