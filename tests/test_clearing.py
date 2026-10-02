import numpy as np

from src.clearing import solve_clearing


def test_no_shock_chain_is_fully_paid():
    assets = np.array([100.0, 20.0, 20.0, 0.0])
    liabilities = np.zeros(4)
    E = np.zeros((4, 4))
    E[0, 1] = 100.0
    E[1, 2] = 100.0
    E[2, 3] = 100.0

    result = solve_clearing(assets, liabilities, E)

    assert result.converged
    np.testing.assert_allclose(result.payments, [1.0, 1.0, 1.0, 1.0])


def test_chain_contagion_matches_hand_calculation():
    # A pays 40/100 = 0.40
    # B has 20 + 40 = 60, pays 60/100 = 0.60
    # C has 20 + 60 = 80, pays 80/100 = 0.80
    assets = np.array([40.0, 20.0, 20.0, 0.0])
    liabilities = np.zeros(4)
    E = np.zeros((4, 4))
    E[0, 1] = 100.0
    E[1, 2] = 100.0
    E[2, 3] = 100.0

    result = solve_clearing(assets, liabilities, E)

    assert result.converged
    np.testing.assert_allclose(result.payments, [0.4, 0.6, 0.8, 1.0])


def test_disconnected_bank_is_not_affected():
    assets = np.array([40.0, 20.0, 20.0, 50.0])
    liabilities = np.zeros(4)
    E = np.zeros((4, 4))
    E[0, 1] = 100.0
    E[1, 2] = 100.0

    result = solve_clearing(assets, liabilities, E)

    assert result.converged
    np.testing.assert_allclose(result.payments, [0.4, 0.6, 1.0, 1.0])


def test_zero_network_means_no_network_contagion():
    assets = np.array([40.0, 20.0, 20.0])
    liabilities = np.zeros(3)
    E = np.zeros((3, 3))

    result = solve_clearing(assets, liabilities, E)

    assert result.converged
    np.testing.assert_allclose(result.payments, np.ones(3))


def test_payments_are_always_bounded():
    assets = np.array([0.0, 100.0])
    liabilities = np.zeros(2)
    E = np.array([[0.0, 100.0], [0.0, 0.0]])

    result = solve_clearing(assets, liabilities, E)

    assert np.all(result.payments >= 0.0)
    assert np.all(result.payments <= 1.0)


def test_cyclic_contagion_propagates_until_stable():
    # A and B owe each other 100.
    # A also owes 60 externally and starts with no assets.
    # Starting from full payment, the feedback loop is:
    # [1.0, 1.0] -> [0.4, 1.0] -> [0.0, 0.4] -> [0.0, 0.0].
    assets = np.array([0.0, 0.0])
    liabilities = np.array([60.0, 0.0])
    E = np.array(
        [
            [0.0, 100.0],
            [100.0, 0.0],
        ]
    )

    result = solve_clearing(assets, liabilities, E)

    assert result.converged
    np.testing.assert_allclose(result.payments, [0.0, 0.0])
    assert result.iterations > 1
