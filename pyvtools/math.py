import numpy as np

def round_and_clip(array, minimum=None, maximum=None, dtype=np.float32):
    """Rounds up values in an array, limiting values to [min, max]"""
    if minimum is None: minimum = np.min(array)
    if maximum is None: maximum = np.max(array)
    return np.clip(array.round(), minimum, maximum).astype(dtype)

def minmax_normalize(array, minimum=None, maximum=None, symmetric=False):
    if minimum is None: minimum = np.min(array)
    if maximum is None: maximum = np.max(array)
    if symmetric: return array * 2 / (maximum - minimum)
    return (array - minimum) / (maximum - minimum)

def invert_minmax_normalize(array, minimum, maximum):
    return array*(maximum - minimum) + minimum