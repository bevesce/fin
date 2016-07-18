from collections import defaultdict
from collections import Counter

from .transactions_parser import parse_transactions
from .grouped_transactions import GroupedTransactions
from ..money import Money
from ..query import by
from ..query import query


class Transactions:
    def __init__(self, transactions=None):
        if isinstance(transactions, str):
            self._transactions = parse_transactions(transactions)
        else:
            self._transactions = transactions or []

    def __len__(self):
        return len(self._transactions)

    def __getitem__(self, index):
        return self._transactions[index]

    def __eq__(self, other):
        if not isinstance(other, Transactions):
            return False
        return Counter(
            str(t) for t in self._transactions
        ) == Counter(
            str(t) for t in other._transactions
        )

    def __str__(self):
        return '\n'.join(str(t) for t in self)

    def __add__(self, other):
        return Transactions(self._transactions + other._transactions)

    def __sub__(self, other):
        return self + other.map(lambda t: -t)

    def append(self, transaction):
        return Transactions(self._transactions + [transaction])

    def map(self, f):
        return Transactions([f(t) for t in self])

    def filter(self, f):
        if isinstance(f, str):
            f = query(f)
        return Transactions([t for t in self if f(t)])

    def sum(self):
        return sum((t.money for t in self), Money())

    def group(self, key):
        if isinstance(key, str):
            key = by(key)
        groups = defaultdict(Transactions)
        for transaction in self:
            transaction_key = key(transaction)
            groups[transaction_key] = groups[transaction_key].append(transaction)
        return GroupedTransactions(dict(groups))
