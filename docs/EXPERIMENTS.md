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

## E3 — Shock severity
Vary R_L while keeping the network and other parameters controlled.

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
