# Libs
import csv
from collections import defaultdict

# Own modules
from hpcparse.accounts import Accounts


class AccountsParser:

    @classmethod
    def parse_slurm_acct(cls, filepath):
        accts_list = []
        try:
            with open(filepath, 'r', newline='') as inputFile:
                records = csv.DictReader(inputFile, delimiter='|')
                for row in records:
                    row = defaultdict(lambda: None, row)
                    try:
                        new_account = Accounts()

                        new_account.account = row['Account']
                        new_account.descr = row['Descr']
                        new_account.org = row['Org']

                        accts_list.append(new_account)
                    except Exception as ex:
                        print(ex)
                        print('error')
        except Exception as ex:
            print(ex)
            print('error')
        return accts_list
