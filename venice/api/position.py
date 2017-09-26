class Position:
    def __init__(self, position_id, direction, pair, volume, volume_closed, fee=None, margin=None,
                 net_profit=None):
        self.position_id = position_id
        self.direction = direction
        self.pair = pair
        self.volume = volume
        self.volume_closed = volume_closed
        self.fee = fee
        self.margin = margin
        self.net_profit = net_profit

    def __str__(self):
        return self.position_id
