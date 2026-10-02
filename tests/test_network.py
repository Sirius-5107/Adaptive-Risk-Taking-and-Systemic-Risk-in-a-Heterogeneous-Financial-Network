import numpy as np

from src.network import generate_network


def test_network_has_expected_group_counts():
    result = generate_network(
        n=100,
        fraction_low_risk=0.5,
        p_within=0.1,
        p_cross=0.05,
        exposure_scale=0.05,
        seed=20261001,
    )

    assert np.sum(result.groups == 0) == 50
    assert np.sum(result.groups == 1) == 50


def test_network_has_no_self_obligations():
    result = generate_network(
        n=50,
        fraction_low_risk=0.5,
        p_within=0.1,
        p_cross=0.05,
        exposure_scale=0.05,
        seed=20261001,
    )

    assert np.all(np.diag(result.obligations) == 0.0)
    assert np.all(result.obligations >= 0.0)


def test_network_is_reproducible_for_same_seed():
    first = generate_network(
        n=30,
        fraction_low_risk=0.4,
        p_within=0.2,
        p_cross=0.05,
        exposure_scale=0.05,
        seed=123,
    )
    second = generate_network(
        n=30,
        fraction_low_risk=0.4,
        p_within=0.2,
        p_cross=0.05,
        exposure_scale=0.05,
        seed=123,
    )

    np.testing.assert_array_equal(first.groups, second.groups)
    np.testing.assert_array_equal(first.obligations, second.obligations)


def test_zero_probabilities_produce_no_network_edges():
    result = generate_network(
        n=20,
        fraction_low_risk=0.5,
        p_within=0.0,
        p_cross=0.0,
        exposure_scale=0.05,
        seed=20261001,
    )

    assert not np.any(result.obligations)


def test_edges_use_configured_exposure_scale():
    result = generate_network(
        n=40,
        fraction_low_risk=0.5,
        p_within=1.0,
        p_cross=1.0,
        exposure_scale=0.25,
        seed=20261001,
    )

    off_diagonal = ~np.eye(40, dtype=bool)
    assert np.all(result.obligations[off_diagonal] == 0.25)
    assert np.all(np.diag(result.obligations) == 0.0)
