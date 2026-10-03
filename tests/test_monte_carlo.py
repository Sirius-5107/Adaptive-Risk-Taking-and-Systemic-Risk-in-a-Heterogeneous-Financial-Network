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


def test_risk_taking_sweep_reproduces():
    from src.experiments import run_risk_taking_sweep

    first = run_risk_taking_sweep(
        values=[0.40, 0.60, 0.80],
        trials=5,
        seed=20261001,
    )
    second = run_risk_taking_sweep(
        values=[0.40, 0.60, 0.80],
        trials=5,
        seed=20261001,
    )
    assert first == second


def test_risk_taking_sweep_preserves_values_and_bounds():
    from src.experiments import run_risk_taking_sweep

    results = run_risk_taking_sweep(
        values=[0.40, 0.60, 0.80],
        trials=5,
        seed=20261001,
    )
    assert [point.q_high for point in results] == [0.40, 0.60, 0.80]
    assert all(0.0 <= point.systemic_failure_probability <= 1.0 for point in results)
    assert all(0.0 <= point.default_rate_low <= 1.0 for point in results)
    assert all(0.0 <= point.default_rate_high <= 1.0 for point in results)
    assert all(point.trials == 5 for point in results)


def test_risk_taking_sweep_rejects_invalid_exposure():
    from src.experiments import run_risk_taking_sweep

    try:
        run_risk_taking_sweep(values=[1.1], trials=1)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for q_high > 1.")


def test_adaptive_update_matches_replicator_rule():
    from src.experiments import _adaptive_update

    assert _adaptive_update(0.50, 0.10, 1.10, 0.90) == 0.505
    assert _adaptive_update(0.50, 0.10, 0.90, 1.10) == 0.495


def test_adaptive_dynamics_reproduces():
    from src.experiments import run_adaptive_dynamics

    first = run_adaptive_dynamics(
        initial_x=0.50,
        eta=0.10,
        steps=3,
        replications_per_step=2,
        seed=20261001,
    )
    second = run_adaptive_dynamics(
        initial_x=0.50,
        eta=0.10,
        steps=3,
        replications_per_step=2,
        seed=20261001,
    )
    assert first == second


def test_adaptive_dynamics_preserves_bounds_and_length():
    from src.experiments import run_adaptive_dynamics

    result = run_adaptive_dynamics(
        initial_x=0.50,
        eta=0.10,
        steps=4,
        replications_per_step=2,
        seed=20261001,
    )
    assert len(result.steps) == 4
    assert result.initial_x == 0.50
    assert 0.0 <= result.final_x <= 1.0
    assert all(0.0 <= step.x_before <= 1.0 for step in result.steps)
    assert all(0.0 <= step.x_after <= 1.0 for step in result.steps)
    assert all(0.0 <= step.systemic_failure_probability <= 1.0 for step in result.steps)


def test_adaptive_dynamics_rejects_invalid_inputs():
    from src.experiments import run_adaptive_dynamics

    for kwargs in (
        {"initial_x": 0.0},
        {"initial_x": 1.0},
        {"eta": -0.1},
        {"steps": 0},
        {"replications_per_step": 0},
    ):
        try:
            run_adaptive_dynamics(**kwargs)
        except ValueError:
            pass
        else:
            raise AssertionError(f"Expected ValueError for {kwargs}.")
