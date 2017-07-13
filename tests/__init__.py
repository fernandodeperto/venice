import sys
import krakenex
import krakencli
import pprint
import unittest

class TestKrakencli(unittest.TestCase):
    def setUp(self):
        self.k = krakencli.Krakencli('kraken.key')
        self.k.connect()

    def tearDown(self):
        self.k.close()

    def sample_test(self):
        pass


def main():
    unittest.main()
