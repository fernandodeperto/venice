import unittest

import pprint

import kraken


class TestKraken(unittest.TestCase):
    def test_get_assets_info(self):
        k = kraken.KrakenAPI()
        k.get_assets_info('ETH')

    # def test_query_orders(self):
    #     k = kraken.KrakenAPI()
    #     k.load_key('/home/fernando/.kraken.key')
    #     k.query_orders(['OLF5GA-E3UFL-WVFQDZ'])

    # def test_get_ohlc(self):
    #     k = kraken.KrakenAPI()
    #     k.get_ohlc('XETHZEUR', 15)

    # def test_get_ticker(self):
    #     k = kraken.KrakenAPI()
    #     k.get_ticker('XETHZEUR')

    # def test_get_balance(self):
    #     k = kraken.KrakenAPI()
    #     k.load_key('/home/fernando/.kraken.key')
    #     k.get_balance()

    # def test_get_positions(self):
    #     k = kraken.KrakenAPI()
    #     k.load_key('/home/fernando/.kraken.key')
