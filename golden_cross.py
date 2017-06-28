import krakenex

k = krakenex.API()
k.load_key('kraken.key')

print(k.query_private('TradeBalance'))
