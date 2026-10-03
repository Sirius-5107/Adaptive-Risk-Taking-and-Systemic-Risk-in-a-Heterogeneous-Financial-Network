"""Controlled parameter experiments for the systemic-risk simulator."""

from __future__ import annotations

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
                trials=trials,
            )
        )

    return tuple(points)
