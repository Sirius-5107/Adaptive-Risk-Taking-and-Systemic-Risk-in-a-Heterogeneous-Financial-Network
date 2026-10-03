from src.experiments import (
    run_cross_group_connectivity_sweep,
    run_matched_density_network_sweep,
    run_parameter_sweep,
    run_shock_severity_sweep,
)
from src.monte_carlo import MonteCarloConfig, run_monte_carlo


def test_monte_carlo_accepts_simulation_kwargs():
    baseline = run_monte_carlo(MonteCarloConfig(trials=5, seed=20261001))
    configured = run_monte_carlo(
        MonteCarloConfig(
            trials=5,
            seed=20261001,
            simulation_kwargs={"p_cross": 0.0},
        )
    )
    assert baseline.trials == configured.trials == 5


def test_parameter_sweep_is_reproducible():
    first = run_parameter_sweep("p_cross", [0.0, 0.05, 0.10], trials=10, seed=20261001)
    second = run_parameter_sweep("p_cross", [0.0, 0.05, 0.10], trials=10, seed=20261001)
    assert first == second


def test_parameter_sweep_preserves_order_and_values():
    results = run_parameter_sweep("p_cross", [0.0, 0.05, 0.10], trials=10, seed=20261001)
    assert [point.value for point in results] == [0.0, 0.05, 0.10]
    assert all(point.parameter == "p_cross" for point in results)
    assert all(point.result.trials == 10 for point in results)


def test_cross_group_connectivity_default_grid():
    results = run_cross_group_connectivity_sweep(trials=5)
    assert len(results) == 11
    assert results[0].value == 0.0
    assert results[-1].value == 0.20


def test_shock_severity_default_grid():
    results = run_shock_severity_sweep(trials=5)
    assert [point.value for point in results] == [0.90, 0.80, 0.70, 0.60, 0.50]
    assert all(point.parameter == "low_return" for point in results)
    assert all(point.result.trials == 5 for point in results)


def test_matched_density_keeps_expected_density_fixed():
    results = run_matched_density_network_sweep(trials=5)
    densities = [point.expected_density for point in results]
    assert len(results) == 6
    assert max(densities) - min(densities) < 1e-12
    assert results[0].p_cross == 0.0
    assert results[-1].p_cross == 0.125


def test_matched_density_reproduces_baseline_pair():
    results = run_matched_density_network_sweep(
        p_cross_values=[0.05],
        trials=5,
    )
    assert results[0].p_within == 0.10


def test_matched_density_sweep_is_reproducible():
    first = run_matched_density_network_sweep(trials=5, seed=20261001)
    second = run_matched_density_network_sweep(trials=5, seed=20261001)
    assert first == second
