# Experiments

## E0 — Deterministic clearing
Hand-checkable cases:
1. No shock
2. One isolated default
3. A→B contagion
4. A→B→C→D cascade
5. Disconnected components

Expected behaviour is calculated by hand before coding.

## E1 — Baseline Monte Carlo
Measure:
- mean default fraction
- systemic-failure probability
- group-specific default rates
- Monte Carlo uncertainty

## E2 — Cross-group connectivity
Sweep p_c while holding the baseline model fixed.

- Grid: p_cross = 0.00, 0.02, ..., 0.20.
- Same trial seed sequence across values.
- This changes both cross-group connectivity and expected overall density; E4 isolates placement at fixed expected density.

## E3 — Shock severity
Vary adverse risky-asset return R_L:
- 0.90, 0.80, 0.70, 0.60, 0.50
- Baseline: R_L = 0.70.
- Same trial seed sequence across values.

This is a shock-severity sensitivity experiment, not calibration.

## E4 — Heterogeneous network structure
Hold expected directed network density fixed while changing within- versus cross-group link placement.

- Baseline: p_within=0.10, p_cross=0.05.
- p_cross grid: 0.000, 0.025, 0.050, 0.075, 0.100, 0.125.
- p_within is solved to preserve expected density.
- Same trial seed sequence across configurations.

Matching is on expected density, not realized edge count.

## E5 — Risk-taking
Vary high-risk risky-asset exposure q_R while fixing q_L=0.20.

- Grid: 0.20, 0.25, ..., 0.80.
- 2,000 trials per point.
- Same trial seed sequence across values.
- Record private payoff, group defaults, payment shortfall, distressed-bank fraction, unpaid interbank obligations, and systemic-failure probability.

Observed:
- high-risk terminal equity: ~0.5039 → ~0.5163
- mean unpaid interbank obligations: ~0.0257 → ~0.0842
- distressed-bank fraction: ~0.41% → ~0.94%
- binary systemic failure: 0% throughout the tested grid

The binary failure metric is therefore too coarse to be the sole loss measure.

## E6 — System-aware risk-intensity optimization
Post-process E5 using

J(q_R) = U_R(q_R) - λ L(q_R)

where U_R is mean terminal equity of high-risk institutions and L is mean unpaid interbank obligations.

Best tested q_R:
- λ=0.00 → 0.80
- λ=0.05 → 0.80
- λ=0.10 → 0.80
- λ=0.20 → 0.50
- λ=0.50 → 0.35

These are discrete-grid optima, not continuous analytical optima.

## E7 — Risk-taking population composition
Vary x, the fraction of institutions using the high-risk strategy, while fixing q_L=0.20 and q_R=0.80.

- Grid: x = 0.05, 0.10, ..., 0.95.
- 2,000 trials per point.
- Same trial seed sequence across values.
- Record aggregate terminal equity and network-distress measures.

Objective:

J(x) = U(x) - λ L(x)

Best tested x:
- λ=0.00 → 0.95
- λ=0.05 → 0.55
- λ=0.10 → 0.40
- λ=0.20 → 0.30
- λ=0.50 → 0.20

The payoff-maximizing composition and system-aware composition differ sharply. These are grid optima, not exact continuous equilibria.

## E8 — Adaptive dynamics
Let x_t be the population fraction using the risky strategy.

Update:
x_(t+1) = clip[x_t + η x_t(1-x_t)(U_R-U_L), 0, 1]

Implementation:
- x_0=0.50
- q_L=0.20
- q_R=0.80
- η=0.10
- 20 steps
- 100 replications per step
- final x=0.5064 in the illustrative run

The risky strategy had a positive payoff advantage at every observed step, but the update was small. This is a population-level computational analogue, not a behavioural calibration or proof of convergence to a particular share.

## Validation status

Completed before the final optimization results:
- deterministic clearing and unit-level simulator checks
- stochastic baseline sanity checks
- reproducible Monte Carlo sweeps with common random numbers
- continuous distress metrics to avoid relying only on binary systemic failure
- explicit objective functions and discrete-grid optimum reporting
- documented model assumptions and limitations

The current primary results use seed 20261001 and 2,000 trials for E5/E7. E8 uses the separate stated replication count.

## E9 — Deferred robustness
A broader robustness study would vary seeds, N, systemic threshold, shock severity, and exposure scales. It is intentionally deferred rather than presented as completed evidence.

## E10 — Optional ML
Deferred. ML on simulated data should only be added after the core simulator and robustness study are complete, with held-out parameter regimes rather than a purely random row split.
