from .transaction import Transaction
from ..exceptions import TransactionParseError

COMMENT = '#'


def parse_transactions(text):
    def parse_transaction(text, line_number):
        try:
            return Transaction(text)
        except TransactionParseError as e:
            raise TransactionParseError(
                '{} at line: {}'.format(e, line_number + 1)
            )

    return [
        parse_transaction(t, i) for i, t in enumerate(text.splitlines())
        if t.strip() and not t.startswith(COMMENT)
    ]
