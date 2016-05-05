from .money import Money
from .money import CategorizedMoney
from datetime import datetime
from collections import defaultdict

DATE_FORMAT = '%Y-%m-%d %H:%M'
COMMENT_IDICATOR = '#'


class Transaction:
    def __init__(self, date, tags=None, amount=None):
        if tags is None:
            date, tags, amount = self._parse(date)
        self.date = date
        self.tags = tuple(tags)
        self.amount = amount

    @staticmethod
    def _parse(text):
        split = text.lower().split(' ')
        date = datetime.strptime(
            split[0] + ' ' + split[1],
            DATE_FORMAT
        )
        try:
            amount = Money(split[-1])
            tags = split[2:-1]
        except:
            amount = Money(split[-2] + split[-1])
            tags = split[2:-2]
        return date, tags, amount

    def __eq__(self, other):
        return (
            self.date == other.date,
            self.tags == other.tags,
            self.amount == other.amount
        )

    def __str__(self):
        return '{} {} {}'.format(
            self.date.strftime(DATE_FORMAT),
            ' '.join(sorted(self.tags)),
            self.amount
        )


class Transactions:
    def __init__(self, transactions=None):
        if isinstance(transactions, str):
            self._transactions = self._parse(transactions)
        else:
            self._transactions = transactions or []

    @staticmethod
    def _parse(text):
        return [
            Transaction(t)
            for t in text.strip().split('\n')
            if t and not t.startswith(COMMENT_IDICATOR)
        ]

    def __len__(self):
        return len(self._transactions)

    def __getitem__(self, index):
        return self._transactions[index]

    def __eq__(self, other):
        return set(
            str(t) for t in self._transactions
        ) == set(
            str(t) for t in other._transactions
        )

    def __str__(self):
        return '\n'.join(str(t) for t in self)

    def __add__(self, other):
        return Transactions(self._transactions + other._transactions)

    def map(self, f):
        return Transactions([f(t) for t in self])

    def filter(self, f):
        return Transactions([t for t in self if f(t)])

    def sum(self):
        return sum((t.amount for t in self), Money())

    def group(self, key):
        groups = defaultdict(list)
        for transaction in self:
            groups[key(transaction)].append(transaction)
        return GroupedTransactions({
            k: Transactions(v)
            for k, v in groups.items()
        })


class GroupedTransactions:
    def __init__(self, groups):
        self._groups = groups

    def __len__(self):
        return len(self._groups)

    def __getitem__(self, key):
        return self._groups[key]

    def __str__(self):
        return '\n'.join(
            str(k) + '\n' + str(v)
            for k, v in self._groups.items()
        )

    def __eq__(self, other):
        if set(self._groups.keys()) != set(self._groups.keys()):
            return False
        for k in self._groups.keys():
            if self[k] != other[k]:
                return False
        return True


    def map(self, f):
        return GroupedTransactions({
            k: v.map(f) for k, v in self._groups.items()
        })

    def filter(self, f):
        return GroupedTransactions({
            k: v.filter(f) for k, v in self._groups.items()
        })

    def sum(self):
        return CategorizedMoney({
            k: v.sum() for k, v in self._groups.items()
        })

    def groups(self):
        return self._groups.keys()
