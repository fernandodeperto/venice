import unittest

from bitfinex.connection import BitfinexConnection


class TestBitfinex(unittest.TestCase):
    def test_connection(self):
        connection = BitfinexConnection(key='wCszP0cowyY7QA2AQ1onGR55pAEfZr0SAoSNEeZ3dZQ',
                                        secret='lJqiiC1hiTjioNi9mqH3lASpnfFGs2BkOiBWvDtjzDG')
        print(connection.key_info())
