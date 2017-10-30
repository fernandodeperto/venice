from decimal import Decimal


class Ticker:
    def __init__(self, time, ask, bid, last, low=0, high=0, volume=0):
        self.time = time
        self.ask = Decimal(ask)
        self.bid = Decimal(bid)
        self.last = Decimal(last)
        self.low = Decimal(low)
        self.high = Decimal(high)
        self.volume = Decimal(volume)

    def __str__(self):
        return '{} ask:{}, bid:{}, last:{}, low:{}, high:{}, vol:{}'.format(
            self.time, self.ask, self.bid, self.last, self.low, self.high, self.volume)
