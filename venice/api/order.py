class Order:
    def __init__(self, order_id, volume, price, close_time=0, expire_time=0, open_time=0, descr='',
                 fee=0):

        self.order_id = order_id
        self.close_time = close_time
        self.descr = descr
        self.expire_time = expire_time
        self.fee = fee
        self.open_time = open_time
        self.price = price
        self.volume = volume

    def __str__(self):
        return self.descr


