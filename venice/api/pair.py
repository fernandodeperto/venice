from decimal import Decimal


class Pair:
    def __init__(self, name, precision, order_min=0, order_max=None):
        self.name = name
        self.precision = precision
        self.order_min = Decimal(order_min)
        self.order_max = Decimal(order_max)

    def __repr__(self):
        return 'Pair(name={}, precision={}, order_min={}, order_max={}'.format(
            self.name, self.precision, self.order_min, self.order_max)

    def __str__(self):
        return self.name
