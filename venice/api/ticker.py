class Ticker:
    def __init__(self, time, ask, bid, last, low=0, high=0, volume=0):
        self.time = time
        self.ask = float(ask)
        self.bid = float(bid)
        self.last = float(last)
        self.low = float(low)
        self.high = float(high)
        self.volume = float(volume)

    def __str__(self):
        return '{} ask:{}, bid:{}, last:{}, low:{}, high:{}, vol:{}'.format(
            self.time, self.ask, self.bid, self.last, self.low, self.high, self.volume)
