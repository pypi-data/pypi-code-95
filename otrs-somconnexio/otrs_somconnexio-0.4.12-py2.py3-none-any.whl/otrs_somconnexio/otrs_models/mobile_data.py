class MobileData:
    type = 'mobile'

    def __init__(
        self, order_id, phone_number, iban, email, sc_icc, icc,
        portability, previous_owner_vat, previous_owner_name,
        previous_owner_surname, previous_provider, product, notes
    ):
        self.order_id = order_id
        self.phone_number = phone_number
        self.iban = iban
        self.email = email
        self.sc_icc = sc_icc
        self.icc = icc
        self.portability = portability
        self.previous_provider = previous_provider
        self.previous_owner_vat = previous_owner_vat
        self.previous_owner_name = previous_owner_name
        self.previous_owner_surname = previous_owner_surname
        self.product = product
        self.notes = notes
