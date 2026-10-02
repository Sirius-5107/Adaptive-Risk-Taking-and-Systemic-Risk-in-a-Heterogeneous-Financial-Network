# Experiments

## E0 — Deterministic clearing
Build hand-checkable cases:
1. No shock
2. One isolated default
3. A→B contagion
4. A→B→C→D cascade
5. Disconnected components

Expected behaviour must be calculated by hand before coding.

## E1 — Baseline Monte Carlo
Measure:
- mean default fraction
- systemic-failure probability
- group-specific default rates
- Monte Carlo uncertainty

## E2 — Cross-group connectivity
Sweep p_c and measure systemic-risk probability and group losses.

Implementation:
- src/experiments.py provides a reproducible parameter-sweep helper.
- Baseline grid: p_cross = 0.00, 0.02, ..., 0.20.
- p_within, balance-sheet parameters, shock parameters, systemic threshold, and trial count are held fixed.
- Each p_cross value uses the same trial seed sequence. This common-random-number design reduces noise when comparing parameter values.
- The sweep changes both cross-group connectivity and expected overall network density. It therefore does not isolate network placement at fixed density; that is the purpose of E4.

Interpretation rule:
- Do not treat a monotonic pattern as evidence of a theorem.
- Report Monte Carlo confidence intervals and inspect whether differences are large relative to simulation uncertainty.
- Preserve the baseline parameter choice independently of observed results.

## E3 — Shock severity
Vary R_L while keeping the network and other parameters controlled.

## E3 — Shock severity
Vary low_return (R_L) while keeping the network, risky exposure fractions, high-state return, shock probability, balance sheets, and clearing settings fixed.

Baseline grid:
- R_L = 0.90, 0.80, 0.70, 0.60, 0.50
- The existing baseline is R_L = 0.70.

Interpretation:
- Lower R_L means a more severe adverse risky-asset state.
- Because the same trial seed sequence is reused across all values, the realized bad/good shock pattern is held comparable.
- Report systemic-failure probability and Monte Carlo confidence intervals.
- This is a shock-severity experiment, not a calibration exercise; the grid is chosen before inspecting results.
- A result that looks monotonic is still an empirical property of this simulator, not a general theorem.

## E4 — Heterogeneous network structure
Hold average density approximately fixed while varying p_LL, p_RR, p_LR, p_RL. This tests whether placement of connections matters beyond density.

## E5 — Risk-taking
Vary q_R/q_L. Record:
- private payoff
- default probability
- systemic-risk probability
- trade-off between individual and system outcomes

## E6 — Adaptive dynamics
Vary x_0 and η. Track x_t and systemic outcomes.

## E7 — Robustness
Repeat with:
- multiple seeds
- different N
- different systemic thresholds
- different shock severity
- different exposure scales

## E8 — Optional ML
Train logistic regression/random forest on simulated environments only after the simulator is validated. Prefer held-out parameter regimes over a purely random row split so the model is tested on genuinely different environments.
