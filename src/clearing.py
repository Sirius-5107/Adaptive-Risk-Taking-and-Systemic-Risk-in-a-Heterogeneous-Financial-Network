"""Core payment-clearing solver for the toy systemic-risk model."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ClearingResult:
    payments: np.ndarray
    converged: bool
    iterations: int

    @property
    def paid_amounts(self) -> np.ndarray:
        return self.payments


def solve_clearing(
    external_assets: np.ndarray,
    external_liabilities: np.ndarray,
    obligations: np.ndarray,
    *,
    tolerance: float = 1e-10,
    max_iterations: int = 1000,
) -> ClearingResult:
    """Solve payment fractions by fixed-point iteration.

    obligations[i, j] is the amount institution i owes institution j.
    payments[i] is the fraction of i's total interbank obligation that is paid.
    """
    assets = np.asarray(external_assets, dtype=float)
    ext_liab = np.asarray(external_liabilities, dtype=float)
    E = np.asarray(obligations, dtype=float)

    n = assets.size
    if ext_liab.shape != (n,) or E.shape != (n, n):
        raise ValueError("Incompatible array shapes.")
    if np.any(assets < 0) or np.any(ext_liab < 0) or np.any(E < 0):
        raise ValueError("Assets, liabilities, and obligations must be non-negative.")
    if np.any(np.diag(E) != 0):
        raise ValueError("Self-obligations are not allowed.")

    total_obligations = E.sum(axis=1)
    payments = np.ones(n, dtype=float)

    for iteration in range(1, max_iterations + 1):
        incoming = payments @ E
        available = assets + incoming

        new_payments = np.ones(n, dtype=float)
        positive = total_obligations > 0
        new_payments[positive] = np.clip(
            (available[positive] - ext_liab[positive])
            / total_obligations[positive],
            0.0,
            1.0,
        )

        if np.max(np.abs(new_payments - payments)) < tolerance:
            return ClearingResult(new_payments, True, iteration)

        payments = new_payments

    return ClearingResult(payments, False, max_iterations)
