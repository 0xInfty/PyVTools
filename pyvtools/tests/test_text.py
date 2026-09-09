import pytest

import pyvtools.text as vtext

_PREFIX_CASES = [
    ("p", -11, "p", -12),
    ("n", -8, "n", -9),
    (r"$\mu$", -5, r"$\mu$", -6),
    ("m", -2, "m", -3),
    ("", 1, "", 0),
    ("k", 4, "k", 3),
    ("M", 7, "M", 6),
]


@pytest.mark.parametrize("name, order, expected_prefix, expected_scale", _PREFIX_CASES)
def test_select_prefix_bands(name, order, expected_prefix, expected_scale):
    prefix, scale = vtext._select_prefix(order, string_scale=True, one_point_scale=False)
    assert prefix == expected_prefix
    assert scale == expected_scale


def test_select_prefix_one_point_scale_shifts_band_down():
    prefix, scale = vtext._select_prefix(-1, string_scale=True, one_point_scale=True)
    assert prefix == ""
    assert scale == 0


def test_select_prefix_disabled_when_string_scale_false():
    prefix, scale = vtext._select_prefix(-2, string_scale=False, one_point_scale=False)
    assert prefix == ""
    assert scale == -2


def test_select_prefix_out_of_range_returns_empty_prefix():
    prefix, scale = vtext._select_prefix(-13, string_scale=True, one_point_scale=False)
    assert prefix == ""
    assert scale == -13


@pytest.mark.parametrize(
    "value, std_dev, expected_nominal, expected_std_dev, expected_prefix, used_prefix",
    [
        (5e-12, 1e-13, 5.0, 0.1, "p", True),
        (5e-9, 1e-10, 5.0, 0.1, "n", True),
        (5e-6, 1e-7, 5.0, 0.1, r"$\mu$", True),
        (5e-3, 1e-4, 5.0, 0.1, "m", True),
        (5.0, 0.1, 5.0, 0.1, "", False),
        (5e3, 100.0, 5.0, 0.1, "k", True),
        (5e6, 1e5, 5.0, 0.1, "M", True),
    ],
)
def test_scaled_ufloat_applies_prefix_scaling(
    value, std_dev, expected_nominal, expected_std_dev, expected_prefix, used_prefix
):
    u, prefix, used = vtext._scaled_ufloat(value, std_dev)
    assert prefix == expected_prefix
    assert used is used_prefix
    assert u.nominal_value == pytest.approx(expected_nominal)
    assert u.std_dev == pytest.approx(expected_std_dev)


def test_scaled_ufloat_without_string_scale_omits_prefix_but_normalizes_mantissa():
    u, prefix, used = vtext._scaled_ufloat(5e-3, 1e-4, string_scale=False)
    assert prefix == ""
    assert used is False
    assert u.nominal_value == pytest.approx(5.0)
    assert u.std_dev == pytest.approx(0.1)


@pytest.mark.parametrize(
    "value, std_dev, expected_prefix, expected_value, expected_error",
    [
        (5e-12, 1e-13, "p", "5.00 pm", "0.10 pm"),
        (5e-9, 1e-10, "n", "5.00 nm", "0.10 nm"),
        (5e-6, 1e-7, r"$\mu$", r"5.00 $\mu$m", r"0.10 $\mu$m"),
        (5e-3, 1e-4, "m", "5.00 mm", "0.10 mm"),
        (5.0, 0.1, "", "5.00 m", "0.10 m"),
        (5e3, 100.0, "k", "5.00 km", "0.10 km"),
        (5e6, 1e5, "M", "5.00 Mm", "0.10 Mm"),
    ],
)
def test_format_value_si_prefixes(
    value, std_dev, expected_prefix, expected_value, expected_error
):
    result = vtext.format_value(value, std_dev, units="m")
    assert result == [expected_value, expected_error]
    assert expected_prefix in result[0]


def test_format_value_one_point_scale_shifts_prefix_for_sub_unit_values():
    normal = vtext.format_value(0.133432, 0.00133432, units="V")
    shifted = vtext.format_value(
        0.133432,
        0.00133432,
        units="V",
        one_point_scale=True,
    )
    assert normal == ["133.4 mV", "1.3 mV"]
    assert shifted == ["0.1334 V", "0.0013 V"]


def test_format_value_one_point_scale_unchanged_when_already_at_base_unit():
    value, std_dev = 5e-3, 5e-5
    normal = vtext.format_value(value, std_dev, units="V")
    shifted = vtext.format_value(
        value,
        std_dev,
        units="V",
        one_point_scale=True,
    )
    assert normal == shifted == ["5.000 mV", "0.050 mV"]


@pytest.mark.parametrize(
    "value, std_dev, kwargs, expected",
    [
        (1.325412, 0.2343413, {}, ["1.33", "0.23"]),
        (1.325412, 0.2343413, {"error_digits": 3}, ["1.325", "0.234"]),
        (
            0.133432,
            0.00332,
            {"units": "V"},
            ["133.4 mV", "3.3 mV"],
        ),
        (
            0.133432,
            0.00332,
            {"one_point_scale": True, "units": "V"},
            ["0.1334 V", "0.0033 V"],
        ),
    ],
)
def test_format_value(value, std_dev, kwargs, expected):
    assert vtext.format_value(value, std_dev, **kwargs) == expected


def test_format_value_without_prefix_scale_uses_scientific_notation():
    value, error = vtext.format_value(
        0.133432,
        0.00332,
        string_scale=False,
        units="V",
    )
    assert value.endswith("V")
    assert error.endswith("V")
    assert "E" in value
    assert "E" in error


def test_format_value_clamps_invalid_error_digits():
    value, error = vtext.format_value(1.325412, 0.2343413, error_digits=0)
    assert value == "1.3"
    assert error == "0.2"


@pytest.mark.parametrize(
    "value, std_dev, kwargs, expected_substrings",
    [
        (1.325412, 0.2343413, {}, [r"\pm", "1.33", "0.23"]),
        (
            0.133432,
            0.00332,
            {"units": "V"},
            [r"\pm", "133.4", "3.3", "mV"],
        ),
        (
            0.133432,
            0.00332,
            {"one_point_scale": True, "units": "V"},
            ["0.1334", "0.0033", "V"],
        ),
    ],
)
def test_format_value_latex(value, std_dev, kwargs, expected_substrings):
    latex = vtext.format_value_latex(value, std_dev, **kwargs)
    for substring in expected_substrings:
        assert substring in latex


def test_format_value_latex_without_prefix_scale_uses_exponent_form():
    latex = vtext.format_value_latex(
        0.133432,
        0.00332,
        string_scale=False,
        units="V",
    )
    assert r"\pm" in latex
    assert r"\times 10^{" in latex
    assert latex.endswith("V")


def test_format_value_latex_custom_symbol():
    latex = vtext.format_value_latex(1.325412, 0.2343413, symbol="$\\sim$")
    assert r"\sim" in latex
    assert r"\pm" not in latex


@pytest.mark.parametrize(
    "value, std_dev, unit_suffix",
    [
        (5e-12, 1e-13, "pm"),
        (5e-9, 1e-10, "nm"),
        (5e-6, 1e-7, r"$\mu$m"),
        (5e-3, 1e-4, "mm"),
        (5.0, 0.1, "m"),
        (5e3, 100.0, "km"),
        (5e6, 1e5, "Mm"),
    ],
)
def test_format_value_latex_places_prefix_outside_parentheses(value, std_dev, unit_suffix):
    latex = vtext.format_value_latex(value, std_dev, units="m")
    assert latex.startswith("(")
    assert r"\pm" in latex
    assert latex.endswith(unit_suffix)
    assert latex.count("(") == 1


def test_format_value_latex_one_point_scale_uses_base_unit():
    latex = vtext.format_value_latex(
        0.133432,
        0.00133432,
        units="V",
        one_point_scale=True,
    )
    assert latex == "(0.1334 \\pm 0.0013) V"
