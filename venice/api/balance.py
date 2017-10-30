from decimal import Decimal


class Balance:
    def __init__(self, currency, amount, available=None, type_='exchange'):
        self.currency = currency
        self.amount = Decimal(amount)
        self.available = Decimal(available) if available else None
        self.type_ = type_

    def __repr__(self):
        return 'Balance(currency={}, amount={}, available={}, type={})'.format(
            self.currency, self.amount, self.available, self.type_)

    def __str__(self):
        return ('{}/{} {}'.format(
            self.available, self.amount, self.currency) if self.available else
            '{} {}'.format(self.amount, self.currency))
