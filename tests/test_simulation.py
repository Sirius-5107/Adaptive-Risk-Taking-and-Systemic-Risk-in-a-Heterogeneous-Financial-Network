import numpy as np

from src.simulation import simulate_once


def test_one_complete_simulation_is_reproducible():
    first = simulate_once(n=30, seed=20261001)
    second = simulate_once(n=30, seed=20261001)

    np.testing.assert_array_equal(first.network.groups, second.network.groups)
    np.testing.assert_array_equal(first.network.obligations, second.network.obligations)
    np.testing.assert_array_equal(first.shock.risky_returns, second.shock.risky_returns)
    np.testing.assert_array_equal(first.clearing.payments, second.clearing.payments)


def test_complete_simulation_produces_valid_outputs():
    result = simulate_once(n=30, seed=20261001)

    assert result.clearing.converged
    assert np.all((result.clearing.payments >= 0.0) & (result.clearing.payments <= 1.0))
    assert np.all(result.shock.shocked_assets >= 0.0)
    assert np.all(result.network.obligations >= 0.0)
    assert np.all(np.diag(result.network.obligations) == 0.0)


def test_stronger_bad_shock_does_not_raise_assets():
    mild = simulate_once(n=30, low_return=0.90, probability_low=1.0, seed=20261001)
    severe = simulate_once(n=30, low_return=0.50, probability_low=1.0, seed=20261001)

    assert np.all(severe.shock.shocked_assets <= mild.shock.shocked_assets)
