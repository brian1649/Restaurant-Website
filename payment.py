class Payment():
    count_id = 0

    def __init__(self, card_name, card_no, delivery_add, expiration, cvv):
        Payment.count_id += 1
        self.__order_id = Payment.count_id
        self.__card_name = card_name
        self.__card_no = card_no
        self.__cvv = cvv
        self.__expiration = expiration
        self.__delivery_add = delivery_add




    def get_order_id(self):
        return self.__order_id

    def get_card_name(self):
        return self.__card_name

    def get_card_no(self):
        return self.__card_no

    def get_expiration(self):
        return self.__expiration

    def get_cvv(self):
        return self.__cvv

    def get_delivery_add(self):
        return self.__delivery_add

    def set_order_id(self, order_id):
        self.__order_id = order_id

    def set_card_name(self, card_name):
        self.__card_name = card_name

    def set_card_no(self, card_no):
        self.__card_no = card_no

    def set_expiration(self, expiration):
        self.__expiration = expiration

    def set_cvv(self, cvv):
        self.__cvv = cvv

    def set_delivery_add(self, delivery_add):
        self.__delivery_add = delivery_add