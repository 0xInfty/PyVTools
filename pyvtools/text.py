from re import findall, match
from builtins import print as _print
from typing import Tuple
from uncertainties import ufloat

#%% SINGLE STRING

def find_numbers(string):
    """Returns a list of numbers (int or float) found on a given string"""
    
    numbers = findall(r"[-+]?\d*\.\d+|[-+]?\d+", string)
    
    if not numbers:
        raise TypeError("There's no number in this string")
    
    for i, n in enumerate(numbers):
        if '.' in n:
            numbers[i] = float(n)
        else:
            numbers[i] = int(n) 
    
    return numbers

def change_separator(string, current_separator, new_separator):
    return new_separator.join(string.split(current_separator))

def break_into_lines(string):
    return change_separator(string, " ", "\n")

#%% LIST OF STRINGS

def filter_by_string_must(string_list, string_must, must=True, start_on=False, end_on=False):
    """Filters list of str by a str required to be always present or absent.
    
    Parameters
    ----------
    string_list : list of str
        The list of strings to filter.
    string_must : str
        The string, or list of strings, that must always be present or 
        always absent on each of the list elements.
    must=True : bool
        If true, then we will filter to strings that contain string_must. 
        If not, then we will filter to strings that do not contain string_must.
    start_on : bool
        If true, then we will filter to strings that start with string_must.
    end_on : bool
        If true, then we will filter to strings that end with string_must.
    
    Returns
    -------
    filtered_string_list: list of str
        The filtered list of strings.
    """
    
    if not isinstance(string_must, list):
        string_must = [string_must]

    if start_on and not end_on:
        check = lambda s, smust : s[:len(smust)] == smust
    elif end_on and not start_on:
        check = lambda s, smust : s[-len(smust):] == smust
    elif start_on and end_on:
        check = lambda s, smust : smust == s
    else:
        check = lambda s, smust : smust in s

    filtered_string_list = []
    for s in string_list:
        do_append = True
        for smust in string_must:
            if must and not check(s, smust):
                do_append = False
                break
            elif not must and check(s, smust):
                do_append = False
                break
        if do_append:
            filtered_string_list.append(s)
            
    return filtered_string_list

#%% LOGGING

class DefaultLogger:
    """Simple logger that just prints to stdout."""
    
    def __init__(self, verbose=True):
        self.verbose = verbose

    def print(self, *args, **kwargs):
        if self.verbose:
            _print(*args, **kwargs)
    
    def print_section_header(self, title, char="=", width=60):
        """Print a section header with consistent formatting."""
        self.print("")
        self.print(char * width)
        self.print(title)
        self.print(char * width)
        self.print("")
    
    def print_title(self, title, char="=", width=60):
        self.print("")
        self.print(char*3, title, char*max(3, width - len(title) - 5))
        self.print("")
    
    def print_dict(self, dictionary):
        """Print the configuration."""
        for k, v in dictionary.items():
            self.print(f"- {k} = {v}")
        self.print("")

class TextLogger(DefaultLogger):
    """Logger that writes to both stdout and a file."""
    
    def __init__(self, filepath, verbose=True):
        self.filepath = filepath
        self.file = open(filepath, 'w')
        super().__init__(verbose)
        
    def print(self, *args, **kwargs):
        msg = ' '.join(str(a) for a in args)
        if self.verbose:
            _print(msg, **kwargs)
        self.file.write(msg + '\n')
        self.file.flush()
    
    def close(self):
        self.file.close()

#%% UNCERTAINTIES

_PREFIXES = ("p", "n", r"$\mu$", "m", "", "k", "M", "G")
_SCALES = (-12, -9, -6, -3, 0, 3, 6, 9, 12)

def _select_prefix(
    order: int,
    string_scale: bool,
    one_point_scale: bool,
) -> Tuple[str, int]:
    if not string_scale or not (-12 <= order < 12):
        return "", order

    offset = -1 if one_point_scale else 0
    for i in range(len(_PREFIXES) - 1):
        if _SCALES[i] + offset <= order < _SCALES[i + 1] + offset:
            return _PREFIXES[i], _SCALES[i]
    return "", order

def _scaled_ufloat(
    value: float,
    std_dev: float,
    string_scale: bool = True,
    one_point_scale: bool = False,
) -> Tuple[ufloat, str, bool]:
    value_parts = f"{value:E}".split("E")
    value_mantissa = float(value_parts[0])
    value_order = int(value_parts[1])

    error_parts = f"{std_dev:E}".split("E")
    error_mantissa = float(error_parts[0])
    error_order = int(error_parts[1])

    prefix, scale = _select_prefix(value_order, string_scale, one_point_scale)
    used_prefix = string_scale and prefix != ""
    scaled_value = value_mantissa * 10 ** (value_order - scale)
    scaled_error = error_mantissa * 10 ** (error_order - scale)
    return ufloat(scaled_value, scaled_error), prefix, used_prefix

def _format_uncertainty(
    value: float,
    std_dev: float,
    error_digits: int = 2,
    string_scale: bool = True,
    one_point_scale: bool = False,
    latex: bool = False,
) -> str:
    if error_digits < 1:
        error_digits = 1

    u, _, _ = _scaled_ufloat(
        value,
        std_dev,
        string_scale=string_scale,
        one_point_scale=one_point_scale,
    )

    if latex:
        fmt = f"{{:.{error_digits}eL}}" if not string_scale else f"{{:.{error_digits}uL}}"
        return fmt.format(u)

    fmt = f"{{:.{error_digits}e}}" if not string_scale else f"{{:.{error_digits}u}}"
    return fmt.format(u)

def _split_formatted_uncertainty(formatted: str) -> Tuple[str, str]:
    grouped = match(r"\((.+)\+\/-(.+)\)e(.+)", formatted)
    if grouped:
        exponent = grouped.group(3)
        return f"{grouped.group(1)}E{exponent}", f"{grouped.group(2)}E{exponent}"

    value_str, error_str = formatted.split("+/-")
    return value_str, error_str

def format_value(
    value: float,
    std_dev: float,
    error_digits: int = 2,
    units: str = "",
    string_scale: bool = True,
    one_point_scale: bool = False,
) -> Tuple[str, str]:
    """Round a value and its uncertainty, returning both as strings."""
    if error_digits < 1:
        error_digits = 1

    u, prefix, _ = _scaled_ufloat(
        value,
        std_dev,
        string_scale=string_scale,
        one_point_scale=one_point_scale,
    )
    fmt = f"{{:.{error_digits}e}}" if not string_scale else f"{{:.{error_digits}u}}"
    value_str, error_str = _split_formatted_uncertainty(fmt.format(u))
    unit_suffix = f" {prefix}{units}".rstrip()
    if unit_suffix:
        return [value_str + unit_suffix, error_str + unit_suffix]
    return [value_str, error_str]

def format_value_latex(
    value: float,
    std_dev: float,
    error_digits: int = 2,
    symbol: str = r"$\pm$",
    units: str = "",
    string_scale: bool = True,
    one_point_scale: bool = False,
) -> str:
    """Round a value and its uncertainty, returning a LaTeX string."""
    body = _format_uncertainty(
        value,
        std_dev,
        error_digits=error_digits,
        string_scale=string_scale,
        one_point_scale=one_point_scale,
        latex=True,
    )

    if symbol not in (r"$\pm$", r"\pm"):
        body = body.replace(r"\pm", symbol.strip("$"))

    _, prefix, _ = _scaled_ufloat(
        value,
        std_dev,
        string_scale=string_scale,
        one_point_scale=one_point_scale,
    )
    unit_suffix = f" {prefix}{units}".rstrip()

    if not string_scale:
        return f"{body}{unit_suffix}"

    if unit_suffix:
        return f"({body}){unit_suffix}"
    return f"({body})"