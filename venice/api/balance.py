class Balance:
    # TODO Fix the available parameter
    def __init__(self, currency, amount, available=-1, type_='exchange'):
        self.currency = currency
        self.amount = amount
        self.available = available
        self.type_ = type_

    def __repr__(self):
        return 'Balance(currency={}, amount={}, available={}, type={})'.format(
            self.currency, self.amount, self.available, self.type_)

    def __str__(self):
        return ('{}/{} {}'.format(
            self.available, self.amount, self.currency) if self.available != -1 else
            '{} {}'.format(self.amount, self.currency))
