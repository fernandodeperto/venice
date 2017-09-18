import abc
import configparser
import logging
import os.path
import smtplib

from collections import namedtuple
from email.mime.text import MIMEText

from kraken.api import KrakenAPI, KrakenError

KrakenStrategyEntry = namedtuple(
    'KrakenStrategyEntry',
    'direction order_type price price2 txid status')

KrakenStrategyEmailConfig = namedtuple(
    'KrakenStrategyEmailConfig',
    'enable fr to server port username password')


class KrakenStrategyAPI(KrakenAPI):
    api = None

    def __init__(self, pair, volume, volume2, interval):
        super().__init__()

        self.pair = pair
        self.volume = volume
        self.volume2 = volume2
        self.interval = interval

        self.ohlc = []
        self.order = None

        config = configparser.ConfigParser()
        config.read(os.path.expanduser('~') + '/.krakenst.conf')

        self.email = self._parse_email_config(**config['email'])

        self.__class__.api = self

    @staticmethod
    def _parse_email_config(enable, fr, to, server, port, username, password):
        return KrakenStrategyEmailConfig(enable, fr, to, server, port, username, password)

    def _send_email(self, subject='', message=''):
        if self.email.enable == 'true':
            try:
                with smtplib.SMTP(self.email.server, port=self.email.port) as smtp_server:
                    msg = MIMEText(message)
                    msg['Subject'] = subject
                    msg['From'] = self.email.fr
                    msg['To'] = self.email.to

                    smtp_server.starttls()
                    smtp_server.login(self.email.username, self.email.password)
                    smtp_server.send_message(msg)
            except:
                raise

    def get_ohlc(self):
        logger = logging.getLogger(__name__)

        if self.ohlc:
            try:
                ohlc = super().get_ohlc(self.pair, self.interval, since=self.ohlc[-1].time - 1)
            except:
                logger.debug('error getting updated OHLC data')
                return self.ohlc

            if ohlc[0].volume <= self.ohlc[-1].volume:
                logger.debug('invalid OHLC data')
                raise KrakenError

            if len(ohlc) > 1:
                logger.debug('add new data')

                self.ohlc[-1] = ohlc[0]
                self.ohlc.append(ohlc[1])

            else:
                logger.debug('update data')

                self.ohlc[-1] = ohlc[0]

        else:
            logger.debug('get new data')

            try:
                self.ohlc = super().get_ohlc(self.pair, self.interval)
            except:
                raise

        logger.debug(self.ohlc[-1])
        return self.ohlc

    def add_order(self, direction, order_type, price=0, price2=0):
        logger = logging.getLogger(__name__)

        if not self.order or (self.order[3] == 'closed' and self.order[0] != direction):
            logger.info('new order: %s %s @ %.3f %.3f', direction, order_type, price, price2)

            self.order = (direction, order_type, price, 'open')

            # if direction == 'sell':
            #     order = super().add_order(self.pair, direction, order_type, self.volume, price, price2)
            #     self.volume = 0

            # else:
            #     if order_type == 'market':
            #         volume = self.volume2 / self.get_price(self.pair)
            #     elif order_type in ['limit', 'stop-loss']:
            #         volume = self.volume2 / price

            #     order = super().add_order(self.pair, direction, order_type, volume, price, price2)
            #     self.volume2 = 0

            # self.order = order.txids

    def update_order(self):
        logger = logging.getLogger(__name__)

        if self.order and self.order[3] == 'open':
            if ((self.order[0] == 'buy' and self.ohlc[-1].close >= self.order[2]) or
                    (self.order[0] == 'sell' and self.ohlc[-1].close <= self.order[2])):

                logger.info('confirm order: {} {} @ {}'.format(self.order[0], self.order[1],
                                                               self.order[2]))

                try:
                    self._send_email('Confirm order', '{} {} @ {}'.format(self.order[0],
                                                                          self.order[1],
                                                                          self.order[2]))
                except Exception as e:
                    logger.debug('error sending e-mail: {}'.format(e))

                self.order = (self.order[0], self.order[1], self.order[2], 'closed')

    def cancel_order(self):
        logger = logging.getLogger(__name__)

        if self.order and self.order[3] == 'open':
            logger.info('cancel order')

            # self._send_email('Cancel order', '')

            # orders = self.query_orders(','.join(self.order))

            # for order in orders:
            #     if order.status in ['open', 'pending']:
            #         self.cancel_order(order.status)

            self.order = None


class KrakenStrategy(metaclass=abc.ABCMeta):
    def __init__(self):
        self.parse_config(self.get_config())

    def get_config(self):
        config = configparser.ConfigParser()
        config.read(os.path.expanduser('~') + '/.krakenst.conf')

        module_name = self.__module__.split('.')[-1]

        return config[module_name]

    @abc.abstractmethod
    def parse_config(self, config):
        pass

    @abc.abstractmethod
    def run(self):
        pass
