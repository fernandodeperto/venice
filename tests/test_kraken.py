import unittest

import pprint

import exchange.kraken


class TestKrakenAPI(unittest.TestCase):
    # def test_public(self):
    #     with exchange.kraken.KrakenAPI() as k:
    #         result = k.query_public('Time')

    #         pprint.pprint(result)

    # def test_private(self):
    #     with exchange.kraken.KrakenAPI() as k:
    #         k.load_key('/home/fernando/.kraken.key')
    #         result = k.query_private('Balance')

    #         pprint.pprint(result)

    def test_query_order(self):
        with exchange.kraken.KrakenAPI() as k:
            k.load_key('/home/fernando/.kraken.key')
            k.query_orders(['OLF5GA-E3UFL-WVFQDZ'])

    def test_get_ohlc(self):
        with exchange.kraken.KrakenAPI() as k:
            k.get_ohlc('XETHZEUR', 15)

    def test_get_ticker(self):
        with exchange.kraken.KrakenAPI() as k:
            k.get_ticker('XETHZEUR')

    def test_get_balance(self):
        with exchange.kraken.KrakenAPI() as k:
            k.load_key('/home/fernando/.kraken.key')
            k.get_balance()

    def test_get_positions(self):
        with exchange.kraken.KrakenAPI() as k:
            k.load_key('/home/fernando/.kraken.key')
            k.get_positions()


