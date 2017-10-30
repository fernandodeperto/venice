from decimal import Decimal


class Order:
    def __init__(self, id_, direction, type_, pair, status, volume, price=0, price2=0,
                 avg_price=None, remaining=None):
        self.id_ = id_
        self.direction = direction
        self.type_ = type_
        self.pair = pair
        self.status = status
        self.volume = Decimal(volume)
        self.price = Decimal(price)
        self.price2 = Decimal(price2)
        self.avg_price = Decimal(avg_price) if avg_price else None
        self.remaining = Decimal(remaining) if remaining else None

    def __str__(self):
        if self.price:
            if self.price2:
                return '{} {} {} @ {} stop {}'.format(
                    self.direction, self.volume, self.pair, self.price, self.price2)
            else:
                return '{} {} {} @ {}'.format(self.direction, self.volume, self.pair, self.price)
        else:
                return '{} {} {}'.format(self.direction, self.volume, self.pair)

    def __repr__(self):
        return (
            'Order(id={}, direction={}, type={}, pair={}, status={}, volume={}, price={},'
            'price2={}, avg_price={}, remaining={}'.format(
                self.id_, self.direction, self.type_, self.pair, self.status, self.volume,
                self.price, self.price2, self.avg_price, self.remaining))
