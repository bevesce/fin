class ParseError(Exception):
    pass


class MoneyParseError(ParseError):
    pass


class TransactionParseError(ParseError):
    pass
