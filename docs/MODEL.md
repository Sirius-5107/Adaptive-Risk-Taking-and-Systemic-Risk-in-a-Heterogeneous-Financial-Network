# Model Specification

## 1. Institutions and network
There are N institutions. A directed edge i→j means institution i owes j an interbank amount E_ij.

Each institution has:
- external assets A_i
- external liabilities X_i
- interbank obligations B_i = Σ_j E_ij
- a strategy s_i ∈ {L,R}

L = lower-risk/conservative; R = higher-risk/risky.

## 2. Heterogeneity
Institutions are split into L and R groups. Edge probabilities may depend on group:
p_LL, p_RR, p_LR, p_RL.

Baseline:
p_LL = p_RR = p_w
p_LR = p_RL = p_c

This lets us study whether *where* connections occur matters in addition to total network density.

## 3. Risk-taking
Strategy s determines risky-asset fraction q_i. Baseline q_R > q_L.

Risky returns have two states:
- R_H with probability 1-π
- R_L with probability π

After the external shock:
A'_i = A_i[(1-q_i) + q_i R_i]

For E5, private outcome is measured by terminal equity after clearing:

W_i = A'_i + I_i - X_i - P_i

where P_i is the interbank amount actually paid. This is an experiment-specific payoff measure, not a universal definition of investor utility.

## 4. Clearing
Let r_i be institution i's payment fraction.

r_i = 1 means full payment; r_i = 0 means no payment.

Incoming interbank cash:
I_i = Σ_j r_j E_ji

Available funds:
F_i = A'_i + I_i

For B_i > 0:
r_i = min(1, max(0, (F_i - X_i)/B_i))

Because incoming payments depend on other institutions' payments, r is solved as a fixed point by iteration:
1. Start with all payments at 1.
2. Recalculate incoming payments.
3. Recalculate every payment fraction.
4. Repeat until max change < epsilon or max iterations is reached.
5. Report non-convergence rather than silently accepting it.

Default indicator:
default_i = 1[r_i < 1-delta]

## 5. Systemic failure
D = number of defaults / N.

For the baseline experiment, define a systemic event as:
D >= tau

tau = 0.30 is an **experimental threshold**, not a universal definition of systemic failure.

An important modelling result is that this binary event can be too coarse. In the baseline risk-taking sweep, systemic failure remained at 0% even though distress increased materially. Therefore the project also records continuous network-distress measures.

## 6. Distress measures
For payment fractions r_i:

Mean payment shortfall:
S = (1/N) Σ_i (1-r_i)

Distressed-bank fraction:
D_distress = number of {i : r_i < 1} / N

Total unpaid interbank obligations:
L = Σ_i,j E_ij(1-r_i)

These measures capture partial-payment losses that a binary systemic-failure indicator can miss.

## 7. Risk optimization
Two separate decisions are studied.

### 7.1 Risk intensity

q_R is the risky-asset exposure of institutions already classified as high-risk.

For a systemic penalty λ:

J(q_R) = U_R(q_R) - λ L(q_R)

where U_R is mean terminal equity of high-risk institutions and L is mean unpaid interbank obligations.

The implementation evaluates this objective on a discrete q_R grid, so the result is the **best tested exposure**, not an analytical continuous optimum.

### 7.2 Risk participation

x is the fraction of institutions using the high-risk strategy.

Holding q_L and q_R fixed, define:

J(x) = U(x) - λ L(x)

where U(x) is mean terminal equity across all institutions and L(x) is mean unpaid interbank obligations.

The composition sweep reuses the same trial seeds across x values, implementing a common-random-number comparison. The current grid is x = 0.05, 0.10, ..., 0.95.

This separates two questions that should not be conflated:

1. How risky should a risky institution be?
2. How many institutions should be risky?

## 8. Monte Carlo
Run the stochastic experiment M times.

SR_hat = systemic failures / M

Approximate Monte Carlo standard error:
SE = sqrt(SR_hat(1-SR_hat)/M)

The interval measures simulation uncertainty conditional on the model; it does not validate the model itself.

## 9. Adaptive dynamics
Let x_t be the fraction using the risky strategy.

A simple replicator-style update is:

x_(t+1) = clip[x_t + eta*x_t*(1-x_t)*(U_R-U_L), 0, 1]

where U_R and U_L are average payoffs for risky and conservative strategies.

This is a transparent computational analogue, **not a reproduction of published analytical dynamics**.

In E6, the simulator applies this rule repeatedly. At each step, x_t determines the population fraction using R, fresh stochastic environments are simulated, and U_R and U_L are estimated from average terminal equity. Multiple replications per step reduce simulation noise. This is a population-level mean-field mechanism: individual institutions do not switch strategy inside one network.

## Hypotheses
H1: Cross-group connectivity changes systemic-risk probability.
H2: More severe shocks increase systemic risk.
H3: Connection placement matters, not only total density.
H4: Private payoff and system-level stability can diverge.
H5: Internalizing systemic losses lowers the optimal intensity and/or population share of risk-taking.

The adaptive-dynamics experiment is used to study the dynamic counterpart of the composition problem rather than being treated as proof of a particular behavioural law.
