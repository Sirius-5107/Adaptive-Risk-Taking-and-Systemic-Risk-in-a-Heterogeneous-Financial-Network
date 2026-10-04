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
- run_risk_taking_sweep() varies q_R over 0.20, 0.25, ..., 0.80 for the current optimization study.
- Each value uses the same trial seed sequence, so the network realization and shock uniforms are comparable across exposure levels.
- Private payoff is mean terminal equity after clearing, computed separately for low-risk and high-risk groups.
- Also record payment shortfall, distressed-bank fraction, unpaid interbank obligations, group-specific default rates, and systemic-failure probability with its Monte Carlo confidence interval.
- q_L remains fixed at 0.20.
- The current study uses 2,000 trials per grid point.

Observed result:
- mean high-risk terminal equity increased from about 0.5039 at q_R=0.20 to 0.5163 at q_R=0.80.
- mean unpaid interbank obligations increased from about 0.0257 to 0.0842.
- distressed-bank fraction increased from about 0.41% to 0.94%.
- binary systemic failure remained 0% across the tested grid.

The binary failure metric was therefore too coarse to be the sole optimization loss.

## E6 — System-aware risk-intensity optimization

Use the E5 sweep to evaluate:

J(q_R) = U_R(q_R) - lambda_systemic * L(q_R)

where U_R is mean terminal equity of high-risk institutions and L is mean unpaid interbank obligations.

Because this is post-processing of the same Monte Carlo sweep, optimization adds no simulation noise.

Current best tested q_R values:
- lambda=0.00 -> q_R=0.80
- lambda=0.05 -> q_R=0.80
- lambda=0.10 -> q_R=0.80
- lambda=0.20 -> q_R=0.50
- lambda=0.50 -> q_R=0.35

Interpretation:
- when systemic losses are ignored, the tested private optimum is at the highest exposure in the grid;
- increasing the systemic penalty shifts the best tested exposure downward.

These are grid optima, not continuous analytical optima.

## E7 — Risk-taking population composition

The second decision is the fraction x of institutions using the high-risk strategy, while q_L and q_R are fixed.

Implementation:
- run_risk_fraction_sweep() varies x over 0.05, 0.10, ..., 0.95.
- q_L=0.20 and q_R=0.80 in the current study.
- Each x uses the same trial seed sequence.
- The sweep records mean terminal equity across all institutions, payment shortfall, distressed-bank fraction, unpaid interbank obligations, and systemic-failure probability.
- The objective is:

J(x) = U(x) - lambda_systemic * L(x)

where U(x) is mean terminal equity across the whole population.

Current best tested fractions:
- lambda=0.00 -> x=0.95
- lambda=0.05 -> x=0.55
- lambda=0.10 -> x=0.40
- lambda=0.20 -> x=0.30
- lambda=0.50 -> x=0.20

The result shows a strong separation between private/aggregate payoff maximization and system-aware composition. As the penalty on unpaid interbank obligations increases, the best tested share of high-risk institutions falls sharply.

These are again discrete-grid optima. They should not be described as exact continuous equilibria.

## E8 — Adaptive dynamics

Let the population fraction using the higher-risk strategy be x_t. Update it from the difference between the two groups' average terminal equity.

Implementation:
- run_adaptive_dynamics() starts from an interior composition x_0 and runs a fixed number of adaptation steps.
- At each step, the simulator is run at the current composition, using fraction_low_risk = 1 - x_t.
- Each step uses multiple independent replications and averages terminal equity before updating.
- The update is:
  x_(t+1) = clip[x_t + eta*x_t*(1-x_t)*(U_R-U_L), 0, 1]
- U_R and U_L are the mean terminal-equity payoffs already defined for E5.
- The experiment records x_t, both payoffs, their difference, and the systemic-failure rate observed at each step.

Current illustrative run:
- x_0 = 0.50
- q_L = 0.20
- q_R = 0.80
- eta = 0.10
- 20 steps
- 100 replications per step
- final x = 0.5064

The risky strategy had a positive payoff advantage at every observed step, but the update was small. This should not be interpreted as convergence to 80% or as a behavioural calibration. It demonstrates that the current payoff differences imply only slow composition change under the chosen update scale.

An important conceptual distinction is:
- q_R = risk intensity conditional on being a risky institution;
- x = fraction of institutions choosing the risky strategy.

The composition sweep and adaptive dynamics therefore answer related but different questions.

## E9 — Robustness
Repeat with:
- multiple seeds
- different N
- different systemic thresholds
- different shock severity
- different exposure scales

## E10 — Optional ML
Train logistic regression/random forest on simulated environments only after the simulator is validated. Prefer held-out parameter regimes over a purely random row split so the model is tested on genuinely different environments.
