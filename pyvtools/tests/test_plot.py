import matplotlib.pyplot as plt
import numpy as np
import pytest

import pyvtools.algebra as valg
import pyvtools.plot as vplot


def test_annotation_positions_up():
    positions = vplot._annotation_positions((0.02, "up"), 3)
    assert positions == pytest.approx([0.9, 0.82, 0.74])


def test_annotation_positions_down():
    positions = vplot._annotation_positions((0.02, "down"), 3)
    assert positions == pytest.approx([0.05, 0.13, 0.21])


def test_annotation_positions_numeric_low():
    positions = vplot._annotation_positions((0.02, 0.05), 2)
    assert positions == pytest.approx([0.05, 0.13])


def test_plot_linear_fit_returns_axes_with_annotations():
    X = np.array([0.0, 1.0, 2.0, 3.0])
    Y = 2.0 * X + 1.0
    result = valg.fit_linear(X, Y)

    fig, ax = plt.subplots()
    returned_ax = vplot.plot_linear_fit(
        X,
        Y,
        result,
        ax=ax,
        show=False,
        text_position=(0.02, "up"),
    )

    assert returned_ax is ax
    assert len(ax.lines) == 2
    assert len(ax.get_legend().get_texts()) == 2
    assert len(ax.texts) == 3
    assert any("m =" in text.get_text() for text in ax.texts)
    assert any("b =" in text.get_text() for text in ax.texts)
    assert any(r"$R^2$" in text.get_text() for text in ax.texts)
    plt.close(fig)


def test_plot_linear_fit_with_errorbars():
    X = np.array([0.0, 1.0, 2.0, 3.0])
    Y = 2.0 * X + 1.0
    dY = np.full_like(X, 0.1)
    result = valg.fit_linear(X, Y, dY=dY)

    fig, ax = plt.subplots()
    vplot.plot_linear_fit(X, Y, result, dY=dY, ax=ax, show=False)

    assert len(ax.containers) == 1
    plt.close(fig)


def test_plot_nonlinear_fit_returns_axes_with_annotations():
    X = np.array([1.0, 2.0, 3.0, 4.0])

    def quadratic(x, a):
        return a * x ** 2

    Y = quadratic(X, 2.0)
    result = valg.fit_nonlinear(X, Y, quadratic, initial_guess=[1.0])

    fig, ax = plt.subplots()
    returned_ax = vplot.plot_nonlinear_fit(
        X, Y,
        quadratic,
        result,
        ax=ax,
        show=False,
    )

    assert returned_ax is ax
    assert len(ax.lines) == 2
    assert len(ax.texts) == 2
    assert any(r"$a_0$" in text.get_text() for text in ax.texts)
    assert any(r"$R^2$" in text.get_text() for text in ax.texts)
    plt.close(fig)
