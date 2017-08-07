# import sys
import os.path
import configparser
import abc
import logging

import smtplib
from email.mime.text import MIMEText

from collections import namedtuple

from kraken.api import KrakenAPI

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
        if self.email.enable is 'true':
            with smtplib.SMTP(self.email.server, port=self.email.port) as smtp_server:
                msg = MIMEText(message)
                msg['Subject'] = subject
                msg['From'] = 'fernando@mendonca.xyz'
                msg['To'] = 'fernando@mendonca.xyz'

                smtp_server.starttls()
                smtp_server.login(self.email.username, self.email.password)
                smtp_server.send_message(msg)

    def get_ohlc(self):
        logger = logging.getLogger(__name__)

        if self.ohlc:
            ohlc = super().get_ohlc(self.pair, self.interval, since=self.ohlc[-1].time - 1)

            if len(ohlc) > 1:
                logger.debug('add new data')

                self.ohlc[-1] = ohlc[0]
                self.ohlc.append(ohlc[1])

            else:
                logger.debug('update data')

                self.ohlc[-1] = ohlc[0]

        else:
            logger.debug('get new data')

            self.ohlc = super().get_ohlc(self.pair, self.interval)

        return self.ohlc

    def add_order(self, direction, order_type, price=0, price2=0):
        logger = logging.getLogger(__name__)

        if not self.order:
            logger.info('new order: %s %s @ %.3f %.3f', direction, order_type, price, price2)

            self._send_email(
                'New order',
                '{} {} @ {} {}'.format(direction, order_type, price, price2))

            self.order = True

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

        else:
            logger.debug('order already exists')

    def update_order(self):
        pass

    def cancel_order(self):
        logger = logging.getLogger(__name__)

        if self.order:
            logger.info('cancel order')

            self._send_email('Cancel order', '')

            # orders = self.query_orders(','.join(self.order))

            # for order in orders:
            #     if order.status in ['open', 'pending']:
            #         self.cancel_order(order.status)

            # self.order = None

            self.order = None

        else:
            logger.debug('order does not exist')


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
