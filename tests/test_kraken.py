import unittest

import pprint

import kraken.kraken


class TestKraken(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_query_orders(self):
        k = kraken.kraken.Kraken()
        k.load_key('/home/fernando/.kraken.key')
        k.query_orders(['OLF5GA-E3UFL-WVFQDZ'])

    def test_get_ohlc(self):
        k = kraken.kraken.Kraken()
        k.get_ohlc('XETHZEUR', 15)

    def test_get_ticker(self):
        k = kraken.kraken.Kraken()
        k.get_ticker('XETHZEUR')

    def test_get_balance(self):
        k = kraken.kraken.Kraken()
        k.load_key('/home/fernando/.kraken.key')
        k.get_balance()

    def test_get_positions(self):
        k = kraken.kraken.Kraken()
        k.load_key('/home/fernando/.kraken.key')


