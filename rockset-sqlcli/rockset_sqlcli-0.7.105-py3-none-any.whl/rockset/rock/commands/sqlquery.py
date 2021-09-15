from .command_auth import AuthCommand
from rockset.query import QueryStringSQLText
import sys
import time


class SQLQuery(AuthCommand):
    def usage(self):
        return """
usage: rock sql --help
       rock sql
       rock sql <sql_statement> [<args>...]

Run a sql query and return results as documents.

arguments:
  <sql-statement>       sql query to run; will read from STDIN if == '-'

examples:

  # To enter into the rock SQL REPL
  $ rock sql

  # To run a simple SQL query
  $ rock sql 'SELECT * from my_collection LIMIT 10'

  # To supply SQL from STDIN, use "-"
  $ echo 'SELECT * from my_collection LIMIT 10' | rock sql -

        """

    def validate_args(self, pargs):
        allowed_args = ['drop_results']
        for arg in pargs['<args>']:
            if arg not in allowed_args:
                return False
        return True

    def go(self):
        if not self.sql_statement:
            try:
                from rockset_sqlcli.rscli.main import cli_main
            except (ImportError, FileNotFoundError) as e:
                raise ImportError(
                    'Python package rockset_sqlcli is not installed. '
                    'Please run `pip3 install rockset_sqlcli` and try again!'
                )
            return cli_main(
                api_server=self.api_server,
                api_key=self.api_key,
                workspace='commons',
                generate_warnings=self.warn,
            )
        elif self.sql_statement == '-':
            self.sql_statement = self.read_stdin('SQL query')
        q = QueryStringSQLText(self.sql_statement)

        # lets do this
        start = time.time()
        cursor = self.client.sql(q=q, generate_warnings=self.warn)

        results = cursor.results()
        warnings = cursor.warnings()
        fields = cursor.fields() or []
        elapsed = round(1000 * (time.time() - start))
        if self.warn and warnings is not None:
            self.wprint(warnings)
        if 'drop_results' in self.args:
            print(
                'Query returned {} rows in {}ms'.format(len(results), elapsed)
            )
        else:
            self.print_list(0, results, field_order=[f['name'] for f in fields])

        return 0
