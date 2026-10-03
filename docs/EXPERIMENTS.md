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
Hold expected directed network density fixed while varying how links are placed within versus across the two risk groups. This tests whether network structure matters beyond overall connectivity.

Implementation:
- run_matched_density_network_sweep() varies p_cross and solves for p_within so expected density equals the baseline configuration (p_within=0.10, p_cross=0.05).
- Default p_cross grid: 0.000, 0.025, 0.050, 0.075, 0.100, 0.125.
- For the 50/50 baseline, p_within values are approximately 0.151, 0.126, 0.100, 0.075, 0.049, 0.024.
- The same Monte Carlo trial seed sequence is reused across configurations.
- Matching is on expected density, not realized edge count. Individual random networks can still contain different numbers of edges; exact edge-count matching would require a different network-construction design.

Interpretation:
- E4 isolates link placement more cleanly than E2 because expected density is controlled.
- Report Monte Carlo confidence intervals.
- No monotonic relationship is assumed in advance.
- The baseline parameter choice remains fixed independently of observed results.

## E5 — Risk-taking
Vary q_R while holding q_L and the rest of the baseline model fixed.

Implementation:
- run_risk_taking_sweep() varies q_R over 0.40, 0.50, 0.60, 0.70, 0.80.
- Each value uses the same trial seed sequence, so the network realization and shock uniforms are comparable across exposure levels.
- Private payoff is mean terminal equity after clearing, computed separately for low-risk and high-risk groups.
- Also record group-specific default rates and systemic-failure probability with its Monte Carlo confidence interval.
- q_L remains fixed at 0.20.

Interpretation:
- This experiment asks whether greater risky-asset exposure changes private outcomes and system-level outcomes differently.
- A higher high-risk-group payoff does not by itself imply that risk-taking is socially beneficial.
- A higher systemic-failure probability does not identify the cause without considering the accompanying group outcomes and model mechanics.
- Results are empirical properties of the simulator; they are not evidence that the same relationship holds in real financial systems.

## E6 — Adaptive dynamics
Let the population fraction using the higher-risk strategy be x_t. Update it from the difference between the two groups' average terminal equity.

Implementation:
- run_adaptive_dynamics() starts from an interior composition x_0 and runs a fixed number of adaptation steps.
- At each step, the simulator is run at the current composition, using fraction_low_risk = 1 - x_t.
- Each step uses multiple independent replications and averages terminal equity before updating. This reduces the chance that one random shock determines the direction of adaptation.
- The update is:
  x_(t+1) = clip[x_t + eta*x_t*(1-x_t)*(U_R-U_L), 0, 1]
- U_R and U_L are the mean terminal-equity payoffs already defined for E5.
- The same deterministic seed rule is used for reproducibility; later steps use new stochastic environments.
- The experiment records x_t, both payoffs, their difference, and the systemic-failure rate observed at each step.

Interpretation:
- A movement in x means the simulated population composition responds to the model's payoff difference; it is not evidence that real institutions adapt this way.
- Because terminal-equity differences can be small, eta is a sensitivity parameter controlling the speed of adaptation, not a calibrated behavioural constant.
- This implementation is population-level: institutions are not individually switching identities inside a single network. It is a computational mean-field analogue of a replicator-style rule.
- If x approaches 0 or 1, the factor x(1-x) naturally slows further movement.
- Do not interpret the direction of adaptation as a theorem or as evidence about real financial behaviour.

## E7 — Robustness
Repeat with:
- multiple seeds
- different N
- different systemic thresholds
- different shock severity
- different exposure scales

## E8 — Optional ML
Train logistic regression/random forest on simulated environments only after the simulator is validated. Prefer held-out parameter regimes over a purely random row split so the model is tested on genuinely different environments.
