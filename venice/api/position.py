from decimal import Decimal


class Position:
    def __init__(self, position_id, direction, pair, volume, volume_closed, fee=None, margin=None,
                 net_profit=None):
        self.position_id = position_id
        self.direction = direction
        self.pair = pair
        self.volume = Decimal(volume)
        self.volume_closed = Decimal(volume_closed)
        self.fee = Decimal(fee)
        self.margin = Decimal(margin)
        self.net_profit = Decimal(net_profit)

    def __str__(self):
        return self.position_id
