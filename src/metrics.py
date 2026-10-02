"""Systemic-risk metrics for Monte Carlo experiments."""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt


@dataclass(frozen=True)
class MonteCarloResult:
    """Monte Carlo estimate of a Bernoulli systemic-failure probability."""

    trials: int
    failures: int
    probability: float
    standard_error: float
    ci_low: float
    ci_high: float


def systemic_failure(default_fraction: float, threshold: float = 0.30) -> bool:
    """Return whether the simulated system crosses the systemic-failure threshold."""
    if not 0.0 <= default_fraction <= 1.0:
        raise ValueError("default_fraction must be in [0, 1].")
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be in [0, 1].")
    return default_fraction >= threshold


def estimate_failure_probability(
    failures: int,
    trials: int,
    *,
    confidence: float = 0.95,
) -> MonteCarloResult:
    """Estimate Bernoulli probability with a normal-approximation interval."""
    if trials <= 0:
        raise ValueError("trials must be positive.")
    if not 0 <= failures <= trials:
        raise ValueError("failures must lie between 0 and trials.")
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be in (0, 1).")

    probability = failures / trials
    standard_error = sqrt(probability * (1.0 - probability) / trials)

    z_values = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}
    z = z_values.get(round(confidence, 2))
    if z is None:
        raise ValueError("confidence must be 0.90, 0.95, or 0.99.")

    margin = z * standard_error
    return MonteCarloResult(
        trials=trials,
        failures=failures,
        probability=probability,
        standard_error=standard_error,
        ci_low=max(0.0, probability - margin),
        ci_high=min(1.0, probability + margin),
    )
