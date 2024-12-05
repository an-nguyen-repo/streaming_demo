import random

def universal_float_format(value: float) -> float:
    return float(f"{value:.3f}")


def random_float_in_range(a: float, b: float) -> float:
    return universal_float_format(random.uniform(a, b))

