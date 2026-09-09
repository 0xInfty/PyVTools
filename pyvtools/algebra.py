from dataclasses import dataclass
from math import sqrt
from typing import Callable, Optional, Sequence, Tuple, Union

import numpy as np
from scipy.optimize import curve_fit
from uncertainties import ufloat

#%% NORMALIZATION

def minmax_normalize(array, minimum=None, maximum=None, symmetric=False):
    if minimum is None: minimum = np.min(array)
    if maximum is None: maximum = np.max(array)
    if symmetric: return array * 2 / (maximum - minimum)
    return (array - minimum) / (maximum - minimum)

def invert_minmax_normalize(array, minimum, maximum):
    return array*(maximum - minimum) + minimum

#%% QUANTIZATION

def round_and_clip(array, minimum=None, maximum=None, dtype=np.float32):
    """Rounds up values in an array, limiting values to [min, max]"""
    if minimum is None: minimum = np.min(array)
    if maximum is None: maximum = np.max(array)
    return np.clip(array.round(), minimum, maximum).astype(dtype)

#%% INTERPOLATION

def sinc_interpolation(signal, interpolation_factor):
  """Credit to Oliver Neill, 2024"""

  # Get Fourier transform
  N = len(signal)
  fourier = np.fft.fft(signal, norm="ortho")

  # Pad Fourier transform with zeroes
  fourier_2 = np.pad(fourier, [0, (interpolation_factor-1)*N])

  # Transform back from Fourier space
  signal_2 = np.fft.ifft(fourier_2, norm="ortho")
  
  return np.sqrt(interpolation_factor)*signal_2 # renormalise

#%% FITTING

Bounds = Union[Tuple[float, float], Tuple[Sequence[float], Sequence[float]]]

@dataclass(frozen=True)
class LinearFitResult:
    slope: ufloat
    intercept: ufloat
    rsq: float

@dataclass(frozen=True)
class NonlinearFitResult:
    parameters: Tuple[ufloat, ...]
    rsq: float
    covariance: np.ndarray

def r_squared(Y: np.ndarray, Y_fit: np.ndarray) -> float:
    ss_res = np.sum((Y - Y_fit) ** 2)
    ss_tot = np.sum((Y - np.mean(Y)) ** 2)
    return 1 - ss_res / ss_tot

def fit_linear(
    X: np.ndarray,
    Y: np.ndarray,
    dY: Optional[np.ndarray] = None,
) -> LinearFitResult:
    """Apply a linear fit y = m*x + b.

    Parameters
    ----------
    X, Y : array-like
        Data to fit.
    dY : array-like, optional
        Standard deviation of Y. When given, a weighted least-squares fit
        is used.

    Returns
    -------
    LinearFitResult
        Slope and intercept as ``ufloat`` values, plus R².

    Notes
    -----
    The returned R² does not take ``dY`` weights into account.
    """
    X = np.asarray(X, dtype=float)
    Y = np.asarray(Y, dtype=float)
    weights = None if dY is None else 1 / np.asarray(dY, dtype=float) ** 2

    coeffs, cov = np.polyfit(X, Y, 1, cov=True, w=weights)
    m, b = coeffs
    dm = sqrt(cov[0, 0])
    db = sqrt(cov[1, 1])
    rsq = r_squared(Y, m * X + b)

    return LinearFitResult(
        slope=ufloat(m, dm),
        intercept=ufloat(b, db),
        rsq=rsq,
    )

def fit_nonlinear(
    X: np.ndarray,
    Y: np.ndarray,
    fitfunction: Callable,
    initial_guess: Optional[Sequence[float]] = None,
    dY: Optional[np.ndarray] = None,
    parameters_bounds: Bounds = (-np.inf, np.inf),
) -> NonlinearFitResult:
    """Apply a nonlinear least-squares fit.

    Parameters
    ----------
    X, Y : np.ndarray
        Data to fit.
    fitfunction : callable
        Model function ``f(X, a0, a1, ...) -> Y``.
    initial_guess : sequence of float, optional
        Starting values for the fit parameters.
    dY : np.ndarray, optional
        Standard deviation of Y. When given, a weighted least-squares fit
        is used.
    parameters_bounds : tuple, optional
        Lower and upper bounds passed to :func:`scipy.optimize.curve_fit`.

    Returns
    -------
    NonlinearFitResult
        Fit parameters as ``ufloat`` values, plus R² and the covariance
        matrix.

    Notes
    -----
    The returned R² does not take ``dY`` weights into account.
    """
    if not isinstance(X, np.ndarray):
        raise TypeError("X should be a np.array")
    if not isinstance(Y, np.ndarray):
        raise TypeError("Y should be a np.array")
    if dY is not None and not isinstance(dY, np.ndarray):
        raise TypeError("dY should be a np.array")
    if len(X) != len(Y):
        raise IndexError("X and Y must have same length")
    if dY is not None and len(dY) != len(Y):
        raise IndexError("dY and Y must have same length")

    sigma = dY
    parameters, covariance = curve_fit(
        fitfunction,
        X, Y,
        p0=initial_guess,
        sigma=sigma,
        absolute_sigma=dY is not None,
        bounds=parameters_bounds,
    )
    rsq = r_squared(Y, fitfunction(X, *parameters))
    fit_parameters = tuple(
        ufloat(value, sqrt(covariance[i, i]))
        for i, value in enumerate(parameters)
    )

    return NonlinearFitResult(
        parameters=fit_parameters,
        rsq=rsq,
        covariance=covariance,
    )
