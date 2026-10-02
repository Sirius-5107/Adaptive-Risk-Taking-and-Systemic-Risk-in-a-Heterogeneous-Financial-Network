from src.monte_carlo import MonteCarloConfig, run_monte_carlo


def test_monte_carlo_is_reproducible():
    config = MonteCarloConfig(trials=30, seed=20261001)
    assert run_monte_carlo(config) == run_monte_carlo(config)


def test_monte_carlo_result_is_bounded():
    result = run_monte_carlo(MonteCarloConfig(trials=30, seed=20261001))
    assert 0.0 <= result.probability <= 1.0
    assert result.trials == 30
    assert 0 <= result.failures <= result.trials
    assert 0.0 <= result.ci_low <= result.ci_high <= 1.0
