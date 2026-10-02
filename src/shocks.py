"""Risky-asset shock mechanics for one simulated financial system."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ShockResult:
    """Realized risky returns and post-shock external assets."""

    risky_returns: np.ndarray
    shocked_assets: np.ndarray


def apply_risky_asset_shock(
    base_assets: np.ndarray,
    groups: np.ndarray,
    *,
    q_low: float,
    q_high: float,
    high_return: float,
    low_return: float,
    probability_low: float,
    seed: int,
) -> ShockResult:
    """Apply an independent two-state risky-asset shock.

    Group 0 uses q_low risky exposure and group 1 uses q_high.
    The remaining asset fraction is held in the safe asset with return 1.
    """
    assets = np.asarray(base_assets, dtype=float)
    groups = np.asarray(groups, dtype=np.int8)

    if assets.ndim != 1 or groups.shape != assets.shape:
        raise ValueError("base_assets and groups must be one-dimensional and aligned.")
    if np.any(assets < 0):
        raise ValueError("base_assets must be non-negative.")
    if not 0.0 <= q_low <= 1.0 or not 0.0 <= q_high <= 1.0:
        raise ValueError("Risky asset fractions must be in [0, 1].")
    if not 0.0 <= probability_low <= 1.0:
        raise ValueError("probability_low must be in [0, 1].")
    if low_return < 0.0 or high_return < 0.0:
        raise ValueError("Returns must be non-negative.")
    if not np.all(np.isin(groups, [0, 1])):
        raise ValueError("groups must contain only 0 and 1.")

    rng = np.random.default_rng(seed)
    bad = rng.random(assets.size) < probability_low
    risky_returns = np.where(bad, low_return, high_return)

    risky_fraction = np.where(groups == 0, q_low, q_high)
    safe_fraction = 1.0 - risky_fraction
    shocked_assets = assets * (safe_fraction + risky_fraction * risky_returns)

    return ShockResult(
        risky_returns=risky_returns,
        shocked_assets=shocked_assets,
    )
