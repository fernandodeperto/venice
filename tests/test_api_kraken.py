import logging
import logging.config
import os
import unittest

from venice.api.kraken import KrakenAPI


logging.config.fileConfig('logging_tests.conf')


class TestKrakenAPI(unittest.TestCase):
    pass
