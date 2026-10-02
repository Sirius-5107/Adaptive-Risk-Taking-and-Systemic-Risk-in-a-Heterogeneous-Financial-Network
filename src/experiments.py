"""Controlled parameter experiments for the systemic-risk simulator."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from .metrics import MonteCarloResult
from .monte_carlo import MonteCarloConfig, run_monte_carlo


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
