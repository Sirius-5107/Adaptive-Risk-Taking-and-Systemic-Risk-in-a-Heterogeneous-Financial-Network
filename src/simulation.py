"""One complete end-to-end systemic-risk simulation."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .clearing import ClearingResult, solve_clearing
from .network import NetworkResult, generate_network
from .shocks import ShockResult, apply_risky_asset_shock


@dataclass(frozen=True)
class SimulationResult:
    """All outputs needed to inspect one simulated financial system."""

    network: NetworkResult
    shock: ShockResult
    clearing: ClearingResult
    external_assets: np.ndarray
    external_liabilities: np.ndarray

    @property
    def default_fraction(self, threshold: float = 1.0 - 1e-8) -> float:
        """Fraction of institutions whose payment fraction is below default threshold."""
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("threshold must be in [0, 1].")
        return float(np.mean(self.clearing.payments < threshold))


def simulate_once(
    *,
    n: int = 100,
    fraction_low_risk: float = 0.50,
    p_within: float = 0.10,
    p_cross: float = 0.05,
    exposure_scale: float = 0.05,
    base_asset: float = 1.00,
    external_liability: float = 0.50,
    q_low: float = 0.20,
    q_high: float = 0.60,
    high_return: float = 1.10,
    low_return: float = 0.70,
    probability_low: float = 0.20,
    tolerance: float = 1e-10,
    max_iterations: int = 1000,
    seed: int = 20261001,
) -> SimulationResult:
    """Generate a network, shock its assets, and clear payments."""
    if base_asset < 0.0 or external_liability < 0.0:
        raise ValueError("Balance-sheet values must be non-negative.")

    seed_sequence = np.random.SeedSequence(seed)
    network_sequence, shock_sequence = seed_sequence.spawn(2)
    network_seed = int(network_sequence.generate_state(1)[0])
    shock_seed = int(shock_sequence.generate_state(1)[0])

    network = generate_network(
        n=n,
        fraction_low_risk=fraction_low_risk,
        p_within=p_within,
        p_cross=p_cross,
        exposure_scale=exposure_scale,
        seed=network_seed,
    )

    external_assets = np.full(n, base_asset, dtype=float)
    external_liabilities = np.full(n, external_liability, dtype=float)

    shock = apply_risky_asset_shock(
        external_assets,
        network.groups,
        q_low=q_low,
        q_high=q_high,
        high_return=high_return,
        low_return=low_return,
        probability_low=probability_low,
        seed=shock_seed,
    )

    clearing = solve_clearing(
        shock.shocked_assets,
        external_liabilities,
        network.obligations,
        tolerance=tolerance,
        max_iterations=max_iterations,
    )

    return SimulationResult(
        network=network,
        shock=shock,
        clearing=clearing,
        external_assets=external_assets,
        external_liabilities=external_liabilities,
    )
