class ExchangeAPIException(Exception):
    pass


class ExchangeAPI:
    # Order types
    MARKET = 'market'
    LIMIT = 'limit'
    STOP = 'stop'
    TRAILING_STOP = 'trailing stop'
    STOP_AND_LIMIT = 'stop_and_limit'

    ORDER_TYPES = [MARKET, LIMIT, STOP, STOP_AND_LIMIT]

    # Currencies
    BTC = 'btc'
    ETH = 'eth'
    LTC = 'ltc'
    IOT = 'iot'
    DSH = 'dsh'
    BCH = 'bch'
    USD = 'usd'

    CURRENCIES = [BTC, ETH, LTC, BCH, USD]

    # Pairs
    BTCUSD = 'btcusd'
    ETHUSD = 'ethusd'
    LTCUSD = 'ltcusd'
    IOTUSD = 'iotusd'
    DSHUSD = 'dshusd'
    BCHUSD = 'bchusd'

    PAIRS = [BTCUSD, ETHUSD, LTCUSD, IOTUSD, DSHUSD, BCHUSD]

    # Candle period
    P5 = '5'
    P15 = '15'
    P30 = '30'
    P1H = '1h'
    P3H = '3h'
    P4H = '4h'

    PERIODS = [P5, P15, P30, P1H, P3H, P4H]

    # Order direction
    BUY = 'buy'
    SELL = 'sell'

    DIRECTIONS = [BUY, SELL]

    # Order status
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    CANCELED = 'canceled'

    def __init__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        pass

    def active_orders(self, pair=None):
        raise NotImplementedError

    def add_order(self, pair, direction, type_, volume, price=0, price2=0):
        raise NotImplementedError

    def balance(self, pair=None):
        raise NotImplementedError

    def cancel_all_orders(self):
        raise NotImplementedError

    def cancel_order(self, id_):
        raise NotImplementedError

    def cancel_orders(self, ids):
        raise NotImplementedError

    @staticmethod
    def currencies(pair):
        return pair[0:3], pair[3:6]

    def ohlc(self, pair, interval, limit=100):
        raise NotImplementedError

    def order_history(self, pair=None, limit=100):
        raise NotImplementedError

    def order_status(self, id_):
        raise NotImplementedError

    def pairs(self):
        raise NotImplementedError

    def ticker(self, pair):
        raise NotImplementedError
