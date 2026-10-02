"""Monte Carlo systemic-risk experiment built on the one-run simulator."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from .metrics import MonteCarloResult, estimate_failure_probability, systemic_failure
from .simulation import simulate_once


@dataclass(frozen=True)
class MonteCarloConfig:
    """Configuration for a reproducible systemic-risk experiment."""

    trials: int = 2000
    systemic_threshold: float = 0.30
    confidence: float = 0.95
    seed: int = 20261001
    simulation_kwargs: Mapping[str, object] = field(default_factory=dict)


def run_monte_carlo(config: MonteCarloConfig = MonteCarloConfig()) -> MonteCarloResult:
    """Run independent seeded simulations and estimate failure probability.

    simulation_kwargs controls model parameters while trial seeds remain
    unchanged. This makes controlled parameter comparisons possible using
    common random numbers.
    """
    failures = 0

    for trial in range(config.trials):
        result = simulate_once(seed=config.seed + trial, **config.simulation_kwargs)
        if systemic_failure(result.default_fraction(), config.systemic_threshold):
            failures += 1

    return estimate_failure_probability(
        failures, config.trials, confidence=config.confidence
    )
