from datetime import datetime


class N19Parser(object):
    def __init__(self, data):
        self.lines = data.decode('utf-8').split("\n")

    def get_name(self):
        presenter_header_line = next(
            line for line in self.lines if line[0:2] == '21'
        )
        return presenter_header_line[123:158]

    def parse(self):
        name = self.get_name()
        payment_return = self.parse_payment_return()
        payment_return['name'] = name
        self.parse_payment_transactions(payment_return['transactions'])
        subno = 0
        for transaction in payment_return['transactions']:
            subno += 1
            transaction['unique_import_id'] = (
                payment_return['name'] + " - " + str(subno).zfill(4)
            )
        return payment_return

    def parse_payment_return(self):
        creditor_header_line = next(line for line in self.lines if line[0:2] == '22')
        payment_return = {
            'date': datetime.strptime(creditor_header_line[45:53], '%Y%m%d'),
            'account_number': creditor_header_line[265:299].strip(),
            'transactions': [],
        }
        return payment_return

    def parse_payment_transactions(self, transactions):
        transaction_lines = [line for line in self.lines if line[0:2] == '23']
        for transaction_line in transaction_lines:
            transaction = {
                'reference': transaction_line[10:45].strip(),
                'reason_code': transaction_line[593:597],
                'amount': (
                    float(transaction_line[88:97]) +
                    (float(transaction_line[97:99]) / 100)
                ),
                'concept': transaction_line[441:581].strip(),
                'partner_name': transaction_line[126:196].strip(),
                'account_number': transaction_line[411:445].strip(),
                'raw_import_data': transaction_line,
                'mandate': transaction_line[45:80].strip(),
            }
            transactions.append(transaction)
