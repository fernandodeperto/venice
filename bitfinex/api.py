class BitfinexAPI:
    def active_orders(self):
        """
        Fetch active orders
        """
        response = self.req('v2/auth/r/orders')
        if response.status_code == 200:
            return response.json()
        else:
            print(response.status_code)
            print(response)
            return ''
