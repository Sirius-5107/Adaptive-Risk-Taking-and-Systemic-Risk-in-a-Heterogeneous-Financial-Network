"""Controlled parameter experiments for the systemic-risk simulator."""

from __future__ import annotations

import numpy as np

from dataclasses import dataclass
from typing import Mapping, Sequence

from .metrics import MonteCarloResult, estimate_failure_probability, systemic_failure
from .monte_carlo import MonteCarloConfig, run_monte_carlo
from .simulation import simulate_once


@dataclass(frozen=True)
class ParameterSweepPoint:
    """Monte Carlo result associated with one parameter value."""

    parameter: str
    value: float
    result: MonteCarloResult


def run_parameter_sweep(
    parameter: str,
    values: Sequence[float],
    *,
    trials: int = 2000,
    systemic_threshold: float = 0.30,
    confidence: float = 0.95,
    seed: int = 20261001,
    base_simulation_kwargs: Mapping[str, object] | None = None,
) -> tuple[ParameterSweepPoint, ...]:
    """Sweep one simulation parameter with common random numbers.

    Every parameter value uses the same trial seed sequence. Only the selected
    simulation parameter changes between sweep points; all other supplied
    simulation arguments remain fixed.
    """
    if not parameter:
        raise ValueError("parameter must be non-empty.")
    if not values:
        raise ValueError("values must contain at least one value.")

    base_kwargs = dict(base_simulation_kwargs or {})
    results: list[ParameterSweepPoint] = []

    for value in values:
        simulation_kwargs = dict(base_kwargs)
        simulation_kwargs[parameter] = value

        config = MonteCarloConfig(
            trials=trials,
            systemic_threshold=systemic_threshold,
            confidence=confidence,
            seed=seed,
            simulation_kwargs=simulation_kwargs,
        )
        results.append(
            ParameterSweepPoint(
                parameter=parameter,
                value=float(value),
                result=run_monte_carlo(config),
            )
        )

    return tuple(results)


def run_cross_group_connectivity_sweep(
    *,
    values: Sequence[float] = tuple(i / 100 for i in range(0, 21, 2)),
    trials: int = 2000,
    systemic_threshold: float = 0.30,
    confidence: float = 0.95,
    seed: int = 20261001,
) -> tuple[ParameterSweepPoint, ...]:
    """Run E2 by varying p_cross while holding the baseline model fixed."""
    return run_parameter_sweep(
        "p_cross",
        values,
        trials=trials,
        systemic_threshold=systemic_threshold,
        confidence=confidence,
        seed=seed,
    )


def run_shock_severity_sweep(
    *,
    values: Sequence[float] = (0.90, 0.80, 0.70, 0.60, 0.50),
    trials: int = 2000,
    systemic_threshold: float = 0.30,
    confidence: float = 0.95,
    seed: int = 20261001,
) -> tuple[ParameterSweepPoint, ...]:
    """Run E3 by varying the adverse-state risky return R_L."""
    return run_parameter_sweep(
        "low_return",
        values,
        trials=trials,
        systemic_threshold=systemic_threshold,
        confidence=confidence,
        seed=seed,
    )
@dataclass(frozen=True)
class MatchedDensitySweepPoint:
    """Monte Carlo result for one matched-density network configuration."""

    p_within: float
    p_cross: float
    expected_density: float
    result: MonteCarloResult


def _expected_directed_density(
    n: int,
    fraction_low_risk: float,
    p_within: float,
    p_cross: float,
) -> float:
    """Return expected directed edge density excluding self-loops."""
    if n <= 1:
        raise ValueError("n must be greater than 1.")

    n_low = int(round(n * fraction_low_risk))
    n_high = n - n_low
    same_pairs = n_low * (n_low - 1) + n_high * (n_high - 1)
    cross_pairs = 2 * n_low * n_high
    return (
        same_pairs * p_within + cross_pairs * p_cross
    ) / (n * (n - 1))


def _solve_p_within(
    n: int,
    fraction_low_risk: float,
    p_cross: float,
    target_density: float,
) -> float:
    """Solve p_within for a fixed expected network density."""
    if not 0.0 <= p_cross <= 1.0:
        raise ValueError("p_cross must be in [0, 1].")

    n_low = int(round(n * fraction_low_risk))
    n_high = n - n_low
    same_pairs = n_low * (n_low - 1) + n_high * (n_high - 1)
    cross_pairs = 2 * n_low * n_high

    if same_pairs == 0:
        raise ValueError("At least two institutions must share a group.")

    p_within = (
        target_density * n * (n - 1) - cross_pairs * p_cross
    ) / same_pairs

    if not 0.0 <= p_within <= 1.0:
        raise ValueError("Requested p_cross cannot preserve target density.")
    return float(p_within)


def run_matched_density_network_sweep(
    *,
    p_cross_values: Sequence[float] = tuple(i / 40 for i in range(6)),
    trials: int = 2000,
    systemic_threshold: float = 0.30,
    confidence: float = 0.95,
    seed: int = 20261001,
    n: int = 100,
    fraction_low_risk: float = 0.50,
    target_p_within: float = 0.10,
    target_p_cross: float = 0.05,
) -> tuple[MatchedDensitySweepPoint, ...]:
    """Run E4 with fixed expected density and varying connection placement."""
    if not p_cross_values:
        raise ValueError("p_cross_values must contain at least one value.")

    target_density = _expected_directed_density(
        n, fraction_low_risk, target_p_within, target_p_cross
    )
    points: list[MatchedDensitySweepPoint] = []

    for p_cross in p_cross_values:
        p_cross = float(p_cross)
        p_within = _solve_p_within(
            n, fraction_low_risk, p_cross, target_density
        )
        config = MonteCarloConfig(
            trials=trials,
            systemic_threshold=systemic_threshold,
            confidence=confidence,
            seed=seed,
            simulation_kwargs={
                "n": n,
                "fraction_low_risk": fraction_low_risk,
                "p_within": p_within,
                "p_cross": p_cross,
            },
        )
        points.append(
            MatchedDensitySweepPoint(
                p_within=p_within,
                p_cross=p_cross,
                expected_density=target_density,
                result=run_monte_carlo(config),
            )
        )

    return tuple(points)


@dataclass(frozen=True)
class AdaptiveStep:
    """One step of the population-level adaptive dynamics."""

    step: int
    x_before: float
    mean_payoff_low: float
    mean_payoff_high: float
    payoff_difference: float
    systemic_failure_probability: float
    x_after: float


@dataclass(frozen=True)
class AdaptiveDynamicsResult:
    """Trajectory produced by the adaptive risk-taking experiment."""

    initial_x: float
    final_x: float
    steps: tuple[AdaptiveStep, ...]


def _adaptive_update(
    x: float,
    eta: float,
    payoff_high: float,
    payoff_low: float,
) -> float:
    """Apply one bounded replicator-style population update."""
    return float(
        min(
            1.0,
            max(
                0.0,
                x + eta * x * (1.0 - x) * (payoff_high - payoff_low),
            ),
        )
    )


def run_adaptive_dynamics(
    *,
    initial_x: float = 0.50,
    eta: float = 0.10,
    steps: int = 20,
    replications_per_step: int = 100,
    systemic_threshold: float = 0.30,
    seed: int = 20261001,
    q_low: float = 0.20,
    q_high: float = 0.60,
) -> AdaptiveDynamicsResult:
    """Run E6 as repeated population-level adaptation.

    x is the fraction using the higher-risk strategy. At each step, a fresh
    set of stochastic environments is simulated at the current composition.
    Mean terminal equity is used as the strategy payoff, matching E5.
    Multiple replications per step reduce noise before updating x.

    This is a computational mean-field analogue: institutions do not switch
    identities individually inside one network. Instead, the population
    fraction is updated from the difference in group-average payoffs.
    """
    if not 0.0 < initial_x < 1.0:
        raise ValueError("initial_x must be strictly between 0 and 1.")
    if eta < 0.0:
        raise ValueError("eta must be non-negative.")
    if steps < 1:
        raise ValueError("steps must be at least 1.")
    if replications_per_step < 1:
        raise ValueError("replications_per_step must be at least 1.")
    if not 0.0 <= q_low <= 1.0 or not 0.0 <= q_high <= 1.0:
        raise ValueError("q_low and q_high must be in [0, 1].")

    x = float(initial_x)
    trajectory: list[AdaptiveStep] = []

    for step in range(steps):
        low_payoff_total = 0.0
        high_payoff_total = 0.0
        systemic_failures = 0

        for replication in range(replications_per_step):
            simulation_seed = seed + step * replications_per_step + replication
            simulation = simulate_once(
                seed=simulation_seed,
                fraction_low_risk=1.0 - x,
                q_low=q_low,
                q_high=q_high,
            )
            low_payoff, high_payoff = _terminal_equity_by_group(simulation)
            low_payoff_total += low_payoff
            high_payoff_total += high_payoff
            systemic_failures += int(
                systemic_failure(
                    simulation.default_fraction(),
                    systemic_threshold,
                )
            )

        mean_low = low_payoff_total / replications_per_step
        mean_high = high_payoff_total / replications_per_step
        payoff_difference = mean_high - mean_low
        x_after = _adaptive_update(
            x, eta, payoff_high=mean_high, payoff_low=mean_low
        )

        trajectory.append(
            AdaptiveStep(
                step=step,
                x_before=x,
                mean_payoff_low=mean_low,
                mean_payoff_high=mean_high,
                payoff_difference=payoff_difference,
                systemic_failure_probability=(
                    systemic_failures / replications_per_step
                ),
                x_after=x_after,
            )
        )
        x = x_after

    return AdaptiveDynamicsResult(
        initial_x=float(initial_x),
        final_x=x,
        steps=tuple(trajectory),
    )

@dataclass(frozen=True)
class RiskTakingSweepPoint:

    """Monte Carlo outcomes for one high-risk exposure level."""

    q_high: float
    systemic_failure_probability: float
    systemic_failure_ci_low: float
    systemic_failure_ci_high: float
    mean_terminal_equity_low: float
    mean_terminal_equity_high: float
    default_rate_low: float
    default_rate_high: float
    mean_payment_shortfall: float
    distressed_bank_fraction: float
    mean_unpaid_interbank: float
    trials: int


def _terminal_equity_by_group(simulation) -> tuple[float, float]:
    """Return mean terminal equity for low- and high-risk groups."""
    payments = simulation.clearing.payments
    obligations = simulation.network.obligations
    incoming = payments @ obligations
    interbank_paid = payments * obligations.sum(axis=1)
    equity = (
        simulation.shock.shocked_assets
        + incoming
        - simulation.external_liabilities
        - interbank_paid
    )

    groups = simulation.network.groups
    low = equity[groups == 0]
    high = equity[groups == 1]
    if low.size == 0 or high.size == 0:
        raise ValueError("Both risk groups must contain at least one institution.")
    return float(low.mean()), float(high.mean())


@dataclass(frozen=True)
class RiskOptimizationPoint:
    """Objective value for one risk-penalty and exposure pair."""

    lambda_systemic: float
    q_high: float
    private_payoff: float
    systemic_loss: float
    objective: float


@dataclass(frozen=True)
class RiskOptimizationResult:
    """System-aware optimum for each systemic-risk penalty."""

    lambda_systemic: float
    optimal_q_high: float
    optimal_objective: float
    points: tuple[RiskOptimizationPoint, ...]


def optimize_risk_taking(
    sweep: Sequence[RiskTakingSweepPoint],
    *,
    lambdas: Sequence[float] = (0.0, 0.05, 0.10, 0.20, 0.50),
) -> tuple[RiskOptimizationResult, ...]:
    """Find the risk exposure maximizing private payoff minus network loss.

    The objective is

        J(q) = U_R(q) - lambda_systemic * L(q),

    where U_R is mean terminal equity of high-risk institutions and L is
    mean unpaid interbank obligations. The sweep is assumed to have already
    been run using common random numbers, so this function adds no simulation
    noise or computational cost.

    lambda_systemic controls how strongly network damage is penalized. At
    lambda_systemic=0 the objective is purely private; larger values place
    more weight on systemic losses.
    """
    if not sweep:
        raise ValueError("sweep must contain at least one result.")
    if not lambdas:
        raise ValueError("lambdas must contain at least one value.")
    if any(float(value) < 0.0 for value in lambdas):
        raise ValueError("lambdas must be non-negative.")

    results: list[RiskOptimizationResult] = []

    for lambda_systemic in lambdas:
        penalty = float(lambda_systemic)
        points = tuple(
            RiskOptimizationPoint(
                lambda_systemic=penalty,
                q_high=point.q_high,
                private_payoff=point.mean_terminal_equity_high,
                systemic_loss=point.mean_unpaid_interbank,
                objective=(
                    point.mean_terminal_equity_high
                    - penalty * point.mean_unpaid_interbank
                ),
            )
            for point in sweep
        )
        optimum = max(points, key=lambda point: point.objective)
        results.append(
            RiskOptimizationResult(
                lambda_systemic=penalty,
                optimal_q_high=optimum.q_high,
                optimal_objective=optimum.objective,
                points=points,
            )
        )

    return tuple(results)


@dataclass(frozen=True)
class RiskFractionSweepPoint:
    """Monte Carlo outcomes for one fraction of high-risk institutions."""

    fraction_high_risk: float
    mean_terminal_equity: float
    mean_payment_shortfall: float
    distressed_bank_fraction: float
    mean_unpaid_interbank: float
    systemic_failure_probability: float
    systemic_failure_ci_low: float
    systemic_failure_ci_high: float
    trials: int


@dataclass(frozen=True)
class RiskFractionOptimizationPoint:
    """Objective value for one systemic-risk penalty and risk-taking fraction."""

    lambda_systemic: float
    fraction_high_risk: float
    private_payoff: float
    systemic_loss: float
    objective: float


@dataclass(frozen=True)
class RiskFractionOptimizationResult:
    """System-aware optimum for each penalty on network damage."""

    lambda_systemic: float
    optimal_fraction_high_risk: float
    optimal_objective: float
    points: tuple[RiskFractionOptimizationPoint, ...]


def run_risk_fraction_sweep(
    *,
    values: Sequence[float] = tuple(i / 20 for i in range(1, 20)),
    trials: int = 2000,
    systemic_threshold: float = 0.30,
    confidence: float = 0.95,
    seed: int = 20261001,
    q_low: float = 0.20,
    q_high: float = 0.80,
) -> tuple[RiskFractionSweepPoint, ...]:
    """Sweep the population fraction using the high-risk strategy.

    The risky fraction changes group composition while q_low and q_high remain
    fixed. Common trial seeds are reused across values. Private payoff is mean
    terminal equity across all institutions; systemic loss is unpaid
    interbank obligations.
    """
    if not values:
        raise ValueError("values must contain at least one value.")
    if trials < 1:
        raise ValueError("trials must be at least 1.")
    if not 0.0 <= q_low <= 1.0 or not 0.0 <= q_high <= 1.0:
        raise ValueError("q_low and q_high must be in [0, 1].")

    points: list[RiskFractionSweepPoint] = []

    for fraction_high_risk in values:
        fraction_high_risk = float(fraction_high_risk)
        if not 0.0 <= fraction_high_risk <= 1.0:
            raise ValueError("fraction_high_risk values must be in [0, 1].")

        total_equity = 0.0
        total_payment_shortfall = 0.0
        distressed_banks = 0
        total_unpaid_interbank = 0.0
        failures = 0

        for trial in range(trials):
            simulation = simulate_once(
                seed=seed + trial,
                fraction_low_risk=1.0 - fraction_high_risk,
                q_low=q_low,
                q_high=q_high,
            )

            payments = simulation.clearing.payments
            obligations = simulation.network.obligations
            incoming = payments @ obligations
            interbank_paid = payments * obligations.sum(axis=1)
            equity = (
                simulation.shock.shocked_assets
                + incoming
                - simulation.external_liabilities
                - interbank_paid
            )

            total_equity += float(equity.mean())
            total_payment_shortfall += float(np.sum(1.0 - payments))
            defaults = payments < (1.0 - 1e-8)
            distressed_banks += int(defaults.sum())
            total_unpaid_interbank += float(
                np.sum(obligations * (1.0 - payments[:, None]))
            )

            if systemic_failure(
                simulation.default_fraction(),
                systemic_threshold,
            ):
                failures += 1

        mc = estimate_failure_probability(
            failures, trials, confidence=confidence
        )
        n = simulation.network.obligations.shape[0]

        points.append(
            RiskFractionSweepPoint(
                fraction_high_risk=fraction_high_risk,
                mean_terminal_equity=total_equity / trials,
                mean_payment_shortfall=(
                    total_payment_shortfall / (trials * n)
                ),
                distressed_bank_fraction=distressed_banks / (trials * n),
                mean_unpaid_interbank=total_unpaid_interbank / trials,
                systemic_failure_probability=mc.probability,
                systemic_failure_ci_low=mc.ci_low,
                systemic_failure_ci_high=mc.ci_high,
                trials=trials,
            )
        )

    return tuple(points)


def optimize_risk_fraction(
    sweep: Sequence[RiskFractionSweepPoint],
    *,
    lambdas: Sequence[float] = (0.0, 0.05, 0.10, 0.20, 0.50),
) -> tuple[RiskFractionOptimizationResult, ...]:
    """Find the high-risk population fraction maximizing private payoff minus network loss.

    The objective is

        J(x) = U(x) - lambda_systemic * L(x),

    where U is mean terminal equity across all institutions and L is mean
    unpaid interbank obligations.
    """
    if not sweep:
        raise ValueError("sweep must contain at least one result.")
    if not lambdas:
        raise ValueError("lambdas must contain at least one value.")
    if any(float(value) < 0.0 for value in lambdas):
        raise ValueError("lambdas must be non-negative.")

    results: list[RiskFractionOptimizationResult] = []

    for lambda_systemic in lambdas:
        penalty = float(lambda_systemic)
        points = tuple(
            RiskFractionOptimizationPoint(
                lambda_systemic=penalty,
                fraction_high_risk=point.fraction_high_risk,
                private_payoff=point.mean_terminal_equity,
                systemic_loss=point.mean_unpaid_interbank,
                objective=(
                    point.mean_terminal_equity
                    - penalty * point.mean_unpaid_interbank
                ),
            )
            for point in sweep
        )
        optimum = max(points, key=lambda point: point.objective)
        results.append(
            RiskFractionOptimizationResult(
                lambda_systemic=penalty,
                optimal_fraction_high_risk=optimum.fraction_high_risk,
                optimal_objective=optimum.objective,
                points=points,
            )
        )

    return tuple(results)



def run_risk_taking_sweep(
    *,
    values: Sequence[float] = (0.40, 0.50, 0.60, 0.70, 0.80),
    trials: int = 2000,
    systemic_threshold: float = 0.30,
    confidence: float = 0.95,
    seed: int = 20261001,
    q_low: float = 0.20,
) -> tuple[RiskTakingSweepPoint, ...]:
    """Run E5 by varying high-risk institutions' risky-asset exposure.

    The same trial seeds are reused across q_high values. This keeps the
    network and realized shock uniforms comparable while changing only q_high.
    Private payoff is measured as mean terminal equity after interbank clearing.
    """
    if not values:
        raise ValueError("values must contain at least one value.")
    if not 0.0 <= q_low <= 1.0:
        raise ValueError("q_low must be in [0, 1].")

    points: list[RiskTakingSweepPoint] = []

    for q_high in values:
        q_high = float(q_high)
        if not 0.0 <= q_high <= 1.0:
            raise ValueError("q_high values must be in [0, 1].")

        failures = 0
        low_equity_total = 0.0
        high_equity_total = 0.0
        low_defaults = 0
        high_defaults = 0
        total_payment_shortfall = 0.0
        distressed_banks = 0
        total_unpaid_interbank = 0.0

        for trial in range(trials):
            simulation = simulate_once(
                seed=seed + trial,
                q_low=q_low,
                q_high=q_high,
            )
            low_equity, high_equity = _terminal_equity_by_group(simulation)
            low_equity_total += low_equity
            high_equity_total += high_equity

            groups = simulation.network.groups
            defaults = simulation.clearing.payments < (1.0 - 1e-8)
            low_defaults += int((defaults & (groups == 0)).sum())
            high_defaults += int((defaults & (groups == 1)).sum())

            payments = simulation.clearing.payments
            total_payment_shortfall += float(np.sum(1.0 - payments))
            distressed_banks += int(defaults.sum())
            total_unpaid_interbank += float(
                np.sum(
                    simulation.network.obligations
                    * (1.0 - payments[:, None])
                )
            )

            if systemic_failure(
                simulation.default_fraction(),
                systemic_threshold,
            ):
                failures += 1

        mc = estimate_failure_probability(
            failures, trials, confidence=confidence
        )
        low_count = trials * (simulation.network.groups == 0).sum()
        high_count = trials * (simulation.network.groups == 1).sum()

        points.append(
            RiskTakingSweepPoint(
                q_high=q_high,
                systemic_failure_probability=mc.probability,
                systemic_failure_ci_low=mc.ci_low,
                systemic_failure_ci_high=mc.ci_high,
                mean_terminal_equity_low=low_equity_total / trials,
                mean_terminal_equity_high=high_equity_total / trials,
                default_rate_low=low_defaults / low_count,
                default_rate_high=high_defaults / high_count,
                mean_payment_shortfall=(
                    total_payment_shortfall
                    / (trials * simulation.network.obligations.shape[0])
                ),
                distressed_bank_fraction=(
                    distressed_banks
                    / (trials * simulation.network.obligations.shape[0])
                ),
                mean_unpaid_interbank=total_unpaid_interbank / trials,
                trials=trials,
            )
        )

    return tuple(points)
