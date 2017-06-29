#!/usr/bin/python3

import sys
import krakenex
import krakenbot
import pprint
import unittest

class TestKrakenbot(unittest.TestCase):
    def setUp(self):
        self.k = krakenex.API()
        self.k.load_key("kraken.key")

        self.c = krakenex.Connection()
        self.k.set_connection(self.c)

    def tearDown(self):
        self.c.close()

    def test_get_ohlc(self):
        result = krakenbot.get_ohlc(self.k, 'XETHZEUR', 15)
        self.assertTrue(result['result'])

    def test_get_ohlc_last(self):
        last = krakenbot.get_ohlc_last(self.k, 'XETHZEUR', 15)
        self.assertTrue(last)

    def test_get_average(self):
        average = krakenbot.get_average(self.k, 'XETHZEUR', 5, 15)
        self.assertTrue(average)

    def test_add_order(self):
        order = krakenbot.add_order(self.k, 'XETHZEUR', 'sell', 'limit', '0.01', price=380, validate=True)
        self.assertTrue(order['result'])

if __name__ == "__main__":
    unittest.main()
