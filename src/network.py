"""Reproducible directed network generator for the systemic-risk model."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class NetworkResult:
    """Generated institution groups and interbank obligations."""

    groups: np.ndarray
    obligations: np.ndarray


def generate_network(
    n: int,
    fraction_low_risk: float,
    p_within: float,
    p_cross: float,
    exposure_scale: float,
    *,
    seed: int,
) -> NetworkResult:
    """Generate a directed two-group financial network.

    Group 0 is lower-risk and group 1 is higher-risk.

    For each ordered pair i != j, an interbank obligation is created with
    probability p_within when both institutions are in the same group and
    p_cross otherwise. Every created edge has obligation exposure_scale.

    A local NumPy Generator is used so the result is fully determined by
    the supplied seed and does not depend on global random state.
    """
    if n <= 0:
        raise ValueError("n must be positive.")
    if not 0.0 <= fraction_low_risk <= 1.0:
        raise ValueError("fraction_low_risk must be in [0, 1].")
    if not 0.0 <= p_within <= 1.0 or not 0.0 <= p_cross <= 1.0:
        raise ValueError("Edge probabilities must be in [0, 1].")
    if exposure_scale <= 0.0:
        raise ValueError("exposure_scale must be positive.")

    rng = np.random.default_rng(seed)

    n_low = int(round(n * fraction_low_risk))
    groups = np.ones(n, dtype=np.int8)
    groups[:n_low] = 0

    # Shuffle group labels so institution index is not correlated with group.
    rng.shuffle(groups)

    same_group = groups[:, None] == groups[None, :]
    probabilities = np.where(same_group, p_within, p_cross)

    edges = rng.random((n, n)) < probabilities
    np.fill_diagonal(edges, False)

    obligations = edges.astype(float) * exposure_scale

    return NetworkResult(groups=groups, obligations=obligations)
