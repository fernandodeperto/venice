class OrderStatus:
    def __init__(self, id_, direction, type_, pair, status, volume, executed_volume, price=0,
                 price2=0, avg_price=None, remaining=None, pivot=None):
        self.id_ = id_
        self.direction = direction
        self.type_ = type_
        self.pair = pair
        self.status = status
        self.volume = volume
        self.executed_volume = executed_volume
        self.price = price
        self.price2 = price2
        self.avg_price = avg_price if avg_price else None
        self.remaining = remaining if remaining else None
        self.pivot = pivot if pivot else None

    @property
    def cost(self):
        return self.executed_volume * (self.avg_price if self.avg_price else self.price)

    def __str__(self):
        return '{} {} {:.5f}/{:.5f} {} @ {:.5f}, avg {:.5f}'.format(
            self.status, self.direction, self.executed_volume, self.volume, self.pair, self.price,
            self.avg_price)

    def __repr__(self):
        return (
            'OrderStatus(id={}, direction={}, type={}, pair={:.5f}, status={}, volume={:.5f}, '
            'executed_volume={:.5f}, price={:.5f}, price2={:.5f}, avg_price={:.5f}, '
            'remaining={:.5f}, pivot={:.5f}'.format(
                self.id_, self.direction, self.type_, self.pair, self.status, self.volume,
                self.price, self.price2, self.avg_price, self.remaining, self.pivot))
