class Reservation:
    count_id = 0

    def __init__(self, user_id, customer_name, dining_date, time, party_size, remarks=""):
        Reservation.count_id += 1
        self.__user_id = user_id
        self.__reservation_id = Reservation.count_id
        self.__customer_name = customer_name
        self.__dining_date = dining_date
        self.__time = time
        self.__party_size = party_size
        self.__remarks = remarks

    # Accessor methods
    def get_user_id(self):
        return self.__user_id
    def get_reservation_id(self):
        return self.__reservation_id

    def get_customer_name(self):
        return self.__customer_name

    def get_dining_date(self):
        return self.__dining_date

    def get_time(self):
        return self.__time

    def get_party_size(self):
        return self.__party_size

    def get_remarks(self):
        return self.__remarks

    # Mutator methods
    def set_user_id(self, user_id):
        self.__user_id = user_id

    def set_customer_name(self, customer_name):
        self.__customer_name = customer_name

    def set_dining_date(self, dining_date):
        self.__dining_date = dining_date

    def set_time(self, time):
        self.__time = time

    def set_party_size(self, party_size):
        self.__party_size = party_size

    def set_remarks(self, remarks):
        self.__remarks = remarks




