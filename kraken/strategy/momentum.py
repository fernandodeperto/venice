from kraken.strategy import KrakenStrategy

class Momentum(KrakenStrategy):
    def parse_config(self, config):
        self.length = config['length']
