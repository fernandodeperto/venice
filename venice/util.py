from decimal import Decimal


def decimal_places(precision):
    return Decimal('10') ** -precision


def decimal_mult(a, b, places):
    return (a * b).quantize(places)


def decimal_div(a,  b, places):
    return (a / b).quantize(places)
