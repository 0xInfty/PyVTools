from typing import Optional, Sequence, Tuple, Union

from matplotlib import ticker
import matplotlib.pyplot as plt
import numpy as np

import pyvtools.text as vtext
from pyvtools.algebra import LinearFitResult, NonlinearFitResult

#%% GENERAL STYLE

def set_style(params=None, params_to_exclude=None):
    """Sets academic style
    
    Source: https://github.com/0xInfty/PyMeepPlasmonics/blob/master/v_plot.py
    """
    
    default_params = {'text.usetex': False, 
                      'font.family':'serif',
                      'font.sans-serif': ['MS Reference Sans Serif', 'sans-serif'], 
                      'mathtext.fontset': 'cm', # Computer Modern
                      'font.weight':500,
                      'figure.titlesize':13,
                      'axes.titlesize':12,
                      'axes.labelsize':11,
                      'legend.fontsize':11,
                      'xtick.labelsize':10,
                      'ytick.labelsize':10,
                      'xtick.minor.visible':True,
                      'ytick.minor.visible':True,
                      'grid.alpha':0.4,
                      'axes.grid':True,
                      'xtick.color':'b0b0b0',
                      'ytick.color':'b0b0b0',
                      'xtick.labelcolor':'black',
                      'ytick.labelcolor':'black',
                      'lines.markersize':8,
                      'hatch.color':'white'}
    if params is not None:
        assert isinstance(params, dict), "new_params must be a dictionary"
        new_params = {**default_params, **params}
    else:
        new_params = default_params
    if params_to_exclude is not None:
        if not (isinstance(params_to_exclude, list) or isinstance(params_to_exclude, tuple)):
            raise ValueError("params_to_exclude must be a list or a tuple")
        for param in params_to_exclude:
            new_params.pop(param)
    plt.rcParams.update(new_params)

def reset_style():
    """Resets style to default"""
    plt.rcParams.update(plt.rcParamsDefault)

def add_style(fig=None, new_figure=False, **kwargs):
    """Gives style to figures to include in Latex PDF files.
    
    This function...
        ...increases font size;
        ...increases linewidth;
        ...increases markersize;
        ...gives format to axis ticks if specified;
        ...stablishes new figure dimensions if specified;
        ...activates grid.
    
    Source: https://github.com/0xInfty/PyMeepPlasmonics/blob/master/v_plot.py

    Parameters
    ----------
    figure_id : int, optional
        ID of the figure where the text will be printed.
        If none is given, the current figure is taken as default.
    new_figure=False : bool, optional
        Indicates whether to make a new figure or not when 
        figure_id=None.
    
    Other Parameters
    ----------------
    xaxisformat : format-like str, optional.
        Used to update x axis ticks format; i.e.: '%.2e'
    yaxisformat : format-like str, optional.
        Used to update y axis ticks format; i.e.: '%.2e'
    dimensions: list with length 4, optional.
        Used to update plot dimensions: [xmin, xmax, ymin, ymax]. Each 
        one should be a number expressed as a fraction of current 
        dimensions.
    
    See Also
    --------
    matplotlib.pyplot.axis
    matplotlib.pyplot.gcf
    """
    
    if fig is None:    
        if new_figure:
            fig = plt.figure()
        else:
            fig = plt.gcf()

    try:
        ax = fig.axes
        ax[0]
    except IndexError:
        ax = [plt.axes()]
    
    kwargs_default = dict(
            fontsize=12,
            linewidth=3,
            markersize=6,
            dimensions=[1.15,1.05,1,1],
            tight_layout=True,
            grid=False,
            xaxisformat=None,
            yaxisformat=None)
    
    kwargs = {key:kwargs.get(key, value) 
              for key, value in kwargs_default.items()}
    
    plt.rcParams.update({'font.size': kwargs['fontsize']})
    plt.rcParams.update({'lines.linewidth': kwargs['linewidth']})
    plt.rcParams.update({'lines.markersize': kwargs['markersize']})
    for a in ax:
        box = a.get_position()
        a.set_position([kwargs['dimensions'][0]*box.x0,
                        kwargs['dimensions'][1]*box.y0,
                        kwargs['dimensions'][2]*box.width,
                        kwargs['dimensions'][3]*box.height])
    
    if kwargs['xaxisformat'] is not None:
        for a in ax:
            a.xaxis.set_major_formatter(ticker.FormatStrFormatter(
                kwargs['xaxisformat']))
        
    if kwargs['yaxisformat'] is not None:
        for a in ax:
            a.yaxis.set_major_formatter(ticker.FormatStrFormatter(
                kwargs['yaxisformat']))
        
    for a in ax:
        a.grid(kwargs['grid'])
        
    fig.tight_layout = kwargs['tight_layout']
    
    plt.show()

    return fig

#%% PLOTTING FITS

def _annotation_positions(
    text_position: Tuple[float, Union[float, str]],
    count: int,
) -> list[float]:
    horizontal, vertical = text_position
    if vertical == "up":
        return [0.9 - 0.08 * i for i in range(count)]
    if vertical == "down":
        return [0.05 + 0.08 * i for i in range(count)]
    if vertical <= 0.08:
        step = 0.08
    else:
        step = -0.08
    return [vertical + step * i for i in range(count)]

def _plot_data(
    ax,
    X: np.ndarray,
    Y: np.ndarray,
    dY: Optional[np.ndarray],
    plot_some_errors: Tuple[bool, int],
) -> None:
    if dY is None:
        ax.plot(X, Y, "b.", zorder=0)
        return

    errorevery = 1
    if plot_some_errors[0]:
        errorevery = max(1, len(Y) // plot_some_errors[1])

    ax.errorbar(
        X, Y, yerr=dY,
        linestyle="", marker=".", 
        color="b", ecolor="b",
        elinewidth=1.5, errorevery=errorevery,
        zorder=0,
    )

def plot_linear_fit(
    X: np.ndarray,
    Y: np.ndarray,
    result: LinearFitResult,
    dY: Optional[np.ndarray] = None,
    ax=None,
    plot_some_errors: Tuple[bool, int] = (False, 20),
    text_position: Optional[Tuple[float, Union[float, str]]] = None,
    mb_units: Tuple[str, str] = ("", ""),
    mb_string_scale: Tuple[bool, bool] = (False, False),
    mb_error_digits: Tuple[int, int] = (3, 2),
    rsq_decimal_digits: int = 3,
    show: bool = True,
):
    """Plot data and a linear fit result."""
    X = np.asarray(X, dtype=float)
    Y = np.asarray(Y, dtype=float)

    if ax is None:
        _, ax = plt.subplots()

    _plot_data(ax, X, Y, dY, plot_some_errors)
    m = result.slope.nominal_value
    b = result.intercept.nominal_value
    ax.plot(X, m * X + b, "r-", zorder=100)
    ax.legend(["Datos", "Ajuste"])

    if text_position is None:
        text_position = (0.02, "up" if m > 1 else "down")

    vertical = _annotation_positions(text_position, 3)
    annotations = [
        (
            "m",
            result.slope,
            mb_error_digits[0],
            mb_units[0],
            mb_string_scale[0],
        ),
        (
            "b",
            result.intercept,
            mb_error_digits[1],
            mb_units[1],
            mb_string_scale[1],
        ),
    ]
    for i, (label, parameter, digits, units, scale) in enumerate(annotations):
        ax.annotate(
            label + " = " + vtext.format_value_latex(
                parameter.nominal_value, parameter.std_dev, 
                error_digits=digits, units=units, 
                string_scale=scale, one_point_scale=True),
            (text_position[0], vertical[i]),
            xycoords="axes fraction",
        )

    rsq_format = r"$R^2$ = {:." + str(rsq_decimal_digits) + "f}"
    ax.annotate(
        rsq_format.format(result.rsq),
        (text_position[0], vertical[-1]),
        xycoords="axes fraction",
    )

    if show:
        plt.show()

    return ax


def plot_nonlinear_fit(
    X: np.ndarray,
    Y: np.ndarray,
    fitfunction,
    result: NonlinearFitResult,
    dY: Optional[np.ndarray] = None,
    ax=None,
    plot_some_errors: Tuple[bool, int] = (False, 20),
    text_position: Tuple[float, Union[float, str]] = (0.02, "up"),
    par_units: Optional[Sequence[str]] = None,
    par_string_scale: Optional[Sequence[bool]] = None,
    par_error_digits: Optional[Sequence[int]] = None,
    rsq_decimal_digits: int = 3,
    show: bool = True,
):
    """Plot data and a nonlinear fit result."""
    X = np.asarray(X, dtype=float)
    Y = np.asarray(Y, dtype=float)
    n = len(result.parameters)

    if ax is None:
        _, ax = plt.subplots()

    _plot_data(ax, X, Y, dY, plot_some_errors)
    x_fit = np.linspace(min(X), max(X), 500)
    parameters = tuple(p.nominal_value for p in result.parameters)
    ax.plot(x_fit, fitfunction(x_fit, *parameters), "r-", zorder=100)
    ax.legend(["Datos", "Ajuste"])

    par_units = list(par_units or [""] * n)
    par_string_scale = list(par_string_scale or [False] * n)
    par_error_digits = list(par_error_digits or [3] * n)

    vertical = _annotation_positions(text_position, n + 1)
    for i, parameter in enumerate(result.parameters):
        ax.annotate(
            f"$a_{i}$ = "+ vtext.format_value_latex(
                parameter.nominal_value, parameter.std_dev, 
                error_digits=par_error_digits[i], units=par_units[i], 
                string_scale=par_string_scale[i], one_point_scale=True),
            (text_position[0], vertical[i]),
            xycoords="axes fraction",
        )

    rsq_format = r"$R^2$ = {:." + str(rsq_decimal_digits) + "f}"
    ax.annotate(
        rsq_format.format(result.rsq),
        (text_position[0], vertical[-1]),
        xycoords="axes fraction",
    )

    if show:
        plt.show()

    return ax