import numpy as np
import pytest

import pyvtools.algebra as valg


@pytest.fixture
def linear_data():
    X = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
    Y = 2.0 * X + 1.0
    return X, Y


def test_r_squared_perfect_fit(linear_data):
    X, Y = linear_data
    assert valg.r_squared(Y, Y) == pytest.approx(1.0)


def test_fit_linear_exact_line(linear_data):
    X, Y = linear_data
    result = valg.fit_linear(X, Y)

    assert result.slope.nominal_value == pytest.approx(2.0, abs=1e-12)
    assert result.intercept.nominal_value == pytest.approx(1.0, abs=1e-12)
    assert result.rsq == pytest.approx(1.0, abs=1e-12)
    assert result.slope.std_dev >= 0
    assert result.intercept.std_dev >= 0


def test_fit_linear_accepts_lists():
    result = valg.fit_linear([0, 1, 2], [1, 3, 5])
    assert result.slope.nominal_value == pytest.approx(2.0, abs=1e-12)
    assert result.intercept.nominal_value == pytest.approx(1.0, abs=1e-12)


def test_fit_linear_with_noise():
    rng = np.random.default_rng(0)
    X = np.linspace(0, 10, 50)
    Y = 3.0 * X - 2.0 + rng.normal(0, 0.5, size=X.shape)
    result = valg.fit_linear(X, Y)

    assert result.slope.nominal_value == pytest.approx(3.0, abs=0.3)
    assert result.intercept.nominal_value == pytest.approx(-2.0, abs=0.5)
    assert 0.9 < result.rsq < 1.0


def test_fit_linear_weighted_prefers_low_uncertainty_points():
    X = np.array([0.0, 1.0, 2.0, 3.0])
    Y = np.array([1.0, 3.0, 5.0, 100.0])
    dY = np.array([0.1, 0.1, 0.1, 10.0])

    unweighted = valg.fit_linear(X, Y)
    weighted = valg.fit_linear(X, Y, dY=dY)

    assert weighted.slope.nominal_value == pytest.approx(2.0, abs=0.2)
    assert abs(unweighted.slope.nominal_value - 2.0) > abs(
        weighted.slope.nominal_value - 2.0
    )


def test_fit_nonlinear_quadratic():
    X = np.array([1.0, 2.0, 3.0, 4.0])

    def quadratic(x, a):
        return a * x ** 2

    Y = quadratic(X, 2.0)
    result = valg.fit_nonlinear(X, Y, quadratic, initial_guess=[1.0])

    assert len(result.parameters) == 1
    assert result.parameters[0].nominal_value == pytest.approx(2.0, abs=1e-6)
    assert result.rsq == pytest.approx(1.0, abs=1e-12)
    assert result.covariance.shape == (1, 1)


def test_fit_nonlinear_two_parameter_model():
    X = np.array([0.0, 1.0, 2.0, 3.0])

    def line(x, m, b):
        return m * x + b

    Y = line(X, 2.0, -1.0)
    result = valg.fit_nonlinear(X, Y, line, initial_guess=[1.0, 0.0])

    m, b = result.parameters
    assert m.nominal_value == pytest.approx(2.0, abs=1e-12)
    assert b.nominal_value == pytest.approx(-1.0, abs=1e-12)


@pytest.mark.parametrize(
    "X, Y, dY, error",
    [
        ([0, 1], [1, 2], None, TypeError),
        (np.array([0, 1]), [1, 2], None, TypeError),
        (np.array([0, 1]), np.array([1, 2, 3]), None, IndexError),
        (np.array([0, 1]), np.array([1, 2]), np.array([0.1]), IndexError),
        (np.array([0, 1]), np.array([1, 2]), [0.1, 0.1], TypeError),
    ],
)
def test_fit_nonlinear_input_validation(X, Y, dY, error):
    def model(x, a):
        return a * x

    with pytest.raises(error):
        valg.fit_nonlinear(X, Y, model, dY=dY)
