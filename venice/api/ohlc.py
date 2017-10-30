from decimal import Decimal


class OHLC:
    def __init__(self, time, open_, high, low, close, volume, vwap=0, count=0):
        self.time = int(time)
        self.open_ = Decimal(open_)
        self.high = Decimal(high)
        self.low = Decimal(low)
        self.close = Decimal(close)
        self.vwap = Decimal(vwap)
        self.volume = Decimal(volume)
        self.count = int(count)

    def __str__(self):
        return '{} O:{}, H:{}, L:{}, C:{}, V:{}'.format(
            self.time, self.open_, self.high, self.low, self.close, self.volume)

    def __repr__(self):
        return 'OHLC(time={}, open={}, high={}, low={}, close={}, volume={})'.format(
            self.time, self.open_, self.high, self.low, self.close, self.volume)
