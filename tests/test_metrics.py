import pytest

from src.metrics import estimate_failure_probability, systemic_failure


def test_systemic_failure_threshold():
    assert systemic_failure(0.30, 0.30)
    assert not systemic_failure(0.29, 0.30)


def test_monte_carlo_estimate():
    result = estimate_failure_probability(25, 1000)

    assert result.probability == 0.025
    assert result.trials == 1000
    assert result.failures == 25
    assert result.standard_error > 0.0
    assert 0.0 <= result.ci_low <= result.probability <= result.ci_high <= 1.0


@pytest.mark.parametrize(
    ("failures", "trials"),
    [(-1, 100), (101, 100), (0, 0)],
)
def test_invalid_counts_are_rejected(failures, trials):
    with pytest.raises(ValueError):
        estimate_failure_probability(failures, trials)
