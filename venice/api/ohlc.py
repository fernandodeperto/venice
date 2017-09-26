class OHLC:
    def __init__(self, time, open_, high, low, close, vwap, volume, count):
        self.time = int(time)
        self.open_ = float(open_)
        self.high = float(high)
        self.low = float(low)
        self.close = float(close)
        self.vwap = float(vwap)
        self.volume = float(volume)
        self.count = int(count)

    def __str__(self):
        return '{} O:{}, H:{}, L:{}, C:{}, V:{}'.format(
            self.time, self.open_, self.high, self.low, self.close, self.volume)
