import numpy as np
import pytest

from src.shocks import apply_risky_asset_shock


def test_shock_is_reproducible():
    assets = np.ones(8)
    groups = np.array([0, 0, 0, 0, 1, 1, 1, 1])

    first = apply_risky_asset_shock(
        assets, groups, q_low=0.20, q_high=0.60,
        high_return=1.10, low_return=0.70,
        probability_low=0.20, seed=123,
    )
    second = apply_risky_asset_shock(
        assets, groups, q_low=0.20, q_high=0.60,
        high_return=1.10, low_return=0.70,
        probability_low=0.20, seed=123,
    )

    np.testing.assert_array_equal(first.risky_returns, second.risky_returns)
    np.testing.assert_array_equal(first.shocked_assets, second.shocked_assets)


def test_high_risk_group_loses_more_under_same_bad_return():
    result = apply_risky_asset_shock(
        np.ones(2), np.array([0, 1]),
        q_low=0.20, q_high=0.60,
        high_return=1.10, low_return=0.70,
        probability_low=1.0, seed=123,
    )

    np.testing.assert_allclose(result.shocked_assets, [0.94, 0.82])


def test_zero_risky_exposure_is_unchanged():
    assets = np.array([2.0, 3.0])
    result = apply_risky_asset_shock(
        assets, np.array([0, 1]),
        q_low=0.0, q_high=0.0,
        high_return=0.10, low_return=0.10,
        probability_low=1.0, seed=123,
    )

    np.testing.assert_array_equal(result.shocked_assets, assets)


def test_invalid_groups_are_rejected():
    with pytest.raises(ValueError):
        apply_risky_asset_shock(
            np.ones(2), np.array([0, 2]),
            q_low=0.2, q_high=0.6,
            high_return=1.1, low_return=0.7,
            probability_low=0.2, seed=123,
        )
