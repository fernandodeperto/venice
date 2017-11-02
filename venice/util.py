import sys

from decimal import Decimal

EPSILON = Decimal.from_float(sys.float_info.epsilon)


def decimal_places(precision):
    return Decimal('10') ** -precision


def decimal_mult(a, b, places):
    return (a * b).quantize(places)


def decimal_div(a,  b, places):
    return (a / b).quantize(places)
