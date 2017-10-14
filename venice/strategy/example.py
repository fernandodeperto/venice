import logging

from .strategy import Strategy


class ExampleStrategy(Strategy):
    def __init__(self, api, intensity, **kwargs):
        super().__init__(api, **kwargs)

        self._intensity = intensity

    def help_text():
        return 'Example strategy'

    def configure_parser(parser):
        parser.add_argument('intensity', type=int, help='strategy intensity')

    def run(self):
        logger = logging.getLogger(__name__)

        # ticker = self._api.ticker()
        # logger.debug('Ticker: {}'.format(ticker))

        # ohlc = self._api.ohlc()
        # logger.debug('OHLC: {}'.format(ohlc))

        # hl2 = self._api.hl2()
        # logger.debug('hl2={}'.format(hl2))

        # order = self._api.order_buy('TestOrder', 1, limit=30, stop=60)
        # logger.debug('order={}'.format(order))

        logger.debug('Running example strategy with intensity {}'.format(self._intensity))

        return None
