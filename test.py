#!/usr/bin/python3

import sys
import krakenex
import krakenbot
import pprint
import unittest

class TestKrakenbot(unittest.TestCase):
    def setUp(self):
        self.k = krakenbot.Krakenbot('kraken.key')
        self.k.connect()

    def tearDown(self):
        self.k.close()

    def test_get_ohlc(self):
        result = self.k.get_ohlc('XETHZEUR', 15)
        self.assertTrue(result['result'])

    def test_get_ohlc_last(self):
        last = self.k.get_ohlc_last('XETHZEUR', 15)
        self.assertTrue(last)

    def test_get_average(self):
        average = self.k.get_average('XETHZEUR', 5, 15)
        self.assertTrue(average)

    def test_add_order(self):
        order = self.k.add_order('XETHZEUR', 'sell', 'limit', '0.01', price=380, validate=True)
        self.assertTrue(order['result'])

if __name__ == "__main__":
    unittest.main()
