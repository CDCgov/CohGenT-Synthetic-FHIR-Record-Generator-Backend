from random import uniform
from decimal import Decimal

def generate_number_from_range(min_value: float, max_value: float) -> float:
    # Get number of decimals for precision of return.
    precision = max(get_precision(min_value), get_precision(max_value))
    value = round(uniform(float(min_value), float(max_value)), precision)
    return value

def get_precision(value: float) -> int:
    d_value: Decimal = Decimal(value)
    d_tuple = d_value.as_tuple()
    exp = d_tuple.exponent
    return abs(exp)