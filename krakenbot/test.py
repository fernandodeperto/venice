#!/usr/bin/python3

import sys
import krakenex
import krakenbot
import pprint
import unittest
import http

class TestKrakenbot(unittest.TestCase):
    def setUp(self):
        self.k = krakenbot.Krakenbot('kraken.key')
        self.k.connect()

    def tearDown(self):
        self.k.close()

    def test_get_ohlc(self):
        result = self.k.get_ohlc('XETHZEUR', 15)

    def test_get_ohlc_last(self):
        last = self.k.get_ohlc_last('XETHZEUR', 15)

    def test_get_average(self):
        average = self.k.get_average('XETHZEUR', 5, 15)

    def test_add_order(self):
        order = self.k.add_order('XETHZEUR', 'sell', 'limit', '0.01', price=380, validate=True)

    def test_query_orders(self):
        result = self.k.query_orders('OQCE6B-JJDBV-3VKBHJ')

    def test_get_ticker(self):
        result = self.k.get_ticker('XETHZEUR')

    def test_get_price(self):
        price = self.k.get_price('XETHZEUR')

if __name__ == "__main__":
    unittest.main()
